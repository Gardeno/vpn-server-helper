import subprocess
import shutil

users = [x for x in subprocess.check_output(["ls", "/home"]).decode("utf8").strip().split('\n') if x != 'ubuntu']

for user in users:
    subprocess.call(['deluser', user])
    shutil.rmtree('/home/{}'.format(user))
