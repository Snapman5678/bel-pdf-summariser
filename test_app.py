import unittest
import os
from app.extraction import FileChecker

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class TestFileChecker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_files_dir = {
            'pdf': [
                os.path.join(SCRIPT_DIR,"documents", "pdf", "Italian-English.pdf"),
                os.path.join(SCRIPT_DIR,"documents", "pdf", "Math-exceeds-50-page.pdf"),
                os.path.join(SCRIPT_DIR,"documents", "pdf", "Scanned.pdf"),
                os.path.join(SCRIPT_DIR,"documents", "pdf", "School-23-page.pdf"),
                os.path.join(SCRIPT_DIR,"documents", "pdf", "Video-Games-9-page.pdf"),
                os.path.join(SCRIPT_DIR,"documents", "pdf", "WW2-42-page.pdf")
            ],
            'docx': [
                os.path.join(SCRIPT_DIR,"documents", "word", "Data-Science-Test-8-page.docx"),
                os.path.join(SCRIPT_DIR,"documents", "word", "IC_Design_Flow-25-page.docx"),
                os.path.join(SCRIPT_DIR,"documents", "word", "India-47-page.docx"),
                os.path.join(SCRIPT_DIR,"documents", "word", "Spanish.docx")
            ]
        }
        cls.max_pages = 50

    def test_pdf_files(self):
        for file_name in self.test_files_dir['pdf']:
            with self.subTest(file_name=file_name):
                file_checker = FileChecker(file_name, self.max_pages)
                is_valid, message = file_checker.check_file()
                print(f"PDF Test {file_name}: {message}")
                if 'exceeds' in file_name:
                    self.assertFalse(is_valid)
                elif 'Scanned' in file_name:
                    self.assertFalse(is_valid)
                elif 'Itialian-English' in file_name:
                    self.assertTrue(is_valid)
                elif 'School-23-page' in file_name:
                    self.assertTrue(is_valid)
                elif 'Video-Games-9-page' in file_name:
                    self.assertTrue(is_valid)
                elif 'WW2-42-page' in file_name:
                    self.assertTrue(is_valid)

    def test_docx_files(self):
        for file_name in self.test_files_dir['docx']:
            with self.subTest(file_name=file_name):
                file_checker = FileChecker(file_name, self.max_pages)
                is_valid, message = file_checker.check_file()
                print(f"DOCX Test {file_name}: {message}")
                if 'Data-Science-Test-8-page' in file_name:
                    self.assertTrue(is_valid)
                elif 'IC_Design_Flow-25-page' in file_name:
                    self.assertTrue(is_valid)
                elif 'India-47-page' in file_name:
                    self.assertTrue(is_valid)
                elif 'Spanish' in file_name:
                    self.assertFalse(is_valid)

if __name__ == '__main__':
    unittest.main()
