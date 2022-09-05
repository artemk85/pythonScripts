---------------------------------------------------------------------------------------------------------------------------------------------------
SELECT f.id AS "ID Экрана", f3.NAME AS "Экран", f.FIELDIDENTIFIER AS "Поле", f2.NAME AS "Вкладка" FROM FIELDSCREENLAYOUTITEM f 
INNER JOIN FIELDSCREENTAB f2 ON f.FIELDSCREENTAB = f2.ID 
INNER JOIN FIELDSCREEN f3 ON f2.FIELDSCREEN = f3.ID

select * from FIELDSCREENLAYOUTITEM f 		-- поле -> экран

select * from FIELDLAYOUT 			-- проекты
select * from FIELDLAYOUTITEM f 		-- проект -> поле

select * from issuetypescreenscheme
select * from issuetypescreenschemeentity
select * from fieldscreenscheme 		-- экраны
select * from fieldscreenschemeitem		-- экраны-поля

Поля
-------------------------
select ID, CFNAME, 
CASE CUSTOMFIELDTYPEKEY
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes' THEN 'Галочки'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:float' THEN 'Число (целое или дробное)'
  WHEN 'com.pyxis.greenhopper.jira:gh-epic-color' THEN 'Colour of Epic'
  WHEN 'com.pyxis.greenhopper.jira:gh-epic-link' THEN 'Epic Link Relationship'
  WHEN 'com.pyxis.greenhopper.jira:gh-epic-label' THEN 'Название Эпики'
  WHEN 'com.pyxis.greenhopper.jira:gh-epic-status' THEN 'Status of Epic'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:labels' THEN 'Метки'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:textfield' THEN 'Текстовое Поле (однострочное)'
  WHEN 'com.onresolve.jira.groovy.groovyrunner:jqlFunctionsCustomFieldType' THEN 'JQL Functions Customfield Type'
  WHEN 'com.pyxis.greenhopper.jira:gh-lexo-rank' THEN 'Global Rank'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:grouppicker' THEN 'Выбор группы (одна группа)'
  WHEN 'com.pyxis.greenhopper.jira:gh-sprint' THEN 'JIRA Sprint Field'
  WHEN 'com.burningcode.jira.issue.customfields.impl.jira-watcher-field:watcherfieldtype' THEN ''
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:textarea' THEN 'Текстовое Поле (многострочное)'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:cascadingselect' THEN 'Список выбора (выпадающий)'
  WHEN 'ru.slie.jira.mf:mf-customfield-progress-sla' THEN '(MF) Progress SLA'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:select' THEN 'Выпадающий список (одиночный выбор)'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:datepicker' THEN 'Дата'
  WHEN 'ru.slie.jira.mf:mf-customfield-disabled' THEN '(MF) Disabled CF'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:datetime' THEN 'Выбор даты и времени'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:userpicker' THEN 'Выбор пользователя (один пользователь)'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:radiobuttons' THEN 'Переключатель'
  WHEN 'ru.slie.jira.mf:mf-customfield-violation-sla' THEN '(MF) Violation SLA'
  WHEN 'com.burningcode.jira.issue.customfields.impl.jira-watcher-field:watcherfieldtype' THEN '???'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:multiuserpicker' THEN 'Выбор пользователя (несколько пользователей)'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect' THEN 'Список выбора (множественный выбор)'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:readonlyfield' THEN 'Текстовое поле (только чтение)'
 END
from customfield
ORDER BY CFNAME

select * from customfield c where id = 10303 	-- поля
select * from customfieldoption 		-- значения полей
select * from customfieldvalue			-- Данные в полях

