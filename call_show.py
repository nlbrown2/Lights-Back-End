# from startShow import startShow
import json
import sys

#this assumes that argv[1] has the json of the show options
if len(sys.argv) >= 2:
  request_string = sys.argv[1]
  # print(request_string)
  request_dict = json.loads(request_string)
  # print(request_dict)
  startShow(request_dict)
else:
  print(len(sys.argv))

