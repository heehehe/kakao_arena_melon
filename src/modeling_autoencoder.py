#-*- coding:utf-8 -*-

from src.basic_utils import *
from src.modeling_utils import *

from sklearn.metrics.pairwise import cosine_similarity
import keras
from keras.models import Sequential, Model
from keras.layers import Input, Dense, Dropout, Activation, Flatten
from keras.layers.normalization import BatchNormalization
from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, LearningRateScheduler
from keras.models import load_model
from keras.initializers import glorot_normal, Zeros, Ones
import keras.backend as K
from keras.optimizers import RMSprop
import tensorflow as tf


def make_autoencoder(train_pv):
    input_dim = train_pv.shape[1]
    c = 500
    model = Sequential()
    model.add(Dense(c, input_dim=input_dim, activation='relu'))
    model.add(Dense(input_dim, activation='sigmoid'))
    model.compile(optimizer='adam', loss='mse') # (optimizer='adadelta', loss='binary_crossentropy')
    
    tmp = train_pv.values
    history = model.fit(tmp, tmp,
                    epochs=4,
                    batch_size=256,
                    shuffle=True)
    
#     model.summary()
    encoder = Model(model.input, model.layers[0].output)
    encoded_imgs = encoder.predict(tmp)
    encoder.save("encoder%s" %small_years)
    del tmp, model, encoder
    gc.collect()
    
    train_data = pd.DataFrame(encoded_imgs)
    del encoded_imgs
    gc.collect()
    
    cosine_array = cosine_similarity(train_data, train_data)
    print('cosine_array complete')
    index2id = {i:u for i, u in enumerate((train_pv.index))}

    cf_dic = {}
    for i in tqdm(range(len(cosine_array))):
        song_id= list(map(index2id.get, list(np.argsort(-cosine_array[i])[1:201])))
        value= list(np.sort(cosine_array[0])[::-1][1:201])
        cf_dic[index2id[i]] = list(zip(song_id,value))

    del cosine_array, train_data
    gc.collect()
    
    return cf_dic

def f7(seq):
    # list에 있는 중복 데이터는 삭제하고, 순서는 유지하는 함수
    # set만 사용하면 순서가 뒤엉키게 됨
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def make_song_by_cf(songs, date, cf_dic):
    songs = [x for x in songs if x in cf_dic]
    if len(songs):
        tmp_list = []
        for song in songs:
            tmp_list.extend(cf_dic[song])
        tmp_list.sort(key = lambda x : x[1], reverse=True)
        tmp_list = f7([i[0] for i in tmp_list if i[1] > 0])
        cur_song = tmp_list[:200]
    else:
        cur_song = popular_date_song[date]['songs']
    cur_song = remove_seen(songs, cur_song)[:100]
    if len(cur_song) < 100:
        update_song = remove_seen(cur_song, popular_date_song[date]['songs'])
        cur_song.extend(update_song)
        cur_song = cur_song[:200]
    return cur_song
    
def pred_v1v3_auto(val_tmp, song_tag_dict, popular_date_tag):
    v1v3_predict = []
    for i in range(len(val_tmp)):
        date = date_dict[val_tmp.iloc[i]['date']]
        cur_song = make_song_by_cf(val_tmp.iloc[i]['songs'], date, cf_dic)
        cur_tag = add_var(val_tmp.iloc[i], 'tags', 'songs', song_tag_dict, popular_date_tag, date)
        v1v3_predict.append({
            "id" : val_tmp.iloc[i]['id'],
            "songs": remove_seen(val_tmp.iloc[i]['songs'], cur_song)[:100],
            "tags": remove_seen(val_tmp.iloc[i]['tags'], cur_tag)[:10],
         })
    return v1v3_predict


if __name__ == '__main__':
    data_path = 'data/'
    small_years = sys.argv[1]

    train = pd.read_parquet(data_path+'train(song_trim).parquet')
    val = pd.read_json(data_path+'val(lower).json')
    test = pd.read_json(data_path+'test(lower).json')
    # song_meta = load_json(data_path+'song_meta.json')
    # genre_gn_all = pd.read_json(data_path+'genre_gn_all.json', typ = 'series')
    # tag_song_dict = load_json(data_path+'tag_song_dict.json')
    song_tag_dict = load_json(data_path+'song_tag_dict.json')
    
    train_pv = pd.read_parquet(data_path+'train_DF_%s.parquet' %small_years)
    cf_dic = make_autoencoder(train_pv)
    
    no_tag, no_song, yes_index, no_both = check_target_type(val)
    v1v3_index= no_tag+yes_index
    
    train['year'] = train['updt_date'].apply( lambda x: int(x[2:4]) )
    train['date'] = train['updt_date'].apply( lambda x: int(str(x[2:4]) + str(x[5:7])) )
    val['year'] = val['updt_date'].apply( lambda x: int(x[2:4]) )
    val['date'] = val['updt_date'].apply( lambda x: int(str(x[2:4]) + str(x[5:7])) )

    year_list = sorted(list(train['year'].unique()))

    v1v3 = val[val.index.isin(v1v3_index)]

    val_tmp = v1v3[v1v3['year'].isin(small_years)]
    print("val year shape", val_tmp.shape)
    
    date_list = sorted(list(train['date'].unique()))
    date_dict = {}
    for i,k in enumerate(date_list):
        date_dict[k] = i
    popular_date_tag = make_popular_date_dict('tags', train, date_list, 13)
    popular_date_song = make_popular_date_dict('songs', train, date_list, 9)
    
    v1v3_predict = pred_v1v3_auto(val_tmp, song_tag_dict, popular_date_tag)
    write_json(v1v3_predict, data_path+'results/v1v3_auto_%s_predict.json' %small_years)
