import wx, datetime, time
import wx.lib.agw.pygauge as pg
from reportdb import ReportDb
from reporter import Report
from sessionmanager import SessionManager

#SESSION = 1
#NOTE_TYPE = "note"
#TIME = "12345"

def ss():
    '''
    Taken from
    http://wiki.wxpython.org/WorkingWithImages#A_Flexible_Screen_Capture_App
    '''
    scrDC = wx.ScreenDC()
    scrDcSize = scrDC.Size
    
    bmap = wx.EmptyBitmap(*scrDcSize)
    bmapx, bmapy = scrDcSize

    memDC = wx.MemoryDC(bmap)
    memDC.Blit(0, 0, bmapx, bmapy, scrDC, 0, 0)
    memDC.SelectObject(wx.NullBitmap)

    startpos = (0,0)
    bmapsize = (wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X), wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y))

    return bmap.GetSubBitmap(wx.RectPS(startpos, bmapsize))

    
class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        super(MainWindow, self).__init__(parent, title=title)
        self.parent = parent
        
        self.db = ReportDb()

        self.session = -1
        self.sessionrunning = False

        self.initialize()

    def initialize(self):
        self.SetWindowStyle(wx.RESIZE_BORDER | wx.CLIP_CHILDREN | wx.STAY_ON_TOP)
        
        self.sizer = wx.GridBagSizer()
        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableRow(1)
        self.createTypeField()
        self.createTimeMeter()

        self.createTimer()
        self.createMenu()

        self.bindHotKeys()

        #Make movable, even when typefield is active, not pretty but works
        self.Bind(wx.EVT_MOTION, self.onMouse)
        self.timemeter.Bind(wx.EVT_MOTION, self.onMouse)

        self.SetSizerAndFit(self.sizer)
        self.SetSizeWH(350, 135)
        self.SetSizeHints(200,self.GetSize().y,-1,-1 )
        self.Show()

    def createTypeField(self):
        self.typefield = wx.TextCtrl(self, value="Submit note: Alt-Enter\nSubmit bug: Alt-Shift-Enter\nScreenshot: Alt-F3", style=wx.TE_MULTILINE)
        self.sizer.Add(self.typefield, (0,0), (3,1), wx.EXPAND)
        self.typefield.Enable(False)
        
    def createTimeMeter(self):
        self.timemeter = pg.PyGauge(self, size=(-1,20))        
        self.sizer.Add(self.timemeter, (3,0), (1,1), wx.EXPAND)

    def createTimer(self):
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.updateTimeMeter, self.timer)
    
    def createMenu(self):
        menubar = wx.MenuBar()

        filemenu = wx.Menu()
        reportmenu = wx.Menu()

        self.newsessopt = filemenu.Append(wx.ID_NEW, "&New Session", "Start a New Session")
        self.closesessopt = filemenu.Append(-1, "Close Session", "Close the Session")        
        filemenu.AppendSeparator()
        quitopt = filemenu.Append(wx.ID_EXIT, "&Quit", "Quit Application")        

        self.genrepopt = reportmenu.Append(-1, "Create Report", "Generate a Report")
        reportmenu.AppendSeparator()
        self.sessmanageropt = reportmenu.Append(-1, "Session Manager", "Open Session Manager")
        
        menubar.Append(filemenu, "&Session")
        menubar.Append(reportmenu, "&Report")

        self.SetMenuBar(menubar)
        self.closesessopt.Enable(False)
        self.genrepopt.Enable(False)
        
        self.Bind(wx.EVT_MENU, self.onQuit, quitopt)
        self.Bind(wx.EVT_MENU, self.newSessionWindow, self.newsessopt)
        self.Bind(wx.EVT_MENU, self.closeSession, self.closesessopt)
        self.Bind(wx.EVT_MENU, self.generateReport, self.genrepopt)
        self.Bind(wx.EVT_MENU, self.openSessionManager, self.sessmanageropt)

    def bindHotKeys(self):
        self.Bind(wx.EVT_CHAR_HOOK, self.onSubmit)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        try:
            import win32con
        except ImportError:
            self.hasw32con = False
        else:
            self.hasw32con = True
            self.RegisterHotKey(100, win32con.MOD_ALT, win32con.VK_F3)
            self.Bind(wx.EVT_HOTKEY, self.onScreenShot, id=100)                

    def updateTimeMeter(self, e):
        self.timemeter.SetValue(self.timemeter.GetValue()+1)
        self.timemeter.Refresh()
        
        if self.timemeter.GetValue() >= self.timemeter.GetRange():
            self.timer.Stop()
            self.timemeter.SetBarColor(wx.RED)
            self.timemeter.Refresh()
            
    def submitNote(self, notetype):
        note = self.typefield.GetValue()
        if not note == "":
            now = datetime.datetime.now()
            timestamp = "%02d:%02d:%02d" % (now.hour, now.minute, now.second)
            
            self.db.writeNote(self.session, timestamp, notetype, note)
            self.typefield.Clear()

    def pauseSession(self):
        if self.timer.IsRunning():
            self.timer.Stop()
            self.timemeter.SetBarColor(wx.Color(212, 228, 255, 255))
            self.timemeter.Refresh()
        else:
            if self.timemeter.GetValue() < self.timemeter.GetRange():
                self.timer.Start(5 * 1000)
                self.timemeter.SetBarColor(wx.GREEN)
                self.timemeter.Refresh()

    def takeScreenShot(self):
        self.Hide()
        time.sleep(0.3)
        bitmap = ss()
        self.Show()

        now = datetime.datetime.now()
        filename = "%d%02d%02d-%02d%02d%02d.png" % (now.year, now.month, now.day,
                                                    now.hour, now.minute, now.second)
        bitmap.SaveFile(filename, wx.BITMAP_TYPE_PNG)
        
        timestamp = "%02d:%02d:%02d" % (now.hour, now.minute, now.second)
            
        self.db.writeNote(self.session, timestamp, "screenshot", filename)
       
    def newSessionWindow(self, e):
        newsesswin = NewSession(None, title="New Session")
        if newsesswin.ShowModal() != wx.ID_CANCEL:
            self.charter = newsesswin.getCharter()
            self.sessiontime = newsesswin.getTime()
            self.reporter = newsesswin.getReporter()
            self.startSession()
        newsesswin.Destroy()

    def startSession(self):
        self.typefield.Enable(True)
        self.timemeter.SetRange(self.sessiontime * 12)
        self.timemeter.SetBarColor(wx.GREEN)
        self.timer.Start(5 * 1000)
        self.sessionrunning = True

        now = datetime.datetime.now()
        starttime = "%02d:%02d" % (now.hour, now.minute)
        date = "%d-%02d-%02d" % (now.year, now.month, now.day)
        self.session = self.db.newSession(starttime, date, self.charter, self.reporter, self.sessiontime)

        self.genrepopt.Enable(True)
        self.newsessopt.Enable(False)
        self.closesessopt.Enable(True)
        self.sessmanageropt.Enable(False)

        self.typefield.Clear()

    def closeSession(self, e):
        self.typefield.Clear()
        self.typefield.Enable(False)
        self.typefield.ChangeValue("Submit note: Alt-Enter\nSubmit bug: Alt-Shift-Enter\nScreenshot: Alt-F3")

        if self.timer.IsRunning():
            self.timer.Stop()
        self.timemeter.SetValue(0)
        self.timemeter.Refresh()
        
        self.newsessopt.Enable(True)
        self.closesessopt.Enable(False)
        self.sessmanageropt.Enable(True)

        self.sessionrunning = False

    def generateReport(self, e):
        try:
            self.report = Report(self.db.getSessionInfo(self.session), self.db.getNotes(self.session))
        except TypeError:
            wx.MessageBox("Session not found", "Error", wx.OK|wx.ICON_ERROR)
        else:
            self.report.generateReport()
            wx.MessageBox("Created %s" % self.report.getReportName(), "Report", wx.OK)

    def openSessionManager(self, e):
        sessman = SessionManager(None, title="Session Manager")
        self.ToggleWindowStyle(wx.STAY_ON_TOP)
        sessman.ShowModal()
        sessman.Destroy()
        self.ToggleWindowStyle(wx.STAY_ON_TOP)

    def onSubmit(self ,e):
        if self.sessionrunning:
            if e.AltDown():
                if e.GetKeyCode() == wx.WXK_RETURN:
                    if e.ShiftDown():
                        self.submitNote("bug")
                    else:
                        self.submitNote("note")
                elif e.GetKeyCode() == wx.WXK_F3 and not self.hasw32con:
                    self.takeScreenShot()
            elif e.GetKeyCode() == wx.WXK_PAUSE:
                if self.sessionrunning:
                    self.pauseSession()        
            else:
                e.Skip()
        else:
            e.Skip()

    def onScreenShot(self, e):
        if self.sessionrunning:
            self.takeScreenShot()
        else:
            e.Skip()
        
    def onPaint(self, e):
        self.timemeter.Refresh()
        e.Skip()

    def onMouse(self, e):
        """
        Adapted from
        http://hasenj.wordpress.com/2009/04/14/making-a-fancy-window-in-wxpython/
        """
        if self.timemeter.HasCapture():
            self.CaptureMouse()
            self.timemeter.ReleaseMouse()
        if not e.Dragging():
            self.dragPos = None
            if self.HasCapture():
                self.ReleaseMouse()
                return
        else:
            if not self.HasCapture():
                self.CaptureMouse()

        if not self.dragPos:
            self.dragPos = e.GetPosition()
        else:
            pos = e.GetPosition()
            displacement = self.dragPos - pos
            self.SetPosition(self.GetPosition() - displacement)
        
    def onQuit(self, e):
        if self.timer.IsRunning():
            self.timer.Stop()
        self.Close()