Поля на экранах
-------------------------
select fs.id as "ID Экрана", fs.name "Имя экрана", fst.name "Вкладка", c.id  "ID custom_field", coalesce(c.cfname, 
 CASE fsl.Fieldidentifier
  WHEN 'assignee' THEN 'Исполнитель'
  WHEN 'priority' THEN 'Приоритет'
  WHEN 'summary' THEN 'Тема'
  WHEN 'description' THEN 'Описание'
  WHEN 'attachment' THEN 'Вложение'
  WHEN 'duedate' THEN 'Срок исполнения'
  WHEN 'reporter' THEN 'Автор'
  WHEN 'components' THEN 'Компоненты'
  WHEN 'issuelinks' THEN 'Связанные запросы'
  WHEN 'versions' THEN 'Проявляется в версиях'
  WHEN 'environment' THEN 'Окружение'
  WHEN 'security' THEN 'Уровень безопасности'
  WHEN 'timetracking' THEN 'Учет времени'
  WHEN 'labels' THEN 'Метки'
  WHEN 'fixVersions' THEN 'Исправить в версиях'
  WHEN 'issuetype' THEN 'Тип запроса'
  WHEN 'resolution' THEN 'Резолюция'  
 END
) "Имя поля" 
from fieldscreen fs
join fieldscreentab fst on fs.id = fst.fieldscreen
join fieldscreenlayoutitem fsl on fst.id = fsl.fieldscreentab
left outer join (select concat('customfield_',cf.id) as ident, cf.cfname, cf.id from customfield cf ) c on c.ident = fsl.fieldidentifier
order by fs.name;

Экраны определенного проекта
-------------------------
select DISTINCT(fs.NAME) FROM ISSUETYPESCREENSCHEMEENTITY itsse
JOIN FIELDSCREENSCHEME fss ON ITSSE.FIELDSCREENSCHEME = fss.ID
JOIN FIELDSCREENSCHEMEITEM fssi ON fssi.FIELDSCREENSCHEME = fss.ID 
JOIN ISSUETYPESCREENSCHEME itss ON itss.ID = ITSSE.SCHEME 
JOIN FIELDSCREEN fs ON fs.ID = fssi.FIELDSCREEN 
WHERE ITSS.NAME = 'MF'

Список экранов и полей определенного проекта
-------------------------
select fs.id as "ID Экрана", fs.name "Имя экрана", fst.name "Вкладка", c.id  as "ID custom_field", coalesce(c.cfname, fsl.Fieldidentifier) "Имя поля" 
from fieldscreen fs
join fieldscreentab fst on fs.id = fst.fieldscreen
join fieldscreenlayoutitem fsl on fst.id = fsl.fieldscreentab
left outer join (select concat('customfield_',cf.id) as ident, cf.cfname, cf.id from customfield cf ) c on c.ident = fsl.fieldidentifier
WHERE fs.NAME IN (
 select DISTINCT(fs.NAME) FROM ISSUETYPESCREENSCHEMEENTITY itsse
 JOIN FIELDSCREENSCHEME fss ON ITSSE.FIELDSCREENSCHEME = fss.ID
 JOIN FIELDSCREENSCHEMEITEM fssi ON fssi.FIELDSCREENSCHEME = fss.ID 
 JOIN ISSUETYPESCREENSCHEME itss ON itss.ID = ITSSE.SCHEME 
 JOIN FIELDSCREEN fs ON fs.ID = fssi.FIELDSCREEN 
 WHERE ITSS.NAME = 'MF'
)
order by fs.name;

