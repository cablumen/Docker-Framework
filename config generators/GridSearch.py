import json
import os
import itertools
from math import ceil
import uuid


# input: a json input_config
# output: a list of dict ranges for each (key, value) pair in the default_config
def get_config_ranges(input_config):
    output = {}

    if type(input_config) is dict:
        for key, value in input_config.items():
            if isinstance(value, list):
                # if config is tuple, get range of values
                output[key] = range_to_list(*value)

            elif isinstance(value, str) or not hasattr(value, "__iter__"):
                # if config is not iterable, add static value
                output[key] = [value]

            else:
                # if config is iterable, recurse
                config_range = to_underscore_notation(key, get_config_ranges(value))
                output.update(config_range)

    return output

def to_underscore_notation(namespace, input_config):
    output_config = {}
    for key, value in input_config.items():
        output_config[namespace + "_" + key] = value

    return output_config

def range_to_list(start, end, step):
    # determine number of steps between start and end
    range_count = ceil(abs(end - start) / step) + 1

    # flip step if end is lower than start
    if end < start and step > 0:
        step = -1 * step

    range_list = list(itertools.islice(itertools.count(start, step), range_count))

    # fix rounding errors
    round_digits = max(len(str(start)), len(str(step)))
    return [round(x, round_digits) for x in range_list]


def print_config_dict(write_file, config_dict):
    config_names = list(config_dict.keys())
    config_ranges = list(config_dict.values())

    config_product = list(itertools.product(*config_ranges))
    config_length = len(config_product)

    write_file.write("[\n")
    for run_index, run_config in enumerate(config_product):
        write_file.write("\t{\n")
        config_hash = uuid.uuid5(uuid.NAMESPACE_OID, str(run_config))
        write_file.write("\t\t\"HASH\": \"" + str(config_hash) + "\",\n")
        run_config_length = len(run_config)
        for config_index, config_value in enumerate(run_config):
            config_name = config_names[config_index]
            print_config(write_file, config_name, config_value)
            print_line_end(write_file, config_index, run_config_length)

        write_file.write("\t}")
        print_line_end(write_file, run_index, config_length)

    write_file.write("]\n")
    print("Wrote " + str(config_length) + " configs to run_config.json")

def print_config(write_file, config_name, config_value):
    write_line = "\t\t\"" + config_name.upper() + "\": "
    if isinstance(config_value, str):
        write_line += "\"" + config_value + "\""

    elif isinstance(config_value, bool):
        write_line += str(config_value).lower()

    else:
        write_line += str(config_value)

    write_file.write(write_line)

def print_line_end(write_file, index, iter_length):
    if index != iter_length - 1:
        write_file.write(",")
    write_file.write("\n")

os.chdir(os.path.dirname(__file__))

default_config_path = None
for root, dirs, files in os.walk("../src/"):
    if "default_config.json" in files:
        default_config_path = os.path.join(root, "default_config.json")
        break

default_config = json.load(open(default_config_path))
config_dict = get_config_ranges(default_config)

run_config_file = open("../run_config.json", "w")
print_config_dict(run_config_file, config_dict)