import sys
import colors
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtGui import QPalette, QColor

class RoundedRectWidget(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Summariser")
        self.setGeometry(100, 100, 1000,800)

        main_widget = RoundedRectWidget(colors.grey)
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout(main_widget)

        # Add a top widget with half the height of the window
        top_widget = RoundedRectWidget(colors.grey)
        main_layout.addWidget(top_widget)

        # Create a QHBoxLayout for the bottom part
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(RoundedRectWidget(colors.white))
        bottom_layout.addWidget(RoundedRectWidget(colors.white))
        bottom_layout.setSpacing(25)
        bottom_layout.setContentsMargins(50,0,50,50)

        # Add the bottom_layout to a widget
        bottom_widget = QWidget()
        bottom_widget.setLayout(bottom_layout)
        main_layout.addWidget(bottom_widget)

    def resizeEvent(self, event):
        """Resize the top widget to half the height of the window."""
        QMainWindow.resizeEvent(self, event)
        top_widget_height = self.height() // 7
        self.centralWidget().layout().itemAt(0).widget().setFixedHeight(top_widget_height)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