select coalesce(c.cfname, fsl.Fieldidentifier) "Имя поля", 'customfield'||'_' ||c.id as "ID custom_field", CASE c.CUSTOMFIELDTYPEKEY
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes' THEN 'Галочки'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:float' THEN 'Число (целое или дробное)'
  WHEN 'com.pyxis.greenhopper.jira:gh-epic-color' THEN 'Colour of Epic'
  WHEN 'com.pyxis.greenhopper.jira:gh-epic-link' THEN 'Epic Link Relationship'
  WHEN 'com.pyxis.greenhopper.jira:gh-epic-label' THEN 'Название Эпики'
  WHEN 'com.pyxis.greenhopper.jira:gh-epic-status' THEN 'Status of Epic'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:labels' THEN 'Метки'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:textfield' THEN 'Текстовое Поле (однострочное)'
  WHEN 'com.onresolve.jira.groovy.groovyrunner:jqlFunctionsCustomFieldType' THEN 'JQL Functions Customfield Type'
  WHEN 'com.pyxis.greenhopper.jira:gh-lexo-rank' THEN 'Global Rank'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:grouppicker' THEN 'Выбор группы (одна группа)'
  WHEN 'com.pyxis.greenhopper.jira:gh-sprint' THEN 'JIRA Sprint Field'
  WHEN 'com.burningcode.jira.issue.customfields.impl.jira-watcher-field:watcherfieldtype' THEN ''
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:textarea' THEN 'Текстовое Поле (многострочное)'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:cascadingselect' THEN 'Список выбора (выпадающий)'
  WHEN 'ru.slie.jira.mf:mf-customfield-progress-sla' THEN '(MF) Progress SLA'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:select' THEN 'Выпадающий список (одиночный выбор)'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:datepicker' THEN 'Дата'
  WHEN 'ru.slie.jira.mf:mf-customfield-disabled' THEN '(MF) Disabled CF'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:datetime' THEN 'Выбор даты и времени'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:userpicker' THEN 'Выбор пользователя (один пользователь)'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:radiobuttons' THEN 'Переключатель'
  WHEN 'ru.slie.jira.mf:mf-customfield-violation-sla' THEN '(MF) Violation SLA'
  WHEN 'com.burningcode.jira.issue.customfields.impl.jira-watcher-field:watcherfieldtype' THEN '???'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:multiuserpicker' THEN 'Выбор пользователя (несколько пользователей)'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:multiselect' THEN 'Список выбора (множественный выбор)'
  WHEN 'com.atlassian.jira.plugin.system.customfieldtypes:readonlyfield' THEN 'Текстовое поле (только чтение)'
 end, fs.name "Имя экрана", fs.id as "ID Экрана", fst.name "Вкладка" 
from fieldscreen fs
join fieldscreentab fst on fs.id = fst.fieldscreen
join fieldscreenlayoutitem fsl on fst.id = fsl.fieldscreentab
left outer join (select concat('customfield_',cf.id) as ident, cf.cfname, cf.id, cf.customfieldtypekey from customfield cf ) c on c.ident = fsl.fieldidentifier
WHERE fs.NAME IN (
 select DISTINCT(fs.NAME) FROM ISSUETYPESCREENSCHEMEENTITY itsse
 JOIN FIELDSCREENSCHEME fss ON ITSSE.FIELDSCREENSCHEME = fss.ID
 JOIN FIELDSCREENSCHEMEITEM fssi ON fssi.FIELDSCREENSCHEME = fss.ID 
 JOIN ISSUETYPESCREENSCHEME itss ON itss.ID = ITSSE.SCHEME 
 JOIN FIELDSCREEN fs ON fs.ID = fssi.FIELDSCREEN 
 WHERE ITSS.NAME = 'FK: Task Management Issue Type Screen Scheme'
)
order by fs.name;

Типы задач и экраны
-------------------------
select c.pname issuetypename, issuetype issuetypeid, f.name screenname, a.id screenid, b.name issuetypescreenname, d.name screenscheme
from issuetypescreenschemeentity a, issuetypescreenscheme b, issuetype c, fieldscreenscheme d, fieldscreenschemeitem e, fieldscreen f
where a.scheme = b.id and a.issuetype = c.id and a.fieldscreenscheme = d.id and E.FIELDSCREENSCHEME = D.ID and E.FIELDSCREEN = f.id order by pname

Статусы задач
-------------------------
SELECT PNAME,
CASE STATUSCATEGORY 
 WHEN 1 THEN 'Нет категории'
 WHEN 2 THEN 'Сделать'
 WHEN 4 THEN 'В процессе'
 WHEN 3 THEN 'Выполнено'
END AS "Category"
, ID
FROM ISSUESTATUS i;

Резолюции
-------------------------
SELECT ID,PNAME,DESCRIPTION FROM RESOLUTION r

Приоритеты
-------------------------
SELECT ID,PNAME,DESCRIPTION FROM PRIORITY p 

