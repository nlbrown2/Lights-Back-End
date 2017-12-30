import paho.mqtt.client as mqtt
import urllib.parse
import os
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
ShowNames = ['Hue Show', 'Snake', 'Tic Tac Toe', 'Reversi', 'Clock', 'Text Scroller', 'Big Text Scroller']
LongShowDescriptions = {
        'Hue Show': 'This program has four parts that are customizable to run at different speeds. Part 1: simultaneous_hue_shift. All LEDs light at the same time to the same color. Color iterates through RGB spectrum. Part 2: serialized_hue_shift. Rather than all LEDs displaying the same color, each successive LED in the chain will display the next color in the spectrum. Each LED iterates through, making a rippling effect. Part 3: non_serialized_hue_shift. The LEDs change in successive order, so the colors still appear to move along the strand, but each successive color is random. Like the lights on the trim of a movie theater. Part 4: random_light_display. Each color and each placement of the color is random. Precursor to rave.py.',
        'Snake': 'This program plays the classic game of snake, but adds a few elements. The snake moves itself automatically around a grid. It looks for nom_noms which make it longer. There is a weighting system implemented to help the snake decide where to move based on the proximity of nom_noms. Though it can see nom_noms and navigate towards them, it cannot see bombs, which make it shorter. When a nom_nom or bomb is hit, the appropriate effect is applied and the item respawns somewhere else on the board. There are also caffeine pills which make the snake move faster, though this is only for visual effect. When a bomb, nom_nom, or caffeine pill is hit, the non-programmable lights will flash. If the snake gets caught in a loop, it will execute a random move to escape the loop. In text output, each node of the snake is numbered, with 1 being the head. 44 represents a bomb, 55 a caffeine pill, and 99 a nom_nom.',
        'Tic Tac Toe': 'This program will train itself in the classic game of tic tac toe. You can set the number of games that it will train with and how many it plays once it has finished training. You can also set the weights for a win or a loss that it uses for training. You can set how much time to wait between each game. We are hard at work with enabling choice of colors!',
        'Reversi': 'Ever heard of the classic game of Reversi/Othello? The game is played with two colors, where each player attempts to control larger portions of the board. The pieces capture enemies by trapping the opponents piece between two of their own. See the full rules and description at: https://en.wikipedia.org/wiki/Reversi Sorry, this is not a hyperlink. We are hard at work to make this a hyperlink.',
        'Clock': 'This program displays a 24 hour clock either in a vertical or horizontal configuration. The horizontal configuration has an optional countdown timer that will flash all the lights when the timer goes off. This program will run for a minute or until there is another show in the queue.',
        'Text Scroller': 'Scrolls an input string across the lights in a specified color for a specified number of times. Can handle up to 2 different strings.',
        'Big Text Scroller': 'Scroll one input string across all of the lights because it is big.'
        }
