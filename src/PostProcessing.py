from os.path import dirname, realpath, join, isdir
from os import mkdir, walk

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
        data_path = join(self.dir_path, "data")
        max_accuracy = 0
        max_accuracy_series = None
        min_loss = 1
        min_loss_series = None
        for root, dirs, files in walk(data_path):
            for directory in dirs:
                if directory != "post-run":
                    series_path = join(data_path, directory)
                    series_hash = directory
                    for root, dirs, files in walk(series_path):
                        for file in files:
                            if file == "stdout.txt":
                                stdout_path = join(series_path, file)
                                with open(stdout_path, "r") as stdout_file:
                                    for last_line in stdout_file:
                                        pass
                                    last_line_split = last_line.split(" - ")
                                    self.write_file.write(series_hash + "\n")
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
