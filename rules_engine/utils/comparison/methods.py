import logging
import re
from typing import Any, List, Literal, Union

from .base import ComparisonBaseMethod


logger = logging.getLogger("bre.comparison")
logger.setLevel("DEBUG")


class IsEmpty(ComparisonBaseMethod):
    """
    The IsEmpty class is a subclass of the ComparisonBaseMethod class.
    It represents a method for evaluating whether an input variable is empty.

    Attributes:
        comparison_method (Literal["is_empty"]): The method type, which is set to "is_empty".
        comparison_variables (bool): The comparison variable used for evaluating the emptiness of the input variable.
                                    If set to False evaluate the input variable is not empty.

    Methods:
        evaluate() -> bool: This method evaluates whether the input variable is empty based on its type and the comparison variable.

    Example Usage:
        is_empty_method = IsEmpty(input_variable="example", comparison_variables=True)
        result = is_empty_method.evaluate()
        print(result)  # Output: False

        is_empty_method = IsEmpty(input_variable="example", comparison_variables=False)
        result = is_empty_method.evaluate()
        print(result)  # Output: True
    """

    comparison_method: Literal["is_empty"] = "is_empty"
    comparison_variables: bool

    def evaluate(self) -> bool:
        # check if the input variable is empty
        logger.info(f"Checking is_empty for {self.variable}")
        if isinstance(self.variable, str):
            return (self.variable.strip() == "") == self.comparison_variables
        elif isinstance(self.variable, list):
            return (self.variable == []) == self.comparison_variables
        elif isinstance(self.variable, dict):
            return (self.variable == {}) == self.comparison_variables
        elif isinstance(self.variable, tuple):
            return (self.variable == ()) == self.comparison_variables
        else:
            return (self.variable is None) == self.comparison_variables


class LessThan(ComparisonBaseMethod):
    """
    The 'LessThan' class is a subclass of the 'ComparisonBaseMethod' class. It represents a method for evaluating whether the input variable is less than the comparison variable.

    Attributes:
        comparison_method (Literal["less_than"]): The method type, which is set to "less_than".
        input_variable (Any): The input variable to be compared.
        comparison_variables (Any): The comparison variable to be compared against.

    Methods:
        evaluate() -> bool: This method evaluates whether the input variable is less than the comparison variable and returns a boolean value.

    Example usage:
        less_than_method = LessThan()
        less_than_method.input_variable = 5
        less_than_method.comparison_variables = 10
        result = less_than_method.evaluate()
        print(result)  # Output: True
    """

    comparison_method: Literal["less_than"] = "less_than"

    def evaluate(self) -> bool:
        logger.info(f"Checking {self.variable} < {self.comparison_variables}")
        return self.variable < self.comparison_variables


class LessThanOrEqual(ComparisonBaseMethod):
    """
    The LessThanOrEqual class is a subclass of the ComparisonBaseMethod class. It represents a method for evaluating whether the input variable is less than or equal to the comparison variable.

    Attributes:
        comparison_method (Literal["less_than_or_equal_to"]): The method type, which is set to "less_than_or_equal_to".
        input_variable (Any): The input variable to be compared.
        comparison_variables (Any): The comparison variable to be compared against.

    Methods:
        evaluate() -> bool: This method evaluates whether the input variable is less than or equal to the comparison variable and returns a boolean value.

    Example usage:
        less_than_or_equal = LessThanOrEqual(input_variable, comparison_variables)
        result = less_than_or_equal.evaluate()
    """

    comparison_method: Literal["less_than_or_equal_to"] = "less_than_or_equal_to"

    def evaluate(self) -> bool:
        logger.info(f"Checking {self.variable} <= {self.comparison_variables}")
        return self.variable <= self.comparison_variables


