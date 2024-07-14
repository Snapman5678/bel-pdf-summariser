import sys
import colors
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGridLayout, QSpacerItem, QSizePolicy, QPushButton
)
from PyQt6.QtGui import QPalette, QColor, QPainter, QFont
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

class BottomRightWidget(RoundedRectWidget):
    def __init__(self, color):
        super().__init__(color)
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
        upload_button = QPushButton("Click or drop a file")
        upload_button.setStyleSheet(f"background: none; border: none; font: 16px 'Inter'; color: {colors.purple};")
        layout.addWidget(upload_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(10)

        # Subtitle below button
        subtitle1 = CustomTextLabel(12, 'Inter', colors.light_black,
                                    'Once the summary has been created your file will\nbe deleted automatically.')
        subtitle1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle1, alignment=Qt.AlignmentFlag.AlignCenter)

        # Spacer to push the buttons to the bottom right
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Add clear and summarise buttons at the bottom right
        button_layout = QHBoxLayout()
        button_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        clear_button = QPushButton("Clear")
        clear_button.setStyleSheet(
            f"background-color: {colors.grey}; color: white; font: 16px 'Inter'; border-radius: 17px; min-width: 120px;min-height:35px;")
        button_layout.addWidget(clear_button)

        button_layout.addSpacing(10)

        summarise_button = QPushButton("Summarize")
        summarise_button.setStyleSheet(
            f"background-color: {colors.purple}; color: white; font: 16px 'Inter'; border-radius: 17px; min-width: 120px;min-height:35px;")
        button_layout.addWidget(summarise_button)

        # Add the button layout to the vertical layout
        layout.addLayout(button_layout)

        layout.addSpacing(20)


        self.setLayout(layout)


class BottomLeftWidget(RoundedRectWidget):
    def __init__(self, color):
        super().__init__(color)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Add your widgets here
        label = CustomTextLabel(12, 'Arial', 'black', 'space space space space space space space space')
        layout.addWidget(label)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Summariser")
        self.setGeometry(100, 100, 1000, 800)

        main_widget = RoundedRectWidget(colors.grey)
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout(main_widget)

        # Add a top widget with half the height of the window
        self.top_widget = TopWidget(colors.grey)
        main_layout.addWidget(self.top_widget)

        # Create a QHBoxLayout for the bottom part
        bottom_layout = QHBoxLayout()
        self.bottom_left_widget = BottomLeftWidget(colors.white)
        self.bottom_right_widget = BottomRightWidget(colors.white)
        bottom_layout.addWidget(self.bottom_left_widget)
        bottom_layout.addWidget(self.bottom_right_widget)
        bottom_layout.setSpacing(25)
        bottom_layout.setContentsMargins(50, 0, 50, 50)

        # Add the bottom_layout to a widget
        bottom_widget = QWidget()
        bottom_widget.setLayout(bottom_layout)
        main_layout.addWidget(bottom_widget)

    def resizeEvent(self, event):
        """Resize the top widget to one-seventh the height of the window."""
        QMainWindow.resizeEvent(self, event)
        top_widget_height = self.height() // 7
        self.top_widget.setFixedHeight(top_widget_height)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
