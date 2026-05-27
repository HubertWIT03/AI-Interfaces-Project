import re
import torch
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast


INPUT_FILE = "tekst_eng.txt"
OUTPUT_FILE = "tekst_pl.txt"
MODEL_NAME = "facebook/mbart-large-50-many-to-many-mmt"


IDIOMS_DICT = {
    "it's raining cats and dogs": "leje jak z cebra",
    "piece of cake": "bułka z masłem",
    "break a leg": "połamania nóg"
}

print("Ładowanie modelu i tokenizatora (to może chwilę potrwać)...")
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = MBart50TokenizerFast.from_pretrained(MODEL_NAME)
model = MBartForConditionalGeneration.from_pretrained(MODEL_NAME).to(device)


tokenizer.src_lang = "en_XX"


def translate_sentence(text):
    """Tłumaczy pojedyncze zdanie/fragment przy użyciu modelu."""
    if not text.strip():
        return text
        
    encoded = tokenizer(text, return_tensors="pt").to(device)
    generated_tokens = model.generate(
        **encoded,
        forced_bos_token_id=tokenizer.lang_code_to_id["pl_PL"]
    )
    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

def process_line(line):
    """
    Przetwarza pojedynczą linię tekstu:
    1. Zabezpiecza tagi i idiomy.
    2. Tłumaczy pozostały tekst.
    3. Przywraca tagi i przetłumaczone idiomy.
    """
    placeholders = {}
    placeholder_idx = 0
    
    
    for en_idiom, pl_idiom in IDIOMS_DICT.items():
        if en_idiom in line.lower():
          
            pattern = re.compile(re.escape(en_idiom), re.IGNORECASE)
            placeholder = f" __IDIOM_{placeholder_idx}__ "
            placeholders[placeholder.strip()] = pl_idiom
            line = pattern.sub(placeholder, line)
            placeholder_idx += 1

    
    tag_pattern = re.compile(r'(\{.*?\})')
    tags = tag_pattern.findall(line)
    
    for tag in tags:
        placeholder = f" __TAG_{placeholder_idx}__ "
        placeholders[placeholder.strip()] = tag
        line = line.replace(tag, placeholder, 1)
        placeholder_idx += 1

   
    translated_line = translate_sentence(line)


    for placeholder, original_value in placeholders.items():
        
        translated_line = re.sub(rf'\s*{placeholder}\s*', original_value, translated_line)

    return translated_line

def main():
    print(f"Rozpoczynam tłumaczenie pliku '{INPUT_FILE}'...")
    

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as infile, \
             open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
             
            for line_number, line in enumerate(infile, 1):
                original_text = line.rstrip('\n')
                
                if not original_text:
                    outfile.write('\n')
                    continue
                    
                translated_text = process_line(original_text)
                outfile.write(translated_text + '\n')
                
                if line_number % 10 == 0:
                    print(f"Przetworzono {line_number} linii...")

        print(f"Zakończono! Wynik zapisano w '{OUTPUT_FILE}'.")
        
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku wejściowego '{INPUT_FILE}'. Utwórz go przed uruchomieniem skryptu.")

if __name__ == "__main__":
    main()