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
import time



def sleep(seconds): # the defualt sleep function from the time module doesnt work, so we need to use this
    start = time.monotonic()
    while(time.monotonic() < start + seconds):
        pass
    return


script_dir = os.path.dirname(__file__)  # get script directory

rel_path = 'clientConfig.json'
abs_file_path = os.path.join(script_dir, rel_path) # open the config file for the client
with open(abs_file_path) as f:
    config = json.loads(f.read())



def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket

    port = config['port'] # get the port of the server
    host = config['host'] # get the ip adress of the server

    print(f'connecting to {host} at {port}...')
    try:
        s.connect((host, port,)) # connect to the server
    except:
        return False
    
    return s

s = connect()

def reconnect():
    global s # get the socket variable
    delay = config['reconnect'] # get the amount of reconnects before stopping
    while delay: # try to reconnect
        s = connect()
        print('reconnecting...', flush=True)
        if s: # if a connection is made, return
            print('connected!')
            return
        sleep(5) # wait for 5 seconds untill reconnecting
        delay -= 1
    exit() # exit if the connection never comes back



def update(key_mask):
    packed = struct.pack('!I', key_mask) # pack the current key mask

    print(f'sending buttons ({key_mask})...', flush=True)
    try:
        s.sendall(packed) # send request
    except:
        s.close()
        reconnect()



wait_frames = config['delay'] # frames to wait between checking inputs

old_mask = 0 # old key mask
frames = wait_frames # frame counter for the time from the last input



while True:
    _ctru.hid_scan_input()
    key_mask = _ctru.hid_keys_held() # get held keys
    if old_mask != key_mask and frames > wait_frames:
        update(key_mask) # tell the server about the change
        frames = 0 # set the old frame counter to 0
    old_mask = key_mask # set the old keymask to the current one
    frames += 1 # increase the frame counter