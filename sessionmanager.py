import wx
from reportdb import ReportDb
from reporter import Report
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin


class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.BORDER_SUNKEN, size=(400,350))
        ListCtrlAutoWidthMixin.__init__(self)

class SessionManager(wx.Dialog):
    def __init__(self, parent, title):
        super(SessionManager, self).__init__(parent, title=title, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.parent = parent
        self.db = ReportDb()
        self.initialize()

    def initialize(self):
        self.panel = wx.Panel(self)

        mainsizer = wx.BoxSizer(wx.VERTICAL)

        sizer=wx.GridBagSizer(0,0)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(0)
        
        vboxbuttons = wx.BoxSizer(wx.VERTICAL)

        self.createListControl()

        self.createButtons()
        
        vboxbuttons.Add(self.genrepbutton, flag=wx.BOTTOM|wx.TOP, border=10)
        vboxbuttons.Add(self.deletebutton)
        vboxbuttons.Add((-1, 200), proportion=1, flag=wx.EXPAND)
        vboxbuttons.Add(self.exitbutton)

        sizer.Add(self.listcontrol,(0,0), (1,1),flag=wx.EXPAND)
        sizer.Add(vboxbuttons, (0,1), (1,1), border=15, flag=wx.ALL|wx.EXPAND)

        self.panel.SetSizer(sizer)
        mainsizer.Add(self.panel, 1, flag=wx.EXPAND)
        self.SetSizerAndFit(mainsizer)
        self.Center()

    def createListControl(self):
        self.listcontrol = AutoWidthListCtrl(self.panel)

        self.listcontrol.InsertColumn(0, "Date", width=70)
        self.listcontrol.InsertColumn(1, "Time", width=50)
        self.listcontrol.InsertColumn(2, "Charter", width=200)

        sessionlist = self.db.getListofSessions()
        index = 0
        for item in sessionlist:
            date = item[1]
            starttime = item[2]
            charter = item[3].replace("\n", " ")
            session_id = item[0]
            pos = self.listcontrol.InsertStringItem(index, date)
            self.listcontrol.SetStringItem(pos, 1, starttime)
            self.listcontrol.SetStringItem(pos, 2, charter)
            self.listcontrol.SetItemData(index, session_id)        
        
    def createButtons(self):
        self.genrepbutton = wx.Button(self.panel, label="Create Report", size=(90,-1))
        self.deletebutton = wx.Button(self.panel, label="Delete Session", size=(90,-1))
        self.exitbutton = wx.Button(self.panel, label="Exit", size=(90,-1), id=wx.ID_OK)

        self.Bind(wx.EVT_BUTTON, self.generateReport, self.genrepbutton)
        self.Bind(wx.EVT_BUTTON, self.deleteSession, self.deletebutton)

    def getSelectionId(self):
        session_id_list = []
        item = self.listcontrol.GetFirstSelected()
        if item == -1:
            return None
        else:
            session_id = self.listcontrol.GetItemData(item)
            session_id_list.append(session_id)
            while True:
                item = self.listcontrol.GetNextSelected(item)
                if item != -1:
                    session_id = self.listcontrol.GetItemData(item)
                    session_id_list.append(session_id)
                else:
                    break
        return session_id_list

    def getSelection(self):
        selectionlist = []
        item = self.listcontrol.GetFirstSelected()
        if item == -1:
            return None
        else:
            selectionlist.append(item)
            while True:
                item = self.listcontrol.GetNextSelected(item)
                if item != -1:
                    selectionlist.append(item)
                else:
                    break
        return selectionlist

    def generateReport(self, e):
        sessions = self.getSelectionId()
        if not sessions:
            wx.MessageBox("No session selected", "Create Report", wx.OK)
            return
        else:
            reportlist = []

            for session_id in sessions:
                report = Report(self.db.getSessionInfo(session_id), self.db.getNotes(session_id))
                report.generateReport()
                reportlist.append(report.getReportName())

            reports = ", ".join(reportlist)
            wx.MessageBox("Created %s" % reports, "Create Report", wx.OK)

    def deleteSession(self, e):
        sessions = self.getSelectionId()
        if not sessions:
            wx.MessageBox("No session selected", "Delete Session", wx.OK)
            return
        else:
            deletioncounter = len(sessions)
            dial = wx.MessageDialog(None, "Really delete %d session(s)?" % deletioncounter, "Delete Sessions", wx.YES_NO | wx.NO_DEFAULT)            
            if dial.ShowModal() != wx.ID_NO:
                for session_id in sessions:
                    self.db.deleteSession(session_id)
                
                listitems = self.getSelection()
                for item in listitems:
                    self.listcontrol.DeleteItem(item)
            else:
                return


if __name__ == "__main__":
    app = wx.App()
    mainWin = SessionManager(None, title = "Session Manager")
    app.MainLoop()
