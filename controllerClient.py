# this is the 3ds client for the server
# it uses sokets and makes requests like this:
#
# ip:port/<input>
# ^   ^      ^
# |   |      |
# |   |      |- the pressed buttons (number)
# |   |-------- the servers port
# |------------ the servers ip
#
# the buttons are gotten from the _ctru(libctru in c) library
#
# all the config variables are in clientConfig.json

import _ctru
import socket
import os
import json
import struct

script_dir = os.path.dirname(__file__)  # get script directory

rel_path = 'clientConfig.json'
abs_file_path = os.path.join(script_dir, rel_path) # open the config file for the client
with open(abs_file_path) as f:
    config = json.loads(f.read())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket

port = config['port'] # get the port of the server
host = config['host'] # get the ip adress of the server

s.connect((host, port,))

def update(key_mask):
    packed = struct.pack('!I', key_mask)

    print(f'sending buttons ({key_mask})', flush=True)
    s.sendall(packed) # send request

print('done loading', flush=True)

old_mask = 0

while True:
    _ctru.hid_scan_input()
    key_mask = _ctru.hid_keys_held() # get held keys
    if old_mask != key_mask:
        update(key_mask) # tell the server about the change
    old_mask = key_mask