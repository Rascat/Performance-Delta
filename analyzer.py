import glob
import os
from typing import List

def get_log_file_names(path_to_log_dir: str) -> List[str]:
    filenames = os.listdir(path_to_log_dir)
    print(filenames)
    return filenames