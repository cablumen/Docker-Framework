from os.path import dirname, realpath, join, isdir
from os import mkdir, walk

from logs import get_logs

class PostProcessing(object):
    def __init__(self):
        # create log folder
        self.dir_path = dirname(realpath(__file__))
        log_path = join(self.dir_path, "logs")
        if not isdir(log_path):
            mkdir(log_path)

        # generate summary file
        summary_path = join(log_path, "summary.txt")
        self.write_file = open(summary_path, "w")
        self.parse_MNIST_stdout()
        self.write_file.close()

    def parse_MNIST_stdout(self):
        max_accuracy = 0
        max_accuracy_series = None
        min_loss = 1
        min_loss_series = None

        # iterate over series directories
        for file_path, metadata in get_logs():
            file_name = file_path.split('/')[-1]
            # parse the stdout file for tensorflow metrics
            if file_name == "stdout.txt":
                series_hash = metadata["HASH"]
                with open(file_path, "r") as stdout_file:
                    # get last_line of file
                    for last_line in stdout_file:
                        pass

                    # print metadata
                    self.write_file.write(str(metadata["HASH"]) + "\n")
                    self.write_file.write("\tSERIES_CONFIG: {\n")
                    for name, value in metadata.items():
                        if name != "HASH":
                            self.write_file.write("\t\t" + name + ":" + str(value) + "\n")
                    self.write_file.write("\t}\n")

                    # print metrics
                    last_line_split = last_line.split(" - ")
                    for metric in last_line_split:
                        if "loss" in metric or "accuracy" in metric:
                            metric_split = metric.split(":")
                            metric_name = metric_split[0]
                            metric_value = float(metric_split[1].strip())
                            if metric_name == "loss":
                                if metric_value < min_loss:
                                    min_loss_series = series_hash
                                    min_loss = metric_value
                            elif metric_name == "accuracy":
                                if max_accuracy < metric_value:
                                    max_accuracy_series = series_hash
                                    max_accuracy = metric_value

                            self.write_file.write("\t" + metric + "\n")
                    self.write_file.write("\n")

        # report best series
        self.write_file.write(max_accuracy_series + " had the highest accuracy of " + str(max_accuracy) + "\n")
        self.write_file.write(min_loss_series + " had the lowest loss of " + str(min_loss) + "\n")


if __name__ == "__main__":
    PostProcessing()
