#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import hashlib
import os
import requests


def get_hash(name):
    readsize = 64 * 1024
    with open(name, 'rb') as f:
        size = os.path.getsize(name)
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
    return hashlib.md5(data).hexdigest()


headers = {'User-Agent': 'SubDB/1.0 (operaxx1/0.1; https://www.operaxx1.com/)'}
url = "http://api.thesubdb.com/"
# url = "http://sandbox.thesubdb.com"
params = {
    # "action": "languages",
    # "action": "search",
    "action": "download",
    'hash': "53f4cb48c49b79439ad63a92b9349fed",
    'language': 'en'
}
responsne = requests.get(url, params=params, headers=headers)
print(responsne.status_code)
print(responsne.text)
