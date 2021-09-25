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


import json
import os
import signal
import socket
import struct
import sys
import time

import keyboard

script_dir = os.path.dirname(__file__)  # get script directory

rel_path = 'serverConfig.json'
# open the config file for the server
abs_file_path = os.path.join(script_dir, rel_path)
with open(abs_file_path) as f:
    config = json.loads(f.read())


options = os.listdir(os.path.join(script_dir, 'configs')
                     )  # find all config files

print('available configs:')
for i in range(len(options)):  # print all options
    opt = options[i]
    print(f'{i}. {opt[:-5]}')

opt = input('choose a config to use: ')

if not opt:
    opt = config['default']  # get the defualt config if none is specified

opt = int(opt)

rel_path = options[opt]  # get file name
abs_file_path = os.path.join(
    script_dir, 'configs', rel_path)  # open the config file
with open(abs_file_path) as f:
    buttons = json.loads(f.read())


pressed = []  # all pressed buttons
values = []  # values of all pressed buttons


start = 0


def parse(inp):
    for value, button in buttons.items():
        value = int(value)  # get button value
        if value & int(inp):  # check if the bites are the same
            if value not in values:  # check if the button is already pressed
                keyboard.press(button)  # press the button
                print(f'pressing {button} ({value})')
                # add the button to the list with pressed buttons
                pressed.append(button)
                # add the button to the list with the values of all buttons
                values.append(value)
        elif value in values:  # check if the button was pressed, but isn't anyomre
            # remove the button from the list wit hpressed buttons
            pressed.remove(button)
            if button not in pressed:  # check if the button should not remain pressed
                keyboard.release(button)  # release the button
                print(f'releasing {button} ({value})')
            # remove the button from the list with all values
            values.remove(value)
#        print(pressed, value, button)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    def signal_handler(_, __):
        s.close()  # close the socket
        sys.exit(0)  # exit from the program
    signal.signal(signal.SIGINT, signal_handler)  # set a handler for SIGINT
    s.bind((config['host'], config['port']))  # bind to the adress
    lastPing = 0
    ping = 0  # seconds
    avrPing = 0  # seconds
    pingMeasurements = 0
    while True:
        s.listen()  # listen for input
        conn, addr = s.accept()  # accept the input
        while True:
            data = conn.recv(1)  # get the data
            if data == b'\x00':  # ping
                ping = time.time() - lastPing
                pingMeasurements += 1
                avrPing = (avrPing * (pingMeasurements - 1) +
                           ping) / pingMeasurements
                print(f'ping is {ping} with an average of {avrPing}')
            elif data == b'\x01':  # input
                data = conn.recv(4)
                # unpact the data and get the int inside of it
                out = struct.unpack('!I', data)[0]
                conn.send(b'\x01')  # send ping
                lastPing = time.time()
                time.sleep(avrPing/2)
                parse(out)  # parse the input
