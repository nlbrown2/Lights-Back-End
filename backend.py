import paho.mqtt.client as mqtt , os, urllib.parse
import time
import datetime
import re
from stackCalls import RequestStack, acceptRequest
import json
import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate('./server.json')
firebase_admin.initialize_app(cred)

# Define globals
# Shows should be a list of dictionaries with name, description, and queue keys
ShowNames = ['Hue Show', 'Snake', 'Tic Tak Toe']
LongShowDescriptions = {
        'Hue Show': 'This program has four parts that are customizable to run at different speeds. Part 1: simultaneous_hue_shift. All LEDs light at the same time to the same color. Color iterates through RGB spectrum. Part 2: serialized_hue_shift. Rather than all LEDs displaying the same color, each successive LED in the chain will display the next color in the spectrum. Each LED iterates through, making a rippling effect. Part 3: non_serialized_hue_shift. The LEDs change in successive order, so the colors still appear to move along the strand, but each successive color is random. Like the lights on the trim of a movie theater. Part 4: random_light_display. Each color and each placement of the color is random. Precursor to rave.py.',
        'Snake': 'This program plays the classic game of snake, but adds a few elements. The snake moves itself automatically around a grid. It looks for nom_noms which make it longer. There is a weighting system implemented to help the snake decide where to move based on the proximity of nom_noms. Though it can see nom_noms and navigate towards them, it cannot see bombs, which make it shorter. When a nom_nom or bomb is hit, the appropriate effect is applied and the item respawns somewhere else on the board. There are also caffeine pills which make the snake move faster, though this is only for visual effect. When a bomb, nom_nom, or caffeine pill is hit, the non-programmable lights will flash. If the snake gets caught in a loop, it will execute a random move to escape the loop. In text output, each node of the snake is numbered, with 1 being the head. 44 represents a bomb, 55 a caffeine pill, and 99 a nom_nom.',
        'Tic Tak Toe': 'Long description for Tic Tak Toe'
        }
ShortShowDescriptions = {
        'Hue Show': 'A visually stunning performance that demonstrates the capabilities of the lights. This program runs four sub-programs that ripple colors across the lights with varying degrees of order.',
        'Snake': 'This program plays the classic game of snake, but adds a few elements. The snake moves itself automatically around a grid. It actively looks for nom_noms which make it longer. It can hit hidden landmines that decrease its length. Caffeine pills will make it move rapidly.',
        'Tic Tak Toe': 'Short descriptions for Tic Tak Toe.'
        }

