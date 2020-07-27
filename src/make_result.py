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
    data_path = sys.argv[1]
    save_path = sys.argv[2]
    auto_path = data_path+'../v1v3_auto*.json'
    cosine_path = data_path+'../v1v3_cosine*.json'
    
    result_auto = make_result(auto_path)
    result_cosine = make_result(cosine_path)
    result_mix = mix_auto_cosine(result_auto, result_cosine)
    write_json(data_path+'v1v3_predict.json')
    result_all = make_result(data_path)
    try:
        write_json(data_path+'*.json', save_path)
    except:
        write_json(data_path+'*.json', save_path, 'utf-16')
    