# -*- coding: utf-8 -*-
#
# 1. Выборка задач с некорректным SLA
# 2. Пересчет SLA по задачам
#
# created by Кочетков Артем
# email : kochetkov.artem@otr.ru
#

import datetime
from jira import JIRA, JIRAError
from logging.handlers import RotatingFileHandler
import logging
import sys
import requests
import config


rotate = logging.handlers.RotatingFileHandler('regenerate_SLA.log', maxBytes=10000000, backupCount=5, encoding='utf-8')
consoleHandler = logging.StreamHandler(sys.stdout)

logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.INFO, handlers=[rotate, consoleHandler])


def jiraConnect(url):
    """
    Connect to JIRA

    :return: JIRA instance
    """
    try:
        jira_options = {'server': url, 'verify': 'certs.pem'}
        jira = JIRA(options=jira_options, basic_auth=(config.RG_LOGIN, config.RG_PASS))
        logging.info(f"Подключение к {config.RG_BASE_URL} установлено.")
        return jira
    except JIRAError as error:
        logging.error(error)


def getIssues(jira):
    jql = f'project = ISV AND status in (Решен, \"Запрос информации\", \"В ожидании\", Закрыта) AND slaFunction = isRunning() ORDER BY updated'
    try:
        ji = jira.search_issues(jql, maxResults=False)
        return ji
    except JIRAError as error:
        logging.error(error)
        return False


def is_issue_old(jira, issue):
    try:
        cur_issue = jira.issue(issue, fields='updated')
        cur_issue_update_time = datetime.datetime.strptime(cur_issue.fields.updated.split(".")[0],"%Y-%m-%dT%H:%M:%S")
        cur_time = datetime.datetime.now()
        
        if (cur_time - cur_issue_update_time).total_seconds() > 60:
            logging.info(f"Разница во времени : {cur_time - cur_issue_update_time} ")
            return True
    except JIRAError as error:
        logging.error(error)
        return False


def updateSLA(cookies, issue):
    try:
        res = requests.get(f"{config.RG_BASE_URL}{config.REGENERATE_SLA_URL}{issue}", cookies=cookies)
        logging.info(f"Для задачи : {issue}, произведен перерасчет SLA !")
    except Exception as error:
        logging.error(error)


if __name__ == '__main__':
    logging.info(f">>>> Старт скрипта {datetime.datetime.now()} <<<<")
    count = 0
    jira = jiraConnect(config.RG_BASE_URL)
    ji = getIssues(jira)
    if ji:
        for issue in ji:
            count += 1
            logging.info(f"Обрабатывается задача № {count} : {issue}")
            if is_issue_old(jira, issue):
                updateSLA(jira._session.cookies.get_dict(), issue)
            else:
                logging.info(f"Задача {issue} создана недавно.")
    else:
        logging.info(f'Нет задач с некорректным SLA статусом.')
