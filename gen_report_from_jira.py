# -*- coding: utf-8 -*-
#
# Создает отчет из данных JIRA
#
# Author: kochetkov1985@mail.ru
#

import config
import os
from jira import JIRA, Issue, JIRAError
import xlsxwriter
import logging
from logging.handlers import RotatingFileHandler
import sys
import psycopg2
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

# ----- Settings PROM -----
BASE_URL = config.JJ_BASE_URL  # ПРОМ JIRA СУЗ
DB_HOST = config.JJ_DB_HOST                # jira-prom-db02
DB_PASS = config.JJ_DB_PASS

# ----- Other Settings ----
REPORT_FILENAME = 'report.xlsx'

LOGIN = config.JJ_LOGIN
PASS = config.JJ_PASS

DB_BASE = config.JJ_DB_BASE
DB_LOGIN = config.JJ_DB_LOGIN

# PROJECT_LIST = ['SDOMS', 'SERMO', 'SETD']
PROJECT_LIST = ['SDOMS']
# MAX_RESULT = 5
MAX_RESULT = False    # Get all issues
START_ROW = 0
START_COL = 0

REPORT_STATUSES = ['В ожидании', 'Запрос информации', 'В работе Л3']

PRIORITY_TRANSLATE = {
    'Highest': 'Наивысший',
    'High': 'Высокий',
    'Medium': 'Средний',
    'Low': 'Низкий',
}

SLA = {
    'В работе': 'Нет',
    'Завершено': 'Нет',
    'На паузе': 'Нет',
    'Просрочено': 'Да',
}
# ------------------------------------

rotate = logging.handlers.RotatingFileHandler('gen_jira_report.txt', maxBytes=10000000, backupCount=5, encoding='utf-8')
consoleHandler = logging.StreamHandler(sys.stdout)

logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                    level=logging.DEBUG, handlers=[rotate, consoleHandler])


def jiraConn(url):
    """
    Connect to JIRA
    :return: JIRA instance
    """
    jira_options = {'server': url, 'verify': False}
    jira = JIRA(options=jira_options, basic_auth=(LOGIN, PASS))
    logging.info(f"Подключение к {BASE_URL} установлено.")
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


def get_overdue_time(jira, issue_key):
    jira_cookies = cookies_jira(jira)
    cookies = {
        'atlassian.xsrf.token': jira_cookies['atlassian.xsrf.token'],
        'JSESSIONID': jira_cookies['JSESSIONID'],
    }
    res = requests.get(
        f"{BASE_URL}/rest/tts-api/1.0/sla/issue/{issue_key}",
        cookies=cookies,
        verify=False
    )
    data = res.json()
    for option in data:
        if option['overdueDuration']:
            return option['overdueDuration']


def get_another_time(jira, issue_key):
    jira_cookies = cookies_jira(jira)
    cookies = {
        'atlassian.xsrf.token': jira_cookies['atlassian.xsrf.token'],
        'JSESSIONID': jira_cookies['JSESSIONID'],
    }
    another_time = {}

    res = requests.get(
        f"{BASE_URL}/rest/tts-api/1.0/sla/issue/{issue_key}",
        cookies=cookies,
        verify=False
    )
    data = res.json()
    if data:
        for option in data:
            if option['overdueDuration']:
                another_time['overdue_time'] = option['overdueDuration']  # Время просрочки
            else:
                another_time['overdue_time'] = ''

            if option['workingDuration']:
                another_time['workingDuration'] = option['workingDuration']  # Время решения
            else:
                another_time['workingDuration'] = ''

            if option['pausedDuration']:
                another_time['pausedDuration'] = option['pausedDuration']  # Время на паузе
            else:
                another_time['pausedDuration'] = ''

            if option['elapsedPercentage']:
                another_time['elapsedPercentage'] = option['elapsedPercentage']  # Затрачено по SLA
            else:
                another_time['elapsedPercentage'] = ''

            if option['targetDate']:
                another_time['targetDate'] = re.sub(r'Z', '', option['targetDate'])  # Плановая дата решения
            else:
                another_time['targetDate'] = ''
    logging.info(f'{issue_key} : {another_time}')
    return another_time


def get_issues(jira, project):
    """
    Get issues from JIRA
    :param jira: экземпляр JIRA
    :param project: ключ проекта
    :return: list issues
    """
    '''jql = f"project = {project} AND " \
          f"issuetype in (Инцидент, 'Запрос консультации') and " \
          f"(created >= '2021-10-01' and created <= '2021-11-30') " \
          f"ORDER BY issuekey DESC"'''
    # jql = f'project={project} ORDER BY created DESC'
    jql = f"issuekey = 'SERMO-35'"

    try:
        ji = jira.search_issues(jql, maxResults=MAX_RESULT)
        return ji
    except JIRAError as error:
        logging.error(error)
        return False


def connectToDB():
    """
    Устанавливается подключение к СУБД
    :return: объект подключения
    """
    try:
        logging.info('Connecting to the PostgreSQL database ...')
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_BASE,
            user=DB_LOGIN,
            password=DB_PASS)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)


