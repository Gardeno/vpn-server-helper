from flask import Flask, request, jsonify
import subprocess
import string
import random
import redis
from os import chmod, getenv, path
from dotenv import load_dotenv
from shutil import copyfile

from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend

from pathlib import Path

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=str(env_path))

REDIS_KEY_USER_INCREMENT = 'user-ids'
REDIS_KEY_USERS_HASH = 'users'

ALLOWED_TYPES = ["administrator", "core", "sensor"]

PATH_TO_EASY_RSA = "/home/ubuntu/EasyRSA-3.0.4/"
FINISHED_KEY_LOCATION = '/home/ubuntu/client-configs/keys/'

app = Flask(__name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


def id_generator(size=20, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


if not redis_client.get(REDIS_KEY_USER_INCREMENT):
    redis_client.set(REDIS_KEY_USER_INCREMENT, '2000')


@app.route('/', methods=['POST', 'GET'])
def main():
    secret_key = request.args.get('secret_key')
    if secret_key != getenv("SECRET_KEY"):
        return b"Invalid secret_key GET parameter", 401
    if request.method == 'POST':
        if not request.json:
            return b"Must post JSON with Content-Type application/json", 400
        if "grow_id" not in request.json:
            return b"Missing `grow_id` in POSTed JSON", 400
        if "type" not in request.json or request.json["type"] not in ALLOWED_TYPES:
            return "Missing `type` in POSTed JSON (must be one of {})".format(", ".join(ALLOWED_TYPES)), 400
        filename = '{}-{}'.format(request.json["grow_id"], request.json["type"])
        path_to_full_key = path.join(PATH_TO_EASY_RSA, 'pki/private', '{}.key'.format(filename))
        path_to_full_cert = path.join(PATH_TO_EASY_RSA, 'pki/issued', '{}.crt'.format(filename))
        if not path.exists(path_to_full_key):
            try:
                subprocess.Popen(['./easyrsa', 'gen-req', filename, 'nopass', 'batch'], cwd=PATH_TO_EASY_RSA)
            except Exception as exception:
                print('Unable to generate key: {}'.format(exception))
                return b"Failed to generate key", 500
        if not path.exists(path_to_full_cert):
            try:
                subprocess.Popen(['./easyrsa', 'sign-req', 'client', filename, 'batch'], cwd=PATH_TO_EASY_RSA)
            except Exception as exception:
                print('Unable to sign request: {}'.format(exception))
                return b"Failed to sign request", 500
        copyfile(path_to_full_key, FINISHED_KEY_LOCATION)
        copyfile(path_to_full_cert, FINISHED_KEY_LOCATION)

        '''
        # TODO : Only allow port 80 access from VPC
        username = id_generator()
        user_id = redis_client.incr(REDIS_KEY_USER_INCREMENT)
        if int(user_id) > 60000:
            return b"Number of users have been exceeded for this tunnel", 500
        redis_client.hset(REDIS_KEY_USERS_HASH, user_id, username)
        subprocess.call(["useradd", "-m", username])
        subprocess.call(["usermod", "-s", "/bin/false", username])
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
        with open(authorized_keys_location, 'w') as content_file:
            chmod(authorized_keys_location, 0o600)
            content_file.write('no-pty,permitopen="localhost:{}"\n{}'.format(user_id, public_key))
        subprocess.call(["chown", "{}:{}".format(username, username), "-R", "/home/{}/.ssh".format(username)])
        return jsonify({"user": {"id": user_id, "username": username}, "server": getenv('TUNNEL_SERVER'),
                        "keys": {"private": str(private_key, 'utf-8'), "public": str(public_key, 'utf-8')}})
        '''
        return jsonify({"success": True})
    return b"Only POSTing allowed", 405
