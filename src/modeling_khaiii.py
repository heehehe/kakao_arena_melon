#-*- coding:utf-8 -*-

from src.modeling_utils import *
from khaiii import KhaiiiApi

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

if __name__ == '__main__':
    data_path = 'data/'

    train = pd.read_parquet(data_path+'train(song_trim).parquet')
    val = pd.read_json(data_path+'val(lower).json')
    test = pd.read_json(data_path+'test(lower).json')
    # song_meta = load_json(data_path+'song_meta.json')
    # genre_gn_all = pd.read_json(data_path+'genre_gn_all.json', typ = 'series')
    tag_song_dict = load_json(data_path+'tag_song_dict.json')
    song_tag_dict = load_json(data_path+'song_tag_dict.json')
    
    train['date'] = train['updt_date'].apply(lambda x: int(str(x[2:4]) + str(x[5:7])) )    # 연도+월
    train['year'] = train['updt_date'].apply(lambda x: int(x[2:4]))                        # 연도
    val['date'] = val['updt_date'].apply(lambda x: int(str(x[2:4]) + str(x[5:7])) )
    val['year'] = val['updt_date'].apply(lambda x: int(x[2:4]))
    test['date'] = test['updt_date'].apply(lambda x: int(str(x[2:4]) + str(x[5:7])) )
    test['year'] = test['updt_date'].apply(lambda x: int(x[2:4]))

    all = pd.concat([train, val, test])
    date_list = sorted(list(all['date'].unique()))
    date_dict = {}       # 해당 연도+월 에 index 부여(?)
    for i,k in enumerate(date_list):
        date_dict[k] = i

    popular_date_tag = make_popular_date_dict('tags', train, date_list, 13)
    popular_date_song = make_popular_date_dict('songs', train, date_list, 9)
    
    ### khaiii 활용한 plylst_title 형태소 분석 통한 태그 생성
    val = add_tags(val)
    test = add_tags(test)
    
    no_tag, no_song, yes_index, no_both = check_target_type(val)
    val2 = val[val.index.isin(no_song)]
    val4 = val[val.index.isin(no_both)]

    no_tag, no_song, yes_index, no_both = check_target_type(test)
    test2 = test[test.index.isin(no_song)]
    test4 = test[test.index.isin(no_both)]
    
    val2_predict = pred_v2(val2, tag_song_dict, song_tag_dict, popular_date_song, popular_date_tag)
    write_json(val2_predict, data_path+'val2_predict.json')

    val4_predict = pred_v4(val4, tag_song_dict, song_tag_dict, popular_date_song, popular_date_tag)
    write_json(val4_predict, data_path+'val4_predict.json', 'utf-16')
    
    test2_predict = pred_v2(test2, tag_song_dict, song_tag_dict, popular_date_song, popular_date_tag)
    write_json(test2_predict, data_path+'test2_predict.json')
    test4_predict = pred_v4(test4, tag_song_dict, song_tag_dict, popular_date_song, popular_date_tag)
    write_json(test4_predict, data_path+'test4_predict.json')