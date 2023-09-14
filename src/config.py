from os import environ
from ast import literal_eval

# TOOD: now it doesn't support native strings...
def get(name, default):
    """Returns container configuration value if defined. Otherwise, returns passed default value"""
    assert isinstance(name, str), "config: name should be of type str"
    # attempt to cast environment value to type of default parameter
    env_value = environ.get(name.upper())
    if env_value:
        env_value = literal_eval(env_value)

    return env_value or default
