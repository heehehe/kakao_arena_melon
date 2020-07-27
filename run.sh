#!/bin/bash

# train, val, test 데이터 용량 축소
# + song_tag_dict / tag_song_dict 생성
python3 src/preprocess_utils.py

# song * id matrix 생성
python3 src/pivot_utils.py

# 모델링 진행
python3 src/modeling_autoencoder.py   # 오토인코더
python3 src/modeling_cosinesim.py     # 코사인 유사도
python3 src/modeling_khaiii.py        # 제목 형태소 분석 통한 태그 추출

# 결과 파일 생성
python3 src/make_result.py
