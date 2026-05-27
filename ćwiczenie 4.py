import os
import csv
import pdfplumber
from docx import Document
import easyocr
from langdetect import detect, DetectorFactory

# Gwarantuje powtarzalność wyników detekcji języka
DetectorFactory.seed = 0 

# Zmienna globalna dla czytnika, aby nie ładować modelu od nowa dla każdego pliku
OCR_READER = None 

def get_ocr_reader():
    """Leniwe ładowanie modelu EasyOCR (tylko wtedy, gdy jest potrzebny)."""
    global OCR_READER
    if OCR_READER is None:
        print("\n[INFO] Inicjalizacja modelu EasyOCR (może potrwać chwilę)...")
        OCR_READER = easyocr.Reader(['pl', 'en'])
    return OCR_READER

def extract_pdf(filepath):
    """Odczytuje tekst z plików PDF za pomocą pdfplumber."""
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_docx(filepath):
    """Odczytuje tekst z plików DOCX za pomocą python-docx."""
    doc = Document(filepath)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def extract_image_ocr(filepath):
    """Wykonuje OCR na obrazach za pomocą EasyOCR."""
    reader = get_ocr_reader()
    # detail=0 sprawia, że biblioteka zwraca czystą listę odczytanych tekstów
    results = reader.readtext(filepath, detail=0)
    # Łączenie elementów listy w jeden ciąg znaków (linijka pod linijką)
    return "\n".join(results)

def detect_language(text):
    """Automatycznie wykrywa język (punkt dodatkowy)."""
    if not text.strip():
        return "Brak tekstu"
    try:
        return detect(text)
    except:
        return "Nieznany"

def process_file(filepath):
    """Router rozpoznający rozszerzenie pliku."""
    ext = os.path.splitext(filepath)[1].lower()
    text = ""
    method = ""

    if ext == '.pdf':
        text = extract_pdf(filepath)
        method = "pdfplumber (PDF)"
    elif ext == '.docx':
        text = extract_docx(filepath)
        method = "python-docx (DOCX)"
    elif ext in ['.png', '.jpg', '.jpeg', '.tiff']:
        text = extract_image_ocr(filepath)
        method = "easyocr (OCR)"
    else:
        return None, "Nieobsługiwany format"

    return text, method

def main():
    print("--- EKSTRAKTOR TEKSTU (PDF, DOCX, OCR - EasyOCR) ---")
    
    report_data = [] 

    while True:
        print("\n1. Przetwórz pojedynczy plik")
        print("2. Przetwórz wiele plików w folderze (Batch Processing)")
        print("3. Wygeneruj raport z przetwarzania i wyjdź")
        
        choice = input("Wybierz opcję (1-3): ")
        
        files_to_process = []
        
        if choice == '1':
            filepath = input("Podaj ścieżkę do pliku (np. dokument.pdf, zdjecie.png): ")
            if os.path.exists(filepath):
                files_to_process.append(filepath)
            else:
                print("Błąd: Plik nie istnieje.")
                
        elif choice == '2':
            folderpath = input("Podaj ścieżkę do folderu z plikami: ")
            if os.path.exists(folderpath) and os.path.isdir(folderpath):
                for filename in os.listdir(folderpath):
                    full_path = os.path.join(folderpath, filename)
                    if os.path.isfile(full_path):
                        files_to_process.append(full_path)
            else:
                print("Błąd: Folder nie istnieje.")
                
        elif choice == '3':
            if not report_data:
                print("Brak danych. Zamykam program...")
                break
                
            report_path = "raport_przetwarzania.csv"
            with open(report_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Plik", "Format", "Metoda", "Język", "Liczba słów"])
                writer.writerows(report_data)
            print(f"Zapisano raport do pliku: {report_path}")
            break
            
        else:
            print("Nieprawidłowy wybór.")
            continue

        for filepath in files_to_process:
            print(f"Przetwarzanie: {filepath} ...")
            text, method = process_file(filepath)
            
            if text is None:
                print(f"Pominięto {filepath}: {method}")
                continue
                
            lang = detect_language(text)
            word_count = len(text.split())
            base_name, ext = os.path.splitext(filepath)
            
            output_txt = f"{base_name}_extracted.txt"
            with open(output_txt, 'w', encoding='utf-8') as f:
                f.write(text)
                
            print(f"--> Sukces. Zapisano tekst jako: {output_txt}")
            
            report_data.append([os.path.basename(filepath), ext, method, lang, word_count])

if __name__ == "__main__":
    main()