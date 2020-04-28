import psycopg2 as pg

class DataBase():
    def __init__(self, dbName = None, user = None, password = None, host = "localhost", port = 5432):
        self.dbName = dbName
        self.user = user
        self.password = password
        self.host = host
        self.port = port

        try:
            self.conn = pg.connect(user = self.user, password = self.password, 
                                host = self.host, dbname = self.dbName)
            self.conn.autocommit = True
            self.cur = self.conn.cursor()
        except pg.DatabaseError as error:
            print("Cannot connected database: " + error)

        print("Connected database")
    
    def __del__(self):
        self.cur.close()
        self.conn.close()
        print("Connection end")
    
    def createTable(self, name, schema):
        self.cur.execute("CREATE TABLE IF NOT EXISTS {name} ( {schema} )".format(name = name, schema = schema))
        print("Table was created")
    
    def insertRow(self, name, schema):
        self.cur.execute("""INSERT INTO {name} VALUES ({schema})""".format(name = name, schema = schema))
    
    def deleteRow(self, name, number):
        self.cur.execute("""DELETE FROM {name} WHERE user_id = {number}""".format(name = name, number = number))

    def findByField(self, name, username):
        self.cur.execute("""SELECT * FROM %s WHERE username = %s""" % (name, username))
        user_data = self.cur.fetchall()
        return user_data
