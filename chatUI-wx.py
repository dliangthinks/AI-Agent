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
                return  # Don't skip the event to prevent newline
        event.Skip()

    def OnText(self, event):
        self.AdjustInputBoxSize()
        event.Skip()

    def AdjustInputBoxSize(self):
        numLines = self.GetNumberOfLines()
        charHeight = self.GetCharHeight()
        height = min(numLines * charHeight + 10, 5 * charHeight + 10)  # Limit to 5 lines
        self.SetMinSize(wx.Size(-1, height))
        self.GetParent().Layout()

class ChatbotGUI(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Project Management Helper", size=(1200, 800))
        panel = wx.Panel(self)

        main_layout = wx.BoxSizer(wx.HORIZONTAL)
        chat_layout = wx.BoxSizer(wx.VERTICAL)

        self.chat_log = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
        self.msg_entry = InputTextCtrl(panel, style=wx.TE_MULTILINE)

        chat_layout.Add(self.chat_log, 1, wx.EXPAND | wx.ALL, 5)
        chat_layout.Add(self.msg_entry, 0, wx.EXPAND | wx.ALL, 5)

        knowledge_sizer = wx.BoxSizer(wx.VERTICAL)
        knowledge_label = wx.StaticText(panel, label="Project Knowledge Base")
        self.knowledge_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)

        knowledge_sizer.Add(knowledge_label, 0, wx.ALL, 5)
        knowledge_sizer.Add(self.knowledge_text, 1, wx.EXPAND | wx.ALL, 5)

        main_layout.Add(chat_layout, 1, wx.EXPAND | wx.ALL, 10)
        main_layout.Add(knowledge_sizer, 1, wx.EXPAND | wx.ALL, 10)

        panel.SetSizer(main_layout)
        self.load_knowledge_base()
        self.Show()

        self.Bind(wx.EVT_BUTTON, self.send_message, id=wx.ID_OK)

        intro_text = ("""
        Hi, I am a friendly conversational helper dedicated to providing detailed and actionable advice to project managers. 
        I offer in-depth guidance on many aspects of project management including planning, risk, team communication and stakeholder engagement. 
        I am an expert in PMI's PMBOK and agile methodologies.
        You can start the consultation with some general questions you may have regarding project management work. Or you can jump right in with current hurdles in your work. 
        The panel on the right will give you a glimpse of our understanding of your specific project and issues. 
        This will serve as a context to all your inquiries so if you notice discrepancies do not hesitate to bring it up.""")
        
        self.update_chat_log("PM Helper", intro_text)

    def send_message(self, event):
        user_message = self.msg_entry.GetValue()
        if not user_message.strip():
            return
        self.msg_entry.Clear()
        self.update_chat_log("You", user_message)

        wx.CallAfter(self.process_response, user_message)

    def process_response(self, user_message):
        response = self.get_agent_response(user_message)
        self.update_chat_log("PM Helper", response)
        self.load_knowledge_base()

    def update_chat_log(self, sender, message):
        self.chat_log.SetInsertionPointEnd()
        # Set text color based on sender
        if sender == "You":
            #self.chat_log.SetTextColour(wx.BLUE)
            
            # Calculate the right-aligned position (3/4 of the width)
            text_width = self.chat_log.GetSize().GetWidth() * 0.5
            right_pos = self.chat_log.GetSize().GetWidth() - text_width
            
            # Add sender name (right-aligned)
            #self.chat_log.BeginBold()
            self.chat_log.WriteText(" " * int(right_pos / 10))  # Approximate space characters
            self.chat_log.WriteText(f"{sender}:\n\n")
            #self.chat_log.EndBold()
            
            # Add message (right-aligned)
            lines = message.split('\n')
            for line in lines:
                self.chat_log.WriteText(" " * int(right_pos / 10))  # Approximate space characters
                self.chat_log.WriteText(f"{line}\n")
        else:
            #self.chat_log.SetTextColour(wx.RED)
            
            # Add sender name (with indentation)
            #self.chat_log.BeginBold()
            self.chat_log.WriteText(f"    {sender}:\n\n")
            #self.chat_log.EndBold()
            
            # Add message (with indentation)
            lines = message.split('\n')
            for line in lines:
                self.chat_log.WriteText(f"    {line}\n")

        self.chat_log.WriteText("\n")  # Add an extra line after the message
        #self.chat_log.EndTextColour()
        self.chat_log.ShowPosition(self.chat_log.GetLastPosition())

    def get_agent_response(self, user_message):
        try:
            response = process_user_input(user_message)  
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