ShortShowDescriptions = {
        'Hue Show': 'A visually stunning performance that demonstrates the capabilities of the lights. This program runs four sub-programs that ripple colors across the lights with varying degrees of order.',
        'Snake': 'This program plays the classic game of snake, but adds a few elements. The snake moves itself automatically around a grid. It actively looks for nom_noms which make it longer. It can hit hidden landmines that decrease its length. Caffeine pills will make it move rapidly.',
        'Tic Tac Toe': 'The lights will play multiple games of tic tac toe against themselves war-games style!',
        'Reversi': 'The lights will play the classic game of Reversi/Othello against themselves!',
        'Clock': 'Displays a 24 hour clock on the lights.',
        'Text Scroller': 'Scrolls one or two input strings across the lights.',
        'Big Text Scroller': 'Scrolls one input string across all of the lights because it is big.'
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
                'description': 'Same as wait1 for the second segment.'
                },
            'speed2': {
                'type': 'Float',
                'default': 1.75,
                'lowerBound': 0,
                'upperBound': 5,
                'description': 'Same as speed1 for the second segment.'
                },
            'wait3': {
                'type': 'Integer',
                'default': 0,
                'lowerBound': 0,
                'upperBound': 5,
                'description': 'Same as wait1 for the third segment.'
                },
            'speed3': {
                'type': 'Float',
                'default': 1.75,
                'lowerBound': 0,
                'upperBound': 5,
                'description': 'Same as speed1 for the third segment.'
                },
            'wait4': {
                'type': 'Integer',
                'default': 0,
                'lowerBound': 0,
                'upperBound': 5,
                'description': 'Same as wait1 for the fourth segment.'
                },
            'speed4': {
                'type': 'Float',
                'default': 1.75,
                'lowerBound': 0,
                'upperBound': 5,
                'description': 'Same as speed1 for the fourth segment.'
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
                },
            'Tic Tac Toe': {
                    'Display_on_lights_boolen':{
                        'type': 'Boolean',
                        'default': True,
                        'lowerBound': False,
                        'upperBound': True,
                        'description': 'Determines if the lights will show the games played after training.'
                        },
                    'Display_on_lights_train_boolen':{
                        'type': 'Boolean',
                        'default': True,
                        'lowerBound': False,
                        'upperBound': True,
                        'description': 'Determines if the lights will show the games played during training.'
                        },
                    'input_number_of_trains':{
                        'type': 'Integer',
                        'default': 100,
                        'lowerBound': 0,
                        'upperBound': 500,
                        'description': 'Determines how many games will be played during the training phase.'
                        },
                    'input_number_of_games':{
                        'type': 'Integer',
                        'default': 10,
                        'lowerBound': 0,
                        'upperBound': 500,
                        'description': 'Determines how many games will be played after the training phase.'
                        },
                    'x_win_weighting':{
                        'type': 'Double',
                        'default': 1,
                        'lowerBound': 0,
                        'upperBound': 20,
                        'description': 'The amount that any move gets reinforced when X wins.'
                        },
                    'o_win_weighting':{
                        'type': 'Double',
                        'default': 1,
                        'lowerBound': 0,
                        'upperBound': 20,
                        'description': 'The amount that any move gets reinforced when O wins.'
                        },
                    'sleep_time':{
                        'type': 'Double',
                        'default': 0.2,
                        'lowerBound': 0,
                        'upperBound': 1,
                        'description': 'The amount of time taken between each real game.'
                        },
                    'sleep_time_train':{
                        'type': 'Double',
                        'default': 0,
                        'lowerBound': 0,
                        'upperBound': 1,
                        'description': 'The amount of time taken between each training game.'
                        },
                    'divisor':{
                        'type': 'Integer',
                        'default': 16,
                        'lowerBound': 1,
                        'upperBound': 64,
                        'description': 'The larger the value, the dimmer the lights will be.'
                        }
                    },
            'Clock': {
                    'orientation':{
                        'type': 'String',
                        'default': 'horizontal',
                        'restricted_value': True,
                        'allowed_values': {'horizontal': True, 'vertical': True},
                        'description': 'The orientation of the board for the clock! Horizontal has a timer :) .'
                        },
                    'timer_value':{
                        'type': 'Double',
                        'default': 0,
                        'lowerBound': 0,
                        'upperBound': 99,
                        'description': 'This feature is only available for the horizontal orientation. This will count down to 0 and then flash the lights.'
                        },
                    'timer_unit':{
                        'type': 'String',
                        'default': 'minutes',
                        'restricted_value': True,
                        'allowed_values': {'seconds': True, 'minutes': True, 'hours': True},
                        'description': 'This determines how long it takes to count down one unit from the timer. Must be either "seconds", "minutes", or "hours".'
                        },
                    'divisor':{
                        'type': 'Integer',
                        'default': 16,
                        'lowerBound': 1,
                        'upperBound': 64,
                        'description': 'The larger the value, the dimmer the lights will be.'
                        }
                    },
            'Text Scroller': {
                    'input_string_top':{
                        'type': 'String',
                        'default': 'Go Blue!',
                        'restricted_value': False,
                        'description': 'This string will be scrolled across the top of the lights.'
                        },
                    'input_string_bottom':{
                        'type': 'String',
                        'default': 'Hail!',
                        'restricted_value': False,
                        'description': 'This string will be scrolled across the bottom of the lights.'
                        },
                    'rainbow_bool':{
                        'type': 'Boolean',
                        'default': False,
                        'lowerBound': False,
                        'upperBound': True,
                        'description': 'This determines if each letter is a different color for both strings.'
                        },
                    'text_color_top':{
                        'type': 'String',
                        'default': 'Blue',
                        'restricted_value': True,
                        'allowed_values': {'Blue': True, 'Red': True, 'Yellow': True, 'Green': True, 'Purple': True},
                        'description': 'Must be one of: "Blue", "Red", "Yellow", "Green", "Purple". Determines what color the text will be across the top given rainbow_bool is false.'
                        },
                    'text_color_bottom':{
                        'type': 'String',
                        'default': 'Blue',
                        'restricted_value': True,
                        'allowed_values': {'Blue': True, 'Red': True, 'Yellow': True, 'Green': True, 'Purple': True},
                        'description': 'Must be one of: "Blue", "Red", "Yellow", "Green", "Purple". Determines what color the text will be across the bottom given rainbow_bool is false.'
                        },
                    'loop_count':{
                        'type': 'Integer',
                        'default': 1,
                        'lowerBound': -1,
                        'upperBound': 100,
                        'description': 'Determines how many times the input strings will loop around.'
                        },
                    'divisor':{
                        'type': 'Integer',
                        'default': 64,
                        'lowerBound': 1,
                        'upperBound': 64,
                        'description': 'The larger the value, the dimmer the lights will be.'
                        }
                    },
            'Big Text Scroller':{
                    'input_string':{
                        'type': 'String',
                        'default': 'Go Blue!',
                        'restricted_value': False,
                        'description': 'This string will be scrolled across all of the lights.'
                        },
                    'rainbow_bool':{
                        'type': 'Boolean',
                        'default': False,
                        'lowerBound': False,
                        'upperBound': True,
                        'description': 'This determines if each letter is a different color for both strings.'
                        },
                    'text_color':{
                        'type': 'String',
                        'default': 'Blue',
                        'restricted_value': True,
                        'allowed_values': {'Blue': True, 'Red': True, 'Yellow': True, 'Green': True, 'Purple': True},
                        'description': 'Must be one of: "Blue", "Red", "Yellow", "Green", "Purple". Determines what color the text will be given rainbow_bool is false.'
                        },
                    'loop_count':{
                        'type': 'Integer',
                        'default': 1,
                        'lowerBound': -1,
                        'upperBound': 100,
                        'description': 'Determines how many times the input strings will loop around.'
                        },
                    'divisor':{
                        'type': 'Integer',
                        'default': 8,
                        'lowerBound': 1,
                        'upperBound': 64,
                        'description': 'The larger the value, the dimmer the lights will be.'
                        }
                    },
            'Reversi':{
                    'train':{
                        'type': 'Boolean',
                        'default': False,
                        'lowerBound': False,
                        'upperBound': True,
                        'description': 'This determines if the lights will train before playing.'
                        },
                    'train_iterations':{
                        'type': 'Integer',
                        'default': 1,
                        'lowerBound': 0,
                        'upperBound': 10,
                        'description': 'Determines how many games the lights will use to train given that train is set to True.'
                        },
                    'number_of_games':{
                        'type': 'Integer',
                        'default': 3,
                        'lowerBound': 0,
                        'upperBound': 10,
                        'description': 'This determines how many games will be played after training.'
                        },
                    'number_of_games':{
                        'type': 'Integer',
                        'default': 3,
                        'lowerBound': 0,
                        'upperBound': 10,
                        'description': 'This determines how many games will be played after training.'
                        },
                    'sleep_time':{
                        'type': 'Double',
                        'default': 0.5,
                        'lowerBound': 0,
                        'upperBound': 5,
                        'description': 'This determines how many seconds are between each move.'
                        },
                    'white_input_no':{
                        'type': 'String',
                        'default': 'computer_random',
                        'restricted_value': True,
                        'allowed_values': {'computer_weight_capture': True, 'computer_random': True},
                        'description': 'Determines if the computer makes random moves or a strategy. must be one of: "computer_weight_capture", "computer_random".'
                        },
                    'black_input_no':{
                        'type': 'String',
                        'default': 'computer_random',
                        'restricted_value': True,
                        'allowed_values': {'computer_weight_capture': True, 'computer_random': True},
                        'description': 'Determines if the computer makes random moves or a strategy. must be one of: "computer_weight_capture", "computer_random".'
                        },
                    'R_value_black':{
                        'type': 'Integer',
                        'default': 255,
                        'lowerBound': 0,
                        'upperBound': 255,
                        'description': 'Sets the red color value for player black.'
                        },
                    'G_value_black':{
                        'type': 'Integer',
                        'default': 0,
                        'Integer': 0,
                        'lowerBound': 0,
                        'upperBound': 255,
                        'description': 'Sets the green value for player black.'
                        },
                    'B_value_black':{
                        'type': 'Integer',
                        'default': 0,
                        'lowerBound': 0,
                        'upperBound': 255,
                        'description': 'Sets the blue value for player black.'
                        },
                    'R_value_white':{
                        'type': 'Integer',
                        'default': 0,
                        'lowerBound': 0,
                        'upperBound': 255,
                        'description': 'Sets the red value for player white.'
                        },
                    'G_value_white':{
                        'type': 'Integer',
                        'default': 255,
                        'lowerBound': 0,
                        'upperBound': 255,
                        'description': 'Sets the green value for player white.'
                        },
                    'B_value_white':{
                        'type': 'Integer',
                        'default': 0,
                        'lowerBound': 0,
                        'upperBound': 255,
                        'description': 'Sets the blue value for player white.'
                        },
                    'divisor':{
                        'type': 'Integer',
                        'default': 16,
                        'lowerBound': 1,
                        'upperBound': 64,
                        'description': 'The larger the value, the dimmer the lights will be.'
                        }
                    }
        }
