import logging
import re
import yaml
import pandas as pd
from typing import Any, Dict, List, Tuple, Union

from pydantic import BaseModel
from dataclasses import dataclass, field

from .exceptions import ParsingRuleException
from .get_external_source import ExternalSourceTypes, get_ext_source
from .models import RulesDefinition, Rule, Comparison, Condition, Transformation
from .utils.variables_mutations import (
    get_permutations,
    get_variables_mutations,
    parse_mutation_key_value,
)

logger = logging.getLogger("bre.v3")
logger.setLevel("DEBUG")


@dataclass
class RulesEngine:
    process_variables: Union[Dict, BaseModel]
    rules_definition_path: str = field(default="")
    rules: Dict = field(default_factory=dict)
    rules_definition: RulesDefinition = field(
        default_factory=lambda: RulesDefinition(rules={})
    )
    parsed_rules: Dict[str, Rule] = field(default_factory=dict)
    ext_data_variables: Dict[str, pd.DataFrame] = field(default_factory=dict)
    ext_data_variables_name: List[str] = field(default_factory=list)

    def __post_init__(self):
        self._parse_rules_definition()
        self._create_external_data_variable()
        self._parse_rules()

    def _parse_rules_definition(self):
        if not self.rules_definition_path and not self.rules:
            raise ValueError(
                "One of `rules_definition_path` and `rules` has to be provided."
            )
        if self.rules:
            self.rules_definition = RulesDefinition(**self.rules)
        else:
            with open(self.rules_definition_path, "r", encoding="utf-8") as f:
                rules_dict = yaml.load(f, yaml.Loader)
                self.rules_definition: RulesDefinition = RulesDefinition(**rules_dict)

    def _create_external_data_variable(self):
        for key, value in self.rules_definition.external_data.items():
            ext_source: ExternalSourceTypes = get_ext_source(value)
            self.ext_data_variables_name.append(key)
            self.ext_data_variables.update({key: ext_source.get_data()})

    def _is_ext_data_variable(self, variable: str):
        return variable in self.ext_data_variables_name

    def _get_variable_value_2(self, variable: Any):
        if isinstance(variable, str):
            pass
        elif isinstance(variable, list):
            pass
        return variable

    def _clean_variable(self, v: str):
        pattern = r"^\$\{(?P<variable>(\w+(?:\.\w+|\[\d+\])*)*)\}$"
        matches = re.match(pattern, v)
        if not matches:
            return None
        return matches["variable"]

    def _parse_transformation(
        self,
        transformation_dict: Dict,
        variable_mutation: str = None,
        mutation_key: str = None,
    ) -> Transformation:
        ### comparison will have the following structure
        #   var_1:
        #     transformation_method:
        #       - param # only one parameter
        #
        for k, v in transformation_dict.items():
            input_variable: str = k
            transformation_method: str = list(v.keys())[0]
            target_value: str = transformation_dict[k][list(v.keys())[0]][0]

            if variable_mutation and mutation_key:
                parsed_mutation = parse_mutation_key_value(
                    mutation_key, variable_mutation
                )
                for k, v in parsed_mutation.items():
                    input_variable = input_variable.replace(k, v)
                    if isinstance(target_value, str):
                        target_value = target_value.replace(k, v)
        transformation = Transformation(
            transformation_method=transformation_method,
            variable=self._clean_variable(input_variable),
            target_value=target_value,
        )
        return transformation

    def _parse_comparison(
        self,
        comparison_dict: Dict[str, Dict],
        variable_mutation: str = None,
        mutation_key: str = None,
    ) -> Comparison:
        ### comparison will have the following structure
        #   var_1:
        #     comparison_method:
        #       - params 1
        #       - params 2
        #       - etc
        #

        for k, v in comparison_dict.items():
            input_variable: str = k
            comparison_method: str = list(v.keys())[0]
            # if isinstance()
            comparison_variables = comparison_dict[k][list(v.keys())[0]]

            if variable_mutation and mutation_key:
                parsed_mutation = parse_mutation_key_value(
                    mutation_key, variable_mutation
                )
                for k, v in parsed_mutation.items():
                    input_variable = input_variable.replace(k, v)
                    for x in comparison_variables:
                        if isinstance(x, str):
                            x = x.replace(k, v)

        if isinstance(comparison_variables, str):
            comparison_variables = [comparison_variables]

        # eval_variable = self._clean_variable_with_eval(input_variable)

        comparison = Comparison(
            comparison_method=comparison_method,
            variable=input_variable,
            comparison_variables=comparison_variables,
        )
        return comparison

    def _get_variables_mutations(self, variable) -> Tuple[List[str], str]:
        cleaned_variable = self._clean_variable(variable)
        if cleaned_variable:
            variable_tree = cleaned_variable.split(".")
            mutations: List[str] = get_variables_mutations(
                self.process_variables,
                variable_tree,
                list(self.ext_data_variables.keys()),
            )
            return mutations, ".".join(cleaned_variable.split(".")[:-1])
        else:
            return [], ""

    def _get_variables_mutations_map(self, variables: List[str]) -> Dict:
        mutation_map = {}
        for variable in variables:
            variables_mutation, mutation_key = self._get_variables_mutations(variable)
            if mutation_key:
                mutation_map[variable] = (
                    variables_mutation,
                    mutation_key,
                )
            else:
                mutation_map[variable] = ([], "")
        return mutation_map

    def _parse_rules(self):
        for rule_name, rule_def in self.rules_definition.rules.items():
            group_name: str = None
            for group_name_, rules in self.rules_definition.groups.items():
                if rule_name in rules:
                    group_name = group_name_
                    break
            if not group_name:
                raise ValueError(
                    f"The rule `{rule_name}` does not belong to any group."
                )
            if "if" in rule_def.keys():
                logical_operator = None
                rule_comparisons: Dict = rule_def["if"]
                rule_transformations: Dict = rule_comparisons.pop(
                    "then", rule_def.pop("then", None)
                )
                if not rule_transformations:
                    raise ValueError(
                        f"`then` key is not present in the rule {rule_name}"
                    )
                # else
                else_transformations: Dict = rule_def.pop(
                    "else", rule_comparisons.pop("else", {})
                )

                if list(rule_comparisons.keys())[0] in ("and", "or"):
                    # we will have only one key and that key is the logical_operator
                    logical_operator = list(rule_comparisons.keys())[0]
                    rule_comparisons = rule_comparisons[logical_operator]
                assert isinstance(rule_comparisons, dict)

                # Check for rules mutations
                comp_variables = rule_comparisons.keys()
                trans_variables = rule_transformations.keys()
                else_variables = else_transformations.keys()
                comp_mutations_map = self._get_variables_mutations_map(comp_variables)
                trans_mutations_map = self._get_variables_mutations_map(trans_variables)
                else_mutations_map = self._get_variables_mutations_map(else_variables)

                # compute permutations from the comparison mutations
                # each permutation should correspond to a rule
                comps_permutations = get_permutations(comp_mutations_map)
                for idx, permutation in enumerate(comps_permutations):
                    logger.info(f"Creating rule from permutation: {rule_name}-{idx}")
                    mutations_applied = []
                    condition: Condition = Condition(
                        logical_operator=logical_operator,
                        comparisons=[],
                        then=[],
                    )
                    for variable, mutation, mutation_key in permutation:
                        logger.info(
                            f"Addition condition for {variable} -> {mutation if mutation else variable}"
                        )
                        comparison = self._parse_comparison(
                            {variable: rule_comparisons[variable]},
                            mutation,
                            mutation_key,
                        )
                        condition.comparisons.append(comparison)
                        if mutation_key:
                            mutations_applied.append(mutation)
                    for k, v in rule_transformations.items():
                        trans_variables_mutation, trans_mutation_key = (
                            trans_mutations_map[k]
                        )
                        if mutations_applied:
                            trans_variables_mutation_ = []
                            for mutation in mutations_applied:
                                for x in trans_variables_mutation:
                                    if (
                                        mutation in x or x in mutation
                                    ) and x not in trans_variables_mutation_:
                                        trans_variables_mutation_.append(x)

                            transformation = {k: v}
                            for m in trans_variables_mutation_:
                                logger.info(f"Addition then condition {k} -> {m}")
                                condition.then.append(
                                    self._parse_transformation(
                                        transformation,
                                        m,
                                        trans_mutation_key,
                                    )
                                )
                        else:
                            for variable in trans_variables:
                                transformation = {
                                    variable: rule_transformations[variable]
                                }
                                trans_variable_mutations = trans_mutations_map.get(k)
                                if (
                                    trans_variable_mutations
                                    and trans_variable_mutations[0]
                                    and trans_variable_mutations[1]
                                ):
                                    mutations: List[str] = trans_variable_mutations[0]
                                    mutation_key: str = trans_variable_mutations[1]
                                    for m in mutations:
                                        logger.info(
                                            f"Addition then condition {k} -> {m}"
                                        )
                                        condition.then.append(
                                            self._parse_transformation(
                                                transformation,
                                                m,
                                                mutation_key,
                                            )
                                        )
                                else:
                                    logger.info(f"No mutation to be applied")
                                    condition.then.append(
                                        self._parse_transformation(transformation)
                                    )

                    # define the rule
                    assert len(condition.comparisons) == len(comp_variables)
                    rule_tmp = Rule(description=rule_def.get("description"))
                    rule_tmp.if_condition = condition

                    # parse else only the if condition is available
                    if else_transformations:
                        for k, v in else_transformations.items():
                            else_variables_mutation, else_mutation_key = (
                                else_mutations_map[k]
                            )
                            if mutations_applied:
                                else_variables_mutation_ = []
                                for mutation in mutations_applied:
                                    for x in else_variables_mutation:
                                        if (
                                            mutation in x
                                            and x not in else_variables_mutation_
                                        ):
                                            else_variables_mutation_.append(x)

                                transformation = {k: v}
                                for m in else_variables_mutation_:
                                    logger.info(f"Addition else condition {k} -> {m}")
                                    rule_tmp.else_transformations.append(
                                        self._parse_transformation(
                                            transformation,
                                            m,
                                            else_mutation_key,
                                        )
                                    )
                            else:
                                for variable in else_variables:
                                    transformation = {
                                        variable: else_transformations[variable]
                                    }
                                    else_variable_mutations = else_mutations_map.get(k)
                                    if (
                                        else_variable_mutations
                                        and else_variable_mutations[0]
                                        and else_variable_mutations[1]
                                    ):
                                        mutations: List[str] = else_variable_mutations[
                                            0
                                        ]
                                        mutation_key: str = else_variable_mutations[1]
                                        for m in mutations:
                                            logger.info(
                                                f"Addition else condition {k} -> {m}"
                                            )
                                            rule_tmp.else_transformations.append(
                                                self._parse_transformation(
                                                    transformation,
                                                    m,
                                                    mutation_key,
                                                )
                                            )
                                    else:
                                        rule_tmp.else_transformations.append(
                                            self._parse_transformation(transformation)
                                        )

                    if mutations_applied:
                        new_rule_name: str = f"{rule_name}-{idx}"
                        self.parsed_rules[new_rule_name] = rule_tmp
                        # add new rule name to the correct group
                        self.rules_definition.groups[group_name].append(new_rule_name)
                        # remove the old one
                        if rule_name in self.rules_definition.groups[group_name]:
                            self.rules_definition.groups[group_name].pop(
                                self.rules_definition.groups[group_name].index(
                                    rule_name
                                )
                            )
                    else:
                        self.parsed_rules[rule_name] = rule_tmp
            else:
                raise ParsingRuleException(
                    f"Error in [{rule_name}] rule: cannot define else without if condition"
                )

    def process_rules(self):
        rule_name = None
        for group_name, rules in self.rules_definition.groups.items():
            logger.info(f"Processing '{group_name}' group")
            for rule_name in rules:
                logger.info(f"Processing '{rule_name}' rule")
                rule: Rule = self.parsed_rules[rule_name]
                if rule.if_condition:
                    # evaluate if condition
                    if rule.if_condition.evaluate(self):
                        # all the rules have been satisfied
                        logger.info("Rule's conditions satisfied")
                        # apply transformation
                        logger.info("Applying then transformations")
                        for transf in rule.if_condition.then:
                            transf.apply(self)
                        ## First hit policy
                        if group_name != "no_group_rules" or (
                            group_name == "no_group_rules"
                            and rule_name in self.rules_definition.global_rules
                        ):
                            break
                    else:
                        logger.info("Rule's conditions not satisfied")
                        if rule.else_transformations:
                            logger.info("Applying else transformations")
                            for transf in rule.else_transformations:
                                transf.apply(self)
                else:
                    logger.info("Applying transformations")
                    # run transformations
                    for transf in rule.transformations:
                        transf.apply(self)
            if rule_name in self.rules_definition.global_rules:
                logger.info(f"Global rule '{rule}' satisfied.")
                break

        logger.info("Engine has processed the business rules.")
        return self.process_variables
