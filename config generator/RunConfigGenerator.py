from glob import glob
from os.path import dirname, join, isfile, abspath, realpath
from json import load as jsonload
from itertools import islice, count, product
from math import ceil, floor, log
from uuid import uuid5, NAMESPACE_OID


def arithmetic(start, end, step):
    assert isinstance(start, int) or isinstance(start, float), "arithmetic: start must be of type int or float"
    assert isinstance(end, int) or isinstance(start, float),   "arithmetic: end must be of type int or float"
    assert isinstance(step, int) or isinstance(step, float),   "arithmetic: step must be of type int or float"
    assert step != 0, "arithmetic: step cannot be 0"

    # TODO: step goes wrong way between start and end

    # determine number of steps between start and end
    range_count = ceil(abs(end - start) / step) + 1
    range_list = list(islice(count(start, step), range_count))

    # fix rounding errors
    round_digits = max(len(str(start)), len(str(step)))
    return [round(x, round_digits) for x in range_list]

def geometric(start, end, ratio):
    assert isinstance(start, int) or isinstance(start, float), "geometric: start must be of type int or float"
    assert isinstance(end, int) or isinstance(start, float),   "geometric: end must be of type int or float"
    assert isinstance(ratio, int) or isinstance(ratio, float), "geometric: ratio must be of type int or float"
    assert ratio > 0, "geometric: ratio must be greater than 0"
    assert ratio != 1, "geometric: ratio cannot be 1"

    range_list = [start * ratio ** x for x in range(floor(log(end / start)/ log(ratio)) + 1)] 

    # fix rounding errors
    round_digits = max(len(str(start)), len(str(ratio)))
    return [round(x, round_digits) for x in range_list]

def interval(start, end, samples):
    assert isinstance(start, int),   "interval: start must be of type int"
    assert isinstance(end, int),     "interval: end must be of type int"
    assert isinstance(end, samples), "interval: samples must be of type int"
    assert samples >= 1, "interval: samples_per_order_of_magnitude must be greater or equal to 0"

    range_list = [10**start]
    for i in [10**i for i in range(start+1, end+2)]:
        for j in range(1, samples + 1):
            sample = i*j/samples
            sample_len = len(str(sample))
            if sample_len > max_len:
                max_len = sample_len
            range_list.append(sample)

    return range_list

def nominal(*args):
    return args

class RunConfigGenerator(object):
    def __init__(self):
        sample_ranges = self.get_sample_ranges(default_config)

        root_path = dirname(dirname(realpath(__file__)))
        run_config_path = join(root_path, "run_config.json")
        self.run_config_file = open(run_config_path, "w")
        self.print(sample_ranges)
        self.run_config_file.close()
    
    def get_sample_ranges(self, input_config):
        output = {}

        if type(input_config) is dict:
            for key, value in input_config.items():
                if isinstance(value, list):
                    # if config is tuple, get range of values
                    sampling_name = value[0]
                    sampling_parameters = value[1:]
                    sampling_algorithm = globals()[sampling_name]

                    output[key] = sampling_algorithm(*sampling_parameters)

                elif isinstance(value, str) or not hasattr(value, "__iter__"):
                    # if config is not iterable, add static value
                    output[key] = [value]

                else:
                    # if config is iterable, recurse
                    config_range = self.to_underscore_notation(key, self.get_sample_ranges(value))
                    output.update(config_range)

        return output

    def to_underscore_notation(self, namespace, input_config):
        output_config = {}
        for key, value in input_config.items():
            output_config[namespace + "_" + key] = value

        return output_config

    def print(self, config_dict):
        config_names = list(config_dict.keys())
        config_ranges = list(config_dict.values())

        config_product = list(product(*config_ranges))
        config_length = len(config_product)

        self.run_config_file.write("[\n")
        for run_index, run_config in enumerate(config_product):
            self.run_config_file.write("\t{\n")
            config_hash = uuid5(NAMESPACE_OID, str(run_config))
            self.run_config_file.write("\t\t\"HASH\": \"" + str(config_hash) + "\",\n")
            run_config_length = len(run_config)
            for config_index, config_value in enumerate(run_config):
                config_name = config_names[config_index]
                self.print_config(config_name, config_value)
                self.print_line_end(config_index, run_config_length)

            self.run_config_file.write("\t}")
            self.print_line_end(run_index, config_length)

        self.run_config_file.write("]\n")
        print("Wrote " + str(config_length) + " configs to run_config.json")

    def print_config(self, config_name, config_value):
        write_line = "\t\t\"" + config_name.upper() + "\": "
        if isinstance(config_value, str):
            write_line += "\"" + config_value + "\""

        elif isinstance(config_value, bool):
            write_line += str(config_value).lower()

        else:
            write_line += str(config_value)

        self.run_config_file.write(write_line)

    def print_line_end(self, index, iter_length):
        if index != iter_length - 1:
            self.run_config_file.write(",")
        self.run_config_file.write("\n")

if __name__ == "__main__":
    # find default_config.json in src folder
    default_config_path = None
    src_path = abspath(join(dirname( __file__ ), '..', 'src'))
    for path in glob(src_path + "/**/*", recursive=True):
        file_name = path.split('/')[-1]
        if isfile(path) and file_name == "default_config.json":
            default_config_path = path
            break

    # parse default_config.json into dict
    default_config_file = open(default_config_path, "r")
    default_config = jsonload(default_config_file)
    default_config_file.close()

    RunConfigGenerator()
