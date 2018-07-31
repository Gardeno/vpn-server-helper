# Setting up a tunnel server

- Install OpenVPN and OpenVPN CA according to the following guide: 

https://www.digitalocean.com/community/tutorials/how-to-set-up-an-openvpn-server-on-ubuntu-18-04

- Install the VPN HTTP Server

```
sudo apt-get update && sudo apt-get install -y binutils libproj-dev gdal-bin supervisor nginx vim python3-pip htop redis-server
sudo pip3 install --upgrade pip
sudo pip3 install uwsgi virtualenv
cd ~ && git clone https://github.com/Gardeno/vpn-server-helper.git && cd vpn-server-helper
virtualenv -p python3 venv && ./venv/bin/pip install -r requirements.txt
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /home/ubuntu/vpn-server-helper/conf/nginx/vpn.gardeno.global /etc/nginx/sites-enabled/vpn.gardeno.global
sudo ln -s /home/ubuntu/vpn-server-helper/conf/supervisor/vpn.gardeno.global.conf /etc/supervisor/conf.d/vpn.gardeno.global.conf
echo -e 'TUNNEL_SERVER="vpn.gardeno.global"\nTUNNEL_KEY="ENTER_YOUR_KEY_HERE"' > /home/ubuntu/vpn-server-helper/.env
sudo mkdir /var/log/vpn.gardeno.global
sudo chown www-data:www-data /var/log/vpn.gardeno.global/
sudo service nginx restart && sudo service supervisor restart
```
