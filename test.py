import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QSizePolicy
from PySide6.QtCore import Qt

class AdaptiveTextEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        #self.setWordWrapMode(Qt.TextWordWrap)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textChanged.connect(self.adjust_width)

    def adjust_width(self):
        doc = self.document()
        doc_size = doc.size()
        margins = self.contentsMargins()
        width = doc_size.width() + margins.left() + margins.right() + 5  # Adding a small buffer
        self.setFixedWidth(width)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Adaptive Width TextEdit")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)  # Align text blocks to the top

        for i in range(5):
            text_edit = AdaptiveTextEdit()
            text_edit.setPlainText(f"This is message {i+1}\n" * (i + 1))
            layout.addWidget(text_edit)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())