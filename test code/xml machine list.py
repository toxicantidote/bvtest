
###

username = input('Username? ')
password = input('Password? ')

import requests
import re
import sqlite3
import json
## nonstandard libraries:
import anytree

## Request wrapper
def make_request(path, type = 'POST', cookies = {}, headers = {}, data = {}, json = {}):
    url = 'https://my.nayax.com/DCS/' + path
    if type == 'POST':
        request = requests.post(url, cookies = cookies, headers = headers, data = data, json = json)
    else:
        request = requests.get(url, cookies = cookies, headers = headers)
    return request

## Login to Nayax
def login(username, password):
	## 1: Get the signin token from the login page.  
	print('Getting login page')
	login_page = make_request('LoginPage.aspx', type = 'GET')
	regexp_token = re.search(r'var token = \'(.+)\'\;', login_page.text)
	if regexp_token:
		token = regexp_token.group(1)
		print('Login token: ' + str(token))

	## 2: Do the login. This redirects back to the login page, but we have the
	## session cookies.
	print('Performing login')
	login_post = make_request('LoginPage.aspx?ReturnUrl=%2fdcs%2fpublic%2fdefault.aspx', type = 'POST', headers = {'signin-token': token, 'Host': 'my.nayax.com', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://my.nayax.com', 'Referer': 'https://my.nayax.com/DCS/LoginPage.aspx?ReturnUrl=%2fdcs%2fpublic%2fdefault.aspx'}, json = {'userName': username, 'password': password, 'action': 'signin', 'newPassword': '', 'oldPassword': '', 'verifyPassword': ''})

	## 3: Get the dashboard. We can get the X-Nayax-Validation-Token value from this
	print('Getting dashboard')
	dashboard = make_request('public/facade.aspx?model=reports/dashboard', type = 'GET', headers = {'Host': 'my.nayax.com', 'Origin': 'https://my.nayax.com'}, cookies = login_post.cookies)
	regexp_nvtoken = re.search(r'var token = \'(.+)\'\;', dashboard.text)
	if regexp_nvtoken:
		nvtoken = regexp_nvtoken.group(1)
		print('NV token: ' + nvtoken)

	return nvtoken, login_post.cookies

## Initialise an in-memory SQlite3 database for storing data
def init_db():
	connection = sqlite3.connect(':memory:')
	cursor = connection.cursor()
	
	cursor.execute('CREATE table machines (id integer, parent integer, name text)')
	cursor.execute('CREATE table operators (id integer, parent integer, name text)')
	connection.commit()
	
	return connection, cursor

## translate actor name to machine name
def actor_to_name(connection, cursor, actor):
	for row in db_cursor.execute('SELECT name FROM operators WHERE id=?', [actor]):
		return row	
	
## get sales for the given machine
def get_sales(auth_token, auth_cookies, start, end, actor):
	print('Requesting cash sales for ' + actor_to_name(actor))
	sales_cash = make_request('public/facade.aspx?responseType=json&model=reports/SalesSummary&action=SalesSummary_Report&&actor_id=' + actor +'&num_of_rows=1000&with_cash=1&with_cashless_external=0&time_period=57&start_date=' + start + 'T00%3A00%3A00&end_date=' + end + 'T23%3A59%3A59.997&report_type=2', type = 'POST', headers = {'X-Nayax-Validation-Token': auth_token, 'Host': 'my.nayax.com', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://my.nayax.com', 'Referer': 'https://my.nayax.com/dcs/public/facade.aspx?model=reports/SalesSummary'}, cookies = auth_cookies)
	sales_card = make_request('public/facade.aspx?responseType=json&model=reports/SalesSummary&action=SalesSummary_Report&&actor_id=' + actor +'&num_of_rows=1000&with_cash=1&with_cashless_external=0&time_period=57&start_date=' + start + 'T00%3A00%3A00&end_date=' + end + 'T23%3A59%3A59.997&report_type=2', type = 'POST', headers = {'X-Nayax-Validation-Token': auth_token, 'Host': 'my.nayax.com', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://my.nayax.com', 'Referer': 'https://my.nayax.com/dcs/public/facade.aspx?model=reports/SalesSummary'}, cookies = auth_cookies)
	
	json_cash = json.loads(sales_cash.text)
	json_card = json.loads(sales_card.text)
	
	
	## todo: split out sales to return them. make sure we only get passed a lowest level actor to avoid big, slow requests.
	
	
	
## 4: Get the machine list in XML format.
print('Getting machine list')
auth_token, auth_cookies = login(username, password)
machines = make_request('public/facade.aspx?model=operations/machine&action=Machine.Machines_Search', type = 'POST', headers = {'X-Nayax-Validation-Token': auth_token, 'Host': 'my.nayax.com', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://my.nayax.com', 'Referer': 'https://my.nayax.com/dcs/public/facade.aspx?model=operations/machine'}, cookies = auth_cookies)

## Init database
db_connection, db_cursor = init_db()

## Pass the machine list to the XML parser
print('Parsing machine list')
for line in machines.text.split('/>'):
	regexp_machine = re.search(r'parent_id=\"(\d+)\" title=\"(.+)\" machine_id=\"(\d+)\"', line)
	regexp_operator = re.search(r'id=\"(\d+)\" parent_id=\"(\d+)\" title=\"(.+)\" actor_type_id', line)
	if regexp_machine:
		parent = regexp_machine.group(1)
		name = regexp_machine.group(2)
		id = regexp_machine.group(3)
		db_cursor.execute('INSERT INTO machines (id, parent, name) VALUES (?, ?, ?)', [id, parent, name])
	elif regexp_operator:
		parent = regexp_operator.group(2)
		name = regexp_operator.group(3)
		id = regexp_operator.group(1)
		db_cursor.execute('INSERT INTO operators (id, parent, name) VALUES (?, ?, ?)', [id, parent, name])
		
	db_connection.commit()

print('-' * 50)	
print('Operators: ')
operators = list(db_cursor.execute('SELECT * FROM operators'))
for row in operators:
	print(row)

print('-' * 50)		
print('Machines: ')
machines = list(db_cursor.execute('SELECT * FROM machines'))
for row in machines:
	print(row)
	
db_connection.close()
print('-' * 50)	
print('Located ' + str(len(machines)) + ' machines under ' + str(len(operators)) + ' operators')

print('All done!')