#-*- coding:utf-8 -*-

from src.basic_utils import *

def update_song(data, all_song):
    for song in data['songs']:
        all_song.update(song)
    return all_song

def make_c1_c2_dict(data, col1, col2):
    c1_c2_dict = {}
    for i in tqdm(data.index):
        for c1 in data.loc[i][col1]:
            if c1 not in c1_c2_dict:
                ## 아직 없을 경우 빈 list 추가
                c1_c2_dict[tag] = []
            for c2 in data.loc[i][col2]:
                c1_c2_dict[c1].extend([c2]) ## song을 업데이트 해준다. 
    return c1_c2_dict


if __name__ == '__main__':
    data_path = 'data/'
    train = pd.read_json(data_path+'train.json')
    val = pd.read_json(data_path+'val.json')
    test = pd.read_json(data_path+'test.json')
    
    all_song = Counter()
    all_song = update_song(train, all_song)
    all_song = update_song(val, all_song)
    all_song = update_song(test, all_song)
    
    ## 3회 이상 등장한 노래만 사용! ==> use_song에 list형태로 담음
    tmp_dict = pd.DataFrame.from_dict(all_song, orient = 'index')
    tmp_dict = tmp_dict[tmp_dict[0] >= 3]
    use_song = list(tmp_dict['index'])
    
    ## 삭제 작업
    for i in tqdm(train.index):
        train.loc[i]['songs'] = list(set(train.loc[i]['songs']) & set(use_song))
        train.loc[i]['tags'] = list(map(lambda x:x.lower(),train.loc[i]['tags']))

    ## val, test도 동일하게 tag에서 대문자를 소문자로 바꿔준다. 
    for i in tqdm(val.index):
        val.loc[i]['tags'] = list(map(lambda x:x.lower(),val.loc[i]['tags']))

    for i in tqdm(test.index):
        test.loc[i]['tags'] = list(map(lambda x:x.lower(),test.loc[i]['tags']))    
        
    train.to_parquet('train(song_trim).parquet')
    val.to_json('val(lower).json', orient='records')
    test.to_json('test(lower).json', orient='records')
    
    ## song_tag_dict / tag_song_dict 생성
    train_tmp = train[['tags', 'songs']]
    song_tag_dict = make_c1_c2_dict(train_tmp, 'songs', 'tags')
    write_json(song_tag_dict, data_path+'song_tag_dict.json')
    tag_song_dict = make_c1_c2_dict(train_tmp, 'tags', 'songs')
    write_json(tag_song_dict, data_path+'tag_song_dict.json')
