# 🏛️ Applied AI Toolkit & Kustosz AI Assistant

A comprehensive suite of Python applications demonstrating the practical use of Artificial Intelligence (AI) and Machine Learning (ML). This repository contains individual CLI scripts exploring different AI domains (NLP, Computer Vision, Audio Processing) and culminates in a fully integrated Desktop Application (GUI) designed for a Museum Archivist persona.

## 🌟 Repository Contents & Features

The repository consists of several independent modules that are eventually merged into a final GUI application.

### 1. Kustosz AI - The Final App (`ćwiczenie6.py` / `ćwiczenie5.py`)
A comprehensive desktop application built with `tkinter` that serves as an assistant for museum archivists. It integrates all the tools below into a single, user-friendly interface with tabs.
* **Digitization:** Extracts text from PDFs, DOCX, and historical image scans using EasyOCR.
* **Translation:** Translates historical documents into English using the Google Translator API.
* **Voice Notes (STT):** Converts archivist's dictated audio notes (WAV) into text.
* **Audio Guides (TTS):** Generates offline narrator voices for museum exhibits based on text input.
* **Image Cataloging (ViT):** Batch processes and classifies old museum photographs using Google's Vision Transformer (`google/vit-base-patch16-224`) via Hugging Face.

### 2. Audio Transcription & Filtering (`audio_transkrypcja.py`)
An advanced audio processing script that allows users to record audio via microphone or load WAV files.
* **Noise Filtering:** Applies a low-pass Butterworth filter to remove high-frequency noise.
* **Model Comparison:** Transcribes audio using two different local models: `openai/whisper-small` and `jonatasgrosman/wav2vec2-large-xlsr-53-polish`.
* **Evaluation:** Calculates the Word Error Rate (WER) to compare model accuracy against a reference text.

### 3. Smart MBart Translator (`translator.py`)
A local, offline translation tool using the `facebook/mbart-large-50-many-to-many-mmt` model.
* Translates text from English to Polish line by line.
* **Idiom Preservation:** Automatically detects and correctly replaces specific English idioms with their Polish equivalents before translation.
* **Tag Preservation:** Safely extracts specific formatting tags (e.g., `{tag}`) before feeding the text to the neural network and restores them precisely after translation.

### 4. Document & Image Extractor (`ćwiczenie 4.py`)
A command-line tool for batch processing and extracting text from multiple file formats.
* Parses text from `.pdf` (using `pdfplumber`) and `.docx` (using `python-docx`).
* Performs Optical Character Recognition (OCR) on images (`.png`, `.jpg`) using `easyocr`.
* Automatically detects the language of the extracted text and generates a summarized CSV report containing file metadata and word counts.

## 🛠️ Technologies & Libraries Used

* **Core:** Python 3, `tkinter` (GUI), `os`, `csv`, `re`, `time`
* **Deep Learning & NLP:** `torch`, `transformers` (Hugging Face), `easyocr`, `deep-translator`, `langdetect`, `evaluate`
* **Audio Processing:** `librosa`, `sounddevice`, `soundfile`, `scipy` (signal filtering), `pyttsx3`, `SpeechRecognition`
* **Document Parsing:** `pdfplumber`, `python-docx`, `Pillow` (Image processing)

## 🚀 Getting Started & Installation

### 1. Install Dependencies
Make sure you have Python 3.8+ installed. It is highly recommended to use a virtual environment. Install the required packages by running:

```bash
pip install torch torchvision torchaudio transformers easyocr pdfplumber python-docx langdetect Pillow pyttsx3 SpeechRecognition deep-translator sounddevice soundfile librosa scipy evaluate numpy
