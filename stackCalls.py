from collections import deque
from time import sleep
import os
import json
#from startShow import startShow

def acceptRequest(request):
    #requests are JSON dictionaries
    if type(request) != type(''):
        print("BAD REQUEST: ", request)
        raise TypeError("Request was not a dict!")
    else:
        #call chris's function here
        # print("Recieved this request: ", request)
        # startShow(request)
        # fout = open('test_dict.txt', 'w')
        # fout.write(request)
        # sleep(1)
	#Try something from os to spawn a new process with a much lower nice value and see how that goes
        print('nice --20 /home/pi/Chris_Code_Repo/Lights-Back-End/Chris_Code_Database/env/bin/python call_show.py ' + json.dumps(request))
        # os.system('sudo nice --20 /home/pi/Chris_Code_Repo/Lights-Back-End/Chris_Code_Database/env/bin/python call_show.py ' + json.dumps(request))
	#Want to use subprocess.Popen so I can grab the PID from it and determine if it is still running or not
	#p = subprocess.Poen(*whatever args are needed*)
	#p.poll() should determine if it is still open or not
        # not sure if this will give us anything, but can look into it in the future

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
        if(type(request) != type('')):
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
