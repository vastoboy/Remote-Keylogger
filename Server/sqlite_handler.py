import sqlite3
from prettytable import from_db_cursor



class SqliteHandler:


    # creates database where connected client info will be stored
    def create_db(self):
        try:
            database_conn_object = sqlite3.connect('clientDatabase.db', check_same_thread=False)
            cursor = database_conn_object.cursor()
            # creates table if it does not exist
            cursor.execute("""CREATE TABLE IF NOT EXISTS connectedNodes(
                                Client_ID INTEGER PRIMARY KEY NOT NULL,
                                Date_Joined DATETIME DEFAULT CURRENT_TIMESTAMP,
                                Node_Name TEXT NULL,
                                IP_Address TEXT NULL,
                                Mac_Address TEXT NULL,
                                Platform TEXT NULL,
                                Release TEXT NULL,
                                Processor TEXT NULL,
                                File_Name TEXT NULL
                                );
                                """)
            # deletes whatever is in the table if it already exists
            cursor.execute('DELETE FROM connectedNodes;');
            database_conn_object.commit()  # commits changes to database
            print("[+]Database Created!!!")
            return database_conn_object  # socket connection object
        except:
            print("[-]Unable To create database!!!")



    # store client information in database when a new connection is made
    def store_node_data(self, client_database_conn, conn, fileName, client_sysinfo_list):
        cursor = client_database_conn.cursor()
       
        # insert client info into database
        cursor.execute(
            "INSERT INTO connectedNodes(Node_Name, IP_Address, Mac_Address, Platform, Release, Processor, File_Name) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (str(client_sysinfo_list[0]), str(client_sysinfo_list[1]),
             str(client_sysinfo_list[2]), str(client_sysinfo_list[3]),
             str(client_sysinfo_list[4]), str(client_sysinfo_list[5]),
             str(fileName)
             ))
        client_database_conn.commit()  # commits changed



	# display system information of connected nodes
    def get_nodes_info(self, db_conn, client_conn_object):
        cursor = db_conn.cursor()
        for conn_obj in range(1, len(client_conn_object)):
            try:
                # check if clients listed in database are still connected to the server
                client_conn_object[conn_obj].send("conn check".encode())
            except:
                # remove information from database and client_conn_object list if not connected
                client_conn_object.remove(client_conn_object[conn_obj])
                cursor.execute("DELETE FROM connectedNodes WHERE Client_ID=?", (str(conn_obj)))

        cursor.execute("SELECT * FROM connectedNodes")  # retrieve all client information in the database
        connected_client = from_db_cursor(cursor)  # insert retrieved client information into a table
        print(connected_client)



    # print out the contents of text file
    def get_file_content(self, client_id, db_conn):
        cursor = db_conn.cursor()
        cursor.execute("SELECT File_Name FROM connectedNodes WHERE Client_ID=?", (str(client_id)))
        fileName = str(cursor.fetchall())
        fileName = fileName[3:]
        fileName = fileName[:-4]
        with open(fileName, "r") as logFile:
            lines = logFile.readlines()
            for line in lines:
                print(line)
            logFile.close()




