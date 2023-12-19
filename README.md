# Attendance_System
出席管理システム

# 構築方法
key作成
(例)
```
ssh-keygen -q -t rsa -N '' -f ~/Attendance_System/flask/app/key/id_rsa
```
pubkeyをラズパイに配置

コンテナ構築
```
docker compose up
```

# 設定変更
## ラズパイとの接続について
- ラズパイのIPは``/flask/app/script.sh``に記載している．必要であれば変更する．
