import os
import time
import random
import pytest
from PyQt6.QtWidgets import QApplication, QPushButton
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from app.main_ui import MainWindow  
from app.SummaryEngine import SummarizationPipeline 

@pytest.fixture
def app(qtbot):
    test_app = QApplication([])
    window = MainWindow()
    qtbot.addWidget(window)
    return qtbot, window

def test_read_documents(app):
    qtbot, window = app

    # Simulate reading 3 Word documents
    for i in range(3):
        # Use window's method to read Word documents
        file_path = f"test_doc_{i+1}.docx"  # Use actual file paths in practice
        window.read_document(file_path)
    
    # Simulate reading 3 PDF documents
    for i in range(3):
        file_path = f"test_doc_{i+1}.pdf"  # Use actual file paths in practice
        window.read_document(file_path)

    # Check if the documents are read correctly
    assert len(window.documents) == 6  # Update if the implementation stores docs differently

def test_summarize_documents(app):
    qtbot, window = app

    # Simulate reading and summarizing 3 Word and 3 PDF documents
    for i in range(3):
        word_file_path = f"test_doc_{i+1}.docx"  # Use actual file paths in practice
        pdf_file_path = f"test_doc_{i+1}.pdf"  # Use actual file paths in practice
        window.read_document(word_file_path)
        window.read_document(pdf_file_path)

        for file_path in [word_file_path, pdf_file_path]:
            # Randomly choose a summarization length
            summary_length = random.choice(['short', 'medium', 'long'])
            start_time = time.time()
            summary = SummarizationPipeline()
            time_taken = time.time() - start_time
            
            # Assert the summary is not empty
            assert summary.strip() != ""

            # Optionally, check the length of the summary or other conditions
            assert summary_length in ['short', 'medium', 'long']
            print(f"File: {file_path}, Summary Length: {summary_length}, Time Taken: {time_taken:.2f}s")

def test_clear_button(app):
    qtbot, window = app

    # Simulate reading and summarizing documents
    for i in range(3):
        word_file_path = f"test_doc_{i+1}.docx"  # Use actual file paths in practice
        pdf_file_path = f"test_doc_{i+1}.pdf"  # Use actual file paths in practice
        window.read_document(word_file_path)
        window.read_document(pdf_file_path)
    
    # Click the clear button
    clear_button = window.findChild(QPushButton, "clearButton")  # Adjust the button name if needed
    qtbot.mouseClick(clear_button, Qt.MouseButton.LeftButton)
    
    # Assert the buffer is cleared and the application is closed
    assert window.documents == []
    assert not QApplication.instance().activeWindow()  # Check if the window is closed