class NewSession(wx.Dialog):
    def __init__(self, parent, title):
        super(NewSession, self).__init__(parent, title=title)
        self.initialize()

    def initialize(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        hboxcharter = wx.BoxSizer(wx.HORIZONTAL)
        hboxreporter = wx.BoxSizer(wx.HORIZONTAL)
        hboxtime = wx.BoxSizer(wx.HORIZONTAL)
        hboxbuttons = wx.BoxSizer(wx.HORIZONTAL)

        self.createInputs()
        self.createButtons()
        
        hboxcharter.Add(self.charterlabel)
        hboxcharter.Add(self.charterfield, flag=wx.LEFT|wx.EXPAND, border=25)

        hboxreporter.Add(self.reporterlabel)
        hboxreporter.Add(self.reporterfield, flag=wx.LEFT, border=25)

        hboxtime.Add(self.timelabel)
        hboxtime.Add(self.timefield, flag=wx.LEFT, border=25)
        
        hboxbuttons.Add(self.okbutton)
        hboxbuttons.Add(self.cancelbutton, flag=wx.LEFT, border=20)
                
        vbox.Add(hboxcharter, flag=wx.ALL, border=10)
        vbox.Add(hboxreporter, flag=wx.ALL, border=10)
        vbox.Add(hboxtime, flag=wx.ALL, border=10)
        vbox.Add(hboxbuttons, flag=wx.ALIGN_RIGHT|wx.ALL, border=10)

        self.SetSizerAndFit(vbox)

    def createInputs(self):
        self.charterlabel = wx.StaticText(self, label="Charter")
        self.charterfield = wx.TextCtrl(self, size=(300,75), style=wx.TE_MULTILINE)

        self.reporterlabel = wx.StaticText(self, label="Reporter")
        self.reporterfield = wx.TextCtrl(self, size=(300,-1))

        self.timelabel = wx.StaticText(self, label="Time (min)")
        self.timefield = wx.SpinCtrl(self, size=(60,-1), value="45", style=wx.TE_RIGHT)
        self.timefield.SetRange(1,180)

    def createButtons(self):
        self.okbutton = wx.Button(self, label="Ok", id=wx.ID_OK)
        self.cancelbutton = wx.Button(self, label="Cancel", id=wx.ID_CANCEL)
        
    def getCharter(self):
        return self.charterfield.GetValue()

    def getTime(self):
        return self.timefield.GetValue()

    def getReporter(self):
        return self.reporterfield.GetValue()


if __name__ == "__main__":
    app = wx.App()
    mainWin = MainWindow(None, title = "Session Reporter")
    app.MainLoop()
