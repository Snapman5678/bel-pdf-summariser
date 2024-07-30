import unittest
import os
import time
from random import choice
from app.extraction import FileChecker , TextPreprocessor , SystemChecker
from app.SummaryEngine import SummarizationPipeline

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
            ],
            'pdf-summary': [
                os.path.join(SCRIPT_DIR,"documents", "pdf", "School-23-page.pdf"),
                os.path.join(SCRIPT_DIR,"documents", "pdf", "Video-Games-9-page.pdf"),
                os.path.join(SCRIPT_DIR,"documents", "pdf", "WW2-42-page.pdf")
            ],
            'docx-summary': [
                os.path.join(SCRIPT_DIR,"documents", "word", "Data-Science-Test-8-page.docx"),
                os.path.join(SCRIPT_DIR,"documents", "word", "IC_Design_Flow-25-page.docx"),
                os.path.join(SCRIPT_DIR,"documents", "word", "India-47-page.docx")
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
    
    def test_summarization(self):
        # Define target word counts based on the provided logic
        target_word_counts = {
            'short': 500,
            'medium': 1000,
            'long': 2000
        }
        summary_levels = list(target_word_counts.keys())

        for file_name in self.test_files_dir['pdf-summary'] + self.test_files_dir['docx-summary']:
            with self.subTest(file_name=file_name):
                file_checker = FileChecker(file_name, self.max_pages)
                is_valid, message = file_checker.check_file()
                self.assertTrue(is_valid, message)

                text = file_checker.extracted_text.getvalue()
                total_pages = file_checker.total_pages

                gpu_available, cpu_cores = SystemChecker.check_hardware()
                n_processes = cpu_cores if not gpu_available else 1

                # Preprocess the text
                preprocessor = TextPreprocessor()
                if n_processes > 1:
                    text = preprocessor.process_in_parallel(text, n_processes)
                else:
                    text = preprocessor.preprocess(text)

                # Choose a random summary level
                summary_level = choice(summary_levels)
                target_word_count = target_word_counts[summary_level]

                # Create a SummarizationPipeline instance
                pipeline = SummarizationPipeline()

                # Measure the time taken for summarization
                start_time = time.time()
                summary = pipeline.summarize(text, summary_level)
                end_time = time.time()

                summary_word_count = len(summary.split())
                time_taken = end_time - start_time

                # Print the results
                print(f"Summarization for {file_name} ({summary_level}):")
                print(f"Summary Length: {summary_word_count} words")
                print(f"Time Taken: {time_taken:.2f} seconds")

                # Check if the summary length is within the expected range
                self.assertGreater(summary_word_count, 0, "Summary should not be empty")
                
                if summary_level == 'short':
                    self.assertLessEqual(summary_word_count, target_word_count, "Summary length exceeds the maximum for short summaries")
                elif summary_level == 'medium':
                    self.assertLessEqual(summary_word_count, target_word_count, "Summary length exceeds the maximum for medium summaries")
                elif summary_level == 'long':
                    self.assertLessEqual(summary_word_count, target_word_count, "Summary length exceeds the maximum for long summaries")


if __name__ == '__main__':
    unittest.main()
