#-*- coding:utf-8 -*-

from src.basic_utils import *
from src.modeling_utils import *
from src.pivot_utils import *
from sklearn.metrics.pairwise import cosine_similarity

def make_cosine_predict(final_result):
    R_df = final_result.pivot(index = 'id', columns ='song', values = 'point').fillna(0)
    del final_result
    
    print("make cosine data")    
    cosine_array = cosine_similarity(R_df, R_df)
    predicted_array = np.zeros(shape=(len(R_df.index),len(R_df.columns))) 
    for i in tqdm(range(len(cosine_array))):
        top_200 = cosine_array[i].argsort()[-201:][::-1]
        top_200 = np.delete(top_200, 0)
        weighted_sum = np.array([0])
        for top_idx in top_200:
            weighted_sum = weighted_sum + (cosine_array[i][top_idx] * R_df.values[top_idx])
        predicted = weighted_sum / len(top_200)
        predicted_array[i] = predicted
    iu_predicted = R_df.values*(-99999) + predicted_array
    
    print("make dic data")    
    cf_dic = {}
    for i in range(len(iu_predicted)):
        cf_dic[R_df.index[i]] = R_df.columns[iu_predicted[i].argsort()[-200:][::-1]].tolist()

    return cf_dic

def pred_v1v3_cosine(val_tmp, song_tag_dict, popular_date_tag):
    v1v3_predict = []
    for i in range(len(val_tmp)):
        date = date_dict[val_tmp.iloc[i]['date']]
        row_number = val_tmp.iloc[i]['id']

        cur_song = list(cf_dic[row_number])
        cur_tag = add_var(val_tmp.iloc[i], 'tags', 'songs', song_tag_dict, popular_date_tag, date)[:10]

        v1v3_predict.append({
            "id" : val_tmp.iloc[i]['id'],
            "songs": remove_seen(val_tmp.iloc[i]['songs'], cur_song)[:100],
            "tags": cur_tag,
        })
    return v1v3_predict


if __name__ == '__main__':
    data_path = 'data/'
    train = pd.read_parquet(data_path+'train(song_trim).parquet')
    val = pd.read_json(data_path+'val(lower).json')
    test = pd.read_json(data_path+'test(lower).json')
    # song_meta = load_json(data_path+'song_meta.json')
    # genre_gn_all = pd.read_json(data_path+'genre_gn_all.json', typ = 'series')
    # tag_song_dict = load_json(data_path+'tag_song_dict.json')
    song_tag_dict = load_json(data_path+'song_tag_dict.json')
    
    train['year'] = train['updt_date'].apply(lambda x: int(x[2:4]))
    train['date'] = train['updt_date'].apply(lambda x: int(str(x[2:4]) + str(x[5:7])) )
    val['year'] = val['updt_date'].apply(lambda x: int(x[2:4]))
    val['date'] = val['updt_date'].apply(lambda x: int(str(x[2:4]) + str(x[5:7])) )
    test['year'] = test['updt_date'].apply( lambda x: int(x[2:4]) )
    test['date'] = test['updt_date'].apply( lambda x: int(str(x[2:4]) + str(x[5:7])) )

    date_list = sorted(list(train['date'].unique()))
    date_dict = {}
    for i,k in enumerate(date_list):
        date_dict[k] = i

    popular_date_tag = make_popular_date_dict('tags', train, date_list, 13)
    popular_date_song = make_popular_date_dict('songs', train, date_list, 9)      
        
    small_years_list = [[i for i in range(4,11)], [i for i in range(11,14)],\
                        [14], [15], [16], [17], [18], [19], [20]]
    
    for small_years in small_years_list:
        #### val
        no_tag, no_song, yes_index, no_both = check_target_type(val)
        v1v3_index = no_tag + yes_index
        v1v3 = val[val.index.isin(v1v3_index)]
        val_tmp = v1v3[v1v3['year'].isin(small_years)]
        tmp = train[(train['year'].isin(small_years))]
        
        like_num = int(np.percentile(tmp['like_cnt'], 70))
        tmp = tmp[(tmp['like_cnt'] > like_num)]
        before_tmp = before_pivot(tmp)
        tmp_dict = before_tmp['song'].value_counts().to_dict()
        before_tmp['count']= before_tmp['song'].apply(lambda x : tmp_dict[x])
        before_tmp = before_tmp[before_tmp['count'] > 1]
        before_val_tmp = before_pivot(val_tmp)
        final_result = pd.concat([before_tmp, before_val_tmp])
        del before_tmp, before_val_tmp
        gc.collect()
        cf_dic = make_cosine_predict(final_result)
        v1v3_predict = pred_v1v3_cosine(val_tmp, song_tag_dict, popular_date_tag)
        write_json(v1v3_predict, data_path+'val1+3_predict_cosine_%s.json' %str(small_years))
        
        #### test
        no_tag, no_song, yes_index, no_both = check_target_type(test)
        v1v3_index = no_tag + yes_index
        v1v3 = val[val.index.isin(v1v3_index)]
        val_tmp = v1v3[v1v3['year'].isin(small_years)]
        tmp = train[(train['year'].isin(small_years))]
        
        like_num = int(np.percentile(tmp['like_cnt'], 70))
        tmp = tmp[(tmp['like_cnt'] > like_num)]
        before_tmp = before_pivot(tmp)
        tmp_dict = before_tmp['song'].value_counts().to_dict()
        before_tmp['count']= before_tmp['song'].apply(lambda x : tmp_dict[x])
        before_tmp = before_tmp[before_tmp['count'] > 1]
        before_val_tmp = before_pivot(val_tmp)
        final_result = pd.concat([before_tmp, before_val_tmp])
        del before_tmp, before_val_tmp
        gc.collect()
        cf_dic = make_cosine_predict(final_result)
        v1v3_predict = pred_v1v3_cosine(val_tmp, song_tag_dict, popular_date_tag)
        write_json(v1v3_predict, data_path+'test1+3_predict_cosine_%s.json' %str(small_years))