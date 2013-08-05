import sqlite3 as sql
import atexit

class ReportDb():
    def __init__(self):
        self.con = sql.connect("reports.db")
        self.c = self.con.cursor()

        self.tables = self.c.execute('''SELECT name FROM sqlite_master WHERE type="table"''').fetchall()
        if not (u'notes',) in self.tables:
            self.createNotesTable()
        if not (u'sessions',) in self.tables:
            self.createSessionsTable()
   
        atexit.register(self.closeDB)
        

    def createNotesTable(self):
        self.c.execute('''CREATE TABLE notes (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INT, time TEXT, note_type TEXT, note TEXT)''')

    def createSessionsTable(self):
        self.c.execute('''CREATE TABLE sessions (session_id INTEGER PRIMARY KEY AUTOINCREMENT, starttime TEXT, date TEXT, charter TEXT, reporter TEXT, length INT)''')
    
    def writeNote(self, session_id, time, note_type, note):
        values = (session_id, time, note_type, note)
        self.c.execute('''INSERT INTO notes (session_id, time, note_type, note) VALUES (?, ?, ?, ?)''', values)
        #kolla om det gar att angra
        self.con.commit()

    def newSession(self, starttime, date, charter, reporter, length):
        values = (starttime, date, charter, reporter, length)
        self.c.execute('''INSERT INTO sessions (starttime, date, charter, reporter, length) VALUES (?, ?, ?, ?, ?)''', values)
        session_id = self.c.execute('''SELECT last_insert_rowid()''').fetchone()[0]
        self.con.commit()
        return session_id

    def getListofSessions(self):
        resultlist = []

        for row in self.c.execute('''SELECT session_id, date, starttime, charter FROM sessions'''):
            resultlist.append(row)
        return resultlist

    def getNotes(self,session_id):
        resultlist = []
        session_id = (session_id,)
        for row in self.c.execute('''SELECT * FROM notes WHERE session_id=? ORDER BY id''',session_id):
            resultlist.append(row)
        return resultlist

    def getSessionInfo(self, session_id):
        session_id = (session_id,)
        result = self.c.execute('''SELECT * FROM sessions WHERE session_id=?''', session_id).fetchone()
        return result
        
    def deleteSession(self, session_id):
        session_id = (session_id,)
        self.c.execute('''DELETE FROM sessions WHERE session_id=?''', session_id)
        self.c.execute('''DELETE FROM notes WHERE session_id=?''', session_id)
        self.con.commit()
        
    def deleteNote(self, note_id):
        note_id = (note_id,)
        self.c.execute('''DELETE FROM notes WHERE id=?''', note_id)
        
    def closeDB(self):
        self.con.close()
     
if __name__ == "__main__":
    a = ReportDb()
    
