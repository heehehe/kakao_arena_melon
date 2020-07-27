#-*- coding:utf-8 -*-

import json, os, io, sys, gc, time, copy, random, warnings
warnings.filterwarnings("ignore")
import distutils.dir_util
import numpy as np
import pandas as pd
from collections import Counter
from tqdm import tqdm

def load_json(fname, encode='utf-8'):
    # json 불러오기
    with open(fname, encoding=encode) as f:
        json_obj = json.load(f)
    return json_obj

def write_json(data, fname, encode='utf-8'):
    # json utf-8로 저장하기
    def _conv(o):
        if isinstance(o, (np.int64, np.int32)):
            return int(o)
        raise TypeError
    parent = os.path.dirname(fname)
    distutils.dir_util.mkpath(parent)
    with io.open(fname, "w", encoding=encode) as f:
        json_str = json.dumps(data, ensure_ascii=False, default=_conv)
        f.write(json_str)
                
def check_target_type(df):
    # 노래 및 태그 유무에 따른 dataframe 인덱스 분할
    no_song_idx = []
    no_tag_idx = []
    no_both_idx = []
    yes_all_idx = []
    for i in df.index:
        ### v1 : 노래 O 태그 X
        if bool(df.loc[i:i, 'songs'].values[0]) & bool(not df.loc[i:i, 'tags'].values[0]):
            no_tag_idx.append(i)
        ### v2 : 노래 X 태그 O
        elif bool(not df.loc[i:i, 'songs'].values[0]) & bool(df.loc[i:i, 'tags'].values[0]):
            no_song_idx.append(i)
        ### v3 : 노래 O 태그 O
        elif bool(df.loc[i:i, 'songs'].values[0]) & bool(df.loc[i:i, 'tags'].values[0]):
            yes_all_idx.append(i)          
        ### v4 : 노래 X 태그 X
        else:
            no_both_idx.append(i)
    print("노래 O 태그 X : {}개".format(len(no_tag_idx)))
    print("노래 X 태그 O : {}개".format(len(no_song_idx)))
    print("노래 O 태그 O : {}개".format(len(yes_all_idx)))
    print("노래 X 태그 X : {}개".format(len(no_both_idx)))
    return no_tag_idx, no_song_idx, yes_all_idx, no_both_idx

def most_popular(playlists, col, topk_count):
    # plylst 내 노래 counter 및 상위 topk_count 노래 출력
    c = Counter()
    for doc in playlists[col]:
        c.update(doc)
    topk = c.most_common(topk_count)
    return c, [k for k, v in topk]

def remove_seen(seen, l):
    # l에서 seen이 없는 요소 출력 (이미 존재하는 노래 및 태그 제거 위함)
    seen = set(seen)
    return [x for x in l if not (x in seen)]
