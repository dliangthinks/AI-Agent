import wx

class AutoHeightTextCtrl(wx.TextCtrl):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, style=wx.TE_MULTILINE | wx.BORDER_NONE | wx.TE_NO_VSCROLL, **kwargs)
        self.Bind(wx.EVT_TEXT, self.OnTextChange)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.SetMinSize((self.GetSize().GetWidth(), self.GetCharHeight() + 10))  # Start with one line height

    def OnTextChange(self, event):
        self.AdjustHeight()
        event.Skip()

    def OnKeyDown(self, event):
        if event.ShiftDown() and event.GetKeyCode() == wx.WXK_RETURN:
            self.AppendText('\n')
            self.AdjustHeight()
        else:
            event.Skip()

    def AdjustHeight(self):
        # Get the current number of lines and set the height accordingly
        num_lines = self.GetNumberOfLines()
        line_height = self.GetCharHeight()
        new_height = (num_lines + 1) * line_height + 10  # Adding some padding
        self.SetMinSize((self.GetSize().GetWidth(), new_height))
        self.GetParent().Layout()

class RoundedRectanglePanel(wx.Panel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

    def Add(self, window, proportion=0, flag=0, border=0):
        self.sizer.Add(window, proportion, flag, border)

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)

        width, height = self.GetSize()
        radius = 15

        path = gc.CreatePath()
        path.AddRoundedRectangle(0, 0, width, height, radius)

        gc.SetPen(wx.Pen(wx.Colour(0, 0, 0), 1))  # Black border
        gc.SetBrush(wx.Brush(wx.Colour(255, 255, 255)))  # White background
        gc.DrawPath(path)

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Auto Height TextCtrl Example')
        panel = wx.Panel(self)
        
        rounded_panel = RoundedRectanglePanel(panel)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.text_ctrl = AutoHeightTextCtrl(rounded_panel)
        rounded_panel.Add(self.text_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        
        sizer.Add(rounded_panel, 1, wx.EXPAND | wx.ALL, 20)
        
        panel.SetSizer(sizer)
        
        self.SetSize((400, 300))
        self.Show()

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame()
        frame.Show()
        return True

if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()