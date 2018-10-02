# -*- coding: utf-8 -*-
# __author__ = 'Gz'
import datetime
import json
import requests

# 权限
# 只允许读sheet
# scope = 'https://www.googleapis.com/auth/spreadsheets.readonly'
# sheet读写权限
scope = 'https://www.googleapis.com/auth/spreadsheets'
# for spark
client_id = '264584935389-b7l2ogdjqgs362o7qtilmlvdm2tk12ij.apps.googleusercontent.com'
client_secret = "h2MoUfqxY2wDY3CaEygOaqnn"
authorization_code = 'refresh_token'
# 第一次使用
# authorization_code = 'authorization_code'
redirect_uri = 'http://localhost'
# 获取code的url
URL = 'https://accounts.google.com/o/oauth2/v2/auth?scope={}&' \
      'access_type=offline&' \
      'include_granted_scopes=true&' \
      'redirect_uri={}&' \
      'response_type=code&' \
      'client_id={}&' \
      'prompt=consent'.format(scope, redirect_uri, client_id)
# 读写权限code
code = '4/AACDx-2x8jaISdRTmW0ctm7vReyty1lP-J7e_wNLkrTNTQ77NNY-0Wv0abXnXysIIL87zSyivseEGpeT5hvVjdg'

# 获取token的body
get_token_data_body = 'code=%s&' \
                      'client_id=%s&' \
                      'client_secret=%s&' \
                      'redirect_uri=%s&' \
                      'grant_type=%s' % (code, client_id, client_secret, redirect_uri, 'authorization_code')
# refresh的body
refresh_token = '1/tjpnv6htQUb-51PkJZVeSx_FBoroUOb7WRuD6zKRH9Q'
refresh_token_data = 'client_id={}&' \
                     'client_secret={}&' \
                     'refresh_token={}&' \
                     'grant_type=refresh_token'.format(client_id, client_secret, refresh_token)


def get_token_data():
    # 授权页拿去code
    # 授权后在url中取code
    print(URL)
    # 获取token data等
    header = {'Host': 'www.googleapis.com', 'Content-Type': 'application/x-www-form-urlencoded'}
    get_token_url = 'https://www.googleapis.com/oauth2/v4/token'
    # 获取token
    # response = requests.post(url=get_token_url, data=get_token_data_body, headers=header)
    # 刷新token
    response = requests.post(url=get_token_url, data=refresh_token_data, headers=header)
    print(get_token_url)
    print(response)
    print(response.text)
    return json.loads(response.text)['access_token']


# sheet_header = {'Authorization': 'Bearer ' + token_data['access_token']}
sheet_id = '16u0AOOm1vRFRBkyE32OlM8xJEQPlp0tLPXuRi3S7nR4'


def add_data(get_data):
    result_add_data = []
    today = str(int(str(datetime.date.today()).replace('-', '')) - 1)
    temp_order = ['all', 'KikaEnUsScenario', 'EnUsBeforeNotMod2Scenario', 'EnUsBeforeMod2Secnario',
                  'EnNotUsBeforeScenario',
                  'PtSecnario']
    # for i in list(get_data.keys()):
    for i in temp_order:
        if i == 'all':
            result_add_data.append([today, 'all', get_data[i]['sessionId_count'], get_data[i]['only_train_sessionId'],
                                    get_data[i]['noly_p_sessionId_count'], get_data[i]['t_p_sessionId_count'],
                                    get_data[i]['all_duid_tag'], get_data[i]['once_duid_tag'],
                                    get_data[i]['once_duid_tag_item'], get_data[i]['more_duid_tag_item']])
        else:
            result_add_data.append(['', i, get_data[i]['sessionId_count'], get_data[i]['only_train_sessionId'],
                                    get_data[i]['noly_p_sessionId_count'], get_data[i]['t_p_sessionId_count'],
                                    get_data[i]['all_duid_tag'], get_data[i]['once_duid_tag'],
                                    get_data[i]['once_duid_tag_item'], get_data[i]['more_duid_tag_item']])
    return result_add_data


