#-*- coding:utf-8 -*-

from src.basic_utils import *
import glob

def make_result(data_path):
    csvfiles, result = [], []
    for file in glob.glob(data_path):
        csvfiles.append(file)
    for i in csvfiles:
        try: result.extend(load_json(i))
        except: result.extend(load_json(i, 'utf-16'))
    return result

def mix_auto_cosine(final_auto, final_cosine):
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

if __name__ == '__main__':
    data_path = 'data/'

    val_auto_path = data_path+'val1+3*_auto*.json'
    val_cosine_path = data_path+'val1+3*_cosine*.json'    
    val_result_auto = make_result(val_auto_path)
    val_result_cosine = make_result(val_cosine_path)
    val_result_mix = mix_auto_cosine(result_auto, result_cosine)
    write_json(data_path+'val1+3_predict.json')
    val_result_all = make_result(data_path+'val*_predict.json')
    try:
        write_json(val_result_all, data_path+'val_result.json')
    except:
        write_json(val_result_all, data_path+'val_result.json', 'utf-16')

    val_auto_path = data_path+'test1+3*_auto*.json'
    val_cosine_path = data_path+'test1+3*_cosine*.json'
    val_result_auto = make_result(val_auto_path)
    val_result_cosine = make_result(val_cosine_path)
    val_result_mix = mix_auto_cosine(result_auto, result_cosine)
    write_json(data_path+'test1+3_predict.json')
    val_result_all = make_result(data_path+'test*_predict.json')
    try:
        write_json(val_result_all, data_path+'result.json')
    except:
        write_json(val_result_all, data_path+'result.json', 'utf-16')
