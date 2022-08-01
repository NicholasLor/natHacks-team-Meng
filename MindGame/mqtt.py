
import paho.mqtt.client as paho
import time

def on_connect(client, userdata, flags, rc):
    print("CONNACK received with code %d." % (rc))

client = paho.Client()
client.on_connect = on_connect
# client.connect("broker.mqttdashboard.com", 1883)
#client.connect("https://test.mosquitto.org/", 8883)

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))
 
client = paho.Client()
client.on_publish = on_publish
client.connect("test.mosquitto.org", 1883)
client.loop_start()

while True:
    temperature = "hello"
    # (rc, mid) = client.publish("encyclopedia/temperature", str(temperature), qos=1)
    client.publish("yo", "JUMP")
    time.sleep(1)

