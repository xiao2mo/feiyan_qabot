#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from utils.constants import STOP_WORDS, FAQ_FILE
import jieba
import numpy as np
from bert_serving.client import BertClient


def save_voice(content, path):
    """ 存储语音文件
    @param content(byte): 语音内容二进制格式
    @param path(str): 存储的路径
    """
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    voice_file = "{}{}.amr".format(path, now)
    with open(voice_file, 'wb') as f:
        f.write(content)


def get_questions_list():
    """ 获取faq所有问题
    """
    corpus = []
    with open(FAQ_FILE, "r") as f:
        for line in f.readlines():
            if line.startswith("- "):
                corpus.append(line.strip()[2:])
    return corpus


def search_related_questions(question, top_k=5):
    """ 根据问题查询关联的前k个问题
    @param question(str): 输入的问题
    @param top_k(int): 前k个，默认为5
    """
    question_encode = BC.encode([question])
    question_encode_norm = question_encode / np.linalg.norm(question_encode)
    score_list = np.dot(CORPUS_ENCODING_NORM, question_encode_norm.T)
    top_k_index = score_list.reshape(-1).argsort()[::-1][:top_k]
    related_question_str = list(np.array(CORPUS)[top_k_index])
    return related_question_str


print('connecting bert server......')
BC = BertClient()

print('getting questions list......')
CORPUS = get_questions_list()

print('encoding questions........')
CORPUS_ENCODING = BC.encode(CORPUS)
CORPUS_ENCODING_NORM = CORPUS_ENCODING / \
    np.linalg.norm(CORPUS_ENCODING, axis=1).reshape(-1, 1)
