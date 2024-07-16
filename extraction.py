import sys
from pypdf import PdfReader
from docx import Document
from langdetect import detect, LangDetectException

def is_english(text):
    try:
        return detect(text) == 'en'
    except LangDetectException:
        return False

def extract_text_from_pdf(file_path, max_pages=50):
    try:
        reader = PdfReader(file_path)
        total_pages = min(len(reader.pages), max_pages)
        extracted_text = []

        for page_number in range(total_pages):
            page = reader.pages[page_number]
            text = page.extract_text()
            
            if not text:
                print(f"Warning: No text found on page {page_number + 1}. This might be a scanned image.")
                continue
            
            if not is_english(text):
                print(f"Error: Non-English content detected on page {page_number + 1}.")
                return None
            
            cleaned_text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
            extracted_text.append(f"--- Page {page_number + 1} ---\n{cleaned_text}")

        return '\n\n'.join(extracted_text) if extracted_text else None
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None

def extract_text_from_docx(file_path, max_pages=50):
    try:
        doc = Document(file_path)
        full_text = []
        page_break_count = 0
        text_buffer = []

        for para in doc.paragraphs:
            if para.text.strip() == '':
                continue
            
            if 'PAGE BREAK' in para.text:
                page_break_count += 1
            
            if page_break_count >= max_pages:
                break
            
            text_buffer.append(para.text)
        
        text = '\n'.join(text_buffer)
        
        if not is_english(text):
            print("Error: The document is not in English.")
            return None
        
        return text
    except Exception as e:
        print(f"Error processing DOCX: {str(e)}")
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_path>")
        return

    file_path = sys.argv[1]
    
    if file_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        print("Unsupported file type. Please provide a .pdf or .docx file.")
        return

    if text:
        print(text)
    else:
        print("Failed to extract text from the document.")

if __name__ == "__main__":
    main()
