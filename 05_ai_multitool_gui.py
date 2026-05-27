import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image
import pyttsx3
import speech_recognition as sr
from deep_translator import GoogleTranslator

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wielofunkcyjny Kombajn AI (Ćwiczenie 5)")
        self.root.geometry("700x550")
        
  
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
      
        self.create_tab_translation()
        self.create_tab_speech_to_text()
        self.create_tab_text_to_speech()
        self.create_tab_vit_classifier()
        
    
        tk.Label(root, text="Logi systemowe:").pack(anchor='w', padx=10)
        self.log_area = scrolledtext.ScrolledText(root, height=8, state='disabled')
        self.log_area.pack(fill='x', padx=10, pady=(0, 10))
        self.log("Aplikacja uruchomiona pomyślnie.")

    def log(self, message):
        """Dodaje wpis do okna logów."""
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        self.root.update()

    # ==========================================
    # ZAKŁADKA 1: TŁUMACZ (Ćwiczenie 1)
    # ==========================================
    def create_tab_translation(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Tłumacz (Tekst)")
        
        tk.Label(tab, text="Wybierz plik tekstowy (.txt) do przetłumaczenia:").pack(pady=10)
        
        self.lbl_trans_file = tk.Label(tab, text="Brak wybranego pliku", fg="blue")
        self.lbl_trans_file.pack()
        self.trans_filepath = None
        
        tk.Button(tab, text="Wybierz plik", command=self.select_trans_file).pack(pady=5)
        tk.Button(tab, text="Przetłumacz na Angielski i Zapisz", command=self.run_translation).pack(pady=20)

    def select_trans_file(self):
        self.trans_filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.trans_filepath:
            self.lbl_trans_file.config(text=os.path.basename(self.trans_filepath))

    def run_translation(self):
        if not self.trans_filepath:
            messagebox.showwarning("Błąd", "Wybierz najpierw plik tekstowy!")
            return
        try:
            with open(self.trans_filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            translated = GoogleTranslator(source='auto', target='en').translate(text)
            
            save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(translated)
                self.log(f"Przetłumaczono i zapisano w: {save_path}")
        except Exception as e:
            self.log(f"Błąd tłumaczenia: {e}")

    # ==========================================
    # ZAKŁADKA 2: ROZPOZNAWANIE MOWY (Ćwiczenie 2)
    # ==========================================
    def create_tab_speech_to_text(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Mowa na Tekst (STT)")
        
        tk.Label(tab, text="Wybierz plik audio (.wav), aby wyciągnąć z niego tekst:").pack(pady=10)
        self.lbl_stt_file = tk.Label(tab, text="Brak pliku", fg="blue")
        self.lbl_stt_file.pack()
        self.stt_filepath = None
        
        tk.Button(tab, text="Wybierz plik WAV", command=self.select_stt_file).pack(pady=5)
        tk.Button(tab, text="Rozpoznaj mowę i Zapisz jako TXT", command=self.run_stt).pack(pady=20)

    def select_stt_file(self):
        self.stt_filepath = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav")])
        if self.stt_filepath:
            self.lbl_stt_file.config(text=os.path.basename(self.stt_filepath))

    def run_stt(self):
        if not self.stt_filepath:
            messagebox.showwarning("Błąd", "Wybierz plik .wav!")
            return
        
        recognizer = sr.Recognizer()
        try:
            self.log("Trwa analiza dźwięku...")
            with sr.AudioFile(self.stt_filepath) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language="pl-PL")
            
            save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.log(f"Rozpoznano mowę. Zapisano tekst w: {save_path}")
        except sr.UnknownValueError:
            self.log("Błąd: Nie rozpoznano żadnych słów w pliku audio.")
        except Exception as e:
            self.log(f"Błąd STT: {e}")

    # ==========================================
    # ZAKŁADKA 3: SYNTEZA MOWY (Ćwiczenie 3)
    # ==========================================
    def create_tab_text_to_speech(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Tekst na Mowę (TTS)")
        
        tk.Label(tab, text="Wpisz tekst do syntezy:").pack(pady=5)
        self.tts_text = tk.Text(tab, height=5, width=50)
        self.tts_text.pack(pady=5)
        
        tk.Label(tab, text="Tempo mowy:").pack()
        self.tts_rate = tk.Scale(tab, from_=50, to=300, orient='horizontal')
        self.tts_rate.set(150)
        self.tts_rate.pack(pady=5)
        
        tk.Button(tab, text="Generuj Mowę i Zapisz (WAV)", command=self.run_tts).pack(pady=10)

    def run_tts(self):
        text = self.tts_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Błąd", "Wpisz tekst do przeczytania!")
            return
            
        save_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Audio files", "*.wav")])
        if not save_path: return
        
        try:
            self.log("Generowanie mowy...")
            engine = pyttsx3.init()
            engine.setProperty('rate', self.tts_rate.get())
            engine.save_to_file(text, save_path)
            engine.runAndWait()
            self.log(f"Wygenerowano dźwięk do pliku: {save_path}")
        except Exception as e:
            self.log(f"Błąd TTS: {e}")

    # ==========================================
    # ZAKŁADKA 4: KLASYFIKACJA ViT (Ćwiczenie 5)
    # ==========================================
    def create_tab_vit_classifier(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Klasyfikacja Obrazów (ViT)")
        
        tk.Label(tab, text="Wybierz folder zawierający obrazy (JPG/PNG):").pack(pady=10)
        self.lbl_vit_folder = tk.Label(tab, text="Brak folderu", fg="blue")
        self.lbl_vit_folder.pack()
        self.vit_folderpath = None
        
        tk.Button(tab, text="Wybierz folder", command=self.select_vit_folder).pack(pady=5)
        tk.Button(tab, text="Rozpocznij Klasyfikację (Model HF)", command=self.run_vit).pack(pady=20)

    def select_vit_folder(self):
        self.vit_folderpath = filedialog.askdirectory()
        if self.vit_folderpath:
            self.lbl_vit_folder.config(text=self.vit_folderpath)

    def load_model(self):
        """Ładowanie modelu i procesora z pliku token.txt"""
        if not os.path.exists("token.txt"):
            raise FileNotFoundError("Brak pliku token.txt w głównym folderze!")
            
        with open("token.txt", "r") as f:
            token = f.read().strip()
            
        self.log("Ładowanie modelu google/vit-base-patch16-224 z Hugging Face...")
        processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224', token=token)
        model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224', token=token)
        return processor, model

    def classify_image(self, image_path, processor, model):
        """Pojedyncza klasyfikacja obrazu"""
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_idx = logits.argmax(-1).item()
        return model.config.id2label[predicted_class_idx]

    def process_images(self, folder_path, processor, model):
        """Przetwarzanie wsadowe z zapisem do pliku"""
        results = []
        valid_ext = ('.jpg', '.jpeg', '.png')
        
        for file in os.listdir(folder_path):
            if file.lower().endswith(valid_ext):
                img_path = os.path.join(folder_path, file)
                self.log(f"Klasyfikowanie: {file}...")
                label = self.classify_image(img_path, processor, model)
                results.append(f"{file}: {label}")
                
        # Zapis do pliku
        output_file = os.path.join(folder_path, "wyniki_klasyfikacji.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(results))
            
        self.log(f"Zakończono! Wyniki zapisano w: {output_file}")

    def run_vit(self):
        if not self.vit_folderpath:
            messagebox.showwarning("Błąd", "Najpierw wybierz folder z obrazami!")
            return
            
        try:
            processor, model = self.load_model()
            self.process_images(self.vit_folderpath, processor, model)
            messagebox.showinfo("Sukces", "Klasyfikacja zakończona pomyślnie!")
        except FileNotFoundError as fnf:
            messagebox.showerror("Błąd Autoryzacji", str(fnf))
            self.log("Upewnij się, że plik token.txt istnieje i zawiera token.")
        except Exception as e:
            self.log(f"Błąd krytyczny ViT: {e}")
            messagebox.showerror("Błąd", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()
