
# installing

- clone this repository
- install [3ds.py](https://github.com/vbe0201/3DS.py) on your 3ds
- rename ``controllerClient.py`` to ``main.py``
- put the ip and host you want to use in ``serverConfig.json`` and ``controllerConfig.json``
- start ``server.py`` on your computer and choose a config file to use
- connect your 3ds to wifi
- open 3ds.py and wait untill it connects to your computer

# making a config file for a game

- for every button on the 3ds that is going to be used, you have to put it's code and the button it represents on the keyobard in a new json file in the directory ``/config``
- you can find every button's code [here](https://libctru.devkitpro.org/hid_8h.html)
