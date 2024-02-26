# Attendance_System

出席管理システム

# 構築方法

サーバ側とラズパイ側の2つをセットアップする必要があります。

<!-- ## ラズパイ側

64BitのDesktop版のOSをインストール（最小インストールでよい）

1. 更新しておく

```
sudo apt update && sudo apt upgrade -y
```

2. クローン

```
git clone https://github.com/SLP-KBIT/Attendance_System.git pi-attendance
```

3. 実行

※CLIでは、実行できないのでVNCなどを使用する（解決案募集中）

```
cd pi-attendance && python main.py
``` -->

## サーバ側

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