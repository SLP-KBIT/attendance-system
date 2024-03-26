# Attendance_System

出席管理システム

# 構築方法

1. クローン

```
git clone https://github.com/SLP-KBIT/Attendance_System.git
```

2. ラズパイのIPアドレス、ユーザ名を``./app/script.sh``に記載する

3. SSH鍵を作成

```
ssh-keygen -q -t rsa -N '' -f ./app/key/id_rsa
```

4. ``./app/key/id_rsa.pub``をラズパイ側の``./ssh/authorized_keys``として配置する

5. コンテナ構築

```
docker network create attendance-network && docker compose up -d
```