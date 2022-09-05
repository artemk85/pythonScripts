# -*- coding:utf -8 -*-
#
# Набор различных служебных функций.
#


from asyncio.log import logger
import random
import config


CHARS = '+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'


def createlogin(name, mode = 'Normal'):
   """
   Формирует из строки ФИО логин, формата ИвановИИ

   :return: string
   """
   try:
      new_name = ""
      if mode == 'Normal':
         name = name.split()

         fio = name[0]
         fname = list(name[1])
         sname = list(name[2])

         new_name = translatestring(f"{fio}{fname[0]}{sname[0]}")
      return new_name
   except IndexError as error:
      print(f"Не удалось создать логин для {name} !")
      try:
         name = name.split()
         new_name = translatestring(f"{name[0]}{name[1][0]}{name[1][2]}")
         return new_name
      except Exception as e:
         print(e)
         return False


def translatestring(name):
   """
   Автор: LarsKort
   Дата: 16/07/2011; 1:05 GMT-4;
   """
   # Словарь с заменами
   slovar = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e',
      'ж':'zh','з':'z','и':'i','й':'i','к':'k','л':'l','м':'m','н':'n',
      'о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h',
      'ц':'c','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e',
      'ю':'u','я':'ja', 'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'E',
      'Ж':'Zh','З':'Z','И':'I','Й':'I','К':'K','Л':'L','М':'M','Н':'N',
      'О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F','Х':'H',
      'Ц':'C','Ч':'Ch','Ш':'Sh','Щ':'Sch','Ъ':'','Ы':'y','Ь':'','Э':'E',
      'Ю':'U','Я':'Ya',',':'','?':'',' ':' ','~':'','!':'','@':'','#':'',
      '$':'','%':'','^':'','&':'','*':'','(':'',')':'','-':'','=':'','+':'',
      ':':'',';':'','<':'','>':'','\'':'','"':'','\\':'','/':'','№':'',
      '[':'',']':'','{':'','}':'','ґ':'','ї':'', 'є':'','Ґ':'g','Ї':'i',
      'Є':'e', '—':''}
        
   # Циклически заменяем все буквы в строке
   for key in slovar:
      name = name.replace(key, slovar[key])
   return name


def generatepassword():
   """
   Генерирует парольную фразу

   :return: text
   """
   password =''
   for i in range(config.LENGTH_PASSWORD):
      password += random.choice(CHARS)
   return password


if __name__ == "__main__":
   for num in range(config.NUM_PASSWORD):
      print(generatepassword())

   # print("-->", createlogin("Кочетков Артем Николаевич"))
   # print("-->", translatestring("КочетковАН"))
