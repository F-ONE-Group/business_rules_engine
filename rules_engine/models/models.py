import re
import datetime  # noqa: F401 required for the eval


from typing import Any, Dict, List, Literal, Optional, Self, Union

from pydantic import BaseModel, Field, model_validator

from ..exceptions import ParsingRuleException
from ..utils.transformation import parse_transformation_method, TransformationMethod
from ..utils.comparison import parse_comparison_method, ComparisonMethod


def transform_variable_for_dict(variable: str) -> str:
    match = re.fullmatch(r"(?P<name>\w+)(?:\[(?P<index>\d+)\])?", variable)

    if not match:
        raise ValueError(f"Invalid input format: {variable}")

    var_name = match.group("name")
    index = match.group("index")

    return f"['{var_name}']{f'[{index}]' if index else ''}"


def evaluate_variable(variable: Any):
    eval_var = variable
    # ensure the value is not numeric
    if isinstance(eval_var, str) and eval_var.isnumeric():
        return eval_var
    try:
        eval_var = eval(f"{variable}")
    except NameError:
        pass
    except SyntaxError:
        pass
    return eval_var


def _evaluate_value(
    engine,
    v: str,
    to_filter: bool = False,
    filter_value: Union[Any, None] = None,
    method: Union[str, None] = None,
):
    var_split = v.split(".")
    ext_var_name = var_split[0]
    if engine._is_ext_data_variable(ext_var_name):
        ext_var_col = var_split[1]
        if method in ("equal_to", "within") and to_filter:
            filter = (
                engine.ext_data_variables[ext_var_name][ext_var_col] == filter_value
            )
            engine.ext_data_variables[ext_var_name] = engine.ext_data_variables[
                ext_var_name
            ][filter]
            eval_string = (
                v.replace(ext_var_name, f"engine.ext_data_variables['{ext_var_name}']")
                + ".tolist()"
            )
        elif method in ("not_equal_to", "not_in") and to_filter:
            filter = (
                engine.ext_data_variables[ext_var_name][ext_var_col] == filter_value
            )
            engine.ext_data_variables[ext_var_name] = engine.ext_data_variables[
                ext_var_name
            ][filter]
            eval_string = (
                v.replace(ext_var_name, f"engine.ext_data_variables['{ext_var_name}']")
                + ".tolist()"
            )
        else:
            # the ext_data variable has been already filtered and we need to fetch the value
            if not engine.ext_data_variables[ext_var_name].empty:
                eval_string = (
                    v.replace(
                        ext_var_name, f"engine.ext_data_variables['{ext_var_name}']"
                    )
                    + ".values[0]"
                )
            else:
                eval_string = "None"
    else:
        if isinstance(engine.process_variables, dict):
            # split variables by dot
            v_: str = ""
            for vv in v.split("."):
                if vv.isnumeric():
                    v_ += f"[{vv}]"
                else:
                    v_ += transform_variable_for_dict(vv)

            # v = "".join([f"['{vv}']" for vv in v.split(".")])
            eval_string = f"engine.process_variables{v_}"
        else:
            v_: List[str] = []
            for vv in v.split("."):
                if vv.isnumeric():
                    v_.append(f"[{vv}]")
                else:
                    v_.append(vv)
            eval_string = f"engine.process_variables.{'.'.join(v_)}"
    return eval_string


def _clean_variable_with_eval(
    engine,
    v: Any,
    to_filter: bool = False,
    filter_value: Union[Any, None] = None,
    method: Union[str, None] = None,
):
    if isinstance(v, str):
        final_eval_string = v
        while True:
            pattern = r"^\$\{(?P<variable>(\w+(?:\.\w+|\[\d+\])*)*)\}$"  # r"\$\{(?P<variable>(\w*\.?\w*)*)\}"
            matches = re.search(pattern, final_eval_string)
            if not matches:
                pattern = r"\$\{(?P<variable>(\w*\.?\w*)*)\}"
                matches = re.search(pattern, final_eval_string)
                if not matches:
                    break
            v_eval_str = _evaluate_value(
                engine, matches["variable"], to_filter, filter_value, method
            )
            final_eval_string = final_eval_string.replace(matches.group(), v_eval_str)
        if final_eval_string == v:
            # no modification done return v
            return evaluate_variable(final_eval_string)
        else:
            return eval(final_eval_string)
    return v


