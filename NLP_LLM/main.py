#code for Basic UI

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QSlider, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt

from summarizer import SummarizationEngine

class SummarizerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.summarizer = SummarizationEngine()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Text Summarizer')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        # Input text box
        self.inputText = QTextEdit()
        self.inputText.setPlaceholderText("Enter your text here...")
        layout.addWidget(self.inputText)

        # Slider for summarization level
        sliderLayout = QHBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(2)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        sliderLayout.addWidget(QLabel("Brief"))
        sliderLayout.addWidget(self.slider)
        sliderLayout.addWidget(QLabel("Comprehensive"))
        layout.addLayout(sliderLayout)
        # Summarize button
        self.summarizeButton = QPushButton("Summarize")
        self.summarizeButton.clicked.connect(self.summarize_text)
        layout.addWidget(self.summarizeButton)

        # Output text box
        self.outputText = QTextEdit()
        self.outputText.setReadOnly(True)
        self.outputText.setPlaceholderText("Summary will appear here...")
        layout.addWidget(self.outputText)

        # Set the main layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def summarize_text(self):
        input_text = self.inputText.toPlainText()
        level = ["low", "medium", "high"][self.slider.value()]
        self.outputText.setPlainText("Processing...")
        QApplication.processEvents()  # Ensure the UI updates
        try:
            summary = self.summarizer.get_summary(input_text, level)
            self.outputText.setPlainText(summary)
        except Exception as e:
            self.outputText.setPlainText(f"An error occurred: {str(e)}")

def main():
    app = QApplication(sys.argv)
    ex = SummarizerUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
