# -*- coding: utf-8 -*-
#
# Создает отчет из данных JIRA
#
# Author: kochetkov.artem@otr.ru
#

import config
import os
from jira import JIRA, Issue, JIRAError
import xlsxwriter
import logging
from logging.handlers import RotatingFileHandler
import sys
import datetime
import requests
import re
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

PROJECT_LIST = ['EXP', 'TSE', 'INC', 'SP', 'REF', 'EB', 'ARP', 'ACT', 'REV', 'BU']
MAX_RESULT = 5
# MAX_RESULT = False    # Get all issues
START_ROW = 0
START_COL = 0

PRIORITY_TRANSLATE = {
    'Blocker': 'Наивысший',
    'Critical': 'Высокий',
    'Major': 'Средний',
    'Minor': 'Низкий',
    'Trivial': 'Незначительный',
}

SLA = {
    'В работе': 'Нет',
    'Завершено': 'Нет',
    'На паузе': 'Нет',
    'Просрочено': 'Да',
}
# ------------------------------------

rotate = logging.handlers.RotatingFileHandler('gen_jira_report.log', maxBytes=10000000, backupCount=5, encoding='utf-8')
consoleHandler = logging.StreamHandler(sys.stdout)

logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.DEBUG, handlers=[rotate, consoleHandler])


def jiraConn(url):
    """
    Connect to JIRA
    :return: JIRA instance
    """
    jira_options = {'server': url, 'verify': 'certs.pem'}
    jira = JIRA(options=jira_options, basic_auth=(config.JJ_LOGIN, config.JJ_PASS))
    logging.info(f"Подключение к {config.JJ_BASE_URL} установлено.")
    return jira


def cookies_jira(jira):
    """
    Получение печенек авторизации из либы
    :return:
    """
    cookies = jira._session.cookies._cookies
    for k, v in cookies.items():
        for kk, vv in v.items():
            if isinstance(vv, dict):
                return {'JSESSIONID': vv['JSESSIONID'].value, 'atlassian.xsrf.token': vv['atlassian.xsrf.token'].value}
    raise Exception("Error get cookies jira")


def get_issues(jira, jql):
    """
    Get issues from JIRA
    :param jira: экземпляр JIRA
    :param project: ключ проекта
    :return: list issues
    """
    try:
        ji = jira.search_issues(jql, maxResults=MAX_RESULT)
        return ji
    except JIRAError as error:
        logging.error(error)
        return False


def get_priority_text_format(file, priority):
    PRIORITY_COLOR = {
        'Blocker': '#8B0000',
        'Critical': '#FF0000',
        'Major': '#DAA520',
        'Minor': '#008000',
        'Trivial': '#001111',
    }

    text_pr = file.add_format(
        {
            'font_name': 'Times New Roman',
            'font_size': 10,
            'text_h_align': 2,
            'text_v_align': 2,
            'font_color': 'white',
            'bg_color': PRIORITY_COLOR[priority],
            'bold': True,
        }
    )
    return text_pr


def get_issue_work_log(jira, issue):
    try:
        total_ts = 0
        if (issue.fields.subtasks):
            for sb in issue.fields.subtasks:
                sb_issue = jira.issue(sb.key)
                if (sb_issue.fields.timespent):
                    total_ts = total_ts + sb_issue.fields.timespent
            h = total_ts // 3600
            min = (total_ts - h * 3600) // 60
            sec = 0
            # print(f"{h} ч {min} мин")
            return f"{h} ч {min} мин"
        else:
            logging.info(f"Задача {issue.key} не имеет подзадач !")
            return False
    except JIRAError as error:
        logging.error(error)
        return False


