#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import datapoint

CONFIG_INI = "config.ini"

# If this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
# Hint: MQTT server is always running on the master device
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

class Weather(object):
    """Class used to wrap action code with mqtt connection
        
        Please change the name refering to your application
    """

    def __init__(self):
        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except :
            self.config = None
        
        api_key = self.config.get("secret").get("datapoint_api_key")
        lat = self.config.get("secret").get("lat")
        lng = self.config.get("secret").get("lng")

        self.conn = datapoint.connection(api_key=api_key)
        self.site = conn.get_nearest_site(lng, lat)

        # start listening to MQTT
        self.start_blocking()
        
    # --> Sub callback function, one per intent
    def weather_like_callback(self, hermes, intent_message):        
        print '[Received] intent: {}'.format(intent_message.intent.intent_name)
        
        forecast = conn.get_forecast_for_site(site.id, "3hourly")
        current_timestep = forecast.now()
        temperature = "%s degrees %s" % (now.temperature.value,
                                         now.temperature.units)
        
        output = "The weather in %s is likely to be %s. Temperature is %s" % (self.site.name,
                                                                              current_timestep.weather.text,
                                                                              temperature)
                                                                              
        print output

        # if need to speak the execution result by tts
        hermes.publish_end_session(intent_message.site_id, output)

    # More callback function goes here...

    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        self.weather_like_callback(hermes, intent_message)

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

if __name__ == "__main__":
    Weather()
