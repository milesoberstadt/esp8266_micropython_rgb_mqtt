import machine
import network
import time
import ubinascii
import webrepl

from umqtt.simple import MQTTClient

# GPIO pin numbers for LED
RED = 14
GREEN = 12
BLUE = 13

CONFIG = {}
client = None

current_red = 1023
current_green = 1023
current_blue = 1023
current_brightness = 1.0
current_state = 0 # On / off

def initPins():
    print('pins initializing')
    global redPWM, greenPWM, bluePWM
    # Red
    redPIN = machine.Pin(RED)
    redPWM = machine.PWM(redPIN)
    redPWM.freq(1000)
    redPWM.duty(0)

    # Green
    greenPIN = machine.Pin(GREEN)
    greenPWM = machine.PWM(greenPIN)
    greenPWM.freq(1000)
    greenPWM.duty(0)

    # Blue
    bluePIN = machine.Pin(BLUE)
    bluePWM = machine.PWM(bluePIN)
    bluePWM.freq(1000)
    bluePWM.duty(0)

def updatePins():
    global redPWM, greenPWM, bluePWM, client, current_red, current_green, current_blue
    #print((current_red, current_brightness, current_state))
    redPWM.duty(int(current_red*current_brightness*current_state))
    greenPWM.duty(int(current_green*current_brightness*current_state))
    bluePWM.duty(int(current_blue*current_brightness*current_state))
    client.publish(CONFIG['state_topic'], b"ON" if current_state is 1 else b"OFF")
    client.publish(CONFIG['brightness_state_topic'], bytes([int(current_brightness*255)]))

def loadConfig():
    print('loading config')
    import ujson as json
    try:
        with open("/config.json") as f:
            config = json.loads(f.read())
    except (OSError, ValueError):
        print("Couldn't load /config.json")
    else:
        CONFIG.update(config)

def mqtt_sub_callback(topic, msg):
    global current_state, current_brightness, current_red, current_green, current_blue
    print((topic, msg))
    s_topic = topic.decode("utf-8")
    s_msg = msg.decode("utf-8")
    print((s_topic, s_msg))
    # Depending on our topic, respond accordingly
    if (s_topic == CONFIG['command_topic']):
        # ON or OFF
        if (s_msg == 'ON'):
            current_state = 1
        else:
            current_state = 0
    elif (s_topic == CONFIG['brightness_command_topic']):
        # 0 - 255
        current_brightness = int(s_msg) / 255
    elif (s_topic == CONFIG['rgb_command_topic']):
        # 0 - 255, 3x, separated by commas, ex 255,255,0
        #print(([int(m*(1023/255)) for m in s_msg.split(',')]))
        messages = s_msg.split(',') #[int(m*(1023/255)) for m in s_msg.split(',')]
        for m in messages:
            print((m))
            print((int(int(m)*(1023/255))))
        current_red = int(int(messages[0])*(1023/255))
        current_green = int(int(messages[1])*(1023/255))
        current_blue = int(int(messages[2])*(1023/255))
        #current_red, current_green, current_blue = [int(m*(1023/255)) for m in s_msg.split(',')]
        #print((current_red, current_green, current_blue))
    updatePins()

def main():
    print('main called')
    # Wait up to 30s for connection
    start_ticks = time.ticks_ms()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        while not wlan.isconnected() and (time.ticks_ms() < start_ticks + 30000):
            pass

    initPins()
    loadConfig()

    global redPWM, greenPWM, bluePWM, client
    client = MQTTClient(CONFIG['client_id'], CONFIG['broker'], 0, CONFIG['mqtt_username'], CONFIG['mqtt_password'])
    client.connect()
    print("Connected to {}".format(CONFIG['broker']))

    # Listen for all the things
    client.set_callback(mqtt_sub_callback)
    client.subscribe(CONFIG['command_topic'])
    client.subscribe(CONFIG['brightness_command_topic'])
    client.subscribe(CONFIG['rgb_command_topic'])

    # Set the light's color so we know we're running
    redPWM.duty(250)

    try:
        while 1:
            client.wait_msg()
    finally:
        client.disconnect()


if __name__ == '__main__':
    main()
