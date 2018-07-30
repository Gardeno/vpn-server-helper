# Setting up a tunnel server

```
sudo apt-get update && sudo apt-get install -y binutils libproj-dev gdal-bin postgresql-client supervisor nginx vim python3-pip htop redis-server
sudo pip3 install --upgrade pip
sudo pip3 install uwsgi virtualenv
cd ~ && git clone https://github.com/Gardeno/tunnel-server.git && cd tunnel-server
virtualenv -p python3 venv && ./venv/bin/pip install -r requirements.txt
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /home/ubuntu/tunnel-server/conf/nginx/tunnel.gardeno.global /etc/nginx/sites-enabled/tunnel.gardeno.global
sudo ln -s /home/ubuntu/tunnel-server/conf/supervisor/tunnel.gardeno.global.conf /etc/supervisor/conf.d/tunnel.gardeno.global.conf
echo -e 'TUNNEL_SERVER="tunnel.gardeno.global"\nTUNNEL_KEY="ENTER_YOUR_KEY_HERE"' > /home/ubuntu/tunnel-server/.env
sudo mkdir /var/log/tunnel.gardeno.global
sudo chown www-data:www-data /var/log/tunnel.gardeno.global/
sudo service nginx restart && sudo service supervisor restart
```

# Notes

Make sure to add `GatewayPorts yes` to `/etc/ssh/sshd_config`

Setting up iptables rules:

```
sudo iptables -I OUTPUT -p tcp --dport 22 -m owner --uid-owner ubuntu -j ACCEPT
sudo iptables -P INPUT DROP
```