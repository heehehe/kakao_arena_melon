#-*- coding:utf-8 -*-

import pandas as pd
import numpy as np
import time, gc
from collections import Counter
from tqdm import tqdm

def before_pivot(data, use_song):
    result = []
    start = time.time()  # 시작 시간 저장     
    for i in tqdm(data.index):
        for song in data.loc[i]['songs']:
            if song in use_song:
                df = pd.DataFrame({
                            'id' : [data.loc[i]['id']],
                            'song' : [song],
                            'point' : 1
                        })
                result += [df]
    final_result = pd.concat(result)
    print(final_result.shape)
    end = time.time()  # 종료 시간 저장     
    print("spend time ", round((end-start)/60, 2))
    return final_result

def make_use_song(train_tmp, thres):
    c = Counter()
    for doc in train_tmp['songs']:
        c.update(doc)
    tmp_dict= pd.DataFrame.from_dict(c, orient = 'index')
    print("before ", tmp_dict.shape)
    tmp_dict = tmp_dict[tmp_dict[0] > thres]
    print("after ", tmp_dict.shape)
    tmp_dict.reset_index(inplace = True)
    ## thres회 초과 등장한 노래만 사용! ==> use_song에 list형태로 담음
    use_song = list(tmp_dict['index'])
    del c, tmp_dict
    gc.collect()
    return use_song

def make_pv_file(train, small_years, thres, data_path):
    ## TRAIN
    print("train only year", train[(train['year'].isin(small_years))].shape)
    train_tmp = train[(train['year'].isin(small_years))]
    
    train_tmp = train_tmp[(train_tmp['like_cnt'] > 0)]
    train_tmp.reset_index(inplace = True, drop = True)
    print("train best playlist", train_tmp.shape)
    
    use_song = make_use_song(train_tmp, thres)
    
    train_df = before_pivot(train_tmp,use_song)
    print('complete train')
    
    del train_tmp 
    gc.collect()
    
    train_df = train_df.pivot(index = 'song', columns ='id', values = 'point').fillna(0)
    train_df.columns = train_df.columns.astype(str)
    print("최종 shape : ", train_df.shape)
    
    train_df.to_parquet(data_path+'train_DF_%s.parquet' %small_years)
    del train_df
    gc.collect()

if __name__ == '__main__':
    data_path = 'data/'
    train = pd.read_parquet(data_path+'train(song_trim).parquet')
    train['year'] = train['updt_date'].apply(lambda x: int(x[2:4]))
    
    year_thres = [([i for i in range(0,11)], 1),
                  ([i for i in range(11,14)], 1),
                  ([14], 1), ([15], 1), ([16], 2), ([17], 2),
                  ([18], 4), ([19], 5), ([20], 2)]
    
    for small_years, thres in year_thres:
        make_pv_file(train, small_years, thres, data_path)
