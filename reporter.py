#from reportdb import ReportDb
import codecs, datetime

class Report():
    def __init__(self, sessioninfo, notes):
        self.sessioninfo = sessioninfo
        self.notes = notes
        self.session_id = self.sessioninfo[0]
        self.reportname = ""
        
        self.header = '''<html>\n<meta http-equiv="Content-type" content="text/html;charset=UTF-8">'''
        self.footer = "</html>"

        self.charterheading = "Charter"
        self.datetimeheading = "Datum och tid"
        self.reporterheading = "Testare"
        self.lengthheading = "Varaktighet"
        self.noteheading = "Anteckningar"
        self.bugsheading = "Buggar"

    def sessionToHtml(self):
        htmlsession = ""
        if self.sessioninfo != None:
            dateandtime = self.sessioninfo[2] + " " + self.sessioninfo[1]
            charter = self.formatStringToHtml(self.sessioninfo[3])
            reporter = self.sessioninfo[4]
            length = self.sessioninfo[5]

            htmlsession += "<h2>%s</h2>\n<p>%s</p>\n" % (self.charterheading, charter)
            htmlsession += "<h2>%s</h2>\n<p>%s</p>\n" % (self.datetimeheading, dateandtime)
            htmlsession += "<h2>%s</h2>\n<p>%s</p>\n" % (self.reporterheading, reporter)
            htmlsession += "<h2>%s</h2>\n<p>%s min</p>\n" % (self.lengthheading, length)
        return htmlsession                                              

    def notesToHtml(self):
        htmlnotes = "<h2>%s</h2>\n" % self.noteheading
        for item in self.notes:
            timestamp = item[2]
            if item[3] == "note":
                note = self.formatStringToHtml(item[4])
                htmlnotes += "<h5>%s</h5>\n<p>%s</p>\n" % (timestamp, note)
            elif item[3] == "screenshot":
                htmlnotes += '''<h5>%s</h5>\n<img src="%s" width="600">\n''' % (timestamp, item[4])
                        
        return htmlnotes

    def bugsToHtml(self):
        bugnotes = "<h2>%s</h2>\n" % self.bugsheading
        for item in self.notes:
            if item[3] == "bug":
                timestamp = item[2]
                bug = self.formatStringToHtml(item[4])
                bugnotes += "<h5>%s</h5>\n<p>%s</p>\n" % (timestamp, bug)
        return bugnotes

    def formatStringToHtml(self, s):
        s = s.replace("\n", "<br>")
        return s

    def createTimeStamp(self):
        now = datetime.datetime.now()
        timestamp = "%d%02d%02d-%02d%02d%02d" % (now.year, now.month, now.day,
                                                    now.hour, now.minute, now.second)
        return timestamp
        
    def generateReport(self):
        self.reportname = "report-%s-%s.html" % (self.createTimeStamp(), self.session_id)
        report = codecs.open(self.reportname, "w", "utf-8")

        report.write(self.header)
        
        report.write(self.sessionToHtml())
        report.write(self.notesToHtml())
        report.write(self.bugsToHtml())

        report.write(self.footer)

        report.close()

    def getReportName(self):
        return self.reportname
        