def get_sheet_data(sheetname, begin_cell, end_column, sheet_header):
    sheet = sheetname + '!'
    bengein = begin_cell
    row_end = end_column
    url = 'https://sheets.googleapis.com/v4/spreadsheets/' + sheet_id + '/values:batchGet?ranges=' + sheet + bengein + ':' + row_end
    response = requests.get(url, headers=sheet_header)
    # print(response.text)
    sheet_data = json.loads(response.text)['valueRanges'][0]['values']
    return {'sheet_data': sheet_data, 'row_count': len(sheet_data)}


def write_sheet(sheetname, begin_column, end_column, count_row, sheet_header, add_data):
    sheet = sheetname + '!'
    begin = begin_column + str(count_row + 1)
    end = end_column + str(count_row + len(add_data))
    input_range = sheet + begin + ':' + end
    url = 'https://sheets.googleapis.com/v4/spreadsheets/' + sheet_id + '/values:batchUpdate'
    # 用户填写什么是什么如果是公式类型会直接解析
    data = {"valueInputOption": 'USER_ENTERED', "data": [{"range": input_range, "values": add_data}, ]}
    response = requests.post(url, json=data, headers=sheet_header)
    print(response.text)


def copy(sheetId, begin_column_number, end_column_number, copy_space, count_row, sheet_header):
    copy_bengin = count_row - copy_space
    copy_end = count_row
    bengin = count_row
    end = count_row + copy_space
    url = 'https://sheets.googleapis.com/v4/spreadsheets/' + sheet_id + ':batchUpdate'
    data = {
        "requests": [
            {"copyPaste": {
                "source": {
                    "sheetId": sheetId,
                    "startRowIndex": copy_bengin,
                    "endRowIndex": copy_end,
                    "startColumnIndex": begin_column_number,
                    "endColumnIndex": end_column_number,
                },
                "destination": {
                    "sheetId": sheetId,
                    "startRowIndex": bengin,
                    "endRowIndex": end,
                    "startColumnIndex": begin_column_number,
                    "endColumnIndex": end_column_number,
                },
                "pasteType": 'PASTE_NORMAL',
                "pasteOrientation": 'NORMAL', },
            }]}
    response = requests.post(url, json=data, headers=sheet_header)
    print(response.text)


def append(sheetname, begin_column, end_column, count_row, sheet_header, add_data):
    sheet = sheetname + '!'
    begin = begin_column + str(count_row + 1)
    end = end_column + str(count_row + len(add_data))
    input_range = sheet + begin + ':' + end
    url = 'https://sheets.googleapis.com/v4/spreadsheets/' + sheet_id + '/values/' + input_range + ':append?valueInputOption=RAW'
    data = {"valueInputOption": 'RAW', "data": [{"range": input_range, "values": add_data}, ]}
    response = requests.post(url, json=data, headers=sheet_header)
    print(response.text)


if __name__ == '__main__':
    get_data = {}
    token = get_token_data()
    print(token)
    # 登录token
    sheet_header = {'Authorization': 'Bearer ' + token}
    sheet_data = get_sheet_data('场景duid变化', 'A1', 'M', sheet_header)
    row_count = sheet_data['row_count']
    print(row_count)
    # copy(0, 0, 14, row_count, 7, sheet_header)
    add_number = 2 + (row_count - 1) * 7
    column = 'C'
    data = [["='训练的sessionId和duid数量统计'!A" + str(add_number), '', "='训练的sessionId和duid数量统计'!C" + str(add_number), '',
             "='训练的sessionId和duid数量统计'!" + column + str(add_number + 1), '',
             "='训练的sessionId和duid数量统计'!" + column + str(add_number + 2), '',
             "='训练的sessionId和duid数量统计'!" + column + str(add_number + 3), '',
             "='训练的sessionId和duid数量统计'!" + column + str(add_number + 4), '',
             "='训练的sessionId和duid数量统计'!" + column + str(add_number + 5)]]
    write_sheet(sheetname='场景duid变化', begin_column='A', end_column='M', count_row=row_count,
                sheet_header=sheet_header, add_data=data)