class GreaterThan(ComparisonBaseMethod):
    """
    Class representing a greater than comparison method.

    This class inherits from the `ComparisonBaseMethod` class and implements the `evaluate` method to perform a greater than comparison between the `input_variable` and `comparison_variables`.

    Attributes:
        comparison_method (Literal["greater_than"]): The method type, set to "greater_than".
        input_variable (Any): The input variable for the comparison.
        comparison_variables (Any): The comparison variable for the comparison.

    Methods:
        evaluate() -> bool: Performs the greater than comparison and returns the result.

    Example usage:
        greater_than_method = GreaterThan()
        greater_than_method.input_variable = 5
        greater_than_method.comparison_variables = 3
        result = greater_than_method.evaluate()
        print(result)  # Output: True
    """

    comparison_method: Literal["greater_than"] = "greater_than"

    def evaluate(self) -> bool:
        logger.info(f"Checking {self.variable} > {self.comparison_variables}")
        return self.variable > self.comparison_variables


class GreaterThanOrEqual(ComparisonBaseMethod):
    """
    The 'GreaterThanOrEqual' class is a subclass of the 'ComparisonBaseMethod' class. It represents a method for evaluating whether the input variable is greater than or equal to the comparison variable.

    Attributes:
        comparison_method (Literal["greater_than_or_equal_to"]): The method type, which is set to "greater_than_or_equal_to".
        input_variable (Any): The input variable to be compared.
        comparison_variables (Any): The comparison variable to be compared against.

    Methods:
        evaluate() -> bool: This method evaluates whether the input variable is greater than or equal to the comparison variable and returns a boolean value.

    Example usage:
        greater_than_or_equal = GreaterThanOrEqual(comparison_method="greater_than_or_equal_to", input_variable=10, comparison_variables=5)
        result = greater_than_or_equal.evaluate()
        print(result)  # Output: True
    """

    comparison_method: Literal["greater_than_or_equal_to"] = "greater_than_or_equal_to"

    def evaluate(self) -> bool:
        logger.info(f"Checking {self.variable} >= {self.comparison_variables}")
        return self.variable >= self.comparison_variables


class EqualTo(ComparisonBaseMethod):
    """
    The 'EqualTo' class is a subclass of 'ComparisonBaseMethod' and represents a method for evaluating whether two variables are equal to each other.

    Attributes:
        comparison_method (Literal["equal_to"]): The method type, which is set to "equal_to".
        input_variable (Any): The input variable to be compared.
        comparison_variables (Any): The variable to be compared with the input variable.

    Methods:
        evaluate() -> bool: Evaluates whether the input variable is equal to the comparison variable. Returns True if they are equal, False otherwise.
    """

    comparison_method: Literal["equal_to"] = "equal_to"

    def evaluate(self) -> bool:
        logger.info(f"Checking {self.variable} == {self.comparison_variables}")
        if isinstance(self.variable, str) and isinstance(
            self.comparison_variables, str
        ):
            return self.variable.strip() == self.comparison_variables.strip()
        elif isinstance(self.comparison_variables, list):
            return any(
                [self.variable == comp_var for comp_var in self.comparison_variables]
            )
        else:
            return self.variable == self.comparison_variables


class NotEqualTo(ComparisonBaseMethod):
    """
    The 'NotEqualTo' class is a subclass of the 'ComparisonBaseMethod' class.
    It represents a method for evaluating whether two variables are not equal to each other.

    Attributes:
        comparison_method (Literal["not_equal_to"]): The method type, which is set to "not_equal_to".
        input_variable (Any): The input variable to be compared.
        comparison_variables (Any): The variable to be compared against the input variable.

    Methods:
        evaluate() -> bool: This method evaluates whether the input variable is not equal to the comparison variable. It returns a boolean value indicating the result of the evaluation.

    Example Usage:
        not_equal = NotEqualTo(input_variable="abc", comparison_variables="def")
        result = not_equal.evaluate()
        print(result)  # Output: True
    """

    comparison_method: Literal["not_equal_to"] = "not_equal_to"

    def evaluate(self) -> bool:
        logger.info(f"Checking {self.variable} != {self.comparison_variables}")
        if isinstance(self.variable, str) and isinstance(
            self.comparison_variables, str
        ):
            return self.variable.strip() != self.comparison_variables.strip()
        elif isinstance(self.comparison_variables, list):
            return any(
                [self.variable != comp_var for comp_var in self.comparison_variables]
            )
        else:
            return self.variable != self.comparison_variables


