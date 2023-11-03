import time
import network
import ujson
from umqtt.simple import MQTTClient
from machine import Pin
from wifi import do_connect


MQTT_CLIENT = None
LED = None

topic = "sensor"
# 下面根据实际情况进行修改


# 打印订阅到的消息
def sub_cb(topic,msg):
    global MQTT_CLIENT
    print(topic,msg)


username = 'emqx'
password = 'public'


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
   
# The callback for when a PUBLISH message is received from the server.
def on_message(topic, msg):
    print("Received message:")
    print("Topic: {}".format(topic))
    print("Payload: {}".format(msg))


def main():
    
    global MQTT_CLIENT,LED
    # 1.链接WiFi
    do_connect()
    MQTT_CLIENT = MQTTClient("ESP32_1","101.43.132.163",1883,"admin","Lj112358",keepalive=60)
    
    print("connectted to mqtt_server !")
    MQTT_CLIENT.set_callback(on_message)  # 设置回调函数
    MQTT_CLIENT.connect()     # 建立连接
    MQTT_CLIENT.subscribe(topic)
    
    time.sleep(1)
    
    while True:
        MQTT_CLIENT.check_msg()
        time.sleep(1)
        # msg = "hello"
        # 发送自动配置MQTT服务的数据包
        # MQTT_CLIENT.publish("sensor", msg)
        
        # time.sleep(1)
    

if __name__ == "__main__":
    main()
                                                                                                                                               
       


