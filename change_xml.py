# -*- coding: utf-8 -*-
#
# created by artemk
# email : kochetkov1985@mail.ru
#

from datetime import datetime
from logging.handlers import RotatingFileHandler
import logging
import sys

rotate = logging.handlers.RotatingFileHandler('confluence_change_xml.log', maxBytes=10000000, backupCount=5,
                                              encoding='utf-8')
consoleHandler = logging.StreamHandler(sys.stdout)

logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.INFO, handlers=[rotate, consoleHandler])


if __name__ == "__main__":
    backup_file = open('entities.xml', 'r')

    print(backup_file.readlines())

    
    backup_file.close()

