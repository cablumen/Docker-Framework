from os import environ
from ast import literal_eval

def get(name, default):
    """Returns container configuration value if defined. Otherwise, returns passed default value"""
    assert isinstance(name, str), "config: name should be of type str"

    # attempt to cast environment value to type of default parameter
    env_value = environ.get(name.upper())
    if env_value:
        try:
            env_value = literal_eval(env_value)
        except SyntaxError:
            # catch string literals
            pass
        except Exception:
            print("Error: unable to delete docker image.")
            raise

    return env_value or default
