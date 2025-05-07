import pytest
from rules_engine.utils.variables_mutations import get_variables_mutations


@pytest.fixture
def test_process_variables():
    return {
        "var1": "test",
        "var2": {
            "var21": "test",
            "var22": [
                {"var221": "test"},
                {"var221": "test"},
            ],
        },
    }


@pytest.mark.parametrize(
    ("process_variables,target_var,expected_mutations"),
    [
        (
            {
                "var1": "test",
                "var2": {
                    "var21": "test",
                    "var22": [
                        {"var221": "test"},
                        {"var221": "test"},
                    ],
                },
            },
            "var2.var22.var221",
            [
                "var2.var22.0",
                "var2.var22.1",
            ],
        ),
        (
            {
                "var1": "test",
                "var2": {
                    "var21": "test",
                    "var22": [
                        {"var221": "test"},
                        {"var221": "test"},
                    ],
                },
            },
            "var1",
            [None],
        ),
        (
            {
                "var1": "test",
                "var2": {
                    "var21": "test",
                    "var22": [
                        {
                            "var221": [
                                {"var2211": "test"},
                                {"var2211": "test"},
                                {"var2211": "test"},
                            ]
                        },
                        {"var221": [{"var2211": "test"}]},
                    ],
                },
            },
            "var2.var22.var221.var2211",
            [
                "var2.var22.0.var221.0",
                "var2.var22.0.var221.1",
                "var2.var22.0.var221.2",
                "var2.var22.1.var221.0",
            ],
        ),
    ],
)
def test_variable_mutations(process_variables, target_var, expected_mutations):
    variable_tree = target_var.split(".")
    mutations = get_variables_mutations(process_variables, variable_tree)
    assert mutations == expected_mutations
