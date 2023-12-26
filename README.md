# Attendance_System
出席管理システム

# 構築方法
1. key作成(テストの場合は必要ない)
(例)
```
ssh-keygen -q -t rsa -N '' -f ~/Attendance_System/flask/app/key/id_rsa
```

2. pubkeyをラズパイに配置(テストの場合は必要ない)

3. コンテナ構築
```
docker compose up
```

# 設定変更
- ラズパイのIPは``/flask/app/script.sh``に記載している．必要であれば変更する．
- main.pyの``debug``を``False``にする．
