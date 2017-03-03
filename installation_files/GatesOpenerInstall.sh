sudo apt update
#Python3 e i componenti necessari
sudo apt install python3-dev -y
sudo apt install python3-pip -y
sudo pip3 install --upgrade pip
sudo pip3 install setuptools
sudo pip3 install Flask
sudo pip3 install pymysql
sudo pip3 install RPi.GPIO
#MySQL 
sudo apt-get install mysql-server mysql-common mysql-client -y
#esecuzione query
mysql -u root -p < script_db.sql

sed -i "s/192.168.1.50/192.168.1.228/g" *.*
