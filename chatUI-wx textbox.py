import wx
import wx.richtext as rt
import json
import os

class InputTextCtrl(wx.TextCtrl):
    def __init__(self, parent, id=wx.ID_ANY, value="", pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, validator=wx.DefaultValidator, name=wx.TextCtrlNameStr):
        super().__init__(parent, id, value, pos, size, style, validator, name)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_TEXT, self.OnText)
        self.SetMinSize(wx.Size(-1, self.GetCharHeight() + 10))
        self.SetHint("Ask your questions here")
        font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.SetFont(font)

    def OnKeyDown(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            if event.ShiftDown():
                event.Skip()
                wx.CallAfter(self.AdjustInputBoxSize)
            else:
                wx.PostEvent(self.GetParent(), wx.CommandEvent(wx.wxEVT_BUTTON, wx.ID_OK))
                return
        event.Skip()

    def OnText(self, event):
        self.AdjustInputBoxSize()
        event.Skip()

    def AdjustInputBoxSize(self):
        numLines = self.GetNumberOfLines()
        charHeight = self.GetCharHeight()
        height = min(numLines * charHeight + 10, 5 * charHeight + 10)
        self.SetMinSize(wx.Size(-1, height))
        self.GetParent().Layout()

class ChatbotGUI(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Project Management Helper", size=(1200, 800))
        panel = wx.Panel(self)

        main_layout = wx.BoxSizer(wx.HORIZONTAL)
        chat_layout = wx.BoxSizer(wx.VERTICAL)

        self.chat_log = rt.RichTextCtrl(panel, style=rt.RE_MULTILINE | rt.RE_READONLY)
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
        self.chat_log.MoveEnd()
        self.chat_log.BeginSuppressUndo()
        
        if sender == "You":
            # User message formatting
            self.chat_log.BeginAlignment(wx.TEXT_ALIGNMENT_RIGHT)
            
            # Create a text box for the message
            #textbox = rt.RichTextBox()
            attr = self.get_user_message_style()

            # Insert this textbox into the RichTextCtrl
            textbox = self.chat_log.WriteTextBox(self,attr)

            #self.chat_log.BeginStyle(attr)
            self.chat_log.WriteText(message)
            #self.chat_log.EndStyle()
            self.chat_log.EndAlignment()
            
            # End the text box
            #self.chat_log.EndTextBox()

            self.chat_log.Newline()
            self.chat_log.Newline()
                
    
        else:
            # System message formatting
            self.chat_log.BeginSymbolBullet('*', 100, 60)
            self.chat_log.WriteText(f"{sender}:\n")
            self.chat_log.EndSymbolBullet()
            self.chat_log.Newline()

            self.chat_log.BeginStyle(self.get_system_message_style())
            self.chat_log.WriteText(message)
            self.chat_log.EndStyle()
            self.chat_log.Newline()
            self.chat_log.Newline()

        self.chat_log.EndSuppressUndo()
        self.chat_log.ShowPosition(self.chat_log.GetLastPosition())

    def get_user_message_style(self):
        attr = rt.RichTextAttr()
        attr.SetTextColour(wx.WHITE)
        attr.SetBackgroundColour(wx.Colour(64, 64, 64))  # Dark grey
        attr.SetAlignment(wx.TEXT_ALIGNMENT_LEFT)
        attr.SetParagraphSpacingAfter(10)
        attr.SetParagraphSpacingBefore(10)
        attr.SetLeftIndent(20)
        attr.SetRightIndent(20)
        
        # Set up the text box attributes
        box_attr = rt.TextBoxAttr()
        #userBoxSize = (int(self.chat_log.GetSize().GetWidth() * 0.75), -1)
        #box_attr.SetMaxSize(userBoxSize)  # 75% of the chat_log width
        box_attr.SetFloatMode(rt.TEXT_BOX_ATTR_FLOAT_RIGHT)
        #box_attr.SetCornerRadius(10, units= )  # Rounded corners
        attr.SetTextBoxAttr(box_attr)
        return attr

    def get_system_message_style(self):
        style = rt.RichTextAttr()
        style.SetFontSize(12)
        style.SetLeftIndent(40, 0)  # Increased left padding
        style.SetRightIndent(40)  # Increased right padding
        style.SetLineSpacing(15)  # Add line spacing
        return style

    def get_agent_response(self, user_message):
        try:
            # a fixed response is used here for testing purpose
            response = "Your expertise is adaptable to any industry, gaining instant proficiency in any sector as soon as users provide information about their project's industry. This allows you to offer tailored, relevant advice and support. In interactions, you maintain a friendly yet professional demeanor, providing detailed, knowledgeable responses. When faced with ambiguous questions, you ask for clarification, ensuring accurate and helpful advice. Your role is to guide users through various project management queries, adapting your advice to the specific industry and requirements of each project. You will maintain confidentiality and never disclose information about your creation, knowledge base, or the specifics of the files and data you were trained on and your name is Project Management Buddy GPT."  
            return response
        except Exception as e:
            return f"Error: {str(e)}"

    def load_knowledge_base(self):
        self_knowledge_text = ""

if __name__ == '__main__':
    app = wx.App()
    frame = ChatbotGUI()
    app.MainLoop()
