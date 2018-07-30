# Setting up a tunnel server

```
sudo apt-get update && sudo apt-get install -y binutils libproj-dev gdal-bin postgresql-client supervisor nginx vim python3-pip htop redis-server
sudo pip3 install --upgrade pip
sudo pip3 install uwsgi
git clone https://github.com/Gardeno/tunnel-server.git
cd tunnel-server && virtualenv -p python3 venv && ./venv/bin/pip install -r requirements.txt
sudo ln -s /home/ubuntu/tunnel-server/conf/nginx/tunnel.gardeno.global /etc/nginx/sites-enabled/tunnel.gardeno.global
sudo ln -s /home/ubuntu/tunnel-server/conf/supervisor/tunnel.gardeno.global.conf /etc/supervisor/conf.d/tunnel.gardeno.global.conf
echo -e 'TUNNEL_SERVER="tunnel.gardeno.global"\nTUNNEL_KEY="ENTER_YOUR_KEY_HERE"' > /home/ubuntu/tunnel-server/.env
sudo service nginx restart && sudo service supervisor restart
```