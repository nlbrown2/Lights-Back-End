from collections import deque
from time import sleep
import os
import json
import subprocess
#from startShow import startShow

def acceptRequest(request):
    #requests are dictionaries
    if type(request) != type({'key': 'value'}):
        print("BAD REQUEST: ", request)
        raise TypeError("Request was not a dict!")
    else:
        #call chris's function here
        print('nice --20 /home/pi/Chris_Code_Repo/Lights-Back-End/Chris_Code_Database/env/bin/python call_show.py ' + json.dumps(request))
        proc = subprocess.Popen(['nice', '--20', '/home/pi/Chris_Code_Repo/Lights-Back-End/Chris_Code_Database/env/bin/python', 'call_show.py', json.dumps(request)])
        return proc

class RequestStack:
    def __init__(self):
        self.stack = deque()
        self.show_names = deque()

    def print(self):
        response = ''
        for x in self.shows:
            response += x
        return response

    def add(self, request, request_name):
        print(type(request))
        print(type({'key': 'value'}))
        print("Add")
        if(type(request) != type({'key': 'value'})):
            print(type(request))
            print('Error in adding', request, 'as it is not a dict')
        self.stack.append(request)
        self.show_names.append(request_name)

    def getNextRequest(self):
        # print(self.stack)
        if(len(self.stack)):
            self.show_names.popleft()
            return self.stack.popleft()
        else:
            return ''

    def getIndex(self, show):
        try:
            for i, name in enumerate(self.show_names):
              if show == name:
                return i
            return -1
        except Exception as ex:
            print("Error getting index for " + show + " ", ex)
            return -1

    def currentLength(self):
        return len(self.stack)

    def print_all(self):
        for x in self.stack:
          print(x)
        for x in self.show_names:
          print(x)