--------------------------------------------------------------
SELECT p.pkey||'-'||i.issuenum as "Номер заявки", 
i.CREATOR as "Автор заявки",
TO_CHAR(i.CREATED,'DD.MM.YYYY HH24:MI') as "Дата заявки",
cg.AUTHOR as "Автор перехода",
TO_CHAR(cg.CREATED,'DD.MM.YYYY HH24:MI') as "Дата перехода",
ci.OLDSTRING||' -> '||ci.NEWSTRING as "Переход",
-- Перечислить необходимые поля отображаемые в заявке
(select stringvalue from customfieldvalue where issue = cg.issueid and customfield = (select id from customfield where cfname = 'Логин пользователя')) as "Логин польз-ля",
(select stringvalue from customfieldvalue where issue = cg.issueid and customfield = (select id from customfield where cfname = 'Номер в ОТП')) as "Номер ОТП",
--(select stringvalue from customfieldvalue where issue = cg.issueid and customfield = (select id from customfield where cfname = 'Метка ОТП')) as "Метка ОТП",
(select label from label where fieldid = (select id from customfield where cfname = 'Метка ОТП') and issue = cg.issueid) as "Метка ОТП",
(select customvalue from customfieldoption where id = (select stringvalue from customfieldvalue where issue = cg.issueid and customfield = (select id from customfield where cfname = 'Категория заявки'))) as "Катег. заявки",
(select stringvalue from customfieldvalue where issue = cg.issueid and customfield = (select id from customfield where cfname = 'Раздел системы')) as "Раздел системы",
(select stringvalue from customfieldvalue where issue = cg.issueid and customfield = (select id from customfield where cfname = 'Номер в Оktell')) as "Номер в Оktell"
FROM changegroup cg 
inner join jiraissue i on cg.issueid = i.id
AND i.CREATED between 
-- Указать диапазон дат
TO_DATE('01.06.2020','DD.MM.YYYY') and TO_DATE('30.06.2020','DD.MM.YYYY')
inner join project p on i.project = p.id
inner join changeitem ci on ci.groupid = cg.id 
-- Указать начальный и конечный статус перехода
AND dbms_lob.compare(ci.OLDSTRING, to_clob('В работе Л1')) = 0
AND dbms_lob.compare(ci.NEWSTRING, to_clob('Анализ Л2')) = 0
inner join app_user au on cg.author = au.user_key
-- Указать наименование проекта
WHERE cg.issueid in (select id from jiraissue where project in (select id from project where pname = 'Сопровождение Минфина БП') ) 
order by "Дата заявки";

------------------------------------- РАБОЧИЕ СТОЛЫ -------------------------------------------
SELECT * FROM PORTALPAGE p 
JOIN PORTLETCONFIGURATION p2 ON p2.PORTALPAGE = p.ID
JOIN GADGETUSERPREFERENCE g ON p2.ID = g.PORTLETCONFIGURATION 
WHERE p.ID = 10805
ORDER BY p.ID

--------------------- Активные пользователи ---------------------------------------
/*select cu.user_name as login, cu.display_name as FIO, cu.email_address
from cwd_user cu, cwd_directory cd 
where cd.id = cu.directory_id and cd.directory_name != 'Active Directory server' and cu.user_name not in (
select cu.user_name 
from cwd_user cu
left join cwd_user_attributes cua on cu.id = cua.user_id 
inner join cwd_directory cd on cd.id = cu.directory_id 
where cua.attribute_name = 'lastAuthenticated' and cd.directory_name != 'Active Directory server'
)*/

/*select cu.user_name as login, cu.display_name as FIO, cu.email_address, cua.attribute_value 
from cwd_user cu
left join cwd_user_attributes cua on cu.id = cua.user_id 
inner join cwd_directory cd on cd.id = cu.directory_id 
where cua.attribute_name = 'lastAuthenticated' and cd.directory_name != 'Active Directory server'*/

select cu.user_name as login, cu.display_name as FIO, cu.email_address, cm.parent_name
from cwd_user cu, cwd_directory cd, cwd_membership cm
where cu.id = cm.child_id and cd.id = cu.directory_id and cd.directory_name != 'Active Directory server' and cm.parent_name in ('jira-administrators', 'group_jira') and cu.user_name not in (
select cu.user_name
from cwd_user cu
left join cwd_user_attributes cua on cu.id = cua.user_id 
inner join cwd_directory cd on cd.id = cu.directory_id 
inner join cwd_membership cm on cu.id = cm.child_id 
where cua.attribute_name = 'lastAuthenticated' and cd.directory_name != 'Active Directory server' and (cm.parent_name in ('jira-administrators', 'group_jira'))
)

