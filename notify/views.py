from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect

import requests, base64, json
import datetime

from .private_val import CLIENT_ID, CLIENT_SECRET, LINE_ACCESS_TOKEN, URI

def index(requst):
    return HttpResponse("Hello")

def auth(request):
    '''認証ページへリダイレクトさせる'''

    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET

    # このif文内の処理をUIではなくコードビハインドで処理したい
    if 'code' not in request.GET:
        print('get code')
        auth_url = 'https://zoom.us/oauth/authorize'
        response_type = 'code'
        # ngrokでlocalhostをSSL形式でアクセスできるようにする
        redirect_uri = URI + '/notify/auth'

        auth_href = auth_url + '?response_type=' + response_type + '&client_id=' + client_id + '&redirect_uri=' + redirect_uri
        
        # return render(request, 'auth/auth.html', {
        #     'auth_href': auth_href
        # })

        return HttpResponseRedirect(auth_href)
    else:
        print('get token')
        auth_url = 'https://zoom.us/oauth/token'
        code = request.GET.get('code')
        grant_type = 'authorization_code'
        redirect_uri = URI + '/notify/auth'

        # basic認証用のコードを作成（client_ID:Client_Secretをbase64エンコード）
        client_basic = base64.b64encode('{0}:{1}'.format(client_id, client_secret).encode())

        # POST用のパラメータとカスタムヘッダを作成する
        post_payload = {
            'code': code,
            'grant_type': grant_type,
            'redirect_uri': redirect_uri
        }
        post_header = {
            # base64エンコードした状態だとbyte形式となるので.decode()でString形式に変換する
            'Authorization': 'Basic {0}'.format(client_basic.decode())
        }

        # # Exec POST
        response = requests.post(auth_url, data=post_payload, headers=post_header)
        response_text = json.loads(response.text)

        if 'access_token' in response_text:
            # 認証結果をセッションに保存
            request.session['zoom_access_token'] = response_text['access_token']
            request.session['zoom_token_type'] = response_text['token_type']
            request.session['zoom_refresh_token'] = response_text['refresh_token']
            request.session['zoom_expires_in'] = response_text['expires_in']
            request.session['zoom_scope'] = response_text['scope']

            return redirect('zoom_auth_complete')
        else:
            return render(request, 'auth/auth.html', {
                'auth_href': ''
            })

def auth_complete(request):
    '''認証完了ページ'''
    get_user_url = 'https://api.zoom.us/v2/users'
    access_token = request.session['zoom_access_token']

    # ユーザー情報の取得
    get_user_headers = {
        'Authorization': 'Bearer {0}'.format(access_token)
    }
    get_user_response = requests.get(get_user_url, headers=get_user_headers)
    get_user_response_text = json.loads(get_user_response.text)
    user_info = get_user_response_text['users'][0]

    # ミーティング情報の取得
    get_list_meetings_url = 'https://api.zoom.us/v2/users/'+ user_info['id'] +'/meetings'
    get_list_meetings_headers = {
        'Authorization': 'Bearer {0}'.format(access_token)
    }
    get_list_meetings_response = requests.get(get_list_meetings_url, headers=get_list_meetings_headers, params={
        'type': 'upcoming',
    })
    get_list_meetings_response_text = json.loads(get_list_meetings_response.text)
    
    # LINE Notifyによる通知
    print('Notify the most upcoming lesson.')
    most_upcoming_lesson = get_list_meetings_response_text['meetings'][0]
    notify(most_upcoming_lesson)

    return render(request, 'auth/complete.html', {
        'response_text': get_list_meetings_response_text['meetings']
    })

# LINENotifyでメッセージを送信
def notify(most_upcoming_lesson):
    # 直近ミーティングの情報を取得し加工
    month = most_upcoming_lesson['start_time'][5:7][1] if most_upcoming_lesson['start_time'][5:7][0] == '0' else most_upcoming_lesson['start_time'][5:7]
    day = most_upcoming_lesson['start_time'][8:10][1] if most_upcoming_lesson['start_time'][8:10][0] == '0' else most_upcoming_lesson['start_time'][8:10]
    hour = int(most_upcoming_lesson['start_time'][12])+9
    minute = most_upcoming_lesson['start_time'][14:16]
    time = str(hour)+':'+str(minute)
    start_time = month+'月'+day+'日'+time
    join_url = most_upcoming_lesson['join_url']
    
    # レッスン前日にメッセージ通知
    dt_today = datetime.datetime.now()
    if int(dt_today.day) - int(day) < 1:
    # if True:
        # LINE Notifyにリクエスト
        url = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN}
        message = 'こんにちは！\n'+start_time+'開始のレッスンは下記のリンク先にあるZoom Meetingをご利用ください😌\n'+join_url
        payload = {'message': message}
        r = requests.post(url, headers=headers, params=payload)