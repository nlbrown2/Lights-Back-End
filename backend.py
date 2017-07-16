import paho.mqtt.client as mqtt , os, urllib.parse
import time

# Define event callbacks

def on_connect(client, userdata, obj, rc):
    print ("on_connect:: Connected with result code "+ str ( rc ) )
    print("rc: " + str(rc))
    print("" )

def on_message(mosq, obj, msg):
    print ("on_message:: this means  I got a message from brokerfor this topic")
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    print ("")

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))
    print ("")

def on_subscribe(mosq, obj, mid, granted_qos):
    print("This means broker has acknowledged my subscribe request")
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(  string)


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

# Continue the network loop, exit when an error occurs
#rc = 0
#while rc == 0:
#    rc = client.loop()
#print("rc: " + str(rc))

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
#client.loop_forever()

client.loop_start()

client.subscribe ("/request" ,2 )

run = True
while run:
    #client.publish ( "/toclientloud", "from python code")

    client.publish  ( "/status", "ON" )
    time.sleep(2)
    client.publish ( "/status", "OFF")
    time.sleep(2)

