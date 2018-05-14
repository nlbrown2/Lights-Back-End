from startShow import startShow
import json
import sys

#this assumes that argv[1] has the json of the show options
if len(sys.argv) >= 2:
  request_string = sys.argv[1]
  print(request_string)
  request_dict = json.loads(request_string)
  print(type(request_dict))
  print(request_dict)
  try:
    print("Type of options: ")
    for key in request_dict['options'].keys():
      request_dict[key] = request_dict['options'][key]
      print(type(request_dict[key]))
  except Exception as e:
    print("no options")
  startShow(request_dict)
else:
  print(len(sys.argv))

