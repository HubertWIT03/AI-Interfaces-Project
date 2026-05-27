import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image
import pyttsx3
import speech_recognition as sr
from deep_translator import GoogleTranslator
import pdfplumber
from docx import Document
import easyocr

class KustoszAI_App:
    def __init__(self, root):
        self.root = root
        self.root.title("Kustosz AI - Asystent Archiwisty Muzealnego")
        self.root.geometry("800x650")
        self.root.configure(padx=10, pady=10)
        
        # Inicjalizacja czytnika OCR (leniwe ładowanie)
        self.ocr_reader = None

        # Tytuł główny
        tk.Label(root, text="Kustosz AI: Cyfryzacja i Analiza Zbiorów", font=("Helvetica", 16, "bold")).pack(pady=(0, 10))

        # Zakładki (Notebook)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        # Tworzenie poszczególnych paneli
        self.create_tab_ocr()       # Ćw 4
        self.create_tab_translate() # Ćw 1
        self.create_tab_stt()       # Ćw 2
        self.create_tab_tts()       # Ćw 3
        self.create_tab_vit()       # Ćw 5

        # Okno logów do komunikacji z użytkownikiem
        tk.Label(root, text="Dziennik operacji (Logi):", font=("Helvetica", 10, "bold")).pack(anchor='w', pady=(10, 0))
        self.log_area = scrolledtext.ScrolledText(root, height=8, state='disabled', bg="#f0f0f0")
        self.log_area.pack(fill='x')
        self.log("Aplikacja Kustosz AI została uruchomiona pomyślnie. Gotowy do pracy.")

    def log(self, message):
        """Dodaje wpis do dziennika logów."""
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, "> " + message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')
        self.root.update()

    # ==========================================
    # ZAKŁADKA 1: CYFRYZACJA (Ekstrakcja tekstu - Ćw 4)
    # ==========================================
    def create_tab_ocr(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="1. Cyfryzacja (OCR/Dokumenty)")
        
        tk.Label(tab, text="Odczytywanie tekstu z plików PDF, DOCX oraz skanów (JPG/PNG).").pack(pady=10)
        self.lbl_ocr_file = tk.Label(tab, text="Brak wybranego pliku", fg="red")
        self.lbl_ocr_file.pack()
        self.ocr_filepath = None
        
        tk.Button(tab, text="Wybierz plik", width=20, command=self.select_ocr_file).pack(pady=5)
        tk.Button(tab, text="Wyciągnij tekst i zapisz do TXT", width=30, bg="lightblue", command=self.run_ocr).pack(pady=20)

    def select_ocr_file(self):
        self.ocr_filepath = filedialog.askopenfilename(filetypes=[("Obsługiwane", "*.pdf *.docx *.png *.jpg *.jpeg")])
        if self.ocr_filepath:
            self.lbl_ocr_file.config(text=os.path.basename(self.ocr_filepath), fg="green")

    def run_ocr(self):
        if not self.ocr_filepath:
            messagebox.showwarning("Błąd", "Najpierw wybierz plik do cyfryzacji!")
            return
            
        ext = os.path.splitext(self.ocr_filepath)[1].lower()
        text = ""
        self.log(f"Rozpoczynam ekstrakcję pliku: {os.path.basename(self.ocr_filepath)}...")
        
        try:
            if ext == '.pdf':
                with pdfplumber.open(self.ocr_filepath) as pdf:
                    text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            elif ext == '.docx':
                doc = Document(self.ocr_filepath)
                text = "\n".join([p.text for p in doc.paragraphs])
            elif ext in ['.png', '.jpg', '.jpeg']:
                if self.ocr_reader is None:
                    self.log("Pobieranie/ładowanie modelu AI do odczytu obrazów (to może chwilę potrwać)...")
                    self.ocr_reader = easyocr.Reader(['pl', 'en'])
                results = self.ocr_reader.readtext(self.ocr_filepath, detail=0)
                text = "\n".join(results)
                
            if not text.strip():
                self.log("Uwaga: Nie wykryto żadnego tekstu w pliku.")
                return
                
            save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Tekst", "*.txt")], title="Zapisz wynik")
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.log(f"Sukces! Wyciągnięty tekst zapisano jako {os.path.basename(save_path)}")
        except Exception as e:
            self.log(f"Błąd podczas cyfryzacji: {e}")

    # ==========================================
    # ZAKŁADKA 2: TŁUMACZ (Ćw 1)
    # ==========================================
    def create_tab_translate(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="2. Tłumacz")
        
        tk.Label(tab, text="Tłumaczenie zarchiwizowanych dokumentów na język angielski dla turystów.").pack(pady=10)
        self.lbl_trans_file = tk.Label(tab, text="Brak wybranego pliku TXT", fg="red")
        self.lbl_trans_file.pack()
        self.trans_filepath = None
        
        tk.Button(tab, text="Wybierz plik TXT", width=20, command=self.select_trans_file).pack(pady=5)
        tk.Button(tab, text="Przetłumacz (-> EN) i Zapisz", width=30, bg="lightblue", command=self.run_translation).pack(pady=20)

    def select_trans_file(self):
        self.trans_filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.trans_filepath:
            self.lbl_trans_file.config(text=os.path.basename(self.trans_filepath), fg="green")

    def run_translation(self):
        if not self.trans_filepath:
            messagebox.showwarning("Błąd", "Wybierz plik .txt!")
            return
        try:
            self.log("Trwa tłumaczenie za pomocą wbudowanego translatora...")
            with open(self.trans_filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            translated = GoogleTranslator(source='auto', target='en').translate(text)
            
            save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")])
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(translated)
                self.log(f"Sukces! Tłumaczenie zapisano w: {os.path.basename(save_path)}")
        except Exception as e:
            self.log(f"Błąd tłumaczenia: {e}")

    # ==========================================
    # ZAKŁADKA 3: NOTATKI GŁOSOWE (STT - Ćw 2)
    # ==========================================
    def create_tab_stt(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="3. Transkrypcja Notatek (STT)")
        
        tk.Label(tab, text="Zamienia notatki głosowe kustosza (WAV) na tekst.").pack(pady=10)
        self.lbl_stt_file = tk.Label(tab, text="Brak pliku WAV", fg="red")
        self.lbl_stt_file.pack()
        self.stt_filepath = None
        
        tk.Button(tab, text="Wybierz notatkę (WAV)", width=20, command=self.select_stt_file).pack(pady=5)
        tk.Button(tab, text="Spisz na tekst i Zapisz (TXT)", width=30, bg="lightblue", command=self.run_stt).pack(pady=20)

    def select_stt_file(self):
        self.stt_filepath = filedialog.askopenfilename(filetypes=[("Audio", "*.wav")])
        if self.stt_filepath:
            self.lbl_stt_file.config(text=os.path.basename(self.stt_filepath), fg="green")

    def run_stt(self):
        if not self.stt_filepath:
            messagebox.showwarning("Błąd", "Wybierz nagranie!")
            return
        
        recognizer = sr.Recognizer()
        try:
            self.log("Analiza dźwięku... proszę czekać.")
            with sr.AudioFile(self.stt_filepath) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data, language="pl-PL")
            
            save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")])
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.log("Sukces! Rozpoznano mowę i spisano notatkę.")
        except sr.UnknownValueError:
            self.log("Błąd: Nie rozpoznano słów. Spróbuj wyraźniejsze nagranie.")
        except Exception as e:
            self.log(f"Błąd STT: {e}")

    # ==========================================
    # ZAKŁADKA 4: AUDIOPRZEWODNIK (TTS - Ćw 3)
    # ==========================================
    def create_tab_tts(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="4. Audioprzewodnik (TTS)")
        
        tk.Label(tab, text="Wpisz lub wklej opis eksponatu, aby wygenerować głos lektora.").pack(pady=5)
        self.tts_text = tk.Text(tab, height=6, width=60)
        self.tts_text.pack(pady=5)
        
        tk.Label(tab, text="Tempo czytania:").pack()
        self.tts_rate = tk.Scale(tab, from_=80, to=250, orient='horizontal')
        self.tts_rate.set(150)
        self.tts_rate.pack(pady=5)
        
        tk.Button(tab, text="Generuj lektora (WAV)", width=30, bg="lightblue", command=self.run_tts).pack(pady=10)

    def run_tts(self):
        text = self.tts_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Błąd", "Brak tekstu!")
            return
            
        save_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Audio", "*.wav")])
        if not save_path: return
        
        try:
            self.log("Trwa generowanie audioprzewodnika...")
            engine = pyttsx3.init()
            engine.setProperty('rate', self.tts_rate.get())
            engine.save_to_file(text, save_path)
            engine.runAndWait()
            self.log("Sukces! Plik audio dla wystawy został zapisany.")
        except Exception as e:
            self.log(f"Błąd TTS: {e}")

    # ==========================================
    # ZAKŁADKA 5: KATALOGOWANIE (ViT - Ćw 5)
    # ==========================================
    def create_tab_vit(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="5. Katalogowanie Zdj. (ViT)")
        
        tk.Label(tab, text="Rozpoznawanie obiektów na starych fotografiach przy użyciu AI.").pack(pady=10)
        self.lbl_vit_folder = tk.Label(tab, text="Brak folderu", fg="red")
        self.lbl_vit_folder.pack()
        self.vit_folderpath = None
        
        tk.Button(tab, text="Wybierz folder ze zdjęciami", width=25, command=self.select_vit_folder).pack(pady=5)
        tk.Button(tab, text="Sklasyfikuj Archiwum", width=30, bg="lightblue", command=self.run_vit).pack(pady=20)

    def select_vit_folder(self):
        self.vit_folderpath = filedialog.askdirectory()
        if self.vit_folderpath:
            self.lbl_vit_folder.config(text=self.vit_folderpath, fg="green")

    def run_vit(self):
        if not self.vit_folderpath:
            messagebox.showwarning("Błąd", "Wybierz folder!")
            return
            
        try:
            if not os.path.exists("token.txt"):
                raise FileNotFoundError("Brak pliku token.txt z kluczem Hugging Face!")
            with open("token.txt", "r") as f:
                token = f.read().strip()
                
            self.log("Łączenie z chmurą i autoryzacja modelu ViT...")
            processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224', token=token)
            model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224', token=token)
            
            results = []
            valid_ext = ('.jpg', '.jpeg', '.png')
            
            for file in os.listdir(self.vit_folderpath):
                if file.lower().endswith(valid_ext):
                    img_path = os.path.join(self.vit_folderpath, file)
                    self.log(f"Analiza fotografii: {file}...")
                    
                    image = Image.open(img_path).convert("RGB")
                    inputs = processor(images=image, return_tensors="pt")
                    outputs = model(**inputs)
                    predicted_class_idx = outputs.logits.argmax(-1).item()
                    label = model.config.id2label[predicted_class_idx]
                    
                    results.append(f"{file}  -->  Rozpoznano: {label}")
                    
            output_file = os.path.join(self.vit_folderpath, "Raport_Katalogowania_AI.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(results))
                
            self.log(f"Katalogowanie ukończone! Raport zapisano w folderze zdjęć.")
            messagebox.showinfo("Sukces", "Klasyfikacja zakończona pomyślnie!")
        
        # TUTAJ JEST KLUCZOWA POPRAWKA BŁĘDU:
        except Exception as e:
            self.log(f"Błąd ViT: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KustoszAI_App(root)
    root.mainloop()