whitelisted_emails = { 'nlbrow@umich.edu', 'cknebel@umich.edu' }

def valid_option(user_input, option_info_dict, user_options, show_name):
    # print(user_input, option_info_dict)
    # print(type(user_options))
    # print("Type of user_options \n \n")
    correct_type = option_info_dict['type']
    # print(correct_type)
    if correct_type == 'Float':
        # print("in Float")
        try:
            user_input = float(user_input)
            return withinBounds(user_input, option_info_dict, user_options, show_name)
        except Exception as e:
            print(e)
            return False
    if correct_type == 'Integer':
        # print("in Integer")
        try:
            user_input = int(user_input)
            return withinBounds(user_input, option_info_dict, user_options, show_name)
        except Exception as e:
            print(e)
            return False
    if correct_type == 'Boolean':
        # print('Boolean', user_input, type(user_input))
        if type(user_input) == type(True):
            return True
        if user_input != 'True' and user_input != 'False':
            return False
        else:
            return True
    if correct_type == 'List of Floats':
        # print("List of float checking")
        try:
            if(not(isinstance(user_input, list))):
                return False
            else:
                try:
                    for item in user_input:
                        item = float(item)
                        if not(withinBounds(item, option_info_dict, user_options, show_name)):
                            return False
                    return True
                except Exception as e:
                    return False
            return True
        except Exception as e:
            print(e)
            return False
    if correct_type == 'String':
        # print("In the String type")
        try:
            if option_info_dict['restricted_value']:
                if user_input in option_info_dict['allowed_values']:
                    return True
                else:
                    # print("\n \n \nReturning FALSE \n \n \n \n")
                    return False
            else:
                return True
        except Exception as e:
            print(e, 'exception')
            return False
    else:
        return False

