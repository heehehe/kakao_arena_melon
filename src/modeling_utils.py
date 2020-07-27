#-*- coding:utf-8 -*-

from src.basic_utils import *

def make_popular_date_dict(var, data, date_list, thres):
    popular_date_dict = []
    for i in range(len(date_list)):
        if i <= thres:
            year = int(str(date_list[i])[0])
            tmp = data[data['year'] == year]
        else:
            tmp = data[data['date'] == date_list[i]]
        _, most_var = most_popular(tmp, var, 100)
        popular_date_dict.append({
            "date" : date_list[i],
            var : most_var,
        })
    return popular_date_dict

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
