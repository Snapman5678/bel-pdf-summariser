import os

import fitz  # PyMuPDF
from docx import Document
from langdetect import detect, LangDetectException


class FileChecker:
    def __init__(self, file_path, max_pages=50):
        self.file_path = file_path
        self.max_pages = max_pages
        self.extracted_text = ""

    def is_english(self, text):
        try:
            return detect(text) == 'en'
        except LangDetectException:
            return False

    def check_pdf(self):
        try:
            doc = fitz.open(self.file_path)
            total_pages = len(doc)
            if total_pages > self.max_pages:
                return False, f"PDF exceeds {self.max_pages} pages."

            extracted_text = []
            for page_number in range(total_pages):
                page = doc.load_page(page_number)
                text = page.get_text("text")
                if not text:
                    return False, f"PDF page {page_number + 1} might be a scanned image."

                if not self.is_english(text):
                    return False, f"Non-English content detected on page {page_number + 1}."

                cleaned_text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
                extracted_text.append(f"--- Page {page_number + 1} ---\n{cleaned_text}")

            self.extracted_text = '\n\n'.join(extracted_text)
            return True, "PDF is valid."
        except Exception as e:
            return False, f"Error processing PDF: {str(e)}"

    def check_docx(self):
        try:
            doc = Document(self.file_path)
            page_count = 0
            text_buffer = []

            for para in doc.paragraphs:
                if 'PAGE BREAK' in para.text:
                    page_count += 1
                if page_count >= self.max_pages:
                    return False, f"DOCX exceeds {self.max_pages} pages."

                text_buffer.append(para.text)

            text = '\n'.join(text_buffer)
            if not self.is_english(text):
                return False, "The document is not in English."

            self.extracted_text = text
            return True, "DOCX is valid."
        except Exception as e:
            return False, f"Error processing DOCX: {str(e)}"

    def check_doc(self):
        try:
            import win32com.client as win32
            word = win32.Dispatch('Word.Application')
            doc = word.Documents.Open(self.file_path)
            text_buffer = []
            page_count = 0

            for i in range(doc.Paragraphs.Count):
                para = doc.Paragraphs[i + 1].Range.Text.strip()
                if 'PAGE BREAK' in para:
                    page_count += 1
                if page_count >= self.max_pages:
                    doc.Close(False)
                    word.Quit()
                    return False, f"DOC exceeds {self.max_pages} pages."

                text_buffer.append(para)

            text = '\n'.join(text_buffer)
            doc.Close(False)
            word.Quit()

            if not self.is_english(text):
                return False, "The document is not in English."

            self.extracted_text = text
            return True, "DOC is valid."
        except Exception as e:
            return False, f"Error processing DOC: {str(e)}"

    def check_file(self):
        ext = os.path.splitext(self.file_path)[1].lower()
        if ext == '.pdf':
            return self.check_pdf()
        elif ext == '.docx':
            return self.check_docx()
        elif ext == '.doc':
            return self.check_doc()
        else:
            return False, "Unsupported file type. Please provide a .pdf, .docx, or .doc file."


class TextExtractor:
    def __init__(self, output_path):
        self.output_path = output_path

    def save_text(self, text):
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            return True
        except Exception as e:
            return False, f"Error saving text: {str(e)}"
