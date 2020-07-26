#-*- coding:utf-8 -*-

from src.basic_utils import *
from khaiii import KhaiiiApi

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

############## v2+v4 #########################

def add_tags(data)
    def do_khaiii_col(data):
        morphs_prep = ['']*len(data)
        for i,d in enumerate(tqdm(data)):
            list_add = []
            try:
                for word in api.analyze(d):
                    for w in word.morphs:
                        if len(w.lex) > 1\
                        and w.tag not in ['NP','VV','VA','JKS','JKC','JKG','JKO','JKB','JKV','JKQ','JX','JC',\
                                          'EP','EF','EC','SF','SP','SS','SE','SO','XSA']\
                        and w.lex not in ['ㅋ','노래','음악','곡','월']:
                        # and w.tag in ['NNG','NNP','MAG','XR']\
                            list_add.append((w.lex, w.tag))
            except:
                pass # 비어있는 경우
            morphs_prep[i] = list_add
        gc.collect()
        return morphs_prep
    
    api = KhaiiiApi()
    title_khaiii = do_khaiii_col(data['plylst_title'].str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]"," "))
    title_khaiii2 = ['']*len(data)
    for i,title in enumerate(tqdm(title_khaiii)):
        title_khaiii2[i] = [t[0] for t in title]
    data['tags_new'] = data['tags'] + title_khaiii2
    tn_list = []
    for tn in tqdm(data['tags_new']):
        tn_list.append(list(set(tn)))
    data['tags_new'] = tn_list
    return data

def add_var1(date, var1, var2_list, var2_var1_dict, popular_date_var1, cur_var1):
    var1_counter = Counter()
    for v2 in var2_list:
        if str(v2) in var2_var1_dict:
            for v1 in var2_var1_dict[str(v2)]:
                var1_counter.update({var1 : 1})
    var1_counter = sorted(var1_counter.items(), key=lambda x : x[1], reverse=True)
    for k in var1_counter[:100]:
        if k[0] not in cur_var1:
            cur_var1.append(k[0])
    if len(cur_var1) == 0:
        cur_var1 = popular_date_var1[date][var1][:100]
    elif len(cur_var1) < 100:
        update_var1 = remove_seen(cur_var1, popular_date_var1[date][var1])
        update_var1 = [u for u in update_var1 if u not in cur_var1]
        cur_var1.extend(update_var1)
    return cur_var1

def pred_v2(data, tag_song_dict, song_tag_dict, popular_date_song, popular_date_tag):
    pred_list = []
    for i in tqdm(data.index):
        date = date_dict[data.loc[i]['date']]
        cur_song = []
        cur_song = add_var1(date, 'songs', data.loc[i]['tags'], tag_song_dict, popular_date_song, cur_song)[:100]
        cur_tag = list(set(data.loc[i]['tags_new']) - set(data.loc[i]['tags']))
        cur_tag = add_var1(date, 'tags', cur_song[:10], song_tag_dict, popular_date_tag, cur_tag)
        cur_tag = remove_seen(data.loc[i]['tags'], cur_tag)[:10]
        pred_list.append({
            "id" : data.loc[i]['id'],
            "songs": cur_song,
            "tags": cur_tag,
        })
    return pred_list

def pred_v4(data, tag_song_dict, song_tag_dict, popular_date_song, popular_date_tag):
    pred_list = []
    for i in tqdm(data.index):
        date = date_dict[data.loc[i]['date']]
        cur_tag = list(set(data.loc[i]['tags_new']) - set(data.loc[i]['tags']))
        cur_song = []
        cur_song = add_var1(date, 'songs', cur_tag[:10], tag_song_dict, popular_date_song, cur_song)[:100]
        cur_tag = add_var1(date, 'tags', cur_song[:10], song_tag_dict, popular_date_tag, cur_tag)[:10]
        pred_list.append({
            "id" : data.loc[i]['id'],
            "songs": cur_song,
            "tags": cur_tag,
        })
    return pred_list