select cu.user_name as login, cu.display_name as FIO, cu.email_address, cm.parent_name,  cua.attribute_value
from cwd_user cu
left join cwd_user_attributes cua on cu.id = cua.user_id 
inner join cwd_directory cd on cd.id = cu.directory_id 
inner join cwd_membership cm on cu.id = cm.child_id 
where cua.attribute_name = 'lastAuthenticated' and cd.directory_name != 'Active Directory server' and (cm.parent_name in ('jira-administrators', 'group_jira'))


############### FOMS ######################
select DISTINCT cu.user_name as login, cu.display_name as FIO 
from cwd_user cu 
inner join cwd_directory cd on cd.id = cu.directory_id 
inner join cwd_membership cm on cu.id = cm.child_id 
where cd.directory_name = 'AD' and cm.lower_parent_name in ('Внутренние пользователи', 'Первая линия СЭД - Практик', 'INFR users', 'jira-software-users', 'jira-administrators', 'SERMO_Operator_L1', 'SPOMS users')
order by cu.user_name

-------------------------------------------------------- ----------------------------------------
1. Список пользователей который входили в Jira и имеют доступ к Jira Software.

select distinct cu.user_name as login, cu.display_name as FIO, cu.email_address, cua.attribute_value
from cwd_user cu
left join cwd_user_attributes cua on cu.id = cua.user_id 
inner join cwd_directory cd on cd.id = cu.directory_id 
inner join cwd_membership cm on cu.id = cm.child_id 
inner join licenserolesgroup lrg ON Lower(cm.parent_name) = Lower(lrg.group_id)
where  cua.attribute_name = 'lastAuthenticated' and cd.directory_name != 'Active Directory server' AND license_role_name = 'jira-software'

2. Список пользователей который не входили в Jira и имеют доступ к Jira Software.

select distinct cu.user_name as login, cu.display_name as FIO, cu.email_address
from cwd_user cu, cwd_directory cd, cwd_membership cm, licenserolesgroup lrg 
where Lower(cm.parent_name) = Lower(lrg.group_id) 
and cu.id = cm.child_id 
and cd.id = cu.directory_id 
and cd.directory_name != 'Active Directory server' 
AND license_role_name = 'jira-software' 
and cu.user_name not in (
select distinct cu.user_name
from cwd_user cu
left join cwd_user_attributes cua on cu.id = cua.user_id 
inner join cwd_directory cd on cd.id = cu.directory_id 
inner join cwd_membership cm on cu.id = cm.child_id 
inner join licenserolesgroup lrg ON Lower(cm.parent_name) = Lower(lrg.group_id)
where  cua.attribute_name = 'lastAuthenticated' and cd.directory_name != 'Active Directory server' AND license_role_name = 'jira-software'
)

-------------------------------- Активность по проектам -----------------------------
select DISTINCT p.pname, cg.author
from changegroup cg 
inner join jiraissue ji on cg.issueid = ji.id
inner join project p on p.id = ji.project
inner join cwd_user cu on cu.user_name = cg.author 
inner join cwd_directory cd on cd.id = cu.directory_id 
where cd.directory_name != 'Active Directory server'
order by p.pname 
-------------------------------- Поля в проекте -------------------------------------
select distinct c.id, c.cfname
from fieldscreen fs
join fieldscreentab fst on fs.id = fst.fieldscreen
join fieldscreenlayoutitem fsl on fst.id = fsl.fieldscreentab
left outer join (select concat('customfield_',cf.id) as ident, cf.cfname, cf.id from customfield cf ) c on c.ident = fsl.fieldidentifier
where fs.name = 'FK: Task Management Create Issue Screen' or fs.name = 'FK: Task Management Edit/View Issue Screen'

-------------------------------- Время по статусам в проекте ------------------------------
select p.pkey ||'-'|| ji.issuenum as issue, ci.oldstring, cg.author, cg.created
from changegroup cg
inner join changeitem ci on cg.id = ci.groupid 
inner join jiraissue ji on ji.id = cg.issueid
inner join project p on ji.project = p.id 
where p.pkey = 'AUDIT' and ci.field = 'status'
order by issue, cg.created

select p.pkey ||'-'|| ji.issuenum as issue, ji.created 
from jiraissue ji
inner join project p on ji.project = p.id 
where p.pkey = 'AUDIT'
order by issue
----------------------------------- Список пользователе по проектам и ролям --------------------