def get_issue_work_log_by_fio(jira, issue):
    try:
        ts = {}
        tFIO = ''
        tWL = ''
        
        if (issue.fields.subtasks):
            for sb in issue.fields.subtasks:
                sb_issue = jira.issue(sb.key)
                if (sb_issue.fields.timespent):
                    tFIO = tFIO + f"{sb_issue.fields.assignee.displayName}\n"
                    
                    h = sb_issue.fields.timespent // 3600
                    min = (sb_issue.fields.timespent - h * 3600) // 60
                    sec = sb_issue.fields.timespent - h * 3600 - min * 60
                    
                    tWL = tWL + f"{h} ч {min} мин {sec} сек \n"
            ts['FIO'] = tFIO
            ts['tWL'] =  tWL
            return ts
        else:
            logging.info(f"Задача {issue.key} не имеет подзадач !")
            return False
    except JIRAError as error:
        logging.error(error)
        return False


def gen_report(jira, file, project_list):
    """
    Формирование отчета
    :param jira: экземпляр JIRA
    :param file: объект файла отчета
    :param project_list: список проектов для отчета
    :return: True or False
    """
    file_ws = file.add_worksheet('Отчет')
    file_ws.freeze_panes(1, 0)
    file_ws.set_column('A:A', 5.56)
    file_ws.set_column('B:B', 12.67)
    file_ws.set_column('C:C', 31.00)
    file_ws.set_column('D:D', 16.89)
    file_ws.set_column('E:E', 27.89)
    file_ws.set_column('F:F', 20.33)
    file_ws.set_column('G:G', 28.78)
    file_ws.set_column('H:H', 43.89)
    file_ws.set_column('I:I', 11.00)
    file_ws.set_column('J:J', 16.89)
    file_ws.set_column('K:K', 16.89)
    file_ws.set_column('L:L', 11.78)
    file_ws.set_column('M:M', 24.78)
    file_ws.set_column('N:N', 11.33)
    file_ws.set_column('O:O', 17.67)
    file_ws.set_column('P:P', 14.11)
    file_ws.set_column('Q:Q', 9.78)
    file_ws.set_column('R:R', 16.89)
    file_ws.set_column('S:S', 12.33)
    file_ws.set_column('T:T', 13.89)
    file_ws.set_column('U:U', 12.33)

    name_format = file.add_format(
        {
            'bold': True,
            'font_name': 'Times New Roman',
            'font_size': 11,
            # 'text_h_align': 2,
            # 'text_v_align': 2,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'shrink': True,
            'border': 1,
            'bg_color': '#C0C0C0',
        }
    )

    text_format = file.add_format(
        {
            'font_name': 'Times New Roman',
            'font_size': 10,
            'text_h_align': 2,
            'text_v_align': 2,
        }
    )

    text_format_2 = file.add_format(
        {
            'font_name': 'Times New Roman',
            'font_size': 10,
            'text_h_align': 1,
            'text_v_align': 2,
        }
    )

    text_warn = file.add_format(
        {
            'font_name': 'Times New Roman',
            'font_size': 10,
            'text_h_align': 2,
            'text_v_align': 2,
            'font_color': 'white',
            'bg_color': 'red',
            'bold': True,
        }
    )

    file_ws.write(START_ROW, START_COL, 'Проект', name_format)
    file_ws.write(START_ROW, START_COL+1, 'Код задачи', name_format)
    file_ws.write(START_ROW, START_COL+2, 'Тип задачи', name_format)
    file_ws.write(START_ROW, START_COL+3, 'Тема', name_format)
    file_ws.write(START_ROW, START_COL+4, 'Трудозатраты', name_format)
    file_ws.write(START_ROW, START_COL+5, 'Тип площадки', name_format)
    file_ws.write(START_ROW, START_COL+6, 'Категория специалиста (ФИО)', name_format)
    file_ws.write(START_ROW, START_COL+7, 'Тип задачи ДТА', name_format)
    file_ws.write(START_ROW, START_COL+8, 'Тип задачи (новые зн)', name_format)
    file_ws.write(START_ROW, START_COL+9, 'Исполнитель', name_format)
    file_ws.write(START_ROW, START_COL+10, 'Автор', name_format)
    file_ws.write(START_ROW, START_COL+11, 'Приоритет', name_format)
    file_ws.write(START_ROW, START_COL+12, 'Статус', name_format)
    file_ws.write(START_ROW, START_COL+13, 'Дата создания', name_format)
    file_ws.write(START_ROW, START_COL+14, 'Дата обновления', name_format)
    file_ws.write(START_ROW, START_COL+15, 'Проект', name_format)
    file_ws.write(START_ROW, START_COL+16, 'Дата решения', name_format)
    file_ws.write(START_ROW, START_COL+17, 'Категория заявки', name_format)
    file_ws.write(START_ROW, START_COL+18, 'Среда', name_format)

    row = START_ROW
    count = 0

    for project in PROJECT_LIST:
        jql = f"project = {project} and created >= '2022-07-01' and created <= '2022-08-31' and issuetype = 'Задача ДТА'  ORDER BY created DESC"
        ji = get_issues(jira, jql)
        for issue in ji:
            row += 1
            count += 1

            logging.info(f"--- Обрабатывается {count} задача ---")
            
            file_ws.write(row, START_COL, project, text_format)
            file_ws.write_url(row, START_COL+1, f"{jira.server_info()['baseUrl']}/browse/{issue.key}", string=issue.key)
            # file_ws.write(row, START_COL+2, issue.fields.issuetype.name, text_format)
            file_ws.write(row, START_COL+3, issue.fields.summary, text_format)
            
            # ts = get_issue_work_log(jira, issue)
            ts = get_issue_work_log_by_fio(jira, issue)
            if ts:
                file_ws.write(row, START_COL+4, ts['tWL'], text_format)
                file_ws.write(row, START_COL+6, ts['tFIO'], text_format)

            # file_ws.write(row, START_COL+5, '', text_format)
            if (issue.fields.customfield_28211):
                file_ws.write(row, START_COL+7, issue.fields.customfield_28211.value, text_format)
            # file_ws.write(row, START_COL+8, '', text_format)
            # if (issue.fields.assignee):
            #     file_ws.write(row, START_COL+9, issue.fields.assignee.displayName, text_format)
            # file_ws.write(row, START_COL+10, issue.fields.reporter.displayName, text_format)
            # file_ws.write(
            #     row,
            #     START_COL+11,
            #     PRIORITY_TRANSLATE[issue.fields.priority.name],
            #     get_priority_text_format(file, issue.fields.priority.name)
            # )
            # file_ws.write(row, START_COL+12, issue.fields.status.name, text_format)
            file_ws.write(
                row, 
                START_COL+13, 
                datetime.datetime.strftime(
                        datetime.datetime.strptime(issue.fields.created.split('.')[0], '%Y-%m-%dT%H:%M:%S'),'%d.%m.%Y %H:%M:%S'
                    ), 
                text_format
            )
            
            # file_ws.write(
            #     row, 
            #     START_COL+14, 
            #     datetime.datetime.strftime(
            #             datetime.datetime.strptime(issue.fields.updated.split('.')[0], '%Y-%m-%dT%H:%M:%S'),'%d.%m.%Y %H:%M:%S'
            #         ), 
            #     text_format
            # )
            
            # if (issue.fields.customfield_10714):
            #     file_ws.write(row, START_COL+17, issue.fields.customfield_10714.value, text_format)
            # if (issue.fields.customfield_10728):
            #     file_ws.write(row, START_COL+18, issue.fields.customfield_10728.value, text_format)


if __name__ == "__main__":
    report_file = f"{os.path.abspath(os.path.curdir)}/{config.REPORT_FILENAME}"
    report = xlsxwriter.Workbook(filename=report_file)      # Create report file
    jira = jiraConn(config.JJ_BASE_URL)                     # Jira Connection
    gen_report(jira, report, PROJECT_LIST)                  # Формирование отчета
    report.close()                                          # Закрытие объекта файла отчета