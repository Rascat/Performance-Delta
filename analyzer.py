import glob
import utils
import os
import json
from typing import List

def analyze(path_to_log_dir: str):
    filenames = get_log_file_names(path_to_log_dir)
    for filename in filenames:
        with open(filename) as file:
            log_list = json.load(file)
            for log in log_list:
                print(log['commit'])
            

def get_log_file_names(path_to_log_dir: str) -> List[str]:
    filenames = utils.get_filenames_by_type(path_to_log_dir, 'json')
    return filenames