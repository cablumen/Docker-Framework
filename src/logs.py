from glob import glob
from os.path import dirname, realpath, join, isfile, relpath
from json import load as jsonload

def get_logs():
    """
    Returns all file paths in log folder with associated metadata
    
    :returns a list of (environmental variables, file path) tuples
    """
    dir_path = dirname(realpath(__file__))
    data_path = join(dir_path, "data")

    # parse metadata in run_config
    run_config_path = open("./run_config.json", "r")
    run_config = jsonload(run_config_path)
    run_config_path.close()
    config_hashes = [x["HASH"] for x in run_config]
    
    filepaths_w_metadata = []
    for path in glob(data_path + "/**/*", recursive=True):
        if isfile(path):
            rel_path = relpath(path, dir_path)
            series_hash = rel_path.split('/')[1]
            if series_hash in config_hashes:
                series_config = [x for x in run_config if x["HASH"] == series_hash][0]
                filepaths_w_metadata.append((path, series_config))

    return filepaths_w_metadata

if __name__ == "__main__":
    get_logs()
