# Remote Sniffer

<img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" alt="Python"><img src="https://img.shields.io/badge/Sqlite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="sqlite">

The Multiclient Python Keylogger is a powerful tool designed to monitor keystrokes on multiple client machines simultaneously. This keylogger is capable of running on various operating systems and can be deployed to gather target's keystrokes.


## Features

* Remote Packet Capture: Capture network packets remotely.



## Installation

Remote Sniffer requires Python 3 and certain dependencies. Use pip to install the required packages:

`pip install -r requirements.txt`



## Usage 

* Start the Server: Run the server program to start the interactive shell and send commands to the client.
* Access the Client: Run the client program to connect to the server.


```

    Remote Sniffer Commands
         'guide':[Display Remote Sniffer user commands]
         'clients':['displays clients within ES index']
         'connected':['display all active connection within ES index']
         'shell':['starts session between the server and the client machine']
         'delete (ES ID)': ['remove specified document from index using ES ID']
         'delete all': ['deletes all documents from ES index']

    Client Commands                                                
        'quit':['quits the session and takes user back to Remote Sniffer interface']           
        'start sniffer' ['start remote sniffer']
        'stop sniffer': ['stops remote sniffer']  

```



## Disclaimer

This code is intended for educational and informational purposes only. Use it responsibly and ensure compliance with applicable laws and regulations. Respect the privacy and security of others.  
The author of this code assume no liability and is not responsible for misuses or damages caused by any code contained in this repository in any event that, accidentally or otherwise, it comes to be utilized by a threat agent or unauthorized entity as a means to compromise the security, privacy, confidentiality, integrity, and/or availability of systems and their associated resources. In this context the term "compromise" is henceforth understood as the leverage of exploitation of known or unknown vulnerabilities present in said systems, including, but not limited to, the implementation of security controls, human or electronically-enabled.

