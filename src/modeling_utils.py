#-*- coding:utf-8 -*-

from collections import Counter
from basic_utils import *

def add_var(row, var, var2, var_dic, popular_var, date):
    # 변수 counter 생성
    var_counter = Counter()
    for v2 in row[var2]:
        if str(v2) in var_dic:
            for v1 in var_dic[str(v2)]:
                var_counter.update({v1 : 1})
    var_counter = sorted(var_counter.items(), key=lambda x : x[1], reverse=True)
    var_list = []
    for k in var_counter[:100]:
        var_list.append(k[0])
    if len(var_list) == 100:
        var_list = popular_var[date][var][:100]
    elif len(var_list) < 100:
        var_list_update = remove_seen(var_list, popular_var[date][var])
        var_list.extend(var_list_update)
        var_list = var_list[:100]
    return var_list

def add_song_by_cf_dic(row, cf_dic):
    row_num = row['id']
    cur_song = remove_seen(row['songs'], cf_dic[row_num])[:100]
    return cur_song    

def add_song_by_autoencoder(row, cf_dic, popular_date):
    
    def f7(seq):
        ### list에 있는 중복 데이터는 삭제하고, 순서는 유지하는 함수
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]
    
    date = row['year']
    songs = [x for x in row['songs'] if x in cf_dic]
    if len(songs):
        tmp_list = []
        for song in songs:
            tmp_list.extend(cf_dic[song])
        tmp_list.sort(key=lambda x : x[1], reverse=True)
        tmp_list = [i[0] for i in tmp_list if i[1]>0]
        tmp_list = f7(tmp_list)
        cur_song = tmp_list[:200]
    else:
        cur_song = popular_date[date-4]['songs']
    cur_song = remove_seen(row['songs'], cur_song)[:100]
    return cur_song