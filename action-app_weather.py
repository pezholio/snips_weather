#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
from lib import PostCodeClient
from forecast import Forecast

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

        self.get_latlng(postcode)

        self.conn = datapoint.connection(api_key=api_key)

        # start listening to MQTT
        self.start_blocking()
        
    # --> Sub callback function, one per intent
    def weather_like_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        
        print '[Received] intent: {}'.format(intent_message.intent.intent_name)
        
        forecast = Forecast(self.conn, self.latitude, self.longitude)

        # if need to speak the execution result by tts
        hermes.publish_end_session(intent_message.session_id, forecast.response())

    # More callback function goes here...

    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        if intent_message.intent.intent_name == 'pezholio:weather_like':
            self.weather_like_callback(hermes, intent_message)
        else:
            return
    
    def get_latlng(self, postcode):
        client = PostCodeClient()
        pc = client.getLookupPostCode(postcode)
        result = json.loads(pc)['result']
        self.latitude = result['latitude']
        self.longitude = result['longitude']
        
    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

if __name__ == "__main__":
    Weather()
