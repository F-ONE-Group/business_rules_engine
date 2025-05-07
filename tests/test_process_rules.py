import os
import pytest

from rules_engine import RulesEngine


TEST_RULES_PATH = os.path.join(os.getcwd(), "tests", "test_rules")


@pytest.fixture
def all_rules_path():
    return os.path.join(TEST_RULES_PATH, "test_all_rules.yml")


@pytest.fixture
def groups_rules_path():
    return os.path.join(TEST_RULES_PATH, "test_groups.yml")


@pytest.fixture
def global_group_rules_path():
    return os.path.join(TEST_RULES_PATH, "test_global_rules.yml")


@pytest.fixture
def all_variables_rules_path():
    return os.path.join(TEST_RULES_PATH, "test_rule_all_variables.yml")


@pytest.fixture
def logic_operator_rules_path():
    return os.path.join(TEST_RULES_PATH, "test_logic_operator.yml")


@pytest.fixture
def ext_data_rules_path():
    return os.path.join(TEST_RULES_PATH, "test_ext_source.yml")


@pytest.fixture
def ext_data_rules_path_fail():
    return os.path.join(TEST_RULES_PATH, "test_ext_source_fail.yml")


@pytest.fixture
def format_rules_path():
    return os.path.join(TEST_RULES_PATH, "test_format.yml")


@pytest.fixture()
def process_variables():
    from .process_variables import test

    return test


def test_process_rules(all_rules_path, process_variables):
    process_variables.pop("result", None)
    process_variables.pop("test_status", None)
    rules_engine = RulesEngine(
        rules_definition_path=all_rules_path, process_variables=process_variables
    )
    vars_output = rules_engine.process_rules()
    for result in vars_output["result"]:
        assert "NOK" not in result
    assert vars_output["test_status"] == True


def test_groups_rules(groups_rules_path, process_variables):
    process_variables.pop("result", None)
    process_variables.pop("test_status", None)
    rules_engine = RulesEngine(
        rules_definition_path=groups_rules_path, process_variables=process_variables
    )
    vars_output = rules_engine.process_rules()
    for result in vars_output["result"]:
        assert "NOK" not in result
    assert vars_output["test_status"] == True


def test_group_global_rules(global_group_rules_path, process_variables):
    process_variables.pop("result", None)
    process_variables.pop("test_status", None)
    rules_engine = RulesEngine(
        rules_definition_path=global_group_rules_path,
        process_variables=process_variables,
    )
    vars_output = rules_engine.process_rules()
    for result in vars_output["result"]:
        assert "NOK" not in result
    assert vars_output["test_status"] == True


def test_rule_all_variables(all_variables_rules_path, process_variables):
    process_variables.pop("result", None)
    process_variables.pop("test_status", None)

    rules_engine = RulesEngine(
        rules_definition_path=all_variables_rules_path,
        process_variables=process_variables,
    )
    vars_output = rules_engine.process_rules()
    assert vars_output["result"] == "2"


def test_logical_operator_rules(logic_operator_rules_path, process_variables):
    process_variables.pop("result", None)
    process_variables.pop("test_status", None)
    rules_engine = RulesEngine(
        rules_definition_path=logic_operator_rules_path,
        process_variables=process_variables,
    )
    vars_output = rules_engine.process_rules()
    for result in vars_output["result"]:
        assert "NOK" not in result
    assert vars_output["test_status"] == True


def test_ext_data_rules(ext_data_rules_path, process_variables):
    process_variables.pop("result", None)
    process_variables.pop("test_status", None)
    rules_engine = RulesEngine(
        rules_definition_path=ext_data_rules_path, process_variables=process_variables
    )
    vars_output = rules_engine.process_rules()
    for result in vars_output["result"]:
        assert "NOK" not in result
    assert vars_output["test_status"] == True


def test_ext_data_rules_fail(ext_data_rules_path_fail, process_variables):
    process_variables.pop("result", None)
    process_variables.pop("test_status", None)
    rules_engine = RulesEngine(
        rules_definition_path=ext_data_rules_path_fail,
        process_variables=process_variables,
    )
    vars_output = rules_engine.process_rules()
    assert vars_output["test_status"] == False
    assert "[NOK] test ext_data_1" in vars_output["result"]