/*select distinct cu.display_name as FIO, cu.user_name as login, cu.email_address, p.pname as proj, pr.NAME as role, cua.attribute_value
from cwd_user cu
left join cwd_user_attributes cua on cu.id = cua.user_id 
inner join cwd_directory cd on cd.id = cu.directory_id 
inner join cwd_membership cm on cu.id = cm.child_id 
inner join licenserolesgroup lrg ON Lower(cm.parent_name) = Lower(lrg.group_id)
LEFT JOIN cwd_membership cmem ON cmem.child_name = cu.lower_user_name
LEFT JOIN projectroleactor pra ON cmem.child_name = pra.roletypeparameter
LEFT JOIN projectrole pr ON pr.ID = pra.PROJECTROLEID
LEFT JOIN project p ON p.ID = pra.PID
where cua.attribute_name = 'lastAuthenticated' and cd.directory_name != 'Active Directory server' AND license_role_name = 'jira-software'*/


select distinct cu.display_name as FIO, cu.user_name as login, cu.email_address, p.pname as proj, pr.NAME as role
from cwd_user cu
left join cwd_user_attributes cua on cu.id = cua.user_id 
inner join cwd_directory cd on cd.id = cu.directory_id 
inner join cwd_membership cm on cu.id = cm.child_id 
inner join licenserolesgroup lrg ON Lower(cm.parent_name) = Lower(lrg.group_id)
LEFT JOIN cwd_membership cmem ON cmem.child_name = cu.lower_user_name
LEFT JOIN projectroleactor pra ON cmem.child_name = pra.roletypeparameter
LEFT JOIN projectrole pr ON pr.ID = pra.PROJECTROLEID
LEFT JOIN project p ON p.ID = pra.PID 
where cd.directory_name != 'Active Directory server' AND license_role_name = 'jira-software' 
and cu.user_name not in (
select distinct cu.user_name
from cwd_user cu
left join cwd_user_attributes cua on cu.id = cua.user_id 
inner join cwd_directory cd on cd.id = cu.directory_id 
inner join cwd_membership cm on cu.id = cm.child_id 
inner join licenserolesgroup lrg ON Lower(cm.parent_name) = Lower(lrg.group_id)
where  cua.attribute_name = 'lastAuthenticated' and cd.directory_name != 'Active Directory server' AND license_role_name = 'jira-software'
)


SELECT DISTINCT u.id, u.user_name, u.display_name, 
 CASE u.active
  WHEN 0 THEN 'Нет'
  WHEN 1 THEN 'Да' 
 END "действующая УЗ", u.email_address, u.created_date, p.pname, pr.NAME, cat.DIRECTORY_NAME
FROM cwd_user u
INNER JOIN cwd_directory cat ON cat.ID = u.DIRECTORY_ID
LEFT JOIN cwd_membership cmem ON cmem.child_name = u.lower_user_name
LEFT JOIN projectroleactor pra ON cmem.child_name = pra.roletypeparameter
LEFT JOIN projectrole pr ON pr.ID = pra.PROJECTROLEID
LEFT JOIN project p ON p.ID = pra.PID 
order by u.user_name;

SELECT DISTINCT u.id, u.user_name, u.display_name, 
 CASE u.active 
  WHEN 0 THEN 'Нет' 
  WHEN 1 THEN 'Да' 
 END "действующая УЗ", u.email_address, u.created_date, p.pname, pr.NAME, cat.DIRECTORY_NAME 
FROM cwd_user u 
INNER JOIN cwd_directory cat ON cat.ID = u.DIRECTORY_ID 
LEFT JOIN cwd_membership cmem ON cmem.child_name = u.lower_user_name 
LEFT JOIN projectroleactor pra ON cmem.child_name = pra.roletypeparameter 
LEFT JOIN projectrole pr ON pr.ID = pra.PROJECTROLEID 
LEFT JOIN project p ON p.ID = pra.PID order by u.user_name


SELECT p.PNAME as "Project", pr.name as "Role name", u.lower_user_name as "Username", u.display_name as "Display name", u.lower_email_address as "e-Mail", u.created_date
SELECT 
	u.id, 
	u.lower_user_name as "Username", 
	u.display_name as "Display name", 
	CASE u.active WHEN 0 THEN 'Нет' WHEN 1 THEN 'Да' END "действующая УЗ", 
	u.lower_email_address as "e-Mail", 
	u.created_date, 
	p.PNAME as "Project", 
	pr.name as "Role name", 
	cat.DIRECTORY_NAME 
