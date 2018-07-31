from flask import Flask, request, jsonify
import subprocess
import string
import random
import redis
from os import chmod, getenv, path
from dotenv import load_dotenv
from shutil import copy

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
MAKE_CONFIG_EXECUTABLE = '/home/ubuntu/client-configs/make_config.sh'
FINAL_OPENVPN_CONFIG_DIRECTORY = '/home/ubuntu/client-configs/files/'

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
        path_to_output_openvpn_config = path.join(FINAL_OPENVPN_CONFIG_DIRECTORY, '{}.ovpn'.format(filename))
        if not path.exists(path_to_output_openvpn_config):
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
            copy(path_to_full_key, FINISHED_KEY_LOCATION)
            copy(path_to_full_cert, FINISHED_KEY_LOCATION)
            try:
                make_config_command = "sudo {} {}".format(MAKE_CONFIG_EXECUTABLE, filename)
                print('Running: {}'.format(make_config_command))
                subprocess.Popen(make_config_command, shell=True)
            except Exception as exception:
                    print('Unable to generate final OpenVPN configuration: {}'.format(exception))
                    return b"Failed to generate configuration", 500
        with open(path.join(FINAL_OPENVPN_CONFIG_DIRECTORY, '{}.ovpn'.format(filename))) as final_openvpn_config:
            return jsonify({"config": final_openvpn_config.read()})
    return b"Only POSTing allowed", 405
