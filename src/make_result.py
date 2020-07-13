#-*- coding:utf-8 -*-

import io, os, json, random, copy
import distutils.dir_util
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from collections import Counter
from tqdm import tqdm
import glob

def load_json(fname):
    with open(fname, encoding="utf-8") as f:
        json_obj = json.load(f)
    return json_obj

def write_json(data, fname):
    def _conv(o):
        if isinstance(o, (np.int64, np.int32)):
            return int(o)
        raise TypeError
    parent = os.path.dirname(fname)
    distutils.dir_util.mkpath(parent)
    with io.open(fname, "w", encoding="utf-8") as f:
        json_str = json.dumps(data, ensure_ascii=False, default=_conv)
        f.write(json_str)
        
def make_result(data_path, save_path):
    csvfiles, result = [], []
    for file in glob.glob():
        csvfiles.append(file)
    for i in csvfiles:
        result.extend(load_json(i))
    write_json(result, save_path)

if __name__ == '__main__':
    make_result(sys.argv[1], sys.argv[2])