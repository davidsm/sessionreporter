#from reportdb import ReportDb
import codecs, datetime
from jinja2 import Environment, FileSystemLoader

class Report():
    def __init__(self, sessioninfo, notes):
        self.template_env = Environment(loader=FileSystemLoader('templates'))
        self.template = self.template_env.get_template("basic_html_report.template")

        self.sessioninfo = sessioninfo
        self.notes = notes
        self.session_id = self.sessioninfo[0]

        self.variables = {}
        
        headings = {}
        headings["charter"] = "Charter"
        headings["datetime"] = "Datum och tid"
        headings["reporter"] = "Testare"
        headings["length"] = "Varaktighet"
        headings["notes"] = "Anteckningar"
        headings["bugs"] = "Buggar"
        self.variables["headings"] = headings

    def sessionToHtml(self):
        if self.sessioninfo != None:
            dateandtime = self.sessioninfo[2] + " " + self.sessioninfo[1]
            charter = self.formatStringToHtml(self.sessioninfo[3])
            reporter = self.sessioninfo[4]
            length = self.sessioninfo[5]

            self.variables['charter'] = charter
            self.variables['dateandtime'] = dateandtime
            self.variables['reporter'] = reporter
            self.variables['length'] = length                                            

    def notesToHtml(self):
        notelist = []
        for item in self.notes:
            if item[3] != "bug":
                notelist.append({"timestamp": item[2],
                            "type": item[3],
                            "note": item[4].split("\n")})
                
        self.variables["notes"] = notelist

    def bugsToHtml(self):
        buglist = []
        for item in self.notes:
            if item[3] == "bug":
                buglist.append({"timestamp": item[2],
                    "type": item[3],
                    "note": item[4]})
        self.variables["bugs"] = buglist

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

        self.sessionToHtml()
        self.notesToHtml()
        self.bugsToHtml()

        report.write(self.template.render(self.variables))
        report.close()

    def getReportName(self):
        return self.reportname
        


