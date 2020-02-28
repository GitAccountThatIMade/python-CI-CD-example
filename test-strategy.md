# Testing strategy and rationale

Throughout the development of the code, tests were created to help ensure 
functional correctness.

**Statement Coverage** was the main strategy to the unit tests present, as while
**Branch Coverage** would be more thorough, it would have been more time
consuming and as such, not a viable solution

The goal for developing the test cases was to observe each line of code, and
attempt to write a test case that covers that line of code.

Most tests cover more than one line each, which is to be expected.  **However**,
the tests were not *designed* to cover the greatest number of statements
possible, as this goes against the idea of unit testing.

**setUp** creates a mock user input object.

**test_get_input_pass** gives the mock input to the get_input function, testing
if it turns it to a dictionary

**test_is_valid_pass** tests if a valid mocked input will be marked valid.

**test_is_valid_no_loc** tests if a mocked input with no location argument is invalid.

**test_is_valid_many_loc** tests if a mocked input with too many location arguments is
invalid.

**test_is_valid_no_arg** tests if a mocked input with no information flags is invalid.

**test_is_valid_only_help** tests if a mock input only providing "help" will be
valid.

**test_is_valid_invalid_help** test if a mock input with "help" along with other
options is invalid (as help may be the only argument present, if present at all)

**test_is_valid_invalid_temp** tests if a mocked invalid "temp" argument is marked
invalid

**test_is_valid_valid_temp** tests if "fahrenheit" is an acceptable input to "temp"


**test_synthesise_request_pass** tests if a given mocked input creates the correct 
intended URL.

**test_synthesise_request_fail** tests if a given mocked input creates an error when it
should.

**test_get_from_url_401** tests if a mocked status code of 401 gives the correct error
response for a bad API.

**test_get_from_url_404** tests if a mocked status code of 404 gives the correct error
response for an invalid URL.

**test_get_from_url_unknown_error** tests if a mocked unknown status code gives back
the error code provided.

**test_get_from_url_time** tests if the time can be taken from the mocked JSON/
dictionary object.

**test_get_from_url_sunrise** tests if the sunrise can be taken from the mocked JSON/
dictionary object.

**test_get_from_url_sunset** tests if the sunset can be taken from the mocked JSON/
dictionary object.

**test_get_from_url_pressure** tests if the program can get the pressure from the mocked
JSON/dictionary object

**test_get_from_url_cloud** tests if the program can get the cloud chance from
the mocked JSON/dictionary object

**test_get_from_url_humidity**  tests if the program can get the humidity from
the mocked JSON/dictionary object

**test_get_from_url_wind** tests if the wind information can be read from the 
mocked JSON/dictionary object

**test_get_from_url_temp_fahrenheit** tests if the temperature can be presented
in fahrenheit from the mocked JSON/dictionary object

