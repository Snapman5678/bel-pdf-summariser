import sys
import colors
import os
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGridLayout, QSpacerItem, QSizePolicy,
    QPushButton, QSlider, QFileDialog
)
from PyQt6.QtGui import QPalette, QColor, QPainter, QFont, QPixmap
from PyQt6.QtSvgWidgets import QSvgWidget


class RoundedRectWidget(QWidget):
    def __init__(self, color):
        super().__init__()
        self.color = QColor(color)
        self.setAutoFillBackground(False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        radius = 15  # Set the radius for the rounded corners

        painter.setBrush(self.color)
        painter.setPen(Qt.GlobalColor.transparent)
        painter.drawRoundedRect(rect, radius, radius)
        painter.end()


class RectWidget(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)


class CustomTextLabel(QLabel):
    def __init__(self, size, font_type, color, text):
        super().__init__()
        self.setText(text)

        # Set font
        font = QFont()
        font.setPointSize(size)
        font.setFamily(font_type)
        self.setFont(font)

        # Set color
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(color))
        self.setPalette(palette)


class TopWidget(RectWidget):
    def __init__(self, color):
        super().__init__(color)
        self.initUI()

    def initUI(self):
        layout = QGridLayout()

        # Add title
        title = CustomTextLabel(30, 'Inter', 'black', 'Content Summarizer')
        layout.addWidget(title, 0, 0)

        # Add subtitle
        title_text = CustomTextLabel(16, 'Inter', 'black', 'Get the gist of any content with one click')
        layout.addWidget(title_text, 1, 0)

        # Add SVG image to the top right
        svg_widget = QSvgWidget("icons/Menu_toggle.svg")
        svg_widget.setFixedSize(25, 25)  # Set the desired size of the SVG image
        layout.addWidget(svg_widget, 0, 2, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        # Add dummy widgets for better control
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum), 0, 1)
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 2, 0)

        # Set layout spacing and margins
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setVerticalSpacing(2)

        self.setLayout(layout)


class FileNameWithTick(QWidget):
    def __init__(self):
        super().__init__()
        self.file_name_label = None
        self.tick_svg = None
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        # Tick SVG on the left
        self.tick_svg = QSvgWidget("icons/Tick.svg")
        self.tick_svg.setFixedSize(24, 24)  # Set desired size for the tick mark SVG
        layout.addWidget(self.tick_svg)

        # File name label on the right
        self.file_name_label = QLabel("")
        layout.addWidget(self.file_name_label)

        self.setLayout(layout)
        self.hide()  # Initially hide the widget

    def show_file_info(self, filename):
        self.file_name_label.setText(os.path.basename(filename))
        self.file_name_label.setStyleSheet(
            "font-family: 'Inter'; font-size: 14px; color: black;"  # Adjust size and color as needed
        )
        self.show()

    def hide_file_info(self):
        self.file_name_label.clear()
        self.hide()


class HoverButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.normal_style = (
            f"background: none; border: none; border-radius: 8px; font: 16px 'Inter'; color: {colors.purple};"
        )
        self.hover_style = (
            f"background-color: {colors.grey}; border: none; border-radius: 8px;"
            f"font: 16px 'Inter'; color: {colors.light_purple};"
        )
        self.setStyleSheet(self.normal_style)
        self.setMouseTracking(True)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.Enter:
            self.setStyleSheet(self.hover_style)
        elif event.type() == QEvent.Type.Leave:
            self.setStyleSheet(self.normal_style)
        return super().eventFilter(obj, event)


