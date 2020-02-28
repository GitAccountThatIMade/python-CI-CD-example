# This will test the weather forecasting file
from weather_forecast import *
import unittest
from unittest.mock import patch
from unittest.mock import Mock


class WeatherForecastTests(unittest.TestCase):

    def setUp(self):
        # Construct a mock object to replace the argparse library, as we can't call command line arguments from here
        self.myMock = Mock()
        self.myMock.add_argument.return_value = None
        self.myMock.add_mutually_exclusive_group.return_value = self.myMock

    @patch('weather_forecast.argparse')
    def test_get_input_pass(self, mock_argparse):
        """
        Test the get_input method
        :param mock_argparse:
        :return None:
        :raises an assertion exception if the test fails:
        """

        # This line of code represents the input of the user
        # The namespace takes the arguments the parser gives
        self.myMock.parse_args.return_value = argparse.Namespace(api='test', cid="5")
        # Replace the call to the argparse constructor
        mock_argparse.ArgumentParser.return_value = self.myMock
        # Finally, call the method, with the external function call replaced by unittest
        self.assertTrue(InputParser().get_input() == {'api': 'test', 'cid': '5'})

    @patch('weather_forecast.argparse')
    def test_is_valid_pass(self, mock_argparse):
        self.myMock.parse_args.return_value = argparse.Namespace(api='test', cid='5', time=True)
        mock_argparse.ArgumentParser.return_value = self.myMock
        test_parser = InputParser()
        test_parser.get_input()
        self.assertTrue(test_parser.is_valid())  # Test if it's valid

    @patch('weather_forecast.argparse')
    def test_is_valid_no_loc(self, mock_argparse):
        self.myMock.parse_args.return_value = argparse.Namespace(api='4')
        mock_argparse.ArgumentParser.return_value = self.myMock
        test_parser = InputParser()
        test_parser.get_input()
        with self.assertRaises(InvalidArgumentException):
            test_parser.is_valid()  # Test if it's not valid

    @patch('weather_forecast.argparse')
    def test_is_valid_many_loc(self, mock_argparse):
        self.myMock.parse_args.return_value = argparse.Namespace(api='4', city="TEST", cid='5', time=True)
        mock_argparse.ArgumentParser.return_value = self.myMock
        test_parser = InputParser()
        test_parser.get_input()
        with self.assertRaises(InvalidArgumentException):
            test_parser.is_valid()  # Test if it's not valid

    @patch('weather_forecast.argparse')
    def test_is_valid_no_arg(self, mock_argparse):
        self.myMock.parse_args.return_value = argparse.Namespace(api='4', city="TEST", cid='5')
        mock_argparse.ArgumentParser.return_value = self.myMock
        test_parser = InputParser()
        test_parser.get_input()
        with self.assertRaises(InvalidArgumentException):
            test_parser.is_valid()  # Test if it's not valid

    @patch('weather_forecast.argparse')
    def test_synthesise_request_pass(self, mock_argparse):
        self.myMock.parse_args.return_value = argparse.Namespace(api='test', cid='5', time=True)
        mock_argparse.ArgumentParser.return_value = self.myMock
        test_parser = InputParser()
        test_parser.get_input()
        self.assertTrue(test_parser.synthesise_request()[1] ==
                        "http://api.openweathermap.org/data/2.5/weather?id=5&APPID=test")  # Test if it's valid

    @patch('weather_forecast.argparse')
    def test_synthesise_request_fail(self, mock_argparse):
        self.myMock.parse_args.return_value = argparse.Namespace(api='test')
        mock_argparse.ArgumentParser.return_value = self.myMock
        test_parser = InputParser()
        test_parser.get_input()
        self.assertTrue(test_parser.synthesise_request()[0] == "ERROR")  # Test if it's valid

    @patch('weather_forecast.requests')
    def test_get_from_url_401(self,mock_requests):
        test_mock = Mock()
        test_mock.status_code = 401
        test_mock.json.return_value = {"test":0}

        mock_requests.get.return_value = test_mock

        test_parser = InputParser()
        self.assertTrue(test_parser.get_from_url("") == "BAD_API")


    @patch('weather_forecast.requests')
    def test_get_from_url_404(self,mock_requests):
        test_mock = Mock()
        test_mock.status_code = 404
        test_mock.json.return_value = {"test":0}

        mock_requests.get.return_value = test_mock

        test_parser = InputParser()
        self.assertTrue(test_parser.get_from_url("") == "LOCATION_UNKNOWN")

    @patch('weather_forecast.requests')
    def test_get_from_url_unknown_error(self,mock_requests):
        test_mock = Mock()
        test_mock.status_code = 1234  # An error that we don't recognise
        test_mock.json.return_value = {"test":0}

        mock_requests.get.return_value = test_mock

        test_parser = InputParser()
        self.assertTrue(test_parser.get_from_url("") == 1234)

    @patch('weather_forecast.requests')
    def test_get_from_url_time(self,mock_requests):
        test_mock = Mock()
        test_mock.status_code = 200
        test_mock.json.return_value = {"timezone":3600}

        mock_requests.get.return_value = test_mock

        test_parser = InputParser()
        test_parser.user_input = {"api":"test", "city":"test", "time":True}
        self.assertTrue(test_parser.get_from_url("") == 'The timezone is 1 hour past GMT.  ')

    @patch('weather_forecast.requests')
    def test_get_from_url_sunrise(self,mock_requests):
        test_mock = Mock()
        test_mock.status_code = 200
        test_mock.json.return_value = {"sys":{"sunrise":1571192970}}

        mock_requests.get.return_value = test_mock

        test_parser = InputParser()
        test_parser.user_input = {"api":"test", "gc":"1,1", "sunrise":True}

        self.assertTrue(test_parser.get_from_url("") == "The sun rises at 02:29 GMT.  ")

    @patch('weather_forecast.requests')
    def test_get_from_url_sunset(self,mock_requests):
        test_mock = Mock()
        test_mock.status_code = 200
        test_mock.json.return_value = {"sys":{"sunset":1571182970}}

        mock_requests.get.return_value = test_mock

        test_parser = InputParser()
        test_parser.user_input = {"api":"test", "city":"test", "sunset":True}

        self.assertTrue(test_parser.get_from_url("") == "The sun sets at 23:42 GMT.  ")
        # assertTrue mean the result will be "The sun sets at 23:42 GMT" is true return.

    @patch('weather_forecast.argparse')
    def test_is_valid_only_help(self,mock_argparse):
        self.myMock.parse_args.return_value = argparse.Namespace(help=True)
        mock_argparse.ArgumentParser.return_value = self.myMock
        test_parser = InputParser()
        test_parser.get_input()
        self.assertTrue(test_parser.is_valid())  # Test if it's valid

    @patch('weather_forecast.argparse')
    def test_is_valid_invalid_help(self, mock_argparse):  # See if it crashes when help isn't the only option
        self.myMock.parse_args.return_value = argparse.Namespace(help=True, cid = "TEST")
        mock_argparse.ArgumentParser.return_value = self.myMock
        test_parser = InputParser()
        test_parser.get_input()
        with self.assertRaises(InvalidArgumentException):
            test_parser.is_valid()  # Test if it's not valid

    @patch('weather_forecast.argparse')
    def test_is_valid_invalid_temp(self, mock_argparse):  # See if it crashes when help isn't the only option
        self.myMock.parse_args.return_value = argparse.Namespace(api="test", cid = "TEST", temp="not_valid")
        mock_argparse.ArgumentParser.return_value = self.myMock
        test_parser = InputParser()
        test_parser.get_input()
        with self.assertRaises(InvalidArgumentException):
            test_parser.is_valid()  # Test if it's not valid

    @patch('weather_forecast.argparse')
    def test_is_valid_valid_temp(self, mock_argparse):  # See if it crashes when help isn't the only option
        self.myMock.parse_args.return_value = argparse.Namespace(api="test", cid = "TEST", temp="fahrenheit")
        mock_argparse.ArgumentParser.return_value = self.myMock
        test_parser = InputParser()
        test_parser.get_input()
        self.assertTrue(test_parser.is_valid())  # Test if it's valid

    @patch('weather_forecast.requests')
    def test_get_from_url_pressure(self,mock_requests):
        test_mock = Mock()
        test_mock.status_code = 200
        test_mock.json.return_value = {"main":{"pressure":1000}}

        mock_requests.get.return_value = test_mock

        test_parser = InputParser()
        test_parser.user_input = {"api":"test", "city":"test", "pressure":True}

        self.assertTrue(test_parser.get_from_url("") == "The pressure is 1000hPa.  ")

    @patch('weather_forecast.requests')
    def test_get_from_url_cloud(self,mock_requests):
        test_mock = Mock()
        test_mock.status_code = 200
        test_mock.json.return_value = {"clouds":{"all":50}}
        mock_requests.get.return_value = test_mock
        TestParser = InputParser()
        TestParser.user_input = {"api":"test", "city":"test", "cloud":True}
        self.assertTrue(TestParser.get_from_url("") == "There is a 50% chance of clouds.  ")

    @patch('weather_forecast.requests')
    def test_get_from_url_humidity(self,mock_requests):
        test_mock = Mock()
        test_mock.status_code = 200
        test_mock.json.return_value = {"main":{"humidity":89}}
        mock_requests.get.return_value = test_mock
        TestParser = InputParser()
        TestParser.user_input = {"api":"test", "city":"test", "humidity":True}
        self.assertTrue(TestParser.get_from_url("") == "The humidity is at 89%.  ")

    @patch('weather_forecast.requests')
    def test_get_from_url_wind(self,mock_requests):
        test_mock = Mock()
        test_mock.status_code = 200
        test_mock.json.return_value = {"wind":{"speed": 20, "deg": 75}}
        mock_requests.get.return_value = test_mock
        TestParser = InputParser()
        TestParser.user_input = {"api":"test", "city":"test", "wind":True}
        self.assertTrue(TestParser.get_from_url("") == "The wind is moving"
                                                       " at 72.0km/h, in a direction of 75 degrees.  ")

    @patch('weather_forecast.requests')
    def test_get_from_url_temp_celsius(self,mock_requests):
        test_mock = Mock()
        test_mock.status_code = 200
        test_mock.json.return_value = {"main":{"temp_max":300, "temp_min": 280}}
        mock_requests.get.return_value = test_mock
        TestParser = InputParser()
        TestParser.user_input = {"api": "test", "city": "test", "temp": "celsius"}
        self.assertTrue(TestParser.get_from_url("") == "The temperature has a high of "
                                                       "26.9 and a low of 6.9 degrees celsius.  ")



if __name__ == "__main__":
    unittest.main()
