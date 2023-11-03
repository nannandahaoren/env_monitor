import time
import network
import ujson
from umqtt.simple import MQTTClient
from machine import Pin

MQTT_CLIENT = None
LED = None
    # print(homeassistant_config_topic)   # 结果 homeassistant/sensor/HA/HA-ESP32-1/config
    # print(homeassistant_config_content) #
    # 结果
'''
        {'unique_id': 'HA-ESP32-1',
        'name': 'Temp',
        'icon': 'mdi:thermometer',
        'state_topic': 'HA-ESP32/1/state',
        'json_attributes_topic': 'HA-ESP32/1/attributes',
        'device': {
            'name': 'ESP32',
            'manufacturer': 'zhangzhongnan',
            'sw_version': '1.0',
            'identifiers': 'ESP32',
            'model': 'HA'}
        }


'''

control_esp32_led_topic = "HA-%s/%s/set" % ("ESP32","12")
# 下面根据实际情况进行修改

# 下面是固定格式，只需替换对应的数据即可
homeassistant_config_topic ="homeassistant/sensor/HA/HA-%s-%s/config" % ("ESP32","12")
homeassistant_config_content = {
    "unique_id":"HA-%s-%s" %("ESP32", "12"),
    "name":"Temp",
    "icon":"mdi:thermometer",
    "state_topic":"HA-%s/%s/state" % ("ESP32", "12"),
    "json_attributes_topic":"HA-%s/%s/attributes" % ("ESP32","12"),
    "conmmand_topic":control_esp32_led_topic, # homeassistant控制esp32的主题
    "device":{
        "identifiers": "ESP32",
        "manufacturer":"zhangzhongnan",
        "model":"HA",
        "name": "ESP32",
        "sw_version":"1.0"
    }
}

homeassistant_state_topic = "HA-%s/%s/state" % ("ESP32","12")   #结果： HA-ESP32/1/state
homeassistant_state_content = 23 # 这里是温度传感器的值，可以改为真正的数值(通过DS18B20采集)

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        # wlan.connect('yutian', 'lj112358')
        # wlan.connect('monster', 'lj112358')
        wlan.connect('津发科技_5G', 'kingfarwuxian')
        i = 1
        while not wlan.isconnected():
            print("正在链接...{}".format(i))
            i += 1
            time.sleep(1)
    print('network config:', wlan.ifconfig())



# 打印订阅到的消息
def sub_cb(topic,msg):
    global MQTT_CLIENT
    print(topic,msg)
    
    if topic == control_esp32_led_topic.encode():
        MQTT_CLIENT.publish(homeassistant_state_topic,msg)   # 发送LED状态给Homeassist
        send_led_state_to_ha(msg)
        
        
def send_led_state_to_ha(state):
    global MQTT_CLIENT
    if state == b"ON":
        MQTT_CLIENT.publish(homeassistant_state_topic,"ON")
        LED.value(1)
    else:
        MQTT_CLIENT.publish(homeassistant_state_topic,"OFF")
        LED.value(0)

def main():
    
    global MQTT_CLIENT,LED
    # 1.联网
    do_connect()
    MQTT_CLIENT = MQTTClient("ESP32","101.43.132.163",1883,"admin","Lj112358",keepalive=800)
    MQTT_CLIENT.set_callback(sub_cb)  # 设置回调函数
    MQTT_CLIENT.connect()     # 建立连接
    MQTT_CLIENT.subscribe(control_esp32_led_topic)
    time.sleep(1)
    
    # 发送自动配置MQTT服务的数据包
    send_content = ujson.dumps(homeassistant_config_content)
    MQTT_CLIENT.publish(homeassistant_config_topic, send_content)
    
    # 创建LED对象
    LED = Pin(2,Pin.OUT)
    LED.value(0)
    
    send_led_state_to_ha(b"OFF")
    
    
    
    for i in range(100):
        MQTT_CLIENT.check_msg()
        #         订阅/发送主题
        time.sleep(0.5)
        
        MQTT_CLIENT.publish(homeassistant_state_topic, "%d" % i )  
        print("ESP32...%d"  % i)
        time.sleep(1)
    
    print("hello")
        
if __name__ == "__main__":
    main()
                                                                                                                                               
       