class BottomRightWidget(RoundedRectWidget):
    def __init__(self, parent_layout, color):
        super().__init__(color)
        self.parent_layout = parent_layout
        self.file_path = None
        self.file_label = None
        self.upload_button = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        layout.addSpacing(30)

        # Add title at the top center
        title = CustomTextLabel(18, 'Inter', 'black', 'UPLOAD YOUR PDF FILE HERE')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Add space between title and SVG image
        layout.addSpacing(100)  # Adjust the amount of spacing as needed

        # File Image in the center
        svg_widget = QSvgWidget("icons/File.svg")
        svg_widget.setFixedSize(197, 207)  # Set the desired size of the SVG image
        layout.addWidget(svg_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Button below file image
        self.upload_button = HoverButton("Click or drop a file")
        self.upload_button.clicked.connect(self.open_file_dialog)

        layout.addWidget(self.upload_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        layout.addSpacing(10)

        # Label to display selected file name and tick mark SVG
        self.file_label = FileNameWithTick()
        layout.addWidget(self.file_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Subtitle below button
        subtitle1 = CustomTextLabel(12, 'Inter', colors.light_black,
                                    'Once the summary has been created your file will\nbe downloaded automatically.')
        subtitle1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle1, alignment=Qt.AlignmentFlag.AlignCenter)

        # Spacer to push the buttons to the bottom right
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Add clear and summarize buttons at the bottom right
        button_layout = QHBoxLayout()
        button_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        clear_button = QPushButton("Clear")
        clear_button.setStyleSheet(
            f"background-color: {colors.grey}; color: white; font: 16px 'Inter';"
            f"border-radius: 17px; min-width: 120px;min-height:35px;")
        button_layout.addWidget(clear_button)

        button_layout.addSpacing(10)

        summarise_button = QPushButton("Summarize")
        summarise_button.setStyleSheet(
            f"background-color: {colors.purple}; color: white; font: 16px 'Inter';"
            f"border-radius: 17px; min-width: 120px;min-height:35px;")
        button_layout.addWidget(summarise_button)

        # Connect buttons to slots
        clear_button.clicked.connect(self.clear_file)
        summarise_button.clicked.connect(self.summarize_file)

        # Add the button layout to the vertical layout
        layout.addLayout(button_layout)

        layout.addSpacing(20)

        self.setLayout(layout)

    def open_file_dialog(self):
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        print(downloads_path)
        pdf_filter = "PDF Files (*.pdf)"
        word_filter = "Word Files (*.doc *.docx)"

        filter_var = pdf_filter
        if self.parent_layout.file_type == 1:
            filter_var = word_filter
        elif self.parent_layout.file_type == 0:
            filter_var = pdf_filter

        self.file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            downloads_path,
            filter_var
        )

        if self.file_path:
            # Handle the selected file path
            print(f"Selected file: {self.file_path}")
            self.show_file_info(self.file_path)

    def show_file_info(self, filename):
        # TODO: Need to check file limitations logic (need to add a filetype checker python file )
        self.file_label.show_file_info(filename)

    def clear_file(self):
        self.file_path = None
        self.file_label.hide_file_info()

    def summarize_file(self):
        if self.file_path:
            # TODO: Implement file summarization logic
            pass
        else:
            print("No file selected.")


# Custom slider widget
class Slider(QWidget):
    valueChanged = pyqtSignal(int)  # Signal to emit slider value

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()

        turtle = QSvgWidget("icons/Min.svg")
        turtle.setFixedSize(20, 20)
        layout.addWidget(turtle)

        self.wheel = QSlider(Qt.Orientation.Horizontal)
        self.wheel.setMinimum(0)
        self.wheel.setMaximum(2)
        self.wheel.setSingleStep(1)
        self.wheel.setStyleSheet(
            """
            QSlider::groove:horizontal {
                background: #787880;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #B25DC8;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            """
        )
        self.wheel.valueChanged.connect(self.emitValueChanged)  # Connect value changed signal
        layout.addWidget(self.wheel)

        hare = QSvgWidget("icons/Max.svg")
        hare.setFixedSize(20, 20)
        layout.addWidget(hare)

        self.setLayout(layout)

    def emitValueChanged(self):
        self.valueChanged.emit(self.wheel.value())  # Emit slider value when it changes


class BottomLeftWidget(RoundedRectWidget):
    def __init__(self, parent_layout, color):
        super().__init__(color)
        self.parent_layout = parent_layout
        self.pdf_button = None
        self.word_button = None
        self.label_image = None
        self.slider = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Button layout
        button_layout = QHBoxLayout()
        self.pdf_button = QPushButton("\u2714 PDF")
        self.word_button = QPushButton("Word")

        # Set default styles
        self.pdf_button.setStyleSheet(f"background-color: {colors.button_black}; color: white;")
        self.word_button.setStyleSheet(f"background-color: {colors.button_grey}; color: {colors.black};")

        # Connect buttons to functions
        self.pdf_button.clicked.connect(self.show_pdf_image)
        self.word_button.clicked.connect(self.show_word_image)

        button_layout.addWidget(self.pdf_button)
        button_layout.addWidget(self.word_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        button_layout.setContentsMargins(30, 20, 0, 0)
        layout.addLayout(button_layout)

        layout.addSpacing(100)

        # Add your widgets here
        label1 = CustomTextLabel(20, 'Inter', 'black', 'SELECT THE RANGE')
        label1.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(label1)

        layout.addSpacing(0)

        # Create a horizontal layout for the slider widget
        slider_layout = QHBoxLayout()
        self.slider = Slider()
        self.slider.valueChanged.connect(self.updateSummaryType)  # Connect slider valueChanged signal
        slider_layout.addWidget(self.slider)

        slider_layout.setContentsMargins(20, 0, 20, 0)
        layout.addLayout(slider_layout)

        label2 = CustomTextLabel(12, 'Inter', colors.light_black, 'Files must be in PDF format and under 10 MB')
        label2.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(label2)

        # Image container
        self.label_image = QLabel()
        layout.addWidget(self.label_image)

        # Display the initial image
        self.show_pdf_image()

        # Limitation section layout
        limitation_layout = QVBoxLayout()

        # Limitation section labels
        bottom_label_title = CustomTextLabel(12, 'Inter', 'red', 'NOTE:')
        bottom_label_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        bottom_label_title.setFont(QFont('Inter', 12, italic=True, ))  # Set italic style here
        limitation_layout.addWidget(bottom_label_title)

        bottom_label = CustomTextLabel(12, 'Inter', 'black',
                                       "1. File should be only in English\n"
                                       "2. File must have less than or equal to 50 pages only.\n"
                                       "3. File can only be of Word or PDF format.")
        bottom_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        bottom_label.setFont(QFont('Inter', 12, italic=True))  # Set italic style here
        limitation_layout.addWidget(bottom_label)

        # Set spacing between items in limitation_layout
        limitation_layout.setSpacing(0)
        limitation_layout.setContentsMargins(15, 0, 0, 20)

        # Add limitation_layout to main layout
        layout.addLayout(limitation_layout)

        self.setLayout(layout)

    def show_pdf_image(self):
        self.pdf_button.setStyleSheet(f"background-color: {colors.button_black}; color: white;")
        self.pdf_button.setText("\u2714 PDF")
        self.word_button.setStyleSheet(f"background-color: {colors.button_grey}; color: {colors.black};")
        self.word_button.setText("Word")

        # Load and display the PDF image
        png_path = "assets/Summarised.png"
        pixmap = QPixmap(png_path)
        if pixmap.isNull():
            print(f"Failed to load image: {png_path}")
        else:
            pixmap = pixmap.scaled(197, 207, Qt.AspectRatioMode.KeepAspectRatio)
            self.label_image.setPixmap(pixmap)
            self.label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set the file_type value
        self.parent_layout.file_type = 0

    def show_word_image(self):
        self.pdf_button.setStyleSheet(f"background-color: {colors.button_grey}; color: {colors.black};")
        self.pdf_button.setText("PDF")
        self.word_button.setStyleSheet(f"background-color: {colors.button_black}; color: white;")
        self.word_button.setText("\u2714 Word")

        # Load and display the Word image
        png_path = "assets/Word.png"
        pixmap = QPixmap(png_path)
        if pixmap.isNull():
            print(f"Failed to load image: {png_path}")
        else:
            pixmap = pixmap.scaled(197, 207, Qt.AspectRatioMode.KeepAspectRatio)
            self.label_image.setPixmap(pixmap)
            self.label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set the file_type value
        self.parent_layout.file_type = 1

    def updateSummaryType(self, value):
        self.parent_layout.summary_type = value


class BottomLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.file_type: int = 0
        self.summary_type: int = 0
        self.bottom_left_widget = None
        self.bottom_right_widget = None
        self.initUI()

    def initUI(self):
        # Create a QHBoxLayout for the bottom part
        bottom_layout = QHBoxLayout()
        self.bottom_left_widget = BottomLeftWidget(self, colors.white)
        self.bottom_right_widget = BottomRightWidget(self, colors.white)
        bottom_layout.addWidget(self.bottom_left_widget)
        bottom_layout.addWidget(self.bottom_right_widget)
        bottom_layout.setSpacing(25)
        bottom_layout.setContentsMargins(50, 0, 50, 50)
        self.setLayout(bottom_layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Summariser")
        self.setGeometry(100, 100, 1000, 800)

        main_widget = RoundedRectWidget(colors.grey)
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout(main_widget)

        # Add a top widget with fixed height
        self.top_widget = TopWidget(colors.grey)
        main_layout.addWidget(self.top_widget, 1)  # Add stretch factor directly here

        # Add the bottom_layout to a widget
        bottom_widget = BottomLayout()
        main_layout.addWidget(bottom_widget, 4)  # Add stretch factor directly here

    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)

        # Resize the top widget to maintain fixed height
        top_widget_height = self.height() // 7
        self.top_widget.setFixedHeight(top_widget_height)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