class StartsWith(ComparisonBaseMethod):
    """
    The `StartsWith` class is a subclass of `ComparisonBaseMethod` and represents a method for evaluating whether a given input variable starts with a specific comparison variable or a list of comparison variables.

    Attributes:
        comparison_method (Literal["starts_with"]): The method type, which is set to "starts_with".
        input_variable (str): The input variable to be evaluated.
        comparison_variables (Union[str, List[str]]): The comparison variable(s) used for evaluation. It can be a single string or a list of strings.

    Methods:
        evaluate() -> bool: This method overrides the base class method and performs the evaluation. It checks if the input variable starts with the comparison variable(s) and returns a boolean value indicating the result.

    Example usage:
        starts_with_method = StartsWith(input_variable="hello world", comparison_variables="hello")
        result = starts_with_method.evaluate()
        print(result)  # Output: True

        starts_with_method = StartsWith(input_variable="hello world", comparison_variables=["hello", "hi"])
        result = starts_with_method.evaluate()
        print(result)  # Output: True

        starts_with_method = StartsWith(input_variable="hello world", comparison_variables="hi")
        result = starts_with_method.evaluate()
        print(result)  # Output: False
    """

    comparison_method: Literal["starts_with"] = "starts_with"
    variable: str
    comparison_variables: Union[str, List[str]]

    def evaluate(self) -> bool:
        logger.info(
            f"Checking if {self.variable} starts with {self.comparison_variables}"
        )
        if isinstance(self.comparison_variables, list):
            return any([self.variable.startswith(v) for v in self.comparison_variables])

        elif isinstance(self.comparison_variables, str):

            return self.variable.startswith(self.comparison_variables)
        else:
            raise TypeError(
                f"Expected str or list as comparison variable, got {type(self.comparison_variables)}"
            )


class EndsWith(ComparisonBaseMethod):
    """
    The 'EndsWith' class is a subclass of the 'ComparisonBaseMethod' class.
    It represents a method for evaluating whether a given input variable ends with a specified comparison variable.

    Attributes:
        comparison_method (Literal["ends_with"]): The method type, which is set to "ends_with".
        input_variable (str): The input variable to be evaluated.
        comparison_variables (Union[str, List[str]]): The comparison variable(s) used for evaluation. It can be either a single string or a list of strings.

    Methods:
        evaluate() -> bool: This method overrides the 'evaluate' method of the 'ComparisonBaseMethod' class. It checks if the input variable ends with the comparison variable(s) and returns a boolean value indicating the result.

    Example usage:
        ends_with_method = EndsWith(input_variable="hello world", comparison_variables=["world", "foo"])
        result = ends_with_method.evaluate()
        print(result)  # Output: True
    """

    comparison_method: Literal["ends_with"] = "ends_with"
    variable: str
    comparison_variables: Union[str, List[str]]

    def evaluate(self) -> bool:
        logger.info(
            f"Checking if {self.variable} ends with {self.comparison_variables}"
        )
        if isinstance(self.comparison_variables, list):
            return any([self.variable.endswith(v)] for v in self.comparison_variables)

        elif isinstance(self.comparison_variables, str):

            return self.variable.endswith(self.comparison_variables)
        else:
            raise TypeError(
                f"Expected str or list as comparison variable, got {type(self.comparison_variables)}"
            )


class ContainsString(ComparisonBaseMethod):
    """
    ContainsString class.

    This class is a subclass of ComparisonBaseMethod and represents a method for evaluating if a string contains another string.

    Attributes:
        comparison_method (Literal["contains_string"]): The method type, which is set to "contains_string".
        input_variable (str): The input string to be evaluated.
        comparison_variables (Union[str, List[str]]): The string or list of strings to compare against the input string.

    Methods:
        evaluate(): Evaluates if the input string contains the comparison string(s) and returns a boolean value.

    Raises:
        TypeError: If the comparison variable is not of type str or list.

    Example:
        contains_string = ContainsString("Hello World", "World")
        result = contains_string.evaluate()
        print(result)  # Output: True
    """

    comparison_method: Literal["contains_string"] = "contains_string"
    variable: str
    comparison_variables: Union[str, List[str]]

    def evaluate(self) -> bool:
        logger.info(f"Checking if {self.variable} contains {self.comparison_variables}")
        if isinstance(self.comparison_variables, list):
            return any(v in self.variable for v in self.comparison_variables)

        elif isinstance(self.comparison_variables, str):
            return self.comparison_variables in self.variable
        else:
            raise TypeError(
                f"Expected str or list as comparison variable, got {type(self.comparison_variables)}"
            )


