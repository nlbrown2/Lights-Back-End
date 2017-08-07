import paho.mqtt.client as mqtt , os, urllib.parse
import time
from stackCalls import RequestStack, acceptRequest
import json

# Define globals
# Shows should be a list of dictionaries with name, description, and queue keys
ShowNames = ['Hue Show', 'Snake', 'Tic Tak Toe']
ShowDescriptions = {
        'Hue Show': 'First, every LED is the same color and they slowly change through the hues. The options for this segement are wait 1 and speed 1. Wait 1 is how much time is spent before transitioning to the next color. speed 1 is how much time is spent for this whole portion of the show. Next, each LED will display the color spectrum in succession. The options for this segment are wait 2 and speed 2. Wait 2 is how much time (in seconds) is waited before the next LED is lit. Speed 2 is how how drastic the color difference between each LED is. The third segement is where each LED is lit after the other, but all the colors are random. The options for this segments are wait 3 and speed 3. Wait 3 determines how much time is spent between each pixel being lit and the speed 3 determines how much difference between each possible color is. Finall, the 4th segment is random colors and positions. The options for this are wait 4, which determines the time between pixel shifts and speed 4, which determines the variety of colors available.',
        'Snake': 'The computer plays the lovable game of snake',
        'Tic Tak Toe': 'The computer plays tic tak toe!'
        }
showString = ''
def getShowDescription(showName):
    try:
        return ShowDescriptions[showName]
    except:
        return 'no description'

Shows = []
for show in ShowNames:
    showDict = {
            'name': show,
            'description': getShowDescription(show),
            'position': -1
            }
    Shows.append(showDict)

def publishShows(mqtt):
    Shows = []
    for show in ShowNames:
        showDict = {
            'name': show,
            'description': getShowDescription(show),
            'position': stack.getIndex(show)
            }
        Shows.append(showDict)
    mqtt.publish( "/options", json.dumps(Shows))

def getShowIndex(show):
    try:
        return stack.getIndex(show)
    #try to get the index of the show from the stack. If not, return sentinel value of -1
    except:
        return -1

# Define event callbacks
def on_connect(client, userdata, obj, rc):
    print ("on_connect:: Connected with result code "+ str ( rc ) )

def on_message(mosq, obj, msg):
    print ("on_message:: this means  I got a message from broker for this topic")
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if(msg.topic == "/request"):
        try:
            stack.add(str(msg.payload, 'utf-8'))
        except ex as Exception:
            print("ERROR: could not add ", str(msg.payload), " to the stack", ex)
        finally:
            print(stack.currentLength())
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

run = True
stack = RequestStack()
while run:
    # client.publish( "/status", "ON" )
    time.sleep(2)
    # client.publish( "/status", "OFF")
    if(stack.currentLength()):
        # print(stack.currentLength())
        acceptRequest(stack.getNext())
    time.sleep(2)