ShowOptions = {
        'Hue Show': {
            'wait1': {
                'type': 'Float',
                'default': 0,
                'lowerBound': 0,
                'upperBound': 5,
                'description': 'This is the time in seconds between each change of color for the first segment. In reality, 0 is not actually 0 seconds.'
                },
            'speed1': {
                'type': 'Float',
                'default': 1.75,
                'lowerBound': 0,
                'upperBound': 5,
                'description': 'Determines how gradual the change is between each color for the first segment. 2 means you see every color, 3 means you see every third color, etc.'
                },
            'wait2': {
                'type': 'Integer',
                'default': 0,
                'lowerBound': 0,
                'upperBound': 5,
                'description': 'Same as wait1 for the second segment'
                },
            'speed2': {
                'type': 'Float',
                'default': 1.75,
                'lowerBound': 0,
                'upperBound': 5,
                'description': 'Same as speed1 for the second segment'
                },
            'wait3': {
                'type': 'Integer',
                'default': 0,
                'lowerBound': 0,
                'upperBound': 5,
                'description': 'Same as wait1 for the third segment'
                },
            'speed3': {
                'type': 'Float',
                'default': 1.75,
                'lowerBound': 0,
                'upperBound': 5,
                'description': 'Same as speed1 for the third segment'
                },
            'wait4': {
                'type': 'Integer',
                'default': 0,
                'lowerBound': 0,
                'upperBound': 5,
                'description': 'Same as wait1 for the fourth segment'
                },
            'speed4': {
                'type': 'Float',
                'default': 1.75,
                'lowerBound': 0,
                'upperBound': 5,
                'description': 'Same as speed1 for the fourth segment'
                },
            },
        'Snake': {
                'Sleep_tme': {
                    'type': 'Float',
                    'default': 0.5,
                    'lowerBound': 0,
                    'upperBound': 2,
                    'description': 'The amount of time between each movement of the snake. Lower number equals faster snake.'
                    },
                'Wait_times': {
                    'type': 'List of Floats',
                    'default': '[0.05, 0.05, 0.05, 0.05, 0.05, 0.1, 0.15, 0.2, 0.2]',
                    'lowerBound': 0,
                    'upperBound': 'Sleep_tme',
                    'description': 'The sleep times for the moves following the snake hitting a caffeine pill. The default make the moves very fast for five moves then slows down over the next four.'
                    },
                'Number_of_nom_noms': {
                    'type': 'Integer',
                    'default': 2,
                    'lowerBound': 1,
                    'upperBound': 10,
                    'description': 'The number of nom_noms on the board at any given time. In practice, lower numbers are better to avoid quick games.'
                    },
                'Number_of_caffeine_pills': {
                    'type': 'Integer',
                    'lowerBound': 0,
                    'upperBound': 10,
                    'default': 5,
                    'description': 'The number of caffeine pills on the board at any given time.'
                    },
                'Level_0_nom_nom': {
                    'type': 'Integer',
                    'lowerBound': 3,
                    'upperBound': 20,
                    'default': 10,
                    'description': 'The weighting placed on a level_o_nom_nom, which is classified as a nom_nom that is adjacent to the head of the snake. Higher values make the snake more likely to turn towards the nom_nom.'
                    },
                'Level_1_nom_nom': {
                    'type': 'Integer',
                    'lowerBound': 2,
                    'upperBound': 'Level_0_nom_nom',
                    'default': 7,
                    'description': 'Same as Level_0_nom_nom but applies to nom_noms that are exactly 2 moves away from the head.'
                    },
                'Level_2_nom_nom': {
                    'type': 'Integer',
                    'lowerBound': 1,
                    'upperBound': 'Level_1_nom_nom',
                    'default': 4,
                    'description': 'Same as Level_0_nom_nom but applies to nom_noms that are exactly 3 moves away from the head.'
                    },
                'Display_on_lights_boolean':{
                    'type': 'Boolean',
                    'default': True,
                    'lowerBound': False,
                    'upperBound': True,
                    'description': 'Determines whether the program is displayed on the lights. If false, only text output is displayed on the screen.'
                    }
                }
        }
whitelisted_emails = { 'nlbrow@umich.edu', 'cknebel@umich.edu' }

def valid_option(user_input, option_info_dict, user_options):
    print(user_input, option_info_dict)
    print(type(user_input))
    correct_type = option_info_dict['type']
    if correct_type == 'Float':
        try:
            user_input = float(user_input)
            return user_input > option_info_dict['lowerBound'] and user_input < option_info_dict['upperBound']
        except Exception as e:
            print(e)
            return False
    if correct_type == 'Integer':
        try:
            user_input = int(user_input)
            return withinBounds(user_input, option_info_dict, user_options)
        except Exception as e:
            print(e)
            return False
    if correct_type == 'Boolean':
        print('Boolean', user_input, type(user_input))
        if type(user_input) == type(True):
            return True
        if user_input != 'True' and user_input != 'False':
            return False
        else:
            return True
    if correct_type == 'List of Floats':
        try:
            if(not(isinstance(user_input, list))):
                return False
            else:
                try:
                    for item in user_input:
                        item = float(item)
                except Exception as e:
                    return False
            return True
        except Exception as e:
            print(e)
            return False
    else:
        return False

def withinBounds(userVal, option_info_dict, user_options):
    try:
        if type(option_info_dict['upperBound']) == type(''):
            #This means the upper bound is another option
            if option_info_dict['upperBound'] in user_options:
                other_option = user_options[option_info_dict['upperBound']]
            else:
                other_option = option_info_dict[option_info_dict['upperBound']]
            if userVal > other_option:
                return False
        else:
            if userVal > option_info_dict['upperBound']:
                return False
        if type(option_info_dict['lowerBound']) == type(''):
            #lower bound is another option
            if option_info_dict['lowerBound'] in user_options:
                other_option = user_options[option_info_dict['lowerBound']]
            else:
                other_option = option_info_dict[option_info_dict['lowerBound']]
            if userVal < other_option:
                return False
        else:
            if userVal < option_info_dict['lowerBound']:
                return False
        print('within bounds')
        return True
    except Exception as e:
        print('error checking bounds', e)


