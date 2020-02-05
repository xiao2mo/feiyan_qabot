#!/bin/bash
ZEROMQ_SOCK_TMP_DIR=/tmp/ bert-serving-start -model_dir ./chatbot/bert_pre_models/chinese_wwm_ext_L-12_H-768_A-12 -cpu -num_worker=1
