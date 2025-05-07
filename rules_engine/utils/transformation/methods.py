import logging
import datetime
import requests
import json
import locale
import os

from typing import Dict, List, Literal
from .base import TransfBaseMethod


logger = logging.getLogger("bre.transformation")
logger.setLevel("DEBUG")

CONVERTER_IP = os.environ.get("CONVERTER_IP", "utilities.f-one.group:4099")
DATE_URL = f"http://{CONVERTER_IP}/convert/date?value="
FLOAT_URL = f"http://{CONVERTER_IP}/convert/float?value="


class Set(TransfBaseMethod):
    """
    The 'Set' class is a subclass of the 'TransfBaseMethod' class.
    It represents a method of type 'set' that is used to set a specific variable in a process.

    Attributes:
        transformation_method (Literal["set"]): The type of the method, which is always set.
        input_variable (str): The name of the variable to be set.
        target_value (Any): The value to which the variable should be set.

    Methods:
        apply(process_variables: Dict) -> None:
            Applies the 'set' method by setting the input_variable in the process_variables dictionary to the target_value.

            Args:
                process_variables (Dict): A dictionary containing the variables of the process.

            Returns:
                None: This method does not return anything.
    """

    transformation_method: Literal["set"] = "set"

    def apply(self, process_variables: Dict) -> Dict:
        logger.info(f"Setting {self.variable} equal to {self.target_value}")

        keys: List[str] = self.variable.split(".")
        temp = process_variables
        for key in keys[:-1]:  # Navigate through all keys but the last
            if "[" in key:
                key_ = key[: key.index("[")]
                index = int(key[key.index("[") + 1 : -1])
                temp = temp[key_].__getitem__(index)
            else:
                if key not in temp and not key.isnumeric():
                    # Initialize a new dict if the key doesn't exist at this level
                    temp[key] = {}
                if key.isnumeric():
                    temp = temp[int(key)]
                else:
                    temp = temp[key]  # Move deeper into the nested dict
        # Set the value for the last key
        temp[keys[-1]] = self.target_value

        return process_variables


class Append(TransfBaseMethod):
    """
    Class representing an 'append' method.

    This class inherits from the 'TransfBaseMethod' class and implements the 'apply' method.
    The 'apply' method appends the 'target_value' to the 'input_variable' in the 'process_variables' dictionary.

    Attributes:
        transformation_method (Literal["append"]): The method type, which is set to "append".

    Methods:
        apply(process_variables: Dict) -> None: Applies the 'append' method to the 'process_variables' dictionary.

    Example Usage:
        append_method = Append()
        append_method.apply(process_variables)

    """

    transformation_method: Literal["append"] = "append"

    def apply(self, process_variables: Dict) -> Dict:
        logger.info(f"Appending {self.target_value} to {self.variable}")
        keys = self.variable.split(".")
        # Navigate to the target container (the one before the last key)
        temp = process_variables
        for key in keys[:-1]:  # All but the last key
            temp = temp.get(key, {})

        # The last key is where the value should be appended or concatenated
        final_key = keys[-1]
        if final_key not in temp:
            # If the final key doesn't exist, decide whether to create a list or string based on target_value type
            temp[final_key] = [] if isinstance(self.target_value, list) else ""

        # Now, append or concatenate to the target container
        if isinstance(temp[final_key], list):
            temp[final_key].append(self.target_value)
        elif isinstance(temp[final_key], str):
            temp[final_key] += (
                f"\n{self.target_value}" if temp[final_key] else str(self.target_value)
            )

        return process_variables


class Format(TransfBaseMethod):
    """
    The 'Format' class is a subclass of the 'TransfBaseMethod' class. It represents a method of formatting values in a specified format.

    Attributes:
        transformation_method (Literal["format"]): The type of the method, which is always set to "format".
        input_variable (str): The name of the input variable to be formatted.
        target_value (Any): The desired format to which the input variable should be formatted.

    Methods:
        apply(process_variables: Dict) -> None:
            Applies the formatting method to the input variable.
            This method converts the input variable to the specified format.
            If the target value is "de_DE.UTF-8", it formats the input variable as a number with two decimal places using the locale module.
            If the target value contains "%m", it formats the input variable as a date or datetime object using the DATE_URL API endpoint.
            The formatted value is then stored back in the process variables dictionary.

            Args:
                process_variables (Dict): A dictionary containing the process variables.

            Raises:
                AssertionError: If the input variable is not of the expected type.

            Returns:
                None
    """

    transformation_method: Literal["format"] = "format"

    def apply(self, process_variables: Dict) -> Dict:
        logger.info(f"Converting {self.variable} to {self.target_value} format")
        # number formatting
        if self.target_value == "de_DE.UTF-8":
            assert isinstance(
                process_variables[self.variable], (int, float)
            ), f"self.variable [{self.variable}] is not int or float"
            locale.setlocale(locale.LC_ALL, self.target_value)
            process_variables[self.variable] = locale.format_string(
                "%.2f", process_variables[self.variable], False
            )

        # date and time formatting
        # VG 02.03.23 united date and time 'cause to the moment for the service there is no difference
        if "%m" in self.target_value.lower():
            assert isinstance(
                process_variables[self.variable], (str, datetime.datetime)
            ), f"self.variable [{self.variable}] is not str or datetime.datetime"
            if isinstance(process_variables[self.variable], str):
                url_string = f"{DATE_URL}{process_variables[self.variable]}&output_format={self.target_value}"
                response = requests.request("GET", url_string, headers={}, data={})
                if response.status_code == 200:
                    formatted_date = json.loads(response.content)["value"]
                    process_variables[self.variable] = formatted_date
            else:
                process_variables[self.variable] = process_variables[
                    self.variable
                ].strftime(self.target_value)
        return process_variables