def validOptions(show_dict):
    valid_option_dict = ShowOptions[show_dict['name']]
    user_options = show_dict['options']
    for option in user_options:
        print(option, type(option))
        if option in valid_option_dict:
            print('found option', option)
            print(valid_option_dict[option])
            if not(valid_option(user_options[option], valid_option_dict[option], user_options)):
                print('invalid option', option)
                return False
        else:
            print('not an option', option)
            return False
    return True

def getShowOptions(showName):
    try:
        return ShowOptions[showName]
    except:
        return 'no options'

def getShortShowDescription(showName):
    try:
        return ShortShowDescriptions[showName]
    except:
        return 'no description'

def getLongShowDescription(showName):
    try:
        return LongShowDescriptions[showName]
    except:
        return 'no description'

def publishShows(mqtt):
    Shows = []
    for show in ShowNames:
        showDict = {
            'name': show,
            'short_description': getShortShowDescription(show),
            'long_description': getLongShowDescription(show),
            'position': stack.getIndex(show),
            'options': getShowOptions(show)
            }
        Shows.append(showDict)
    mqtt.publish( "/options", json.dumps(Shows))

def getShowIndex(show):
    try:
        return stack.getIndex(show)
    #try to get the index of the show from the stack. If not, return sentinel value of -1
    except:
        return -1

def always_allowed_email(email):
    if type(email) != type('test'):
        return False
    if not re.match(r"[^@]+@[^@]+\.[^@]+"):
        #Invalid email!
        return False
    if email not in whitelisted_emails:
        return False
    else:
        return True

# Define event callbacks
def on_connect(client, userdata, obj, rc):
    print ("on_connect:: Connected with result code "+ str ( rc ) )

def on_message(mosq, obj, msg):
    print ("on_message:: this means  I got a message from broker for this topic")
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if(msg.topic == "/request"):
        try:
            request_string = str(msg.payload, 'utf-8')
            print(request_string)
            request_dict = json.loads(str(request_string).strip("'<>() ").replace('\'', '\"'))
            auth_token = request_dict['user_token']
            decoded_token = auth.verify_id_token(auth_token)
            # After decoding the token, check the time and person.
            print('\n \n', decoded_token['email'])
            if decoded_token['email'] and not always_allowed_email(decoded_token['email']):
                #if there is an email in the otken and it is not always allowed, check the time.
                time = datetime.datime.now().time()
                if time.hour < 9 or time.hour > 23:
                    #do nothing
                    print("Too Early")
                    return
                else:
                    print(decoded_token, 'decoded user token')
                    print(request_dict, 'request dictionary')
                    print('options' in request_dict)
                    if 'options' in request_dict:
                        for option in request_dict['options']:
                            if(option != 'no options'):
                                try:
                                    request_dict['options'][option] = json.loads(request_dict['options'][option])
                                except Exception as ex:
                                    print('error reading JSON from', request_dict['options'][option], ex)
                    request_name = request_dict['name']
                    if 'options' in request_dict:
                        if validOptions(request_dict):
                            # stack.add(request_dict, request_name)
                            print('valid options')
                            print(request_dict, type(request_dict['options']))
                    else:
                        print('no options')
                        # stack.add(request_dict, request_name)
        except Exception as ex:
            print("ERROR: could not add ", str(msg.payload), " to the stack", ex)
        finally:
            print(request_dict)
    if(msg.topic == "/get"):
        if(str(msg.payload == "show list")):
            publishShows(mosq)

def on_publish(mosq, obj, mid):
    print ("published")

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)


client = mqtt.Client(clean_session=True)
# Assign event callbacks
client.on_message = on_message
client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe

# Uncomment to enable debug messages
client.on_log = on_log


# user name has to be called before connect
client.username_pw_set("Rpi", "cRxSyAsZwUd8")
# Uncomment in PROD
# client.tls_set('/etc/ssl/certs/ca-certificates.crt')

client.connect('m12.cloudmqtt.com', 10048, 60)
client.loop_start()
#This puts the client's publish and subscribe into a different thread, so any blocking work done here won't matter

client.subscribe("/request", 2)
client.subscribe("/get", 2)
run = True
stack = RequestStack()
while run:
    # client.publish( "/status", "ON" )
    time.sleep(2)
    # client.publish( "/status", "OFF")
    # if(stack.currentLength()):
        # try:
            # request_dict = json.loads(stack.getNext())
            # acceptRequest(json.loads(stack.getNext()))
        # except:
            # print("Error in decoding request")
    time.sleep(2)
