#!/bin/bash

# kakao arena 제출 파일 생성
FILE_PATH="folder_name/*.json"
SAVE_PATH="folder_name/result.json"

# usage : python3 make_result.py [파일목록경로] [저장경로]
python3 make_result.py $FILE_PATH $SAVE_PATH
