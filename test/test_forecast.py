import datapoint
import vcr

from .. import forecast

class TestForecast(object):
    
    def connection(self):
        return datapoint.connection(api_key="0df1de30-94a9-4f6f-b4d4-114b3a9237be")
    
    @vcr.use_cassette('fixtures/vcr_cassettes/gets_a_forecast.yaml', record_mode='new_episodes')
    def test_returns_a_forecast(self):
        f = forecast.Forecast(self.connection(), 51.501009, -0.141588)
        assert f.response() == 'The weather in Westminster is likely to be Cloudy. Temperature is 9 degrees C'
