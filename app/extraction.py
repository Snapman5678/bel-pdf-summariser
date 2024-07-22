import os
import fitz  # PyMuPDF
from docx import Document
from langdetect import detect, LangDetectException
from io import StringIO
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class FileChecker:
    def __init__(self, file_path, max_pages=50):
        self.file_path = file_path
        self.max_pages = max_pages
        self.extracted_text = StringIO()

    def is_english(self, text):
        try:
            return detect(text) == "en"
        except LangDetectException:
            return False

    def check_pdf(self):
        try:
            doc = fitz.open(self.file_path)
            total_pages = len(doc)
            if total_pages > self.max_pages:
                return False, f"PDF exceeds {self.max_pages} pages."

            for page_number in range(total_pages):
                page = doc.load_page(page_number)
                text = page.get_text("text")
                if not text:
                    return (
                        False,
                        f"PDF page {page_number + 1} might be a scanned image.",
                    )

                if not self.is_english(text):
                    return (
                        False,
                        f"Non-English content detected on page {page_number + 1}.",
                    )

                cleaned_text = "\n".join(
                    line.strip() for line in text.split("\n") if line.strip()
                )
                self.extracted_text.write(
                    f"--- Page {page_number + 1} ---\n{cleaned_text}\n\n"
                )

            return True, "PDF is valid."
        except Exception as e:
            logging.error(f"Error processing PDF: {str(e)}")
            return False, f"Error processing PDF: {str(e)}"

    def check_docx(self):
        try:
            doc = Document(self.file_path)
            page_count = 0
            text_buffer = StringIO()

            for para in doc.paragraphs:
                if "PAGE BREAK" in para.text:
                    page_count += 1
                if page_count >= self.max_pages:
                    return False, f"DOCX exceeds {self.max_pages} pages."

                text_buffer.write(para.text + "\n")

            text = text_buffer.getvalue()
            if not self.is_english(text):
                return False, "The document is not in English."

            self.extracted_text.write(text)
            return True, "DOCX is valid."
        except Exception as e:
            logging.error(f"Error processing DOCX: {str(e)}")
            return False, f"Error processing DOCX: {str(e)}"

    def check_doc(self):
        try:
            import win32com.client as win32

            word = win32.Dispatch("Word.Application")
            doc = word.Documents.Open(self.file_path)
            text_buffer = StringIO()
            page_count = 0

            for i in range(doc.Paragraphs.Count):
                para = doc.Paragraphs[i + 1].Range.Text.strip()
                if "PAGE BREAK" in para:
                    page_count += 1
                if page_count >= self.max_pages:
                    doc.Close(False)
                    word.Quit()
                    return False, f"DOC exceeds {self.max_pages} pages."

                text_buffer.write(para + "\n")

            text = text_buffer.getvalue()
            doc.Close(False)
            word.Quit()

            if not self.is_english(text):
                return False, "The document is not in English."

            self.extracted_text.write(text)
            return True, "DOC is valid."
        except Exception as e:
            logging.error(f"Error processing DOC: {str(e)}")
            return False, f"Error processing DOC: {str(e)}"

    def check_file(self):
        ext = os.path.splitext(self.file_path)[1].lower()
        if ext == ".pdf":
            return self.check_pdf()
        elif ext == ".docx":
            return self.check_docx()
        elif ext == ".doc":
            return self.check_doc()
        else:
            return (
                False,
                "Unsupported file type. Please provide a .pdf, .docx, or .doc file.",
            )


class TextExtractor:
    def __init__(self):
        self.text = StringIO()

    def save_text(self, text):
        try:
            self.text.write(text)
            return True
        except Exception as e:
            logging.error(f"Error saving text: {str(e)}")
            return False, f"Error saving text: {str(e)}"

    def get_text(self):
        return self.text.getvalue()

    def clear_text(self):
        self.text.truncate(0)  # Clear the text buffer
        self.text.seek(0)
