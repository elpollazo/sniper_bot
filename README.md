# sniper_bot

This bot is used to monitoring in real time stock of RTX-3070 graphic card and buy it when is available. This is done by continously requesting 9 Add-To-Cart links (ATC) of different RTX-3070 models. The bot was tested on Linux.

Ussage:

1. Clone this repository: git clone https://github.com/elpollazo/sniper_bot
2. Install the libraries: ./install.sh
3. Set the parameters of the configuration file in ./objects/config.json. The description of the parameters needed are below.
4. To start the bot: python3 main.py --page amazon --card rtx-3070