class RulesDefinition(BaseModel):
    rules: Dict[str, Dict]
    groups: Dict = Field(default_factory=dict)
    external_data: Dict = Field(default_factory=dict)
    global_rules: List = Field(default_factory=list)
    no_group_rules: List = Field(default_factory=list)
    rules_in_group: List = Field(default_factory=list)
    parsed_rules: Dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_rules_definition(self: Self) -> Self:
        self.global_rules = self.groups.pop("global", [])

        for group_name, group_rules in self.groups.items():
            for rule in group_rules:
                if rule not in self.rules:
                    raise ValueError(
                        f"The rule [{rule}] defined in [{group_name}] cannot be found"
                    )
                self.rules_in_group.append(rule)

        for rule in self.rules:
            if rule not in self.rules_in_group:
                self.no_group_rules.append(rule)

        self.groups["no_group_rules"] = self.no_group_rules

        return self


class Comparison(BaseModel):
    comparison_method: str
    variable: Any
    comparison_variables: Union[Any, List[Any]]

    @model_validator(mode="after")
    def val_comparison_variables(self: Self) -> Self:
        if (
            isinstance(self.comparison_variables, list)
            and len(self.comparison_variables) == 1
        ):
            self.comparison_variables = self.comparison_variables[0]
        return self

    def evaluate_comparison_variables(self, engine):
        if isinstance(self.comparison_variables, list):
            eval_comp_vars: List[Any] = []
            for comparison_variable in self.comparison_variables:
                comparison_variable = _clean_variable_with_eval(
                    engine,
                    comparison_variable,
                    True,
                    self.variable,
                    self.comparison_method,
                )
                eval_comp_var = evaluate_variable(comparison_variable)
                eval_comp_vars.append(eval_comp_var)
            self.comparison_variables = eval_comp_vars
        else:
            self.comparison_variables = _clean_variable_with_eval(
                engine,
                self.comparison_variables,
                True,
                self.variable,
                self.comparison_method,
            )
            self.comparison_variables = evaluate_variable(self.comparison_variables)

    def evaluate(self, engine) -> bool:
        self.variable = _clean_variable_with_eval(engine, self.variable)
        # evaluate for each of the comparison variable
        self.evaluate_comparison_variables(engine)
        # self.variable = evaluate_variable(self.variable)
        method: ComparisonMethod = parse_comparison_method(self.dict())
        return method.evaluate()


class Transformation(BaseModel):
    transformation_method: str
    variable: Any
    target_value: Any

    def apply(self, engine):
        self.target_value = _clean_variable_with_eval(engine, self.target_value)
        # self.variable = evaluate_variable(self.variable)
        method: TransformationMethod = parse_transformation_method(self.dict())
        if isinstance(engine.process_variables, BaseModel):
            res = method.apply(engine.process_variables.dict())
            engine.process_variables = engine.process_variables.__class__(**res)
        else:
            engine.process_variables = method.apply(engine.process_variables)


class Condition(BaseModel):
    logical_operator: Optional[Literal["and", "or"]]
    then: List[Transformation]
    comparisons: List[Comparison] = []

    @model_validator(mode="after")
    def validate_logical_operator(self: Self) -> Self:
        if len(self.comparisons) > 1 and self.logical_operator is None:
            raise ParsingRuleException(
                "Multiple comparisons without 'and' or 'or' are not allowed."
            )
        return self

    def evaluate(self, engine) -> bool:
        # evaluate the condition
        # comparisons_result = [comparison.evaluate() for comparison in self.comparisons]
        # multiple conditions are allowed only with logical operators
        if self.logical_operator == "or":
            for comparison in self.comparisons:
                result = comparison.evaluate(engine)
                if result:
                    return True
            return False
            # return any(comparisons_result)
        elif self.logical_operator == "and":
            for comparison in self.comparisons:
                result = comparison.evaluate(engine)
                if not result:
                    return False
            return True
            # return all(comparisons_result)
        else:
            # there is only one comparison condition
            return self.comparisons[0].evaluate(engine)


class Rule(BaseModel):
    description: Optional[str] = None
    if_condition: Optional[Condition] = None
    transformations: Optional[List[Transformation]] = Field(default_factory=list)
    else_transformations: Optional[List[Transformation]] = Field(default_factory=list)
