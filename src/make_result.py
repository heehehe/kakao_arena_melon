#-*- coding:utf-8 -*-

from src.basic_utils import *
import glob

def make_result(data_path):
    ### 결과 합치기
    csvfiles, result = [], []
    for file in glob.glob(data_path):
        csvfiles.append(file)
    for i in csvfiles:
        try: result.extend(load_json(i))
        except: result.extend(load_json(i, 'utf-16'))
    return result

def mix_auto_cosine(final_auto, final_cosine):
    ### cosine에서의 song + autoencoder에서의 tag 예측
    final_all = []
    for i in tqdm(range(len(final_auto))):
        for j in range(len(final_cosine)):
            if final_auto[i]['id'] == final_cosine[j]['id']:
                final_all.append({
                    "id" : final_auto[i]['id'],
                    "songs": final_cosine[j]['songs'],
                    "tags": final_auto[i]['tags'],
                })
    return final_all

def save_result(data_name, data_path='data/'):
    ### 결과 저장
    auto_path = data_path+data_name+'1+3*_auto*.json'
    cosine_path = data_path+data_name+'1+3*_cosine*.json'    
    result_auto = make_result(auto_path)
    result_cosine = make_result(cosine_path)
    result_mix = mix_auto_cosine(result_auto, result_cosine)
    write_json(data_path+data_name+'1+3_predict.json')
    result_all = make_result(data_path+data_name+'*_predict.json')
    try:
        write_json(result_all, data_path+data_name+'_result.json')
    except:
        write_json(result_all, data_path+data_name+'_result.json', 'utf-16')

if __name__ == '__main__':
    save_result('val')
    save_result('test')