def withinBounds(userVal, option_info_dict, user_options, show_name):
    try:
        if type(option_info_dict['upperBound']) == type(''):
            # print('position 1')
            #This means the upper bound is another option
            if option_info_dict['upperBound'] in user_options:
                # print('position 2')
                other_option = user_options[option_info_dict['upperBound']]
                # print('position 3')
            else:
                # print('position 4')
                # print(option_info_dict)
                other_option = ShowOptions[show_name][option_info_dict['upperBound']]['default']
                # print(other_option)
                # print('position 5')
            if userVal > other_option:
                # print('position 6')
                return False
        else:
            if userVal > option_info_dict['upperBound']:
                # print('position 7')
                return False
        if type(option_info_dict['lowerBound']) == type(''):
            #lower bound is another option
            # print('position 1')
            if option_info_dict['lowerBound'] in user_options:
                # print('position 2')
                other_option = user_options[option_info_dict['lowerBound']]
                # print('position 4')
            else:
                # print('position 3')
                other_option = ShowOptions[show_name][[option_info_dict['lowerBound']]]
            if userVal < other_option:
                # print('position 5')
                return False
        else:
            # print('position 6')
            if userVal < option_info_dict['lowerBound']:
                # print('position 7')
                return False
        # print('within bounds')
        return True
    except Exception as e:
        print('error checking bounds', e)


def validOptions(show_dict):
    valid_option_dict = ShowOptions[show_dict['name']]
    user_options = show_dict['options']
    for option in user_options:
        # print(option, type(option))
        if option in valid_option_dict:
            # print('found option', option)
            # print(valid_option_dict[option])
            if not(valid_option(user_options[option], valid_option_dict[option], user_options, show_dict['name'])):
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

Shows = []
for show in ShowNames:
    showDict = {
        'name': show,
        'short_description': getShortShowDescription(show),
        'long_description': getLongShowDescription(show),
        'options': getShowOptions(show)
        }
    Shows.append(showDict)
