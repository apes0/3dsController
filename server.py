# this is the server for the 3ds to connect
# it uses a socket server to run
#
# the buttons are gotten like an intiger
# the url requested would look like this:
#
# ip:port/<input>
# ^   ^      ^
# |   |      |
# |   |      |- the pressed buttons (number)
# |   |-------- the servers port
# |------------ the servers ip
#
# the input is just an int that has each bit assigned to a different button
# it looks like this:
#
# 1 0 0 1 0 ...
# ^ ^ ^ ^ ^
# | | | | |
# | | | | |- button not pressed
# | | | |--- button pressed
# | | |----- button not pressed
# | |------- button not pressed
# |--------- button pressed
#
# all the config variables are in serverConfig.json
# button mappings are stored in the folder "configs"

import os
import json
import keyboard
import socket
import struct
import signal
import sys

script_dir = os.path.dirname(__file__)  # get script directory

rel_path = 'serverConfig.json'
abs_file_path = os.path.join(script_dir, rel_path) # open the config file for the server
with open(abs_file_path) as f:
    config = json.loads(f.read())

options = os.listdir(os.path.join(script_dir, 'configs')) # find all config files

print('available configs:')
for i in range(len(options)): # print all options
    opt = options[i]
    print(f'{i}. {opt[:-5]}')

opt = int(input('choose a config to use: '))

if not opt:
    opt = config['default'] # get the defualt config if none is specified

rel_path = options[opt] # get file name
abs_file_path = os.path.join(script_dir, 'configs', rel_path) # open the config file
with open(abs_file_path) as f:
    buttons = json.loads(f.read())

pressed = [] # all pressed buttons

def parse(inp):
    for value in buttons.keys():
        button = buttons[value] # get button to click
        value = int(value) # get button value
        if value & int(inp): # check if the bites are the same
            if value not in pressed: # this if is inside, so that we dont trigger the elif
                pressed.append(value) # add the button to the list with pressed buttons
                keyboard.press(button) # press the button
                print(f'pressing {button} ({value})')
        elif value in pressed: # check if the button was pressed, but isn't anyomre
            pressed.remove(value) # remove the button from the list wit hpressed buttons
            keyboard.release(button) # release the button
            print(f'releasing {button} ({value})')
#        print(pressed, value, button)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    def signal_handler(_, __):
        s.close() # close the socket
        sys.exit(0) # exit from the program
    signal.signal(signal.SIGINT, signal_handler) # set a handler for SIGINT
    s.bind((config['host'], config['port'])) # bind to the adress
    while True:
        s.listen() # listen for input
        conn, addr = s.accept() # accept the input
        while True:
            data = conn.recv(4) # get the data
            out = struct.unpack('!I', data)[0] # unpact the data and get the int inside of it
            parse(out) # parse the input