def disconnectFromDB(dbConn):
    """
    Закрывается соединение с СУБД
    :param dbConn: экземпляр объекта подключения к базе
    :return: Null
    """
    try:
        dbConn.close()
        logging.info('Database connection closed.')
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)


def get_count_from_db(conn, issue_id):
    """
    Возвращает кол-во переходв в статусы 'В работе Л3', 'В ожидании' и 'Запрос информации'
    :return: dict or False
    """
    transition_count = {}
    try:
        cur = conn.cursor()

        for status in REPORT_STATUSES:
            sql = f"select count(ci.newstring) from changeitem ci, changegroup cg, jiraissue ji, project p " \
                  f"where field = 'status' and ci.groupid = cg.id and ji.id = cg.issueid and p.id = ji.project " \
                  f"and ji.id = {issue_id} and ci.newstring = '{status}'"
            cur.execute(sql)
            row = cur.fetchone()

            if row is not None and row[0] != 0:
                transition_count[status] = row[0]
            else:
                transition_count[status] = ''

        logging.info(f'For issue {issue_id} : {transition_count}')
        return transition_count
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return False


def get_priority_text_format(file, priority):
    PRIORITY_COLOR = {
        'Highest': '#8B0000',
        'High': '#FF0000',
        'Medium': '#DAA520',
        'Low': '#008000',
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


def get_formatted_time(sla_time, overdue: bool = False):
    """
    Разбиват строку типа 'PT110H7M58.641S' на часы, минуты и секунды
    :param sla_time: строка с временем
    :param overdue: False или True - если это время переработки
    :return: dict с часом, минутой и секундой
    """
    time = {}

    hour = re.search(r'(\d+)H', sla_time)
    minute = re.search(r'(\d+)M', sla_time)
    sec = re.search(r'(\d+)\.\d+?S', sla_time)

    if not overdue:
        if hour:
            time['hour'] = f"{hour.group(1)} ч."
        else:
            time['hour'] = ''

        if minute:
            time['min'] = f"{minute.group(1)} мин."
        else:
            time['min'] = '0 мин.'

        if sec:
            time['sec'] = f"{sec.group(sec.lastindex)} сек."
        else:
            time['sec'] = '0 сек.'

    if overdue:
        if hour:
            hour = hour.group(1)
        else:
            hour = 0

        if minute:
            minute = minute.group(1)
        else:
            minute = 0

        if sec:
            sec = sec.group(sec.lastindex)
        else:
            sec = 0

        time['hour'] = getTimeInHours(hour, minute, sec)

    return time


def getTimeInHours(h, m, s: str):
    timeinhours = 0
    hour = int(h) * 3600 if h else 0
    min = int(m) * 60 if m else 0
    sec = int(s) if s else 0

    timeinhours = (hour + min + sec) / 3600

    return round(timeinhours, 2)


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

    file_ws.write(START_ROW, START_COL, '№ п/п', name_format)
    file_ws.write(START_ROW, START_COL+1, 'Уникальный номер Заявки', name_format)
    file_ws.write(START_ROW, START_COL+2, 'Подсистема', name_format)
    file_ws.write(START_ROW, START_COL+3, 'Дата регистрации Заявки', name_format)
    file_ws.write(START_ROW, START_COL+4, 'Статус Заявки', name_format)
    file_ws.write(START_ROW, START_COL+5, 'Категория', name_format)
    file_ws.write(START_ROW, START_COL+6, 'Заявитель', name_format)
    file_ws.write(START_ROW, START_COL+7, 'Полное описание', name_format)
    file_ws.write(START_ROW, START_COL+8, 'Приоритет', name_format)
    file_ws.write(START_ROW, START_COL+9, 'Дата решения Заявки', name_format)
    file_ws.write(START_ROW, START_COL+10, 'Дата закрытия Заявки', name_format)
    file_ws.write(START_ROW, START_COL+11, 'Отметка о нарушении сроков исполнения', name_format)
    file_ws.write(START_ROW, START_COL+12, 'Код закрытия', name_format)
    file_ws.write(START_ROW, START_COL+13, 'Просрочено времени (ч)', name_format)
    file_ws.write(START_ROW, START_COL+14, 'Время решения', name_format)
    file_ws.write(START_ROW, START_COL+15, 'Время на паузе', name_format)
    file_ws.write(START_ROW, START_COL+16, 'Затрачено по SLA (%)', name_format)
    file_ws.write(START_ROW, START_COL+17, 'Плановая дата решения', name_format)
    file_ws.write(START_ROW, START_COL+18, 'Кол-во переводов в статус "В ожидании"', name_format)
    file_ws.write(START_ROW, START_COL+19, 'Кол-во переводов в статус "Запрос информации"', name_format)
    file_ws.write(START_ROW, START_COL+20, 'Кол-во переводов в статус "В работе Л3"', name_format)

    row = START_ROW
    text_f = ''

    c = connectToDB()
    count = 0

    for project in project_list:
        ji = get_issues(jira, project)
        for issue in ji:
            row += 1
            count += 1
            logging.info(f"--- Обрабатывается {count} задача ---")
            file_ws.write(row, START_COL, row, text_format)
            # file_ws.write(row, START_COL+1, issue.key, text_format)
            file_ws.write_url(row, START_COL+1, f"{jira.server_info()['baseUrl']}/browse/{issue.key}", string=issue.key)
            file_ws.write(row, START_COL+2, issue.fields.customfield_13804, text_format)
            file_ws.write(row, START_COL+3, datetime.datetime.strftime(
                datetime.datetime.strptime(issue.fields.created.split('.')[0], '%Y-%m-%dT%H:%M:%S'),
                '%d.%m.%Y %H:%M:%S'), text_format)
            file_ws.write(row, START_COL+4, issue.fields.status.name, text_format)
            file_ws.write(row, START_COL+5, issue.fields.issuetype.name, text_format)
            file_ws.write(row, START_COL+6, issue.fields.reporter.displayName, text_format)
            file_ws.write(row, START_COL+7, issue.fields.description, text_format_2)

            file_ws.write(
                row,
                START_COL+8,
                PRIORITY_TRANSLATE[issue.fields.priority.name],
                get_priority_text_format(file, issue.fields.priority.name)
            )
            if issue.fields.customfield_14022:
                file_ws.write(row, START_COL+9, datetime.datetime.strftime(
                    datetime.datetime.strptime(issue.fields.customfield_14022.split('.')[0], '%Y-%m-%dT%H:%M:%S'),
                    '%d.%m.%Y %H:%M:%S'), text_format)
            if issue.fields.customfield_14008:
                file_ws.write(row, START_COL+10, datetime.datetime.strftime(
                    datetime.datetime.strptime(issue.fields.customfield_14008.split('.')[0], '%Y-%m-%dT%H:%M:%S'),
                    '%d.%m.%Y %H:%M:%S'), text_format)

            other_time = get_another_time(jira, issue.key)
            if other_time:
                if issue.fields.customfield_13600:
                    file_ws.write(row, START_COL+11, SLA[issue.fields.customfield_13600], text_format)
                    if SLA[issue.fields.customfield_13600] == 'Да':
                        file_ws.write(row, START_COL + 11, SLA[issue.fields.customfield_13600], text_warn)
                        file_ws.write(row, START_COL + 13,
                                      get_formatted_time(other_time['overdue_time'], True)['hour'],
                                      text_warn)

                time = get_formatted_time(other_time['workingDuration'])
                file_ws.write(row, START_COL + 14, f"{time['hour']} {time['min']} {time['sec']}", text_format)

                time = get_formatted_time(other_time['pausedDuration'])
                file_ws.write(row, START_COL + 15, f"{time['hour']} {time['min']}", text_format)

                if other_time['elapsedPercentage']:
                    if int(other_time['elapsedPercentage']) <= 100:
                        text_f = text_format
                    if int(other_time['elapsedPercentage']) > 100:
                        text_f = text_warn
                    file_ws.write(row, START_COL + 16, other_time['elapsedPercentage'], text_f)

                if other_time['targetDate']:
                    file_ws.write(row, START_COL + 17, datetime.datetime.strftime(
                        datetime.datetime.strptime(other_time['targetDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S'),
                        '%d.%m.%Y %H:%M:%S'), text_format)

            if issue.fields.customfield_10108:
                file_ws.write(row, START_COL+12, issue.fields.customfield_10108.value, text_format)

            transition_count = get_count_from_db(c, issue.id)
            if transition_count:
                file_ws.write(row, START_COL + 18, transition_count['В ожидании'], text_format)
                file_ws.write(row, START_COL + 19, transition_count['Запрос информации'], text_format)
                file_ws.write(row, START_COL + 20, transition_count['В работе Л3'], text_format)
    disconnectFromDB(c)


def send_mail(send_from, send_to, subject, message, files=[],
              server=config.SMTP_SERVER, port=25, username=config.SMTR_LOGIN, password=config.SMTP_PASS,
              use_tls=True):
    """Compose and send email with provided info and attachments.
    Args:
        send_from (str): from name
        send_to (list[str]): to name(s)
        subject (str): message title
        message (str): message body
        files (list[str]): list of file paths to be attached to email
        server (str): mail server host name
        port (int): port number
        username (str): server auth username
        password (str): server auth password
        use_tls (bool): use TLS mode
    """
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = ', '.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))

    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename={}'.format(Path(path).name))
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    smtp.debuglevel = 1
    if use_tls:
        smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()


if __name__ == "__main__":
    report_file = f"{os.path.abspath(os.path.curdir)}/{REPORT_FILENAME}"
    report = xlsxwriter.Workbook(filename=report_file)      # Create report file
    jira = jiraConn(BASE_URL)                               # Jira Connection
    gen_report(jira, report, PROJECT_LIST)                  # Формирование отчета
    report.close()                                          # Закрытие объекта файла отчета

    send_mail(
        config.EMAIL_SEND_TO,
        config.EMAIL_SEND_COPY,
        'Report JIRA Issues',
        'Список задач проекта SDOMS (Инцидент и Запрос консультации) с 01.10.2021 по 30.11.2021 г.',
        [report_file],
    )
