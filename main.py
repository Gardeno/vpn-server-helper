from flask import Flask, request, jsonify
import subprocess
import string
import random
import redis
from os import chmod, getenv
from dotenv import load_dotenv

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=str(env_path))

REDIS_KEY_USER_INCREMENT = 'user-ids'
REDIS_KEY_USERS_HASH = 'users'

if not redis.get(REDIS_KEY_USER_INCREMENT):
    redis.set(REDIS_KEY_USER_INCREMENT, '2000')


def id_generator(size=20, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


app = Flask(__name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


@app.route('/', methods=['POST', 'GET'])
def main():
    tunnel_key = request.args.get('tunnel_key')
    if tunnel_key != getenv("TUNNEL_KEY"):
        return b"Invalid tunnel_key GET parameter", 401
    if request.method == 'POST':
        # TODO : Only allow port 80 access from VPC
        username = id_generator()
        user_id = redis_client.incr(REDIS_KEY_USER_INCREMENT)
        redis_client.hset(REDIS_KEY_USERS_HASH, user_id, username)
        subprocess.call(["useradd", "-m", username])
        subprocess.call(["mkdir", "-p", "/home/{}/.ssh".format(username)])
        key = rsa.generate_private_key(
            backend=crypto_default_backend(),
            public_exponent=65537,
            key_size=2048
        )
        private_key = key.private_bytes(
            crypto_serialization.Encoding.PEM,
            crypto_serialization.PrivateFormat.TraditionalOpenSSL,
            crypto_serialization.NoEncryption()
        )
        public_key = key.public_key().public_bytes(
            crypto_serialization.Encoding.OpenSSH,
            crypto_serialization.PublicFormat.OpenSSH
        )
        authorized_keys_location = "/home/{}/.ssh/authorized_keys".format(username)
        with open(authorized_keys_location, 'wb') as content_file:
            chmod(authorized_keys_location, 0o600)
            content_file.write(public_key)
        subprocess.call(["chown", "{}:{}".format(username, username), "-R", "/home/{}/.ssh".format(username)])
        return jsonify({"user": {"id": user_id, "username": username}, "server": getenv('TUNNEL_SERVER'),
                        "keys": {"private": str(private_key, 'utf-8'), "public": str(public_key, 'utf-8')}})
    return b"Only POSTing allowed", 405
