import paho.mqtt.client as mqtt , os, urllib.parse
import time
from stackCalls import RequestStack, acceptRequest

# Define event callbacks

def on_connect(client, userdata, obj, rc):
    print ("on_connect:: Connected with result code "+ str ( rc ) )

def on_message(mosq, obj, msg):
    print ("on_message:: this means  I got a message from broker for this topic")
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if(msg.topic == "/request"):
        try:
            stack.add(str(msg.payload))
        except ex as Exception:
            print("ERROR: could not add ", str(msg.payload), " to the stack", ex)
        finally:
            print(stack.currentLength())

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
