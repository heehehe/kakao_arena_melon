#!/bin/bash

# kakao arena 제출 파일 생성
FILE_PATH="data/results/"
SAVE_PATH="data/results/result.json"
 
python3 src/preprocess_utils.py
python3 src/pivot_utils.py

python3 src/modeling_autoencoder.py
python3 src/modeling_cosinesim.py
python3 src/modeling_khaiii.py

# usage : python3 make_result.py [파일목록경로] [저장경로]
python3 src/make_result.py $FILE_PATH $SAVE_PATH
