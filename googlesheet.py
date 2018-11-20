# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import requests
import json
import os

"""
googlesheet权限
https://www.googleapis.com/auth/spreadsheets.readonly	允许对用户工作表及其属性进行只读访问。
https://www.googleapis.com/auth/spreadsheets	允许对用户工作表及其属性进行读/写访问。
https://www.googleapis.com/auth/drive.readonly	允许以只读方式访问用户的文件元数据和文件内容。
https://www.googleapis.com/auth/drive.file	对文件创建或打开的文件的每文件访问权限。
https://www.googleapis.com/auth/drive	访问所有用户文件的完整，允许的范围。仅在严格必要时才请求此范围。
"""
PATH = os.path.dirname(os.path.abspath(__file__))
PATH_client_secret = PATH + "/client_secret.json"


def token_config(data):
    with open(PATH + '/token_config.json', 'w') as config:
        json.dump(data, config)


def get_token_config():
    with open(PATH + '/token_config.json') as config:
        result = json.load(config)
        return result


def access_token(data):
    with open(PATH + '/access_token_config.json', 'w') as config:
        json.dump(data, config)


def get_access_token_config():
    with open(PATH + '/access_token_config.json') as config:
        result = json.load(config)['access_token']
        return result


rs = requests.session()


class GoogleOAuth2:

    def __init__(self):
        self.client_id = ""
        self.client_secret = ""
        self.auth_uri = ""
        self.token_uri = "https://www.googleapis.com/oauth2/v4/token"
        self.redirect_uri = ""

    def get_config(self, config_path=PATH_client_secret):
        with open(config_path) as config:
            config = json.load(config)
            self.client_id = config["installed"]["client_id"]
            self.client_secret = config["installed"]["client_secret"]
            self.auth_uri = config["installed"]["auth_uri"]
            self.token_uri = config["installed"]["token_uri"]
            self.redirect_uri = config["installed"]["redirect_uris"]

    def get_code(self, scope, config_path=PATH_client_secret):
        self.get_config(config_path)
        url = "https://accounts.google.com/o/oauth2/auth?" \
              "scope=%s&" \
              "access_type=offline&" \
              "redirect_uri=%s&" \
              "response_type=code&" \
              "client_id=%s&" \
              "prompt=consent" % (scope, self.redirect_uri[0], self.client_id)
        print(url)
        print("请点击URL,为客户端授权,并获取跳转后URL的code值")
        return input('请输入code值:')

    def first_get_token(self, scope, config_path=PATH_client_secret):
        self.get_config(config_path)
        code = self.get_code(scope)
        url = self.token_uri
        header = {'Host': 'www.googleapis.com', 'Content-Type': 'application/x-www-form-urlencoded'}
        data = {'code': code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                "redirect_uri": self.redirect_uri[0],
                "grant_type": 'authorization_code',
                "access_type": "access_token"
                }
        response = rs.post(url=url, data=data, headers=header)
        token_config(json.loads(response.text))
        access_token(json.loads(response.text))

    def refresh_token(self, config_path=PATH_client_secret):
        self.get_config(config_path)
        url = self.token_uri
        refresh_token = get_token_config()['refresh_token']
        header = {'Host': 'www.googleapis.com', 'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            "grant_type": 'refresh_token',
        }
        response = rs.post(url=url, data=data, headers=header)
        access_token(json.loads(response.text))

    def get_access_token(self, scope, config_path=PATH_client_secret):
        if os.path.exists(PATH + '/token_config.json') is False:
            self.first_get_token(scope, config_path)
        else:
            self.refresh_token(config_path)
        return get_access_token_config()


class GoogleSheet:
    def __init__(self, scope, sheet_id):
        self.access_token = GoogleOAuth2().get_access_token(scope)
        self.sheet_id = sheet_id
        self.sheet_header = {'Authorization': 'Bearer ' + self.access_token}

    def read_sheet(self, sheet_no, begin_cell, end_cell):
        read_url = 'https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}!{}:{}'.format(self.sheet_id, sheet_no,
                                                                                             begin_cell, end_cell)
        response = rs.get(url=read_url, headers=self.sheet_header)
        print(response.text)
        result = json.loads(response.text)['values']
        return result

    # def write_sheet(self):




if __name__ == '__main__':
    GS = GoogleSheet('https://www.googleapis.com/auth/spreadsheets', '1OnABAiAUjIQTDlkJZnzLx2eybzRviJ5kEzJQic-oTdE')
    sheet = GS.read_sheet('api', 'A1', 'G')
    print(sheet)
