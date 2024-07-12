import wx
import json
import os
from agent import process_user_input, read_knowledge_base, write_knowledge_base

class InputTextCtrl(wx.TextCtrl):
    def __init__(self, parent, id=wx.ID_ANY, value="", pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, validator=wx.DefaultValidator, name=wx.TextCtrlNameStr):
        super().__init__(parent, id, value, pos, size, style, validator, name)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_TEXT, self.OnText)
        self.SetMinSize(wx.Size(-1, self.GetCharHeight() + 10))

    def OnKeyDown(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            if event.ShiftDown():
                event.Skip()
                wx.CallAfter(self.AdjustInputBoxSize)
            else:
                wx.PostEvent(self.GetParent(), wx.CommandEvent(wx.wxEVT_BUTTON, wx.ID_OK))
        else:
            event.Skip()

    def OnText(self, event):
        self.AdjustInputBoxSize()
        event.Skip()

    def AdjustInputBoxSize(self):
        numLines = self.GetNumberOfLines()
        charHeight = self.GetCharHeight()
        height = min(numLines * charHeight + 10, 100)  # Limit max height
        self.SetMinSize(wx.Size(-1, height))
        self.GetParent().Layout()

class ChatbotGUI(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Project Management Helper", size=(1200, 800))
        panel = wx.Panel(self)

        # Main layout is horizontal: chat window and KB window
        main_layout = wx.BoxSizer(wx.HORIZONTAL)

        # Chat Log layout consists of three vertical parts : intro text, chat log, and input box
        chat_layout = wx.BoxSizer(wx.VERTICAL)

        # Add introductory text to chat log
        intro_text = ("""Hi, I am a friendly conversational helper dedicated to providing detailed and actionable advice to project managers. I offer in-depth guidance on many aspects of project management including planning, risk, team communication and stakeholder engagement. I am an expert in PMI's PMBOK and agile methodologies. You can start the consultation with some general questions you may have regarding project management work. Or you can jump right in with current hurdles in your work. The panel on the right will give you a glimpse of our understanding of your specific project and issues. This will serve as a context to all your inquiries so if you notice discrepancies do not hesitate to bring it up.""")
        
        # Create a StaticBox for the intro text
        intro_box = wx.StaticBox(panel, label="Introduction")
        intro_box_sizer = wx.StaticBoxSizer(intro_box, wx.VERTICAL)

        # Add the intro text to the StaticBoxSizer
        intro_text_ctrl = wx.StaticText(intro_box, label=intro_text)
        intro_text_ctrl.Wrap(self.GetSize().GetWidth() - 20)  # Adjust wrap width
        intro_box_sizer.Add(intro_text_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Chat log
        self.chat_log = wx.ScrolledWindow(panel, style=wx.VSCROLL)
        self.chat_log_sizer = wx.BoxSizer(wx.VERTICAL)
        self.chat_log.SetSizer(self.chat_log_sizer)
        self.chat_log.SetScrollRate(0, 10)

        # Input area
        self.msg_entry = InputTextCtrl(panel, style=wx.TE_MULTILINE)

        # Adding intro text, chat log and input area to chat layout
        chat_layout.Add(intro_box_sizer, 0, wx.EXPAND | wx.ALL, 5)
        chat_layout.Add(self.chat_log, 1, wx.EXPAND | wx.ALL, 5)
        chat_layout.Add(self.msg_entry, 0, wx.EXPAND | wx.ALL, 5)

        # Knowledge database window
        knowledge_sizer = wx.BoxSizer(wx.VERTICAL)
        knowledge_label = wx.StaticText(panel, label="Project Knowledge Base")
        self.knowledge_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        knowledge_sizer.Add(knowledge_label, 0, wx.ALL, 5)
        knowledge_sizer.Add(self.knowledge_text, 1, wx.EXPAND | wx.ALL, 5)

        # Add chat and knowledge sizers to main sizer
        main_layout.Add(chat_layout, 2, wx.EXPAND | wx.ALL, 10)
        main_layout.Add(knowledge_sizer, 1, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(main_layout)
        self.load_knowledge_base()
        self.Show()

        # Bind the OK event (triggered by Return key) to send_message
        self.Bind(wx.EVT_BUTTON, self.send_message, id=wx.ID_OK)

    def send_message(self, event):
        user_message = self.msg_entry.GetValue()
        if not user_message.strip():
            return
        self.msg_entry.Clear()
        self.update_chat_log("You", user_message, is_user=True)

        # Call agent's process_user_input function
        response = self.get_agent_response(user_message)

        self.update_chat_log("PM Helper", response, is_user=False)
        self.load_knowledge_base()  # Reload the knowledge base after each interaction

    def update_chat_log(self, sender, message, is_user):
        message_panel = wx.Panel(self.chat_log)
        message_sizer = wx.BoxSizer(wx.HORIZONTAL)

        if is_user:
            box = wx.StaticBox(message_panel, label=sender)
            box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

            text = wx.StaticText(box, label=message)
            text.Wrap(min(self.GetSize().GetWidth() * 0.6, text.GetSize().GetWidth()))
            box_sizer.Add(text, 0, wx.ALL, 5)

            message_sizer.AddStretchSpacer()
            message_sizer.Add(box_sizer, 0, wx.EXPAND | wx.RIGHT, 10)
        else:
            indent = 20
            text = wx.StaticText(message_panel, label=message)
            text.Wrap(self.GetSize().GetWidth() - indent - 20)

            message_sizer.AddSpacer(indent)
            message_sizer.Add(text, 1, wx.EXPAND | wx.RIGHT, 10)

        message_panel.SetSizer(message_sizer)
        self.chat_log_sizer.Add(message_panel, 0, wx.EXPAND | wx.ALL, 5)

        self.chat_log.Layout()
        self.chat_log.Scroll(0, self.chat_log.GetVirtualSize().GetHeight())

    def get_agent_response(self, user_message):
        try:
            response = process_user_input(user_message)  
            self.load_knowledge_base()  # Reload the knowledge base after each interaction
            return response
        except Exception as e:
            return f"Error: {str(e)}"

    def load_knowledge_base(self):
        knowledge = read_knowledge_base()
        self.knowledge_text.Clear()
        for category, items in knowledge.items():
            self.knowledge_text.AppendText(f"{category}:\n")
            for key, value in items.items():
                self.knowledge_text.AppendText(f"  {key}: {value}\n")
            self.knowledge_text.AppendText("\n")

if __name__ == '__main__':
    app = wx.App()
    frame = ChatbotGUI()
    app.MainLoop()