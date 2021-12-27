# KRManager
## 概要
毎週発生するZoomミーティング情報のLINEメッセージ送信を自動化した。

/// イメージ図を挿入 ///

## LINE自動通知
主にDjangoを用いて、以下の処理を行った。
- Zoom APIを用いたミーティング情報の取得
- LINE Notifyを用いたメッセージ通知

## Zoom自動ログイン
ZoomのAPI認証時に必要なログインは、WebクローラーであるSeleniumを用いて自動化した。

## プログラムの自動実行
以下のコマンドを記したシェルスクリプトを作成し、rontabを用いて毎週土曜日に定期的に実行する。
- ローカル環境を一時的に外部公開：ngrok http <ポート番号>
- ローカルサーバの起動：python3 manage.py runserver <ポート番号>
- Zoom APIの認証ページに遷移：python3 access.py
