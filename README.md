# esp8266_micropython_rgb_mqtt
Micropython for driving an RGB LED on an ESP8266

## config.json
This needs a config.json file with all your secrets. All the topics should relate to whatever your MQTT schema is, I'm using HomeAssistant.
```
{
    "broker": "BROKER_IP_HERE",
    "client_id": "client_ID_here",
    "mqtt_username": "",
    "mqtt_password": "",
    "command_topic": "home/led-strip/set",
    "state_topic": "home/led-strip",
    "brightness_state_topic": "home/led-strip/brightness",
    "brightness_command_topic": "home/led-strip/brightness/set",
    "rgb_state_topic": "home/led-strip/rgb",
    "rgb_command_topic": "home/led-strip/rgb/set",
}
```
