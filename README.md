# Business Rules Engine

A Python package for creating and managing business rules.

## Installation

Install via pip:

```bash
pip install business-rules-engine
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/F-ONE-Group/business_rules_engine.git
```

## Usage

### Importing the RuleEngine

```python
from rules_engine.rules_engine import RulesEngine
```

### Initializing the RuleEngine

Create an instance of the `RulesEngine` class:

```python
engine = RulesEngine()
```

### Public Methods

#### 1. `process_rules`

Processes the loaded rules and applies transformations based on the conditions defined in the rules. This method evaluates the rules and modifies the `process_variables` attribute accordingly.

```python
engine.process_rules()
```

### Creating a Rule YAML File

To create a rule YAML file for the Business Rules Engine, follow the structure below. This format allows you to define rules with conditions and actions.

#### Basic Structure

A rule YAML file consists of a `rules` section, where each rule is defined with a name, conditions, and actions. Here's an example:

```yaml
rules:
  rule_name:
    if:
      ${variable_name}:
        condition_type:
          - condition_value
    then:
      ${result_variable}:
        action_type:
          - action_value
    else:
      ${result_variable}:
        action_type:
          - alternative_action_value
```

#### Example Rule

Below is an example of a rule that checks if a string variable is empty and appends a result based on the condition:

```yaml
rules:
  check_empty_string:
    if:
      ${string_variable}:
        is_empty:
          - true
    then:
      ${result}:
        append:
          - "[OK] String is empty"
    else:
      ${result}:
        append:
          - "[NOK] String is not empty"
```

#### Explanation of Components

- **`if`**: Defines the condition to evaluate. For example, `is_empty` checks if a variable is empty.
- **`then`**: Specifies the actions to perform if the condition is true. For example, `append` adds a message to a result list.
- **`else`**: Specifies the actions to perform if the condition is false.

#### Supported Conditions and Actions

- **Conditions**: `is_empty`, `less_than`, `greater_than`, `equal_to`, `not_equal_to`, `starts_with`, `ends_with`, `contains_string`, `within`, `not_in`, `matches_pattern`.
- **Actions**: `append`, `set`, and more depending on your use case.

#### Creating a YAML File

1. Create a new `.yml` file in your project directory.
2. Use the structure and examples above to define your rules.
3. Save the file and load it into the `RuleEngine` using the `load_rules` method:

```python
engine.load_rules("path/to/your_rules.yml")
```

This will allow the engine to evaluate the rules against your variables.

### Example Workflow

1. Load rules from a YAML file.
2. Process the rules to evaluate conditions and apply transformations.

```python
import os
from rules_engine import RulesEngine

# define the absolute path to the rules definition file
rules_definition_path = os.path.join(os.getcwd(), "test_rule.yaml")

# Initialize the engine
engine = RulesEngine(
    process_variables={"string_variable": ""},
    rules_definition_path=rules_definition_path,
)

# Process rules
engine.process_rules()

# Access the modified variables
print("Processed Variables:", engine.process_variables)

```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
