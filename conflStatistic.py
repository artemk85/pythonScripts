# -*- coding: utf-8 -*-
#


import requests
import logging
from logging.handlers import RotatingFileHandler


BASE_URL = 'http:///confluence.otr.ru'
LOGIN = 'kochetkov.artem'
PASS = 'zgaNGka2hHeC8cAD'

rotate = logging.handlers.RotatingFileHandler('gen_confl_statistics.txt', maxBytes=10000000, backupCount=5, encoding='utf-8')
consoleHandler = logging.StreamHandler(sys.stdout)

logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.DEBUG, handlers=[rotate, consoleHandler])


if __name__ == '__main__':
    pass
