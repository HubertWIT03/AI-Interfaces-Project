import os
import time
import numpy as np
import sounddevice as sd
import soundfile as sf
import librosa
from scipy.signal import butter, lfilter
import torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, WhisperProcessor, WhisperForConditionalGeneration
import evaluate

SAMPLE_RATE = 16000  
DURATION = 10       

t
WAV2VEC_MODEL = "jonatasgrosman/wav2vec2-large-xlsr-53-polish"
WHISPER_MODEL = "openai/whisper-small" 

device = "cuda" if torch.cuda.is_available() else "cpu"


def detect_noise_level(audio_data):
    """Wykrywa poziom szumu (RMS - Root Mean Square)."""
    rms = np.sqrt(np.mean(audio_data**2))
    dbFS = 20 * np.log10(rms) if rms > 0 else -100
    print(f"[Analiza] Średni poziom głośności/szumu: {dbFS:.2f} dBFS")
    return dbFS

def apply_lowpass_filter(data, cutoff_freq=4000, sr=SAMPLE_RATE, order=5):
    """
    Stosuje filtr dolnoprzepustowy (usuwa wysokie szumy/piski).
    Parametry (cutoff_freq) można regulować ręcznie.
    """
    print(f"[Filtracja] Aplikowanie filtru dolnoprzepustowego (odcięcie: {cutoff_freq}Hz)...")
    nyq = 0.5 * sr
    normal_cutoff = cutoff_freq / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = lfilter(b, a, data)
    return filtered_data

def record_from_microphone(filename="nagranie_z_mikrofonu.wav"):
    """Nagrywa dźwięk z mikrofonu systemowego."""
    print(f"\n[Mikrofon] Nagrywanie rozpocznie się za 2 sekundy. Mów przez {DURATION} sekund...")
    time.sleep(2)
    print(">>> NAGRYWANIE TRWA <<<")
    
    
    audio_data = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait() 
    
    print(">>> KONIEC NAGRYWANIA <<<")
    audio_data = audio_data.flatten()
    
    
    sf.write(filename, audio_data, SAMPLE_RATE)
    return audio_data, filename

def process_audio_file(filepath, apply_filter=False, cutoff=4000):
    """Wczytuje, bada szum i opcjonalnie filtruje dźwięk."""
    print(f"\n--- Przetwarzanie pliku: {filepath} ---")
    audio, sr = librosa.load(filepath, sr=SAMPLE_RATE)
    
    detect_noise_level(audio)
    
    if apply_filter:
        audio = apply_lowpass_filter(audio, cutoff_freq=cutoff, sr=sr)
        
        filepath = filepath.replace(".wav", "_filtered.wav")
        sf.write(filepath, audio, SAMPLE_RATE)
        
    return audio, filepath


def transcribe_wav2vec(filepath):
    print("[Wav2Vec2] Ładowanie modelu...")
    processor = Wav2Vec2Processor.from_pretrained(WAV2VEC_MODEL)
    model = Wav2Vec2ForCTC.from_pretrained(WAV2VEC_MODEL).to(device)
    
    audio, _ = librosa.load(filepath, sr=16000)
    inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True).to(device)
    
    with torch.no_grad():
        logits = model(inputs.input_values).logits
        
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)[0]
    return transcription

def transcribe_whisper(filepath):
    print("[Whisper] Ładowanie modelu...")
    processor = WhisperProcessor.from_pretrained(WHISPER_MODEL)
    model = WhisperForConditionalGeneration.from_pretrained(WHISPER_MODEL).to(device)
    
    audio, _ = librosa.load(filepath, sr=16000)
    input_features = processor(audio, sampling_rate=16000, return_tensors="pt").input_features.to(device) 
    
   
    forced_decoder_ids = processor.get_decoder_prompt_ids(language="polish", task="transcribe")
    
    with torch.no_grad():
        predicted_ids = model.generate(input_features, forced_decoder_ids=forced_decoder_ids)
        
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
    return transcription

def compare_transcriptions(reference_text, hyp_w2v, hyp_whisper):
    """Oblicza dokładność rozpoznania (np. Word Error Rate)."""
    wer_metric = evaluate.load("wer")
    
    
    ref = reference_text.lower()
    h_w2v = hyp_w2v.lower()
    h_whi = hyp_whisper.lower()
    
    wer_w2v = wer_metric.compute(predictions=[h_w2v], references=[ref])
    wer_whi = wer_metric.compute(predictions=[h_whi], references=[ref])
    
    print("\n========= RAPORT PORÓWNAWCZY =========")
    print(f"Tekst oryginalny: {reference_text}")
    print("-" * 40)
    print(f"Wav2Vec2  : {hyp_w2v}")
    print(f"Błąd (WER): {wer_w2v:.2%} (Im mniej, tym lepiej)")
    print("-" * 40)
    print(f"Whisper   : {hyp_whisper}")
    print(f"Błąd (WER): {wer_whi:.2%} (Im mniej, tym lepiej)")
    print("========================================")


def main():
    print("Wybierz tryb działania:")
    print("1. Przetestuj gotowe pliki audio (czysty i zaszumiony)")
    print("2. Nagraj dźwięk z mikrofonu na żywo")
    
    wybor = input("Twój wybór (1/2): ")
    
    reference_text = input("Podaj poprawny tekst (transkrypt), aby móc porównać wyniki: ")
    
    if wybor == '1':
        file_path = input("Podaj ścieżkę do pliku WAV (np. czysty.wav): ")
        if not os.path.exists(file_path):
            print("Plik nie istnieje!")
            return
            
        use_filter = input("Zastosować filtrację szumów? (t/n): ").lower() == 't'
        _, final_path = process_audio_file(file_path, apply_filter=use_filter)
        
        t_w2v = transcribe_wav2vec(final_path)
        t_whi = transcribe_whisper(final_path)
        
        compare_transcriptions(reference_text, t_w2v, t_whi)
        
    elif wybor == '2':
        _, saved_path = record_from_microphone()
        
        use_filter = input("Zastosować filtrację zarejestrowanego dźwięku? (t/n): ").lower() == 't'
        if use_filter:
            _, final_path = process_audio_file(saved_path, apply_filter=True)
        else:
            final_path = saved_path
            
        t_w2v = transcribe_wav2vec(final_path)
        t_whi = transcribe_whisper(final_path)
        
        compare_transcriptions(reference_text, t_w2v, t_whi)
        
    else:
        print("Niepoprawny wybór.")

if __name__ == "__main__":
    main()
