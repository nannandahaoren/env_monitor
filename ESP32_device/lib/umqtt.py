import time
import network
import ujson
from simple import MQTTClient  # 上面的步骤就是在下载umqtt.simple到ESP32设备
from machine import Pin


# 回调函数，用于打印订阅到的消息
def sub_cb(topic, msg):
    global MQTT_CLIENT
    print(topic, msg)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.


# The callback for when a PUBLISH message is received from the server.
def on_message(topic, msg):
    print("消息主题: {}".format(topic))
    print("消息内容: {}".format(msg))