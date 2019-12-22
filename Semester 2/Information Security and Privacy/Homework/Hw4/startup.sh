#!/bin/bash

PROD="true"
SEED="randomseed"
ROOT_PWD="root"
DATABASE="hw4_ex3"

if [ $# -gt 1 ]; then
    PROD="true"
    SEED=$1
    shift
fi

echo "[+] Launching MySQL "
sudo mysqld_safe --user=root 2>&1 &
sleep 5
sudo mysqladmin -u root password "$ROOT_PWD" 2>&1
tfile=`mktemp`

cat > $tfile <<HERE
SET @@SESSION.SQL_LOG_BIN=0;
DROP DATABASE IF EXISTS test;

CREATE DATABASE IF NOT EXISTS $DATABASE;
USE $DATABASE;
CREATE TABLE users(id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                   name varchar(100) not null,
                   password varchar(100) not null);

CREATE TABLE messages(name varchar(100) not null,
                      message varchar(200) not null);
HERE

echo "[+] creating database and tables"
sudo mysql -uroot -p$ROOT_PWD < $tfile 2>&1
rm $tfile

if [ "$PROD" == "true" ]; then
    echo "[+] Launching flask web app in background, seed $SEED"
    python3 site.py $SEED 2>&1 &
    sleep 1
fi

echo "[+] Launching bash shell with $@"
$@