class MatchPatterns(ComparisonBaseMethod):
    """
    The 'MatchPatterns' class is a subclass of the 'ComparisonBaseMethod' class.
    It represents a method for evaluating whether a given input variable matches a specified pattern.

    Attributes:
        comparison_method (Literal["matches_pattern"]): The method type, which is set to "matches_pattern".
        input_variable (str): The input variable to be evaluated.
        comparison_variables (str): The comparison variable, which represents the pattern to be matched against the input variable.

    Methods:
        evaluate() -> bool: This method evaluates whether the input variable matches the specified pattern. It uses the 're.findall()' function to find all occurrences of the pattern in the input variable. If any matches are found, it returns True; otherwise, it returns False.

    Note:
        The 'MatchPatterns' class inherits the 'comparison_method', 'input_variable', and 'comparison_variables' attributes from the 'ComparisonBaseMethod' class. It also overrides the 'evaluate()' method to provide the specific implementation for pattern matching.

    Example Usage:
        >>> method = MatchPatterns(input_variable="Hello World", comparison_variables="Hello")
        >>> method.evaluate()
        True
    """

    comparison_method: Literal["matches_pattern"] = "matches_pattern"
    variable: str
    comparison_variables: str

    def evaluate(self) -> bool:
        logger.info(f"Checking if {self.variable} matches {self.comparison_variables}")
        pattern = self.comparison_variables
        matches = re.findall(pattern, self.variable)
        return True if matches else False


class Within(ComparisonBaseMethod):
    """
    The 'Within' class is a subclass of the 'ComparisonBaseMethod' class.
    It represents a method for evaluating whether the 'input_variable' is within the 'comparison_variables' list.

    Attributes:
        comparison_method (Literal["within"]): The method type, which is set to "within".
        comparison_variables (List[Any]): A list of values to compare the 'input_variable' against.

    Methods:
        evaluate() -> bool: Evaluates whether the 'input_variable' is within the 'comparison_variables' list and returns a boolean value.

    Note:
        This class inherits the 'comparison_method' and 'input_variable' attributes from the 'ComparisonBaseMethod' class.

    Example:
        within_method = Within(comparison_method="within", input_variable=5, comparison_variables=[1, 2, 3, 4, 5])
        result = within_method.evaluate()
        print(result)  # Output: True
    """

    comparison_method: Literal["within"] = "within"
    comparison_variables: Union[List[Any], str]

    def evaluate(self) -> bool:
        logger.info(f"Checking if {self.variable} in {self.comparison_variables}")
        return self.variable in self.comparison_variables


class NotIn(ComparisonBaseMethod):
    """
    The 'NotIn' class is a subclass of the 'ComparisonBaseMethod' class. It represents a method for evaluating whether a given input variable is not present in a comparison variable.

    Attributes:
    - comparison_method (Literal["not_in"]): The method type, which is set to "not_in".
    - comparison_variables (List[Any]): The comparison variable, which is a list of any type.

    Methods:
    - evaluate() -> bool: This method overrides the 'evaluate' method of the 'ComparisonBaseMethod' class. It returns True if the input variable is not present in the comparison variable, and False otherwise.
    Note:
        This class inherits the 'comparison_method' and 'input_variable' attributes from the 'ComparisonBaseMethod' class.

    Example:
        within_method = Within(comparison_method="within", input_variable=6, comparison_variables=[1, 2, 3, 4, 5])
        result = within_method.evaluate()
        print(result)  # Output: True
    """

    comparison_method: Literal["not_in"] = "not_in"
    comparison_variables: Union[List[Any], str]

    def evaluate(self) -> bool:
        logger.info(f"Checking if {self.variable} not in {self.comparison_variables}")
        return self.variable not in self.comparison_variables
