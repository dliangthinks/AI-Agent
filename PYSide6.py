import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QTextEdit, QPlainTextEdit, QLabel, QScrollArea, QSplitter, QSizePolicy)
from PySide6.QtGui import QFont, QColor, QPalette              
from PySide6.QtCore import Qt, Signal, QTimer

class InputTextEdit(QPlainTextEdit):
    enter_pressed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Ask your questions here")
        font = QFont()
        font.setPointSize(14)
        self.setFont(font)
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        
        self.document().contentsChanged.connect(self.adjust_height)
        # Set initial height to one line
        single_line_height = self.fontMetrics().height()
        self.setFixedHeight(single_line_height+10)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            if event.modifiers() & Qt.ShiftModifier:
                cursor = self.textCursor()
                cursor.insertText("\n")
                self.setTextCursor(cursor)
                self.adjust_height()
            else:
                self.enter_pressed.emit()
                # Shrink the input area back to one line
                single_line_height = self.fontMetrics().height()
                self.setFixedHeight(single_line_height+10)
                event.accept()
        else:
            super().keyPressEvent(event)

    def adjust_height(self):
        pixels_per_unit = self.fontMetrics().height()
        # how many lines are there already
        doc_height = self.document().size().height()
        if doc_height < 5:
            new_pixel_height = doc_height * pixels_per_unit + 1
            if new_pixel_height != self.height():
                self.setFixedHeight(new_pixel_height+10)

class CustomTextBlock(QTextEdit):
    def __init__(self, text, is_user=False, parent_width=None):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont("Arial", 12 if is_user else 14))
        self.setPlainText(text)
        self.setSizePolicy (QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.is_user = is_user
        self.parent_width = parent_width

        palette = self.palette()

        if is_user:
            palette.setColor(QPalette.Base, QColor(64, 64, 64))  # Dark gray
            self.setStyleSheet("""
                QTextEdit {
                    border-radius: 15px;
                    padding: 5px;
                    background-color: #404040;
                }
            """)
        else:
            palette.setColor(QPalette.Base, Qt.black)
            self.setStyleSheet("""
                QTextEdit {
                    padding: 5px;
                    background-color: black;
                }
            """)
        palette.setColor(QPalette.Text, Qt.white)
        self.setPalette(palette)

        self.document().contentsChanged.connect(self.adjust_size)
        self.adjust_size()



    # def sizeHint(self):
    #     # Get the size needed to display all the text
    #     doc_size = self.document().size().toSize()
    #     # Add any margins or padding you have
    #     return QSize(doc_size.width() + 20, doc_size.height() + 20)
    
   
    def adjust_size(self):

        
        docuSize = self.document().size()
        print(f"selfwidth: {docuSize}")
        # width doesn't exceed 400px
        widthNeeded = min (400, docuSize.width())
        print (widthNeeded)
        margins = self.contentsMargins()
        width = docuSize.width() + margins.left() + margins.right() + 5  # Adding a small buffer
        self.setFixedWidth(width)
        print (f"final: {width}")

        
        
        # these numbers are very important for the radius to show!!!!
        # self.document().setTextWidth(self.viewport().width() - 10)
        # size = self.document().size()
        # self.setFixedSize(size.width() + 20, size.height() + 10)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_size()

class ChatLog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)
        
        # Set black background
        palette = self.palette()
        palette.setColor(QPalette.Window, Qt.black)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def add_message(self, text, is_user=False):
        block = CustomTextBlock(text, is_user)

        if is_user:
            wrapper = QWidget()
            wrapper_layout = QHBoxLayout(wrapper)
            # this line adds an invisible box in front of the next widget
            wrapper_layout.addStretch()
            wrapper_layout.addWidget(block)
            self.layout.addWidget(wrapper)
        else:
            self.layout.addWidget(block)
        

        # Scroll to the bottom
        QTimer.singleShot(0, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        if self.parent() and isinstance(self.parent(), QScrollArea):
            scrollbar = self.parent().verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            if item.widget():
                if isinstance(item.widget(), CustomTextBlock):
                    item.widget().setMaximumWidth(self.width() * 0.7)
                item.widget().adjustSize()

class ChatbotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Management Helper")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Create a splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # Left side: Chat area
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)

        self.chat_log = ChatLog()
        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_scroll_area.setWidget(self.chat_log)

        # Set black background for chat scroll area
        chat_scroll_palette = self.chat_scroll_area.palette()
        chat_scroll_palette.setColor(QPalette.Window, Qt.black)
        self.chat_scroll_area.setAutoFillBackground(True)
        self.chat_scroll_area.setPalette(chat_scroll_palette)

        self.msg_entry = InputTextEdit()
        self.msg_entry.enter_pressed.connect(self.send_message)

        chat_layout.addWidget(self.chat_scroll_area)
        chat_layout.addWidget(self.msg_entry)

        # Right side: Project Knowledge Base
        kb_widget = QWidget()
        kb_layout = QVBoxLayout(kb_widget)

        kb_label = QLabel("Project Knowledge Base")
        kb_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        self.kb_text = QTextEdit()
        self.kb_text.setReadOnly(True)
        self.kb_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: white;
                border: none;
                font-size: 12px;
            }
        """)

        kb_layout.addWidget(kb_label)
        kb_layout.addWidget(self.kb_text)

        # Add widgets to splitter
        splitter.addWidget(chat_widget)
        splitter.addWidget(kb_widget)

        # Set initial sizes (70% chat, 30% KB)
        splitter.setSizes([int(self.width() * 0.7), int(self.width() * 0.3)])

        main_layout.addWidget(splitter)

        self.update_chat_log("PM Helper", "Welcome! How can I assist you today?")
        self.update_knowledge_base("Initial project knowledge will be displayed here.")

    def send_message(self):
        user_message = self.msg_entry.toPlainText().strip()
        if user_message:
            self.update_chat_log("You", user_message)
            self.msg_entry.clear()
            self.process_response(user_message)

    def process_response(self, user_message):
        response = self.get_agent_response(user_message)
        self.update_chat_log("PM Helper", response)
        self.update_knowledge_base("Updated knowledge based on the conversation.")

    def update_chat_log(self, sender, message):
        self.chat_log.add_message(f"{sender}: {message}", sender == "You")
        self.chat_scroll_area.verticalScrollBar().setValue(
            self.chat_scroll_area.verticalScrollBar().maximum()
        )
        
    def get_agent_response(self, user_message):
        return "This is a placeholder response from the PM Helper."
    
    def update_knowledge_base(self, content):
        self.kb_text.setPlainText(content)

if __name__ == '__main__':
    app = QApplication([])
    window = ChatbotGUI()
    window.show()
    app.exec()