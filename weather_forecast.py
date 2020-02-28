"""
The file to be tested.
It gets weather data, and provides it to the user based on arguments
"""
import argparse  # Gets the input data from the user
import datetime  # To handle the sunrise, etc. conversion
import requests  # Used to receive web page data


# Exception for when the arguments are invalid
class InvalidArgumentException(Exception):
    """
    An error class to raise if the user inputs something incorrectly
    """
    def __init__(self, to_display="The arguments entered were invalid"):
        Exception.__init__(self)
        self.message = to_display

    def __str__(self):
        return self.message


class InputParser:
    """
    This class facilitates receiving a command line argument and using that to get relevant
    weather data for the user
    """
    def __init__(self):
        """
        Define the argument parser that will be used to facilitate user input
        """
        self.command_parser = argparse.ArgumentParser(description="Weather Commands",
                                                      argument_default=argparse.SUPPRESS,
                                                      add_help=False)

        # Help OR API key are required
        # Add mutually exclusive group
        help_api_group = self.command_parser.add_mutually_exclusive_group(required=True)

        # The key for the api, must be present
        help_api_group.add_argument("-api", help="The api key to access the weather."
                                                 "  Mandatory if [help] is not present")
        # Help should only be displayed if alone
        help_api_group.add_argument("-help", action='store_true',
                                    help="Display this help menu.  "
                                         "Mandatory if [api] is not present")

        # Some other commands needed

        # Location
        self.command_parser.add_argument("-city", help="Uses a city name as the location. Enter "
                                                       "'[city]' or '[city],[country code]' ")
        self.command_parser.add_argument("-cid", help="Uses a city ID as the location")
        self.command_parser.add_argument("-gc",
                                         help="Uses a geographical coordinates as the location."
                                              "Enter '[latitude],[longitude]")
        self.command_parser.add_argument("-z", help="Uses a zip as the location. Enter '[zip],"
                                                    "[country code]' or it will default to US")

        # Optional temperature argument

        self.command_parser.add_argument("-temp", nargs="?", const='celsius',
                                         help="Display the temperature in [celsius]"
                                              " or [fahrenheit].  Default is celsius")

        #  Other optional flags
        self.command_parser.add_argument("-time", action='store_true',
                                         help="Display the timezone")
        self.command_parser.add_argument("-pressure", action='store_true',
                                         help="Display the pressure")
        self.command_parser.add_argument("-cloud", action='store_true',
                                         help="Display the cloud levels")
        self.command_parser.add_argument("-humidity", action='store_true',
                                         help="Display the humidity")
        self.command_parser.add_argument("-wind", action='store_true',
                                         help="Display the wind")
        self.command_parser.add_argument("-sunset", action='store_true',
                                         help="Display the sunset time")
        self.command_parser.add_argument("-sunrise", action='store_true',
                                         help="Display the sunrise time")


        self.user_input = {}  # The default input to be parsed in

    def get_input(self):
        """
        Use the parser to obtain input, then convert the returned Namespace
        into a python dictionary for easy reading
        :return: the arguments given as a dictionary
        :raises:
        """
        request_as_dict = vars(self.command_parser.parse_args())
        # DEBUG
        # print(type(self.command_parser))
        self.user_input = request_as_dict
        return request_as_dict

    def is_valid(self):
        """
        Checks if the dictionary given is valid for use with the open weather api.
        :return: True if the input is valid, otherwise raises an exception
        :raises InvalidArgumentException: If the given arguments are bad
        """

        # Sanitise the thing for multiple commands
        if "help" in self.user_input:
            if len(self.user_input) > 1:
                raise InvalidArgumentException("[-help] should not be present with other arguments")
            return True  # Help on its own is valid, so if here, the input is acceptable

        group_one = ["city", "cid", "gc", "z"]  # One of these should be present.  No more, no less
        group_one_count = 0  # Store the number of group one keys
        for arg in self.user_input:
            if arg in group_one:
                group_one_count += 1

        if group_one_count > 1:  # Too many location args
            raise InvalidArgumentException("Only one instance of [-city],"
                                           " [-cid], [-gc], or [-z] permitted")
        if group_one_count == 0:  # Not enough location args
            raise InvalidArgumentException("One instance of [-city], [-cid],"
                                           " [-gc], or [-z] must be present")

        # Test if user has input one location but no other information been asked
        if group_one_count == 1 and len(self.user_input) == 0:
            raise InvalidArgumentException("Only location and there is no "
                                           "chosen information e.g., time or temperature ")

        # Ensure actual information is asked for by the user
        if "api" in self.user_input and len(self.user_input) < 3:
            raise InvalidArgumentException("No chosen information flags (e.g. [-time],"
                                           " [-sunrise], etc. See [-help]")
        # Ensure the temp flag was either left at the default or changed to fahrenheit
        if "temp" in self.user_input:
            if self.user_input["temp"].lower() != "celsius" and \
                    self.user_input["temp"].lower() != "fahrenheit":
                raise InvalidArgumentException("Temperature must be in either celsius "
                                               "or fahrenheit!")


        # If no exception is raised, this must be valid!

        return True

    def synthesise_request(self):
        """
        Produces either a string that is a valid URL to get the information
        from the open weather api or the help
        :return: Either the URL to get the information the user wants,
         or ERROR, or HELP (if help is called)
        """
        try:  # Test for any errors
            self.is_valid()
        except InvalidArgumentException as arg_except:
            return ["ERROR", "ERROR: " + str(arg_except)]  # Get the message stored in the exception

        if "help" in self.user_input:
            # At this point, it must be valid and so only the help arg is present
            return ["HELP", self.command_parser.format_help()]  # Get the help string

        base_string = "http://api.openweathermap.org/data/2.5/weather?"  # The string the arguments
        #  are added to
        api_key = self.user_input['api']  # Get the api key for lookup

        location = ""

        # The following for loop looks for the one instance of the location
        # argument and gives it to "location"
        for location_arg in ["city", "cid", "gc", "z"]:
            if location_arg in self.user_input:
                if location_arg == "gc":  # This requires a little extra work to split
                    lat_lon = self.user_input[location_arg].split(',')
                    location += "lat=" + lat_lon[0] + "&" + "lon=" + lat_lon[1]
                else:
                    # Everything else is okay, as the arguments can be instantly applied.
                    if location_arg == "cid":
                        location += "id="
                    elif location_arg == "z":
                        location += "zip="
                    elif location_arg == "city":
                        location += "q="

                    location += self.user_input[location_arg]

        return ["SUCCESS", base_string + location + "&APPID=" + api_key]

    def get_from_url(self, url):
        """
        Gets the information from the given URL and constructs it into a valid string
        :param url: The URL to get the data from
        :return: The string with all the data the user wants
        """

        my_response = requests.get(url=url)
        if my_response.status_code == 401:  # Handle different errors
            return "BAD_API"
        if my_response.status_code == 404:
            return "LOCATION_UNKNOWN"
        if my_response.status_code != 200:  # Otherwise, return the error
            return my_response.status_code

        # Everything is okay, we can proceed
        weather_json = my_response.json()

        output_string = ""

        # Get the timezone difference from UTC in hours
        if "time" in self.user_input:
            time_offset = weather_json["timezone"]//3600
            # The following statement contains "ternary" operations (or as close as can
            # get in python, which is just for the grammar of the response
            output_string += "The timezone is " + str(abs(time_offset)) + " hour" \
                             + ["s ", " "][abs(time_offset) == 1] + \
                             ["before", "past"][time_offset > 0] + " GMT.  "

        if "sunrise" in self.user_input:
            time_up = weather_json["sys"]["sunrise"]
            output_string += "The sun rises at " \
                             + str(datetime.datetime.utcfromtimestamp(time_up).strftime("%H:%M "))\
                             + "GMT.  "

        if "sunset" in self.user_input:
            time_dn = weather_json["sys"]["sunset"]
            output_string += "The sun sets at " \
                             + str(datetime.datetime.utcfromtimestamp(time_dn).strftime("%H:%M ")) \
                             + "GMT.  "

        if "pressure" in self.user_input:
            pressure = weather_json["main"]["pressure"]  # Get the pressure (in hPa)
            output_string += "The pressure is " + str(pressure) + "hPa.  "

        if "cloud" in self.user_input:
            cloudiness = weather_json["clouds"]["all"]  # Get the percentage chance of clouds
            output_string += "There is a " + str(cloudiness) + "% chance of clouds.  "

        if "humidity" in self.user_input:
            humidity = weather_json["main"]["humidity"]
            output_string += "The humidity is at " + str(humidity) + "%.  "

        if "wind" in self.user_input:
            wind = weather_json["wind"]
            # Get the wind, convert it from m/s to k/h
            output_string += "The wind is moving at " + str(wind["speed"]*3.6) + "km/h, "
            output_string += "in a direction of " + str(wind["deg"]) + " degrees.  "

        if "temp" in self.user_input:
            temp_max = (weather_json["main"]["temp_max"] - 273.15)
            temp_min = (weather_json["main"]["temp_min"] - 273.15)

            temp_max = [(lambda temperature: temperature * 9/5 + 32)(temp_max),
                        temp_max][self.user_input["temp"].lower() == "celsius"]
            temp_min = [(lambda temperature: temperature * 9 / 5 + 32)(temp_min),
                        temp_min][self.user_input["temp"].lower() == "celsius"]


            output_string += "The temperature has a high of " + str(round(temp_max, 1)) + \
                             " and a low of "+  str(round(temp_min, 1)) + " degrees " + \
                             self.user_input["temp"].lower() + ".  "

        return output_string


if __name__ == "__main__":
    PARSER = InputParser()
    PARSER.get_input()
    URL_ARR = PARSER.synthesise_request()
    if URL_ARR[0] == "SUCCESS":  # Ensure that the URL is a valid URL
        RESULT = PARSER.get_from_url(URL_ARR[1])
        if RESULT == "BAD_API":
            print("The api key is invalid!")
        elif RESULT == "LOCATION_UNKNOWN":
            print("The location entered cannot be found!")
        elif RESULT.isalpha():  # If it is a number, it is another miscellaneous error
            print("A value was entered incorrectly")
        else:  # Otherwise, print the wanted results
            print(RESULT)
    else:
        print(URL_ARR[1])  # Display the error, OR help, depending on what the user put
