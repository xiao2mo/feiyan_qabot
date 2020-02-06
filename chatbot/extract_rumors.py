#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@description: 从数据库中，提取谣言数据，并以rasa nlu的训练数据格式保存。
"""
# 添加python包的路径
import sys
import os
PARENT_PATH = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(PARENT_PATH)

import pymongo
from utils.constants import MONGO_HOST

MONGO_CLIENT = pymongo.MongoClient(host=MONGO_HOST)
MONGO_RUMORS = MONGO_CLIENT["2019-nCoV"].DXYRumors

# 路径常量
NLU_PATH = 'chatbot/data/nlu'
NLU_FILE = os.path.join(PARENT_PATH, NLU_PATH, 'rumor_nlu.md')
RESPONSE_FILE = os.path.join(PARENT_PATH, NLU_PATH, 'responses_rumor.md')
EDA_PATH = os.path.join(os.path.dirname(__file__), 'eda')
NORMAL_FILE = os.path.join(EDA_PATH, 'rumor.txt')
AUGMENT_FILE = os.path.join(EDA_PATH, 'rumor_augmented.txt')

# EDA常量
NUM_AUG = 2 # 一条数据增强次数。
ALPHA = 0.05 # 替换的百分比

def get_rumors():
    """ 获取谣言列表
    @return title(str): 谣言问题
    @return main_summary(str): 谣言简要回答
    @return body(str): 回答详情
    """
    return [{
        "title": one["title"],
        "main_summary": one["mainSummary"].strip().replace("\n",""),
        "body": one["body"].strip().replace("\n","")
    } for one in MONGO_RUMORS.find()]

if __name__ == "__main__":
    rumors = get_rumors()
    
    # 写入response文件
    with open(RESPONSE_FILE, "w") as f:
        line = ""
        for i, item in enumerate(rumors):
            line += "## rumor_{}\n".format(i+1)
            line += "* faq/rumor_{}\n".format(i+1)
            line += "\t- {}\\n{}\n".format(item["main_summary"], item["body"])
            line += "\n"
        f.write(line)
    
    # 写入未增强的语料
    with open(NORMAL_FILE, 'w') as f:
        line = ""
        for i, item in enumerate(rumors):
            line += "{}\t{}".format(i, item["title"])
            line += "\n"
        f.write(line)
    
    os.system(f"python {EDA_PATH}/code/augment.py --input {NORMAL_FILE} --output {AUGMENT_FILE} --num_aug={NUM_AUG} --alpha={ALPHA}")

    # 将增强后的语料写成nlu格式
    content = ""
    with open(AUGMENT_FILE, 'r') as f:
        for count, line in enumerate(f.readlines()):
            line_arr = line.split('\t')
            if count % (NUM_AUG+1) == 0 and count!= 0:
                content += "\n"
            if count % (NUM_AUG+1) == 0:
                content += "## intent:faq/rumor_{}\n".format(int(line_arr[0])+1)
            content += "- {}\n".format(line_arr[1].replace(" ", "").replace("\n",""))
    
    with open (NLU_FILE, 'w', encoding='utf-8') as f:
        f.write(content)