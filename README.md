# Setting up a tunnel server

- Install OpenVPN and OpenVPN CA according to the following guide: 

https://www.digitalocean.com/community/tutorials/how-to-set-up-an-openvpn-server-on-ubuntu-18-04

Use the `conf/openvpn/server.conf` file to extend that tutorial. Create a directory at `/home/ubuntu/clients/{config,setup}`
instead of using `~/client-configs`. For now, CA and server are together in the current dev environment

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
echo -e 'TUNNEL_SERVER="vpn.gardeno.global"\nSECRET_KEY="ENTER_YOUR_KEY_HERE"' > /home/ubuntu/vpn-server-helper/.env
sudo mkdir /var/log/vpn.gardeno.global
sudo chown www-data:www-data /var/log/vpn.gardeno.global/
sudo service nginx restart && sudo service supervisor restart
```

# IP Tables

Backup / restore to avoid reboot:

```
iptables-save > /opt/iptables.backup
iptables-restore < /opt/iptables.backup
```

```
iptables -I FORWARD -s 13.0.0.0/16 --jump REJECT --protocol all
# Allow clients to access their own subnet
iptables -I FORWARD -s 13.0.16.0/20 -d 13.0.16.0/20 --jump ACCEPT --protocol all
iptables -I FORWARD -s 13.0.32.0/20 -d 13.0.32.0/20 --jump ACCEPT --protocol all
```