FROM projectroleactor pra 
 INNER JOIN projectrole pr ON pr.ID = pra.PROJECTROLEID 
 INNER JOIN project p ON p.ID = pra.PID 
 INNER JOIN app_user au ON au.user_key = pra.ROLETYPEPARAMETER 
 RIGHT JOIN cwd_user u ON u.lower_user_name = au.lower_user_name 
 INNER JOIN cwd_directory cat ON cat.ID = u.DIRECTORY_ID 
UNION 
SELECT 
	u.id, 
	u.lower_user_name as "Username", 
	u.display_name as "Display name", 
	CASE u.active WHEN 0 THEN 'Нет' WHEN 1 THEN 'Да' END "действующая УЗ", 
	u.lower_email_address as "e-Mail", 
	u.created_date, 
	p.PNAME as "Project", 
	pr.name as "Role name", 
	cat.DIRECTORY_NAME 
FROM projectroleactor pra 
 INNER JOIN projectrole pr ON pr.ID = pra.PROJECTROLEID 
 INNER JOIN project p ON p.ID = pra.PID 
 INNER JOIN cwd_membership cmem ON cmem.parent_name = pra.roletypeparameter 
 INNER JOIN app_user au ON au.lower_user_name = cmem.lower_child_name 
 RIGHT JOIN cwd_user u ON u.lower_user_name = au.lower_user_name 
 INNER JOIN cwd_directory cat ON cat.ID = u.DIRECTORY_ID 
 order by 1, 2, 3;

SELECT DISTINCT 
	u.id, 
	u.user_name, 
	u.display_name, 
	CASE u.active WHEN 0 THEN 'Нет' WHEN 1 THEN 'Да' END "действующая УЗ", 
	u.email_address, 
	u.created_date, 
	p.pname "Проект", 
	pr.NAME "Роль", 
	cat.DIRECTORY_NAME 
FROM cwd_user u  
 INNER JOIN cwd_directory cat ON cat.ID = u.DIRECTORY_ID AND u.DIRECTORY_ID in ('10100', '1') 
 LEFT JOIN cwd_membership cmem ON cmem.child_name = u.lower_user_name 
 LEFT JOIN projectroleactor pra ON cmem.child_name = pra.roletypeparameter 
 LEFT JOIN projectrole pr ON pr.ID = pra.PROJECTROLEID
 LEFT JOIN project p ON p.ID = pra.PID order by u.user_name 

----------------------------- Дата последнего логина и кол-во логинов ---------------------------------------------
SELECT user_id, display_name, updated_date last_login, attribute_value login_count FROM cwd_user a, cwd_user_attributes b where attribute_name = 'login.count'
and a.id = b.user_id order by last_login DESC

------------------------------------------------- Дубли в задачах ------------------------------------------------------------
select ji.id, p.pkey ||'-'|| ji.issuenum as issue 
from jiraissue ji, (select ji.summary, ji.description, count(*)
		from jiraissue ji, project p
		where p.pkey in ('SDOMS','SERMO','SDISP','SRMP') and ji.project = p.id and created between '2021-08-01 00:00:00' and '2021-08-03 23:59:59'
		group by ji.summary, ji.description
		having count(*)>1) dup_sum_desc, project p
where created between '2021-08-01 00:00:00' and '2021-08-03 23:59:59' 
and p.pkey in ('SDOMS','SERMO','SDISP','SRMP') 
and ji.project = p.id 
and ji.reporter = 'telegram_bot'
and ji.summary = dup_sum_desc.summary and ji.description = dup_sum_desc.description 
order by id
-------------------------------------------------- Пропали переходы -------------------------------------------------------------------
select * from os_wfentry 
where id = (select workflow_id from jiraissue where issuenum = 2689 and project = (select id from project where pkey = 'ADMIN'));

update os_wfentry set state = 1 where id = (select workflow_id from jiraissue where issuenum = 4 and project = (select id from project where pkey = 'TTWO'));