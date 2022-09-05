# -*- coding: utf-8 -*-
#
# created by artemk
# email : kochetkov1985@mail.ru
#

from datetime import datetime
from logging.handlers import RotatingFileHandler
import logging
import sys
import requests
import config


rotate = logging.handlers.RotatingFileHandler('confluence_export_import.log', maxBytes=10000000, backupCount=5,
                                              encoding='utf-8')
consoleHandler = logging.StreamHandler(sys.stdout)

logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.INFO, handlers=[rotate, consoleHandler])


if __name__ == "__main__":
    sess = requests.Session()
    sess.auth = (config.TEST_LOGIN, config.TEST_PASSW)
    response = sess.get(config.TEST_BASE_URL_LOGIN)   #получаем cookie
    cookies = response.cookies
    pageID = '2785281'

    response = requests.request(
        "GET",
        f"{config.TEST_BASE_URL}{config.EXPORT_URL}{pageID}",
        cookies=cookies
    )

    open(f"{pageID}.zip", 'wb').write(response.content)
    