ShowsJSON = json.dumps(Shows)
#print(ShowsJSON)
def publishShows(mqtt):
    #print("Publish shows")
    #print(type(ShowsJSON))
    # stack.print_all()
    for showDict in Shows:
        # print(stack.getIndex(showDict['name']))
        showDict['position'] = stack.getIndex(showDict['name'])
        # showDict.update({'position', stack.getIndex(showDict['name'])})
    ShowsJSON = json.dumps(Shows)
    mqtt.publish( "/options", ShowsJSON)

def getShowIndex(show):
    try:
        return stack.getIndex(show)
    #try to get the index of the show from the stack. If not, return sentinel value of -1
    except:
        return -1

def always_allowed_email(email):
    if type(email) != type('test'):
        return False
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        #Invalid email!
        return False
    if email not in whitelisted_emails:
        print("not a whitelist email")
        return False
    else:
        # print("returning true")
        return True

# Define event callbacks
# def on_connect(client, userdata, obj, rc):
#     x = 5
    # print ("on_connect:: Connected with result code "+ str ( rc ) )

def quiet_hours():
	time = datetime.datetime.now().time()
	# print(time.hour > 23 or time.hour < 9)
	return time.hour < 9 or time.hour > 23;

def on_message(mosq, obj, msg):
    # print ("on_message:: this means  I got a message from broker for this topic")
    # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if(msg.topic == "/request"):
        #print("got a request")
        try:
            request_string = str(msg.payload, 'utf-8')
            # print(request_string)
            request_dict = json.loads(str(request_string).strip("'<>() ").replace('\'', '\"'))
            auth_token = request_dict['user_token']
            decoded_token = auth.verify_id_token(auth_token)
            # After decoding the token, check the time and person.
            # print('\n \n', decoded_token['email'])
            # print(always_allowed_email(decoded_token['email']))

            if decoded_token['email'] and (always_allowed_email(decoded_token['email']) or not quiet_hours()):
                #if there is an email in the otken and it is not always allowed, check the time.
                # print("\n \n \n")
                # print(decoded_token, 'decoded user token')
                # print(request_dict, 'request dictionary')
                # print('options' in request_dict)
                if 'options' in request_dict:
                    for option in request_dict['options']:
                        #if the option is not no options and the type of the option is not a string, parse the JSON
                        show_name = request_dict['name']
                        if(option != 'no options' and ShowOptions[show_name][option]['type'] != 'String'):
                            try:
                                request_dict['options'][option] = json.loads(request_dict['options'][option])
                            except Exception as ex:
                                print('error reading JSON from', request_dict['options'][option], ex)
                request_name = request_dict['name']
                if 'options' in request_dict:
                    if validOptions(request_dict):
                        stack.add(request_string, request_name)
                        # print('valid options')
                        # print(request_dict, type(request_dict['options']))
                else:
                    # print('no options')
                    stack.add(request_string, request_name)
            publishShows(mosq)
        except Exception as ex:
            print("ERROR: could not add ", str(msg.payload), " to the stack", ex)
    if(msg.topic == "/get"):
        #print(str(msg.payload, 'utf-8') == 'show list')
        if(str(msg.payload, 'utf-8') == "show list"):
            #print("Publishing show")
            publishShows(mosq)

# def on_publish(mosq, obj, mid):
#     x = 5
    # print ("published")

#def on_subscribe(mosq, obj, mid, granted_qos):
#    x = 5
    # print("Subscribed: " + str(mid) + " " + str(granted_qos))

#def on_log(mosq, obj, level, string):
#    x = 5
    # print(string)


client = mqtt.Client(clean_session=True)
# Assign event callbacks
client.on_message = on_message
#client.on_connect = on_connect
# client.on_publish = on_publish
#client.on_subscribe = on_subscribe

# Uncomment to enable debug messages
#client.on_log = on_log


# user name has to be called before connect
client.username_pw_set("Rpi", "cRxSyAsZwUd8")
# Uncomment in PROD
# client.tls_set('/etc/ssl/certs/ca-certificates.crt')
client.connect('m12.cloudmqtt.com', 10048)
client.loop_start()
#This puts the client's publish and subscribe into a different thread, so any blocking work done here won't matter

client.subscribe("/request", 2)
client.subscribe("/get", 2)
run = True
stack = RequestStack()
while run:
    time.sleep(2)
    # print(stack.currentLength())
    if(stack.currentLength()):
        try:
            request_dict = stack.getNextRequest()
            publishShows(client)
            acceptRequest(request_dict)
        except:
            print("Error in decoding request", e)
    time.sleep(2)
