#!/bin/sh

# エラー時に停止
set -e

# 接続先ユーザ名・ホスト名・パス・ファイル名
remote_user="kbit01"
remote_host="133.92.145.205"
remote_file="~/attendance_system/data.json"
local_file="data.json"
remote_key="key/id_rsa"

eval "$(ssh-agent -s)"

ssh-add $remote_key

echo "JSONファイルを取得"
scp -i $remote_key -oStrictHostKeyChecking=no "$remote_user@$remote_host:$remote_file" .

echo "データベースに保存"
python json_read.py

echo "JSONファイルを初期化"
echo "[]" > $local_file

sleep 1

echo "空のJSONファイルを送信中"
scp -i $remote_key -oStrictHostKeyChecking=no $local_file "$remote_user@$remote_host:$remote_file" 

echo "JSONファイルを削除"
rm $local_file

ssh-agent -k
