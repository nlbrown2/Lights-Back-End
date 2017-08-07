from collections import deque
from lightShows import startShow

def acceptRequest(request):
    if type(request) != type('string'):
        print("BAD REQUEST: ", request)
        raise TypeError("Request was not a string!")
    else:
        #call chris's function here
        print("Recieved this request: ", request)

class RequestStack:
    def __init__(self):
        self.stack = deque()

    def add(self, request):
        if(type(request) != type('test')):
            print(type(request))
            raise TypeError("Bad Request: ", request)
        self.stack.append(request)

    def getNext(self):
        if(len(self.stack)):
            return self.stack.popleft()
        else:
            return ''

    def getIndex(self, show):
        try:
            return self.stack.index(show)
        except:
            return -1

    def currentLength(self):
        return len(self.stack)
