#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from utils.constants import STOP_WORDS, FAQ_FILE, RUMOR_FILE
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

def read_nlu_file(path):
    """ 读取nlu文件，并返回每个意图的第一个例子
    """
    corpus = []
    flag = 0
    with open(path, "r") as f:
        for line in f.readlines():
            if line.startswith("##"):
                flag = 1
            if line.startswith("- ") and flag == 1:
                corpus.append(line.strip()[2:])
                flag = 0
    return corpus


def get_questions_list():
    """ 获取faq所有问题
    """
    corpus = []
    corpus += read_nlu_file(FAQ_FILE)
    corpus += read_nlu_file(RUMOR_FILE)
    return corpus


def search_related_questions(question, top_k=5):
    """ 根据问题查询关联的前k个问题
    @param question(str): 输入的问题
    @param top_k(int): 前k个，默认为5
    """
    vocabulary = set()
    corpus_tokens = []
    for sentence in CORPUS:
        # 分词
        tokens = jieba.cut(sentence)
        # 去除停用词
        tokens_without_stops = [token for token in tokens if token not in STOP_WORDS]
        corpus_tokens.append(tokens_without_stops)
        for word in tokens_without_stops:
            vocabulary.add(word)
    vocabulary = sorted(list(vocabulary))
    search_dict = {}
    for word in vocabulary:
        search_dict[word] = []
        for i, tokens in enumerate(corpus_tokens):
            count = tokens.count(word)
            if count != 0:
                search_dict[word].append([i, count])
    # 进行检索
    question_tokens = jieba.cut(question)
    question_tokens_without_stops = [token for token in question_tokens if token not in STOP_WORDS]
    # 相关的问题有
    related_question = []
    for token in question_tokens_without_stops:
        if token in search_dict.keys():
            related_question += search_dict[token]
    # 相关问题匹配到的次数
    related_question_dict = {}
    for id_count_pair in related_question:
        if id_count_pair[0] in related_question_dict:
            related_question_dict[id_count_pair[0]] += id_count_pair[1]
        else:
            related_question_dict[id_count_pair[0]] = id_count_pair[1]
    # 进行排序
    sorted_question = sorted(related_question_dict.items(), key=lambda item:item[1], reverse=True)
    # 输出相似问题排名
    related_question_str = []
    for question in sorted_question:
        related_question_str.append(CORPUS[question[0]])
    return related_question_str[:top_k]
    # question_encode = BC.encode([question])
    # question_encode_norm = question_encode / np.linalg.norm(question_encode)
    # score_list = np.dot(CORPUS_ENCODING_NORM, question_encode_norm.T)
    # top_k_index = score_list.reshape(-1).argsort()[::-1][:top_k]
    # related_question_str = list(np.array(CORPUS)[top_k_index])
    # return related_question_str


# print('connecting bert server......')
# BC = BertClient()

# print('getting questions list......')
CORPUS = get_questions_list()

# print('encoding questions........')
# CORPUS_ENCODING = BC.encode(CORPUS)
# CORPUS_ENCODING_NORM = CORPUS_ENCODING / \
#     np.linalg.norm(CORPUS_ENCODING, axis=1).reshape(-1, 1)
