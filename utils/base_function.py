#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime


def save_voice(content, path):
    """ 存储语音文件
    @param content(byte): 语音内容二进制格式
    @param path(str): 存储的路径
    """
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    voice_file = "{}{}.amr".format(path, now)
    with open(voice_file, 'wb') as f:
        f.write(content)
