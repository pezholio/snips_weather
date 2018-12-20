#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
from lib import PostCodeClient

import io
import datapoint
import json

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
        postcode = self.config.get("secret").get("postcode")
        
        lat_lng = self.get_latlng(postcode)

        self.conn = datapoint.connection(api_key=api_key)
        self.site = self.conn.get_nearest_site(lat_lng[1], lat_lng[0])

        # start listening to MQTT
        self.start_blocking()
        
    # --> Sub callback function, one per intent
    def weather_like_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        
        print '[Received] intent: {}'.format(intent_message.intent.intent_name)
        
        forecast = self.conn.get_forecast_for_site(self.site.id, "3hourly")
        current_timestep = forecast.now()
        temperature = "%s degrees %s" % (current_timestep.temperature.value,
                                         current_timestep.temperature.units)
        
        output = "The weather in %s is likely to be %s. Temperature is %s" % (self.site.name,
                                                                              current_timestep.weather.text,
                                                                              temperature)
                                                                              
        print output

        # if need to speak the execution result by tts
        hermes.publish_end_session(intent_message.session_id, output)

    # More callback function goes here...

    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        self.weather_like_callback(hermes, intent_message)
    
    def get_latlng(self, postcode):
        client = PostCodeClient()
        pc = client.getLookupPostCode(postcode)
        result = json.loads(pc)['result']
        return [result['latitude'], result['longitude']]
        
    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

if __name__ == "__main__":
    Weather()
