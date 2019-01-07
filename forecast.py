class Forecast:
    
    def __init__(self, connection, lat, lng):
        self.connection = connection
        self.site = self.connection.get_nearest_site(lng, lat)
        self.forecast = self.forecast_for_site(self.site)
    
    def response(self):
        return "The weather in %s is likely to be %s. Temperature is %s" % (self.site.name,
                                                                            self.forecast.weather.text,
                                                                            self.temperature())
        
    def forecast_for_site(self, site):
        forecast = self.connection.get_forecast_for_site(site.id, "3hourly")
        return forecast.now()
        
    def temperature(self):
        return "%s degrees %s" % (self.forecast.temperature.value,
                                  self.forecast.temperature.units)
