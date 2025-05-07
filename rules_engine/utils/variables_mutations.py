import re
from typing import Any, Dict, List, Tuple, Union

from pydantic import BaseModel


def parse_mutation_key_value(mutation_key: str, variable_mutation: str):
    mutation_keys: List[str] = mutation_key.split(".")

    parsed_mutation = {}
    current_idx = 0
    for idx, m in enumerate(mutation_keys):
        if idx < len(mutation_keys) - 1:
            next_idx = variable_mutation.find(mutation_keys[idx + 1])
            parsed_mutation[m] = f"{variable_mutation[current_idx:next_idx -1]}"
            current_idx = next_idx
        else:
            parsed_mutation[m] = f"{variable_mutation[current_idx:]}"

    return parsed_mutation


def transform_variable_for_dict(variable: str) -> str:
    match = re.fullmatch(r"(?P<name>\w+)(?:\[(?P<index>\d+)\])?", variable)

    if not match:
        raise ValueError(f"Invalid input format: {variable}")

    var_name = match.group("name")
    index = match.group("index")

    return f"['{var_name}']{f'[{index}]' if index else ''}"


def _get_eval_string(
    process_variables: Union[Dict, BaseModel],
    variable: str,
    eval_string: str,
):
    if isinstance(process_variables, dict):
        new_eval_string = eval_string + transform_variable_for_dict(variable)
    else:
        new_eval_string = eval_string + f".{variable}"
    return new_eval_string


def _compute_mutations(
    process_variables: Union[Dict, BaseModel],
    variable_tree: List[str],
    eval_string: str = None,
    external_data_vars: List[str] = [],
) -> Dict:
    mutations: Dict = {}
    if not eval_string:
        eval_string = "process_variables"

    var = variable_tree.pop(0)
    if not variable_tree or var in external_data_vars:
        # it is the last element. The eval is not required
        mutations.update({var: None})
    else:
        eval_string = _get_eval_string(process_variables, var, eval_string)
        var_value = eval(eval_string)
        if isinstance(var_value, dict):
            mutations.update(
                {
                    var: _compute_mutations(
                        process_variables,
                        variable_tree,
                        eval_string,
                    )
                }
            )
        elif isinstance(var_value, list):
            var_value_len = len(var_value)
            for idx in range(var_value_len):
                list_eval_string = eval_string + f"[{idx}]"
                mutations.update(
                    {
                        f"{var}.{idx}": _compute_mutations(
                            process_variables,
                            variable_tree.copy(),
                            list_eval_string,
                            external_data_vars,
                        )
                    }
                )
        else:
            mutations.update({var: None})

    return mutations


def _stringify_mutations(mutations: Dict):
    stringified_mutations = []
    for key, value in mutations.items():
        tmp = key
        if value is not None:
            tmps = _stringify_mutations(value)
            for t in tmps:
                if t:
                    stringified_mutations.append(tmp + f".{t}")
                else:
                    stringified_mutations.append(tmp)
        else:
            stringified_mutations.append(value)

    return stringified_mutations


def get_variables_mutations(
    process_variables: Union[Dict, BaseModel],
    variable_tree: List[str],
    external_data_vars: List[str] = [],
):
    mutations = _compute_mutations(
        process_variables, variable_tree, external_data_vars=external_data_vars
    )
    return _stringify_mutations(mutations)


def generate_permutations(data: Dict[str, Tuple[List[str], str]]) -> List[Tuple[Any]]:
    keys = list(data.keys())
    value_lists = [values[0] if values[0] else [None] for values in data.values()]
    parent_values = [values[1] if values[1] else None for values in data.values()]

    max_length = max(len(lst) for lst in value_lists)

    permutations = []
    for i in range(max_length):
        row = tuple(
            (key, value_lists[j][i % len(value_lists[j])], parent_values[j])
            for j, key in enumerate(keys)
        )
        permutations.append(row)

    return permutations


def get_permutations(mutations: Dict):
    sorted_mutations = dict(
        sorted(
            mutations.items(),
            key=lambda item: len(item[1][1].split(".")),
            reverse=True,
        )
    )

    return generate_permutations(sorted_mutations)
