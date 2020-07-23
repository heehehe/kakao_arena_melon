#-*- coding:utf-8 -*-

from collections import Counter

def add_var(row, var, var2, var_dict, popular_var, date):
    # 변수 counter 생성
    var_counter = Counter()
    for v2 in row[var2]:
        if str(v2) in var_dict:
            for v1 in var_dict[str(v2)]:
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

def add_by_cf_dic(row, cf_dic):
    row_num = row['id']
    cur_song = remove_seen(row['songs'], cf_dic[row_num])[:100]
    return cur_song    
    