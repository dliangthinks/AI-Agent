import wx
import textwrap

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

class CustomChatLog(wx.ScrolledWindow):
    def __init__(self, parent):
        super().__init__(parent, style=wx.VSCROLL)
        self.messages = []
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetScrollRate(0, 20)

    def AddMessage(self, sender, message):
        self.messages.append((sender, message))
        self.UpdateVirtualSize()
        self.Refresh()
        self.ScrollToBottom()
    def OnSize(self, event):
        self.UpdateVirtualSize()
        self.Refresh()
        event.Skip()

    def UpdateVirtualSize(self):
        dc = wx.ClientDC(self)
        dc.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        width, height = self.GetClientSize()
        total_height = self.CalculateTotalHeight(dc, width)
        self.SetVirtualSize((width, total_height))

    def CalculateTotalHeight(self, dc, width):
        y = 10
        for sender, message in self.messages:
            if sender == "You":
                wrapped_text = textwrap.fill(message, width=int(width * 0.7 / dc.GetTextExtent('W')[0]))
                lines = wrapped_text.split('\n')
                text_height = len(lines) * dc.GetCharHeight()
                y += text_height + 30
            else:
                wrapped_text = textwrap.fill(f"{sender}: {message}", width=int(width * 0.9 / dc.GetTextExtent('W')[0]))
                lines = wrapped_text.split('\n')
                y += len(lines) * dc.GetCharHeight() + 20
        return y

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        dc.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        width, height = self.GetClientSize()
        y = 10
        for sender, message in self.messages:
            if sender == "You":
                # User message
                wrapped_text = textwrap.fill(message, width=int(width * 0.7 / dc.GetTextExtent('W')[0]))
                lines = wrapped_text.split('\n')
                max_width = min(max(dc.GetTextExtent(line)[0] for line in lines) + 40, width * 0.75)
                text_height = len(lines) * dc.GetCharHeight()

                # Draw rounded rectangle
                rect = wx.Rect(width - max_width - 10, y, max_width, text_height + 20)
                dc.SetBrush(wx.Brush(wx.Colour(64, 64, 64)))  # Dark grey
                dc.SetPen(wx.Pen(wx.Colour(64, 64, 64)))
                dc.DrawRoundedRectangle(rect, 10)

                # Draw text
                dc.SetTextForeground(wx.WHITE)
                text_y = y + 10
                for line in lines:
                    dc.DrawText(line, width - dc.GetTextExtent(line)[0] - 30, text_y)
                    text_y += dc.GetCharHeight()

                y += text_height + 30
            else:
                # System message
                dc.SetTextForeground(wx.BLACK)
                wrapped_text = textwrap.fill(f"{sender}: {message}", width=int(width * 0.9 / dc.GetTextExtent('W')[0]))
                lines = wrapped_text.split('\n')
                for line in lines:
                    dc.DrawText(line, 10, y)
                    y += dc.GetCharHeight()
                y += 20

    def ScrollToBottom(self):
        if self.GetScrollRange(wx.VERTICAL) > 0:
            self.Scroll(0, self.GetScrollRange(wx.VERTICAL))
class ChatbotGUI(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Project Management Helper", size=(1200, 800))
        panel = wx.Panel(self)

        main_layout = wx.BoxSizer(wx.HORIZONTAL)
        chat_layout = wx.BoxSizer(wx.VERTICAL)

        self.chat_log = CustomChatLog(panel)
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
        
        self.chat_log.AddMessage("PM Helper", intro_text)

    def send_message(self, event):
        user_message = self.msg_entry.GetValue()
        if not user_message.strip():
            return
        self.msg_entry.Clear()
        self.chat_log.AddMessage("You", user_message)

        wx.CallAfter(self.process_response, user_message)

    def process_response(self, user_message):
        response = self.get_agent_response(user_message)
        self.chat_log.AddMessage("PM Helper", response)
        self.load_knowledge_base()

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
