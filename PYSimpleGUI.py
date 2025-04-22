import PySimpleGUI as sg
import json
import os
from agent import process_user_input, read_knowledge_base, write_knowledge_base

# Set the PySimpleGUI backend to PyQt5
sg.set_options(dpi_awareness=True)
sg.theme('DefaultNoMoreNagging')

class ChatbotGUI:
    def __init__(self):
        # Chat window layout
        chat_layout = [
            [sg.Multiline(size=(60, 30), key='-CHAT-', disabled=True, autoscroll=True, font=('Arial', 10))],
            [sg.Input(key='-INPUT-', font=('Arial', 10))],
            [sg.Button('Send', bind_return_key=True)]
        ]

        # Knowledge base window layout
        kb_layout = [
            [sg.Text("Project Knowledge Base", font=('Arial', 12, 'bold'))],
            [sg.Multiline(size=(40, 35), key='-KB-', disabled=True, font=('Arial', 10))]
        ]

        # Main layout
        layout = [
            [sg.Column(chat_layout), sg.VSeparator(), sg.Column(kb_layout)]
        ]

        self.window = sg.Window("Project Management Helper", layout, size=(1200, 800), finalize=True)

        # Add introductory text to chat log
        intro_text = """
        Hi, I am a friendly conversational helper dedicated to providing detailed and actionable advice to project managers. 
        I offer in-depth guidance on many aspects of project management including planning, risk, team communication, and stakeholder engagement. 
        I am an expert in PMI's PMBOK and agile methodologies.
        You can start the consultation with some general questions you may have regarding project management work. Or you can jump right in with current hurdles in your work. 
        The panel on the right will give you a glimpse of our understanding of your specific project and issues. 
        This will serve as a context to all your inquiries so if you notice discrepancies do not hesitate to bring it up.
        """
        self.update_chat_log("PM Helper", intro_text)

        # Load knowledge base
        self.load_knowledge_base()

    def run(self):
        while True:
            event, values = self.window.read()
            if event == sg.WINDOW_CLOSED:
                break
            if event == 'Send':
                user_message = values['-INPUT-'].strip()
                if user_message:
                    self.update_chat_log("You", user_message)
                    self.window['-INPUT-'].update('')  # Clear input field
                    response = self.get_agent_response(user_message)
                    self.update_chat_log("PM Helper", response)
                    self.load_knowledge_base()

        self.window.close()

    def update_chat_log(self, sender, message):
        chat = self.window['-CHAT-']
        current_text = chat.get()
        new_text = f"{current_text}\n{sender}: {message}"
        chat.update(value=new_text)
        # Scroll to the bottom
        chat.Widget.verticalScrollBar().setValue(chat.Widget.verticalScrollBar().maximum())

    def get_agent_response(self, user_message):
        try:
            response = process_user_input(user_message)
            return response
        except Exception as e:
            return f"Error: {str(e)}"

    def load_knowledge_base(self):
        knowledge = read_knowledge_base()
        kb_text = ""
        for category, items in knowledge.items():
            kb_text += f"{category}:\n"
            for key, value in items.items():
                kb_text += f"  {key}: {value}\n"
            kb_text += "\n"
        self.window['-KB-'].update(kb_text)

if __name__ == '__main__':
    gui = ChatbotGUI()
    gui.run()
