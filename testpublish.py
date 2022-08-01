import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, message):
    if str(message.payload.decode("utf-8")) == "JUMP":
        print("jump")
        return True

mqttBroker ="test.mosquitto.org"

client = mqtt.Client("Smartphone")

client.connect(mqttBroker, 1883) 
print("connected")

client.loop_start()

client.subscribe("yo")
client.on_message=on_message 

time.sleep(60)
client.loop_stop()