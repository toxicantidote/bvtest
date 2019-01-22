## Nayax sales data reporting tool
## Alex Farrell - September 2018
##
## Requires 'anytree' package (available from PyPi).
##
## This script grabs sales data for Nayax and allows you to generate reports
## based on this with fees and totals shown.
##

## Stylesheet to include in all HTML output
css = """
body {
    font-family: Arial;
    width: 100%;
}

.refund {
    color: #00A008;
    font-weight: bold;
}
.bill {
    color: #FF0000;
    font-weight: bold;
}
.refund:first-child, .bill:first-child {
    text-align: right;
}
table {
    border-collapse: collapse;
}
table tr * {
    border: 1px solid #000000;
}
table tr th {
    text-transform: capitalize;
}

ul, li {
    width: 70%;
    list-style: none;
    margin-top: 5px;
}

a {
    color: #82b1ff;
    text-decoration: none;    
}
a:hover {
    color: #ff614c;
}

.img-machine {
  background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAPCAIAAABSnclZAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAACeSURBVChTY+g/uQgr2nn36P///xkUJrvhQquv7YRKh68rgesDsuGCUOn2o3MgcnMvrAOS6NJAoeNPLgLR1dd3sEg3HpoO5ABR6pZ60nUD7canG2g4UB9EN5CNLo0VIaQ9l2cAzYQgIBtdunh3N8RpQARkQwSBSvEZDgwiUJRYL4gBmgM3HMiGyIGiBIiBkQN0MJABAZ9+foFE1////wHZEu3YGXacMgAAAABJRU5ErkJggg==');

  background-repeat: no-repeat;
  display: inline-block;
  height: 15px;
  width: 10px;
  border: 0;
  padding-right: 10px;
}
.img-operator {
  background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAABuhpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIiB4bWxuczpzdEV2dD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL3NUeXBlL1Jlc291cmNlRXZlbnQjIiB4bWxuczpzdFJlZj0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL3NUeXBlL1Jlc291cmNlUmVmIyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M2IChXaW5kb3dzKSIgeG1wOkNyZWF0ZURhdGU9IjIwMTUtMDItMTJUMTA6MTM6NTIrMDI6MDAiIHhtcDpNb2RpZnlEYXRlPSIyMDE1LTA3LTA5VDE4OjE1OjI4KzAzOjAwIiB4bXA6TWV0YWRhdGFEYXRlPSIyMDE1LTA3LTA5VDE4OjE1OjI4KzAzOjAwIiBkYzpmb3JtYXQ9ImltYWdlL3BuZyIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDo1NTIzNDY3OTI2NEQxMUU1ODFGNUM2NDMzNDNFODBFMCIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDo1NTIzNDY3QTI2NEQxMUU1ODFGNUM2NDMzNDNFODBFMCIgeG1wTU06T3JpZ2luYWxEb2N1bWVudElEPSJ4bXAuZGlkOjdGNkY0MTU5RDJBQUU0MTFBODNDREE5OEUwRjE2RTAzIj4gPHhtcE1NOkhpc3Rvcnk+IDxyZGY6U2VxPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0iY3JlYXRlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDo3RjZGNDE1OUQyQUFFNDExQTgzQ0RBOThFMEYxNkUwMyIgc3RFdnQ6d2hlbj0iMjAxNS0wMi0xMlQxMDoxMzo1MiswMjowMCIgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoV2luZG93cykiLz4gPHJkZjpsaSBzdEV2dDphY3Rpb249InNhdmVkIiBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOkIzN0E1NzRFMzVCQkU0MTFBQTNGQ0QxQ0Q3M0VGRUU3IiBzdEV2dDp3aGVuPSIyMDE1LTAyLTIzVDEwOjM0OjA0KzAyOjAwIiBzdEV2dDpzb2Z0d2FyZUFnZW50PSJBZG9iZSBQaG90b3Nob3AgQ1M2IChXaW5kb3dzKSIgc3RFdnQ6Y2hhbmdlZD0iLyIvPiA8cmRmOmxpIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6OTkzQUI1QjA2NjI1RTUxMUJDMEZDN0E3NTNGMkJDNzgiIHN0RXZ0OndoZW49IjIwMTUtMDctMDhUMTY6MTg6MDUrMDM6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCBDUzYgKFdpbmRvd3MpIiBzdEV2dDpjaGFuZ2VkPSIvIi8+IDwvcmRmOlNlcT4gPC94bXBNTTpIaXN0b3J5PiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo5OTNBQjVCMDY2MjVFNTExQkMwRkM3QTc1M0YyQkM3OCIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDo3RjZGNDE1OUQyQUFFNDExQTgzQ0RBOThFMEYxNkUwMyIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/Plb+PDkAAAEXSURBVHjaYvz//z8DLrDIe+4UIJWNJDQpbmtyPja1TAz4AQ8anx+XQkIGEQ2GnkF/0fi/yTWoFIi9oWwQXYZLISNy9AOjGxRLKmhqpIB4K9SgZ2hyN4HJ4TuKQUBDRIDUBSCWJiFo7gCxIdCwLyxIgtFQr2oC8Q8kcRkgPgzEtkD8BEmcF4iPA7E/EC9FNkgeiG8BTb+BlrphzCdAuQdociAXicK9BhQAhUsRECtBA/gqUNM/oLgQkG2BFEYngOLvgOIgl2sD8UIg3g7E82EuuokUg+5AbAPER4G4C4iToeIgw0DOSwFiSyA+AhU3BOIKJhzJgBVKs6CJs6DJw5PRCMhrX5HEQCn0M5T9GU09sjhyifgVIMAAlWRPXyv4xUIAAAAASUVORK5CYII=');

  background-repeat: no-repeat;
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 0;
  padding-right: 10px;
}
.img-close {
    background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsIAAA7CARUoSoAAAAKVSURBVDhPlZRbaxNBFMf/u7lnt6VFSaX4YgWxQatWTRTEN18sigRFfPZFBKtWfRbUB/0GClK8Pogg9EFUpE1N7IU2oF/AR5Hm2iSml+zujGd2JzZptmJ+MJnJmTNnZv7n7CjLpwe4ogCcA3aPdshMdtX+dfcQPsKLeiegAlbMgpuWs3ozzTE2z4uDeDxQtkXsKaVMAVkpB9/7H/Bo3YBlOo4C52gbQRrj5g0omFFfBzu1k4L2iYC7OMsvQU/l4Q2EpFdn1GmHWkyDJ9IPlXNne87ouqIXYv4nf30tZ61AFYloRuhZGn+E4oOrLTdrIGzFh6MoPrlv+7YhNCzFwry+UqUNHZai4JW4xrPXz3EmbQ1yty7w5XiYZ/fSpaRt3TR48WiIl0d2c7Uta0To7SLqpolAZhr5a2ekFciNJeCb+wzLMBB6M++2lIrLRbOu6BEEXs7CWKki8C2Nwt3LKN67Av/CFKxaGf5naehDcendimpXtQv64DACrxdhenzwznyA58sEmOqF/9U89P3uwQSq4iq9gzZ4CHz4JHlR4VKzDp6Avi8mZ91RuasSAKNWGDsPbyYJZhpgVBq+7ynkRs/+4whCQxfEgtLti/AtTML8TZo9/gTfUxpXpaY3ElsGdb1y4c4leGc/wlyrIfD8K7Q9B6ANREnTORirq/BnppC/mZDerVCW5agJK/kOVqWC4HiKsnlcWilRIvsvZmCUy+DJCWltheqwVUOhXe90DuHJn9CGjjnGJvToYWjJX+hJF1yvTRpKM2XR7qj59W4E+/rt/24Et++Av6tnI51yrcC+sqKqMOkJMqnITfpCOmqM0fO1ZpeVwH5gxVb2A9v0anSCCKb2RmhAoUoj9GKLU27xxXQC4xx/AK+VPy32Ww7cAAAAAElFTkSuQmCC');
    background-repeat: no-repeat;
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 0;
    float: right;
    top: 10px;
}



.feetable {
    display: none;
    right: 10%;
    top: 25%;
    position: fixed;
    width: 50%;
    height: 50%;
    overflow-x: auto;
    overflow-y: auto;
    border: 1px solid #000000;
    background-color: #e3e9f2;
    padding: 10px;
}

.products {
    margin-top: 40px;
    height: 50%;
    margin-bottom: 40px;
}
"""

## Javascript to include
javascript = """
var tree = document.querySelectorAll('ul.tree a:not(:last-child)');
for(var i = 0; i < tree.length; i++){
    tree[i].addEventListener('click', function(e) {
        var parent = e.target.parentElement;
        var classList = parent.classList;
        if(classList.contains("open")) {
            classList.remove('open');
            var opensubs = parent.querySelectorAll(':scope .open');
            for(var i = 0; i < opensubs.length; i++){
                opensubs[i].classList.remove('open');
            }
        } else {
            classList.add('open');
        }
        e.preventDefault();
    });
}
function toggleVis(target) {
    var oldvis = document.getElementsByClassName("feetable");
    for (var i = 0; i < oldvis.length; i++) {
        oldvis[i].style.display = "none";
    }

    if (document.getElementById("fee-" + target).style.display == "block") {
        document.getElementById("fee-" + target).style.display = "none";
    } else {
        document.getElementById("fee-" + target).style.display = "block";
    }

}

function hideTable(target) {
    document.getElementById("fee-" + target).style.display = "none";
}
"""

###

import requests
import re
import sqlite3
import json
import pickle
from concurrent.futures import ThreadPoolExecutor
import time
from tkinter import *
from tkinter import messagebox, filedialog, simpledialog
import tkinter.ttk as ttk
import tkinter.font as tkFont
from tkinter.constants import CENTER, LEFT, N, E, W, S
import calendar
import datetime
import anytree
import traceback
import random
import string

## Request wrapper
def make_request(path, type = 'POST', cookies = {}, headers = {}, data = {}, json = {}, retry = 0):
    url = 'https://my.nayax.com/DCS/' + path
    try:
        if type == 'POST':
            request = requests.post(url, cookies = cookies, headers = headers, data = data, json = json)
        else:
            request = requests.get(url, cookies = cookies, headers = headers)
    ## retry half a second later up to three times if the request fails
    except requests.exceptions.ConnectionError:
        if retry < 3:
            time.sleep(0.5)
            request = make_request(path, type, cookies, headers, data, json, retry = retry + 1)
    return request

## Login to Nayax
def login(username, password):
    nvtoken = None

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
    if re.search(r'UNKNOWNCREDS', login_post.text):
        print('Incorrect login')
        return None, None    

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
    sqlite3.register_adapter(bool, int)
    sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
    cursor = connection.cursor()
   
    cursor.execute('CREATE TABLE machines (id integer, parent integer, name text, active bool)')
    cursor.execute('CREATE TABLE operators (id integer, parent integer, name text)')
    cursor.execute('CREATE TABLE sales (id integer, cash_amount real DEFAULT 0, cash_count int DEFAULT 0, card_amount real DEFAULT 0, card_count int DEFAULT 0)')
    cursor.execute('CREATE TABLE fees (id integer, name text, amount real DEFAULT 0, type text, value real DEFAULT 0)')
    cursor.execute('CREATE TABLE sales_product (machine_id int, product text, cash_amount real DEFAULT 0, cash_count int DEFAULT 0, card_amount real DEFAULT 0, card_count int DEFAULT 0)')
    
    connection.commit()
    
    return connection, cursor

## translate actor name to operator or machine name
def actor_to_name(cursor, actor, check_machines = False):
    for row in cursor.execute('SELECT name FROM operators WHERE id=?', [actor]):
        return row[0]
    
    if check_machines == True:
        for row in cursor.execute('SELECT name FROM machines WHERE id=?', [actor]):
            return row[0]
    
    return None
        
## determine if machine was active during period
def get_active(tree, auth_token, auth_cookies, id, start, end):
    ## override: if the machine has card sales, it was active
    if tree[id].sales_card_count > 0:
        return id, True

    ## start/end are YYYY-MM-DD

    url = 'public/facade.aspx?model=operations/machine&action=MachineHistory.Get&machine_id=' + str(id)
    machine_history = make_request(url, type = 'POST', headers = {'X-Nayax-Validation-Token': auth_token, 'Host': 'my.nayax.com', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://my.nayax.com', 'Referer': 'https://my.nayax.com/dcs/public/facade.aspx?model=operations/machine'}, cookies = auth_cookies)
    
    ## work out if the machine has been active at any point during the reporting period
    #print('MACHINE_HISTORY:\n' + machine_history.text)
    events_active = []
    start_datestamp = datetime.datetime.strptime(start + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_datestamp = datetime.datetime.strptime(end + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
    has_active_event = False
    has_deactive_event = False
    payable = False
    for match in re.finditer(r'changed_item="(Status|Device)" changed_from="(Active|Not Active|\d+|Empty field)" changed_to="(Active|Not Active|\d+|Empty field)" updated_at="([\d\-\.\:T]+)\.(\d+)"', machine_history.text):
        match_from = match.group(2)        
        match_to = match.group(3)
        match_datestamp = datetime.datetime.strptime(match.group(4), '%Y-%m-%dT%H:%M:%S')        
        
        ## check if it was activated ever
        if (match_from == 'Not Active' or match_from == 'Empty field') and (match_to == 'Active' or re.search(r'\d+', match_to)):        
            has_active_event = True
            ## check if it was activated during this period
            if match_datestamp >= start_datestamp and match_datestamp <= end_datestamp:
                ## if so, this is billable for DTU fees
                payable = True
                break        
        
        ## check if it was deactivated
        if (match_from == 'Active' or re.search(r'\d+', match_from)) and (match_to == 'Not Active' or match_to == 'Empty field'):
            ## if deactivated during this period, it is billable
            if match_datestamp >= start_datestamp and match_datestamp <= end_datestamp:
                payable = True
                break
            elif match_datestamp <= start_datestamp:
                has_deactive_event = True

    if has_active_event == True and has_deactive_event == False:
        payable = True
        
    return id, payable      
            

## make an anytree structure with the operators and machines            
def make_tree(cursor):        

    print('Making tree')
    tree = dict()
    root_node = None
    
    ## fill the tree
    operators = list(cursor.execute('SELECT * FROM operators ORDER BY name ASC'))
    for row in operators:
        tree[row[0]] = anytree.Node(row[0], record_name = row[2], record_type = 'operator', sales_cash_amount = 0, sales_cash_count = 0, sales_card_amount = 0, sales_card_count = 0, active = None, fees = [], get_product_sales = False)
        
    machines = list(cursor.execute('SELECT * FROM machines ORDER BY name ASC'))
    for row in machines:
        tree[row[0]] = anytree.Node(row[0], record_name = row[2], record_type = 'machine', sales_cash_amount = 0, sales_cash_count = 0, sales_card_amount = 0, sales_card_count = 0, active = None, fees = [], get_product_sales = False)
        
    ## do relationships
    operators = list(cursor.execute('SELECT * FROM operators'))
    for row in operators:
        try:
            tree[row[0]].parent = tree[row[1]]
        except KeyError:
            root_node = tree[row[0]]
        
    machines = list(cursor.execute('SELECT * FROM machines'))
    for row in machines:
        tree[row[0]].parent = tree[row[1]]

    return tree, root_node
    
## get sales for the given machine
def get_sales(auth_token, auth_cookies, start, end, actor):
    actor = str(actor)
    #print('Retrieving sales data for ' + actor + '..')    
    sales_cash = make_request('public/facade.aspx?responseType=json&model=reports/SalesSummary&action=SalesSummary_Report&&actor_id=' + actor + '&payment_method=3&num_of_rows=1000000&with_cash=1&with_cashless_external=0&time_period=57&start_date=' + start + 'T00%3A00%3A00&end_date=' + end + 'T23%3A59%3A59.997&report_type=2', type = 'POST', headers = {'X-Nayax-Validation-Token': auth_token, 'Host': 'my.nayax.com', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://my.nayax.com', 'Referer': 'https://my.nayax.com/dcs/public/facade.aspx?model=reports/SalesSummary'}, cookies = auth_cookies)
    sales_card = make_request('public/facade.aspx?responseType=json&model=reports/SalesSummary&action=SalesSummary_Report&&actor_id=' + actor + '&payment_method=1&num_of_rows=1000000&with_cash=0&with_cashless_external=0&time_period=57&start_date=' + start + 'T00%3A00%3A00&end_date=' + end + 'T23%3A59%3A59.997&report_type=2', type = 'POST', headers = {'X-Nayax-Validation-Token': auth_token, 'Host': 'my.nayax.com', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://my.nayax.com', 'Referer': 'https://my.nayax.com/dcs/public/facade.aspx?model=reports/SalesSummary'}, cookies = auth_cookies)
    
    json_cash = json.loads(sales_cash.text)
    json_card = json.loads(sales_card.text)   
    
    return actor, json_cash, json_card
       
## clean foreign characters from names
def clean_name(name):
    name = re.sub('&amp;', '&', name)
    name = re.sub(r'[^\w\s\-\.\&\'\/\(\)]', '', name)
    return name
    
## process the sales json in to the database
def process_sales(cursor, json_cash, json_card):    
    for entry in json_cash['data'][1]:
        machine_id = entry['machine_id']        
        try:
            cash_amount = entry['total_amount']
        except:
            cash_amount = 0
            
        try:
            cash_count = entry['total_count']
        except:
            cash_count = 0
        cursor.execute('UPDATE sales SET cash_amount=?, cash_count=? WHERE id=?', [cash_amount, cash_count, machine_id])
        if cursor.rowcount == 0:
            cursor.execute('INSERT INTO sales (id, cash_amount, cash_count) VALUES (?,?,?)', [machine_id, cash_amount, cash_count])        
        
    for entry in json_card['data'][1]:
        machine_id = entry['machine_id']        
        try:
            card_amount = entry['total_amount']
        except:
            card_amount = 0
            
        try:
            card_count = entry['total_count']
        except:
            card_count = 0
        cursor.execute('UPDATE sales SET card_amount=?, card_count=? WHERE id=?', [card_amount, card_count, machine_id])
        if cursor.rowcount == 0:
            cursor.execute('INSERT INTO sales (id, card_amount, card_count) VALUES (?,?,?)', [machine_id, card_amount, card_count])            
       
def operator_machine_count(search_node):
    return len(anytree.search.findall_by_attr(node = search_node, value = 'machine', name = 'record_type'))
    
def operator_direct_machines(search_node):
    count = 0
    for child in search_node.children:
        if child.record_type == 'machine':
            count += 1

    return count
    
def operator_child_count(search_node):
    return len(anytree.search.findall_by_attr(node = search_node, value = 'operator', name = 'record_type'))
    
def reduce_tree(search_node):
    nodes = []
    if operator_machine_count(search_node) < 500:
        #print('Operator ' + search_node.record_name + ' has less than 500 machines. Using node.')
        nodes.append(search_node)
    else:
        #print('Operator ' + search_node.record_name + ' has too many machines. Descending tree..')
        if operator_child_count(search_node) == 0 or operator_direct_machines(search_node) > 0:
            #print('Operator ' + search_node.record_name + ' has no operators under it, or has direct machines. Giving up.')
            nodes.append(search_node)
        else:
            for child in search_node.children:                
                nodes = nodes + reduce_tree(child)
            
    return nodes

def get_machine_list(db_cursor, db_connection, auth_token, auth_cookies):    
    ## 4: Get the machine list in XML format.
    print('Getting machine list')
    
    machines = make_request('public/facade.aspx?model=operations/machine&action=Machine.Machines_Search', type = 'POST', headers = {'X-Nayax-Validation-Token': auth_token, 'Host': 'my.nayax.com', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://my.nayax.com', 'Referer': 'https://my.nayax.com/dcs/public/facade.aspx?model=operations/machine'}, cookies = auth_cookies)

    ## Pass the machine list to the XML parser
    print('Parsing machine list')
    for line in machines.text.split('/>'):
        regexp_machine = re.search(r'parent_id=\"(\d+)\" title=\"(.+)\" machine_id=\"(\d+)\"', line)
        regexp_operator = re.search(r'id=\"(\d+)\" parent_id=\"(\d+)\" title=\"(.+)\" actor_type_id', line)
        if regexp_machine:
            parent = regexp_machine.group(1)
            name = clean_name(regexp_machine.group(2))
            id = regexp_machine.group(3)
            db_cursor.execute('INSERT INTO machines (id, parent, name) VALUES (?, ?, ?)', [id, parent, name])
        elif regexp_operator:
            parent = regexp_operator.group(2)
            name = clean_name(regexp_operator.group(3))
            id = regexp_operator.group(1)
            db_cursor.execute('INSERT INTO operators (id, parent, name) VALUES (?, ?, ?)', [id, parent, name])
            
        db_connection.commit()

    operators = list(db_cursor.execute('SELECT * FROM operators'))
    machines = list(db_cursor.execute('SELECT * FROM machines'))
        
    print('-' * 50) 
    print('Located ' + str(len(machines)) + ' machines under ' + str(len(operators)) + ' operators')

    ## 5: Work out which operators to query to balance query size and speed (otherwise Nayax times out). Build a tree of operators and machines.
    tree, root_node = make_tree(db_cursor)
    
    return tree, root_node

def get_sales_data(tree, root_node, db_cursor, auth_token, auth_cookies, start_date, end_date, update_callback = None):    
    query_operators = reduce_tree(root_node)

    ## 6: Get cash and card sales data for machines
    print('Getting sales data..')
    executor = ThreadPoolExecutor(max_workers = 25)
    thread_list = []
    done = 0
    for op in query_operators:
        thread_list.append(executor.submit(get_sales, auth_token, auth_cookies, start_date, end_date, op.name))
        done += 1
        print('[' + str(done) + '/' + str(len(query_operators)) + '] Getting sales data for operator ' + actor_to_name(db_cursor, op.name) + '..', end='\r')
        if update_callback != None:
            update_callback('Requesting ' + actor_to_name(db_cursor, op.name))
        
    for thread_child in thread_list:    
        id, json_cash, json_card = thread_child.result()
        print('[' + str(thread_list.index(thread_child) + 1) + '/' + str(len(thread_list)) + '] Processing sales data for ' + actor_to_name(db_cursor, id), end='\r')
        if update_callback != None:
            update_callback('Processing ' + actor_to_name(db_cursor, op.name))
            
        process_sales(db_cursor, json_cash, json_card)        

    print('Adding sales to tree..')
    sales = list(db_cursor.execute('SELECT * FROM sales'))
    for row in sales:
        try:
            tree[row[0]].sales_cash_amount = row[1]
            tree[row[0]].sales_cash_count = row[2]
            tree[row[0]].sales_card_amount = row[3]
            tree[row[0]].sales_card_count = row[4]
        except KeyError:
            #print('Could not find tree entry for ID ' + str(row[0]))
            pass
            
    return tree

def get_active_info(tree, machines, db_cursor, auth_token, auth_cookies, id, start_date, end_date):
    ## 7: Check which machines are active for this period
    executor = ThreadPoolExecutor(max_workers = 25)
    total_machines = len(machines)
    thread_active = []
    for row in machines:
        id = row[0]
        name = row[2]
        print('[' + str(machines.index(row)) + '/' + str(total_machines) + '] Checking if ' + str(name) + ' was active during period..', end='\r')
        thread_active.append(executor.submit(get_active, auth_token, auth_cookies, id, start_date, end_date))
        
    for thread_child in thread_active:
        id, active = thread_child.result()
        try:
            tree[id].active = active
            db_cursor.execute('UPDATE machines SET active=? WHERE id=?', [active, id])
        except:
            pass

def generate_html(db_cursor, root_node):        
    ## 8: Make the HTML list
    print('Generating output..')
    outHTML = open('out.html', 'w')
    outHTML.write('<!DOCTYPE html>\n<html><head><title>Sales data</title></head><body>')
    generate_html_list(outHTML, db_cursor, root_node)
    outHTML.write('</body></html>')
    outHTML.close()

## calendar and datepicker classes from http://code.activestate.com/recipes/580725-tkinter-datepicker-like-the-jquery-ui-datepicker/

def get_calendar(locale, fwday):
    # instantiate proper calendar class
    if locale is None:
        return calendar.TextCalendar(fwday)
    else:
        return calendar.LocaleTextCalendar(fwday, locale)

class Calendar(ttk.Frame):
    datetime = calendar.datetime.datetime
    timedelta = calendar.datetime.timedelta

    def __init__(self, master=None, year=None, month=None, firstweekday=calendar.MONDAY, locale=None, activebackground='#b1dcfb', activeforeground='black', selectbackground='#003eff', selectforeground='white', command=None, borderwidth=1, relief="solid", on_click_month_button=None):
        """
        WIDGET OPTIONS

            locale, firstweekday, year, month, selectbackground,
            selectforeground, activebackground, activeforeground, 
            command, borderwidth, relief, on_click_month_button
        """

        if year is None:
            year = self.datetime.now().year
        
        if month is None:
            month = self.datetime.now().month

        self._selected_date = None

        self._sel_bg = selectbackground 
        self._sel_fg = selectforeground

        self._act_bg = activebackground 
        self._act_fg = activeforeground
        
        self.on_click_month_button = on_click_month_button
        
        self._selection_is_visible = False
        self._command = command

        ttk.Frame.__init__(self, master, borderwidth=borderwidth, relief=relief)
        
        self.bind("<FocusIn>", lambda event:self.event_generate('<<DatePickerFocusIn>>'))
        self.bind("<FocusOut>", lambda event:self.event_generate('<<DatePickerFocusOut>>'))
    
        self._cal = get_calendar(locale, firstweekday)

        # custom ttk styles
        style = ttk.Style()
        style.layout('L.TButton', (
            [('Button.focus', {'children': [('Button.leftarrow', None)]})]
        ))
        style.layout('R.TButton', (
            [('Button.focus', {'children': [('Button.rightarrow', None)]})]
        ))

        self._font = tkFont.Font()
        
        self._header_var = StringVar()

        # header frame and its widgets
        hframe = ttk.Frame(self)
        lbtn = ttk.Button(hframe, style='L.TButton', command=self._on_press_left_button)
        lbtn.pack(side=LEFT)
        
        self._header = ttk.Label(hframe, width=15, anchor=CENTER, textvariable=self._header_var)
        self._header.pack(side=LEFT, padx=12)
        
        rbtn = ttk.Button(hframe, style='R.TButton', command=self._on_press_right_button)
        rbtn.pack(side=LEFT)
        hframe.grid(columnspan=7, pady=4)

        self._day_labels = {}

        days_of_the_week = self._cal.formatweekheader(3).split()
 
        for i, day_of_the_week in enumerate(days_of_the_week):
            ttk.Label(self, text=day_of_the_week, background='grey90').grid(row=1, column=i, sticky=N+E+W+S)

        for i in range(6):
            for j in range(7):
                self._day_labels[i,j] = label = ttk.Label(self, background = "white")
                
                label.grid(row=i+2, column=j, sticky=N+E+W+S)
                label.bind("<Enter>", lambda event: event.widget.configure(background=self._act_bg, foreground=self._act_fg))
                label.bind("<Leave>", lambda event: event.widget.configure(background="white"))

                label.bind("<1>", self._pressed)
        
        # adjust its columns width
        font = tkFont.Font()
        maxwidth = max(font.measure(text) for text in days_of_the_week)
        for i in range(7):
            self.grid_columnconfigure(i, minsize=maxwidth, weight=1)

        self._year = None
        self._month = None

        # insert dates in the currently empty calendar
        self._build_calendar(year, month)

    def _build_calendar(self, year, month):
        if not( self._year == year and self._month == month):
            self._year = year
            self._month = month

            # update header text (Month, YEAR)
            header = self._cal.formatmonthname(year, month, 0)
            self._header_var.set(header.title())

            # update calendar shown dates
            cal = self._cal.monthdayscalendar(year, month)

            for i in range(len(cal)):
                
                week = cal[i] 
                fmt_week = [('%02d' % day) if day else '' for day in week]
                
                for j, day_number in enumerate(fmt_week):
                    self._day_labels[i,j]["text"] = day_number

            if len(cal) < 6:
                for j in range(7):
                    self._day_labels[5,j]["text"] = ""

        if self._selected_date is not None and self._selected_date.year == self._year and self._selected_date.month == self._month:
            self._show_selection()

    def _find_label_coordinates(self, date):
         first_weekday_of_the_month = (date.weekday() - date.day) % 7
         
         return divmod((first_weekday_of_the_month - self._cal.firstweekday)%7 + date.day, 7)
        
    def _show_selection(self):
        """Show a new selection."""

        i,j = self._find_label_coordinates(self._selected_date)

        label = self._day_labels[i,j]

        label.configure(background=self._sel_bg, foreground=self._sel_fg)

        label.unbind("<Enter>")
        label.unbind("<Leave>")
        
        self._selection_is_visible = True
        
    def _clear_selection(self):
        """Show a new selection."""
        i,j = self._find_label_coordinates(self._selected_date)

        label = self._day_labels[i,j]
        label.configure(background= "white", foreground="black")

        label.bind("<Enter>", lambda event: event.widget.configure(background=self._act_bg, foreground=self._act_fg))
        label.bind("<Leave>", lambda event: event.widget.configure(background="white"))

        self._selection_is_visible = False

    # Callback

    def _pressed(self, evt):
        """Clicked somewhere in the calendar."""
        
        text = evt.widget["text"]
        
        if text == "":
            return

        day_number = int(text)

        new_selected_date = datetime.datetime(self._year, self._month, day_number)
        if self._selected_date != new_selected_date:
            if self._selected_date is not None:
                self._clear_selection()
            
            self._selected_date = new_selected_date
            
            self._show_selection()
        
        if self._command:
            self._command(self._selected_date)

    def _on_press_left_button(self):
        self.prev_month()
        
        if self.on_click_month_button is not None:
            self.on_click_month_button()
    
    def _on_press_right_button(self):
        self.next_month()

        if self.on_click_month_button is not None:
            self.on_click_month_button()
        
    def select_prev_day(self):
        """Updated calendar to show the previous day."""
        if self._selected_date is None:
            self._selected_date = datetime.datetime(self._year, self._month, 1)
        else:
            self._clear_selection()
            self._selected_date = self._selected_date - self.timedelta(days=1)

        self._build_calendar(self._selected_date.year, self._selected_date.month) # reconstruct calendar

    def select_next_day(self):
        """Update calendar to show the next day."""

        if self._selected_date is None:
            self._selected_date = datetime.datetime(self._year, self._month, 1)
        else:
            self._clear_selection()
            self._selected_date = self._selected_date + self.timedelta(days=1)

        self._build_calendar(self._selected_date.year, self._selected_date.month) # reconstruct calendar


    def select_prev_week_day(self):
        """Updated calendar to show the previous week."""
        if self._selected_date is None:
            self._selected_date = datetime.datetime(self._year, self._month, 1)
        else:
            self._clear_selection()
            self._selected_date = self._selected_date - self.timedelta(days=7)

        self._build_calendar(self._selected_date.year, self._selected_date.month) # reconstruct calendar

    def select_next_week_day(self):
        """Update calendar to show the next week."""
        if self._selected_date is None:
            self._selected_date = datetime.datetime(self._year, self._month, 1)
        else:
            self._clear_selection()
            self._selected_date = self._selected_date + self.timedelta(days=7)

        self._build_calendar(self._selected_date.year, self._selected_date.month) # reconstruct calendar

    def select_current_date(self):
        """Update calendar to current date."""
        if self._selection_is_visible: self._clear_selection()

        self._selected_date = datetime.datetime.now()
        self._build_calendar(self._selected_date.year, self._selected_date.month)

    def prev_month(self):
        """Updated calendar to show the previous week."""
        if self._selection_is_visible: self._clear_selection()
        
        date = self.datetime(self._year, self._month, 1) - self.timedelta(days=1)
        self._build_calendar(date.year, date.month) # reconstuct calendar

    def next_month(self):
        """Update calendar to show the next month."""
        if self._selection_is_visible: self._clear_selection()

        date = self.datetime(self._year, self._month, 1) + \
            self.timedelta(days=calendar.monthrange(self._year, self._month)[1] + 1)

        self._build_calendar(date.year, date.month) # reconstuct calendar

    def prev_year(self):
        """Updated calendar to show the previous year."""
        
        if self._selection_is_visible: self._clear_selection()

        self._build_calendar(self._year-1, self._month) # reconstruct calendar

    def next_year(self):
        """Update calendar to show the next year."""
        
        if self._selection_is_visible: self._clear_selection()

        self._build_calendar(self._year+1, self._month) # reconstruct calendar

    def get_selection(self):
        """Return a datetime representing the current selected date."""
        return self._selected_date
        
    selection = get_selection

    def set_selection(self, date):
        """Set the selected date."""
        if self._selected_date is not None and self._selected_date != date:
            self._clear_selection()

        self._selected_date = date

        self._build_calendar(date.year, date.month) # reconstruct calendar

# see this URL for date format information:
#     https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

class Datepicker(ttk.Entry):
    def __init__(self, master, entrywidth=None, entrystyle=None, datevar=None, dateformat="%Y-%m-%d", onselect=None, firstweekday=calendar.MONDAY, locale=None, activebackground='#b1dcfb', activeforeground='black', selectbackground='#003eff', selectforeground='white', borderwidth=1, relief="solid"):
        
        if datevar is not None:
            self.date_var = datevar
        else:
            self.date_var = StringVar()

        entry_config = {}
        if entrywidth is not None:
            entry_config["width"] = entrywidth
            
        if entrystyle is not None:
            entry_config["style"] = entrystyle
    
        ttk.Entry.__init__(self, master, textvariable=self.date_var, **entry_config)

        self.date_format = dateformat
        
        self._is_calendar_visible = False
        self._on_select_date_command = onselect

        self.calendar_frame = Calendar(self.winfo_toplevel(), firstweekday=firstweekday, locale=locale, activebackground=activebackground, activeforeground=activeforeground, selectbackground=selectbackground, selectforeground=selectforeground, command=self._on_selected_date, on_click_month_button=lambda: self.focus())

        self.bind_all("<1>", self._on_click, "+")

        self.bind("<FocusOut>", lambda event: self._on_entry_focus_out())
        self.bind("<Escape>", lambda event: self.hide_calendar())
        self.calendar_frame.bind("<<DatePickerFocusOut>>", lambda event: self._on_calendar_focus_out())


        # CTRL + PAGE UP: Move to the previous month.
        self.bind("<Control-Prior>", lambda event: self.calendar_frame.prev_month())
        
        # CTRL + PAGE DOWN: Move to the next month.
        self.bind("<Control-Next>", lambda event: self.calendar_frame.next_month())

        # CTRL + SHIFT + PAGE UP: Move to the previous year.
        self.bind("<Control-Shift-Prior>", lambda event: self.calendar_frame.prev_year())

        # CTRL + SHIFT + PAGE DOWN: Move to the next year.
        self.bind("<Control-Shift-Next>", lambda event: self.calendar_frame.next_year())
        
        # CTRL + LEFT: Move to the previous day.
        self.bind("<Control-Left>", lambda event: self.calendar_frame.select_prev_day())
        
        # CTRL + RIGHT: Move to the next day.
        self.bind("<Control-Right>", lambda event: self.calendar_frame.select_next_day())
        
        # CTRL + UP: Move to the previous week.
        self.bind("<Control-Up>", lambda event: self.calendar_frame.select_prev_week_day())
        
        # CTRL + DOWN: Move to the next week.
        self.bind("<Control-Down>", lambda event: self.calendar_frame.select_next_week_day())

        # CTRL + END: Close the datepicker and erase the date.
        self.bind("<Control-End>", lambda event: self.erase())

        # CTRL + HOME: Move to the current month.
        self.bind("<Control-Home>", lambda event: self.calendar_frame.select_current_date())
        
        # CTRL + SPACE: Show date on calendar
        self.bind("<Control-space>", lambda event: self.show_date_on_calendar())
        
        # CTRL + Return: Set to entry current selection
        self.bind("<Control-Return>", lambda event: self.set_date_from_calendar())

    def set_date_from_calendar(self):
        if self.is_calendar_visible:
            selected_date = self.calendar_frame.selection()

            if selected_date is not None:
                self.date_var.set(selected_date.strftime(self.date_format))
                
                if self._on_select_date_command is not None:
                    self._on_select_date_command(selected_date)

            self.hide_calendar()
      
    @property
    def current_text(self):
        return self.date_var.get()
        
    @current_text.setter
    def current_text(self, text):
        return self.date_var.set(text)
        
    @property
    def current_date(self):
        try:
            date = datetime.datetime.strptime(self.date_var.get(), self.date_format)
            return date
        except ValueError:
            return None
    
    @current_date.setter
    def current_date(self, date):
        self.date_var.set(date.strftime(self.date_format))
        
    @property
    def is_valid_date(self):
        if self.current_date is None:
            return False
        else:
            return True

    def show_date_on_calendar(self):
        date = self.current_date
        if date is not None:
            self.calendar_frame.set_selection(date)

        self.show_calendar()

    def show_calendar(self):
        if not self._is_calendar_visible:
            self.calendar_frame.place(in_=self, relx=0, rely=1)
            self.calendar_frame.lift()

        self._is_calendar_visible = True

    def hide_calendar(self):
        if self._is_calendar_visible:
            self.calendar_frame.place_forget()
        
        self._is_calendar_visible = False

    def erase(self):
        self.hide_calendar()
        self.date_var.set("")
    
    @property
    def is_calendar_visible(self):
        return self._is_calendar_visible

    def _on_entry_focus_out(self):
        if not str(self.focus_get()).startswith(str(self.calendar_frame)):
            self.hide_calendar()
        
    def _on_calendar_focus_out(self):
        if self.focus_get() != self:
            self.hide_calendar()

    def _on_selected_date(self, date):
        self.date_var.set(date.strftime(self.date_format))
        self.hide_calendar()
        
        if self._on_select_date_command is not None:
            self._on_select_date_command(date)

    def _on_click(self, event):
        str_widget = str(event.widget)

        if str_widget == str(self):
            if not self._is_calendar_visible:
                self.show_date_on_calendar()
        else:
            if not str_widget.startswith(str(self.calendar_frame)) and self._is_calendar_visible:
                self.hide_calendar()
    
class GUI():
    def __init__(self):
        self.root = Tk()
        self.root.report_callback_exception = self.handle_exception
        self.root.title('Sales reporting')
        self.root.geometry('1300x600')
        self.root.resizable(False, False)
        
        self.frame_main = ttk.Frame(self.root)
        self.frame_main.pack(fill = BOTH, expand = 1)
    
    def handle_exception(self, *args):
        err = traceback.format_exception(*args)
        messagebox.showerror('An exception occurred!', err)
    
    def run(self):
        self.initial_screen()
        print('GUI: Updating..')
        self.root.update()
        print('GUI: Ready. Entering main loop')
        self.root.mainloop()
    
    def sales_data_callback(self, message):
        try:
            self.load_message.configure(text = 'Sales data: ' + message + '...')
            self.root.update()
        except:
            pass
    
    def check_initial_screen(self):
        username = self.login_user_value.get()
        password = self.login_pass_value.get()
        self.start_date = self.daterange_start.get()
        self.end_date = self.daterange_end.get()        
        
        if username == '' or password == '' or self.start_date == '' or self.end_date == '':
            messagebox.showerror('Missing information', 'Please complete all fields')
            return      
        
        if self.start_date > self.end_date:
            messagebox.showerror('Invalid date range', 'The start date must occur before the end date')
            return
            
        try:
            datetime.datetime.strptime(self.start_date, '%Y-%m-%d')
            datetime.datetime.strptime(self.end_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror('Invalid dates', 'The start and end dates must be in the format YYYY-MM-DD (e.g. 2018-02-05 for February 5th, 2018)')
            return

        self.button_initial.configure(state = 'disabled', text = 'Logging in..')
        self.root.update()            
        
        self.auth_token, self.auth_cookies = login(username, password)
        if self.auth_token == None:
            messagebox.showerror('Login failed', 'Could not log in to Nayax. Are you sure your login is correct?')
            self.button_initial.configure(state = 'normal', text = 'Start')
            self.root.update()
            return
        
        self.frame_initial.destroy()
        
        #style_big = ttk.Style()
        #style_big.configure('biginfo', font=('Helvetica', 20))
        self.load_message = ttk.Label(self.frame_main, text = 'Please wait: Getting machine list...')
        self.load_message.grid(row = 0, column = 0)
        self.root.update()
        
        self.db_connection, self.db_cursor = init_db() 
        self.tree, self.root_node = get_machine_list(self.db_cursor, self.db_connection, self.auth_token, self.auth_cookies)
        
        self.load_message.configure(text = 'Please wait: Getting sales data...')
        self.root.update()
        self.tree = get_sales_data(self.tree, self.root_node, self.db_cursor, self.auth_token, self.auth_cookies, self.start_date, self.end_date, update_callback = self.sales_data_callback)
        
        self.load_message.grid_forget()
        self.make_tree()
        self.make_control()
        self.root.update()
    
    def initial_screen(self):
        self.frame_initial = ttk.Frame(self.frame_main)      
        
        self.login_user_value = StringVar()
        ttk.Label(self.frame_initial, text = 'Nayax username').grid(row = 0, column = 0)        
        self.login_user = ttk.Entry(self.frame_initial, textvariable = self.login_user_value, width = 20)
        self.login_user.grid(row = 0, column = 1)
        
        self.login_pass_value = StringVar()
        ttk.Label(self.frame_initial, text = 'Nayax password').grid(row = 1, column = 0)        
        self.login_pass = ttk.Entry(self.frame_initial, textvariable = self.login_pass_value, width = 20, show = '*')
        self.login_pass.grid(row = 1, column = 1)
               
        ttk.Label(self.frame_initial, text = 'Report start date (YYYY-MM-DD)').grid(row = 2, column = 0)        
        self.daterange_start = Datepicker(self.frame_initial)
        self.daterange_start.grid(row = 2, column = 1)
        
        ttk.Label(self.frame_initial, text = 'Report end date (YYYY-MM-DD)').grid(row = 3, column = 0)        
        self.daterange_end = Datepicker(self.frame_initial)
        self.daterange_end.grid(row = 3, column = 1)
        
        self.button_initial = ttk.Button(self.frame_initial, text = 'Start', command = self.check_initial_screen)
        self.button_initial.grid(row = 4, column = 0, columnspan = 2, sticky = 'ew')
        
        self.frame_initial.grid(row = 0, column = 0, sticky = 'news')        
    
    def fee_container(self, parent):
        self.fees_row_index = 0
        self.frame_fees = ttk.Frame(parent)
        self.fees = []
        
        
        ## new fee widgets
        self.frame_fees_new = ttk.Labelframe(self.frame_fees, text = 'New fee')
        
        self.fee_name_value = StringVar()
        self.fee_amount_value = DoubleVar()
        self.fee_type_value = StringVar()        
        
        ttk.Label(self.frame_fees_new, text = 'Fee name').grid(row = 0, column = 0)
        ttk.Label(self.frame_fees_new, text = 'Amount').grid(row = 0, column = 1)
        ttk.Label(self.frame_fees_new, text = 'Rate').grid(row = 0, column = 2)
        
        self.fee_name = ttk.Entry(self.frame_fees_new, textvariable = self.fee_name_value, width = 25)
        self.fee_amount = ttk.Spinbox(self.frame_fees_new, format = '%.2f', increment = 0.01, textvariable = self.fee_amount_value)
        self.fee_type = ttk.Combobox(self.frame_fees_new, values = ['% of total income (before other fees)', '% of total revenue (after other fees)', 'dollars per transaction', '% of CC sales income', 'dollars per CC sale', '% of cash sales income', 'dollars per cash sale', 'dollars per active DTU'], textvariable = self.fee_type_value, width = 30)        
        
        self.fee_name.grid(row = 1, column = 0)
        self.fee_amount.grid(row = 1, column = 1)
        self.fee_type.grid(row = 1, column = 2)
        ttk.Button(self.frame_fees_new, text = 'Add fee', command = self.add_fee).grid(row = 1, column = 4)
        
        self.frame_fees_new.grid(row = 0, column = 0, rowspan = 2, sticky = 'ew')
        
        ## current fee container
        self.frame_fees_current = ttk.LabelFrame(self.frame_fees, text = 'Current fees')
        self.frame_fees_current.grid(row = 2, column = 0, sticky = 'ew')        
        
        return self.frame_fees
        
    def add_fee(self, fee_name = None, fee_amount = None, fee_type = None):
        if fee_name == None:
            fee_name = str(self.fee_name_value.get())
            fee_amount = float(self.fee_amount_value.get())
            fee_type = self.fee_type_value.get()
            
        fee_calc_value = DoubleVar()
       
        fee_print = fee_name + ': ' + ('%.2f' % fee_amount) + ' ' + fee_type
        
        widget_text = ttk.Label(self.frame_fees_current, text = fee_print)
        widget_calc = ttk.Entry(self.frame_fees_current, textvariable = fee_calc_value, state = 'readonly')        
        widget_button = ttk.Button(self.frame_fees_current, text = 'Remove', command = lambda: self.remove_fee(widget_text))
        
        widget_text.grid(row = self.fees_row_index, column = 1)
        widget_button.grid(row = self.fees_row_index, column = 0)
        widget_calc.grid(row = self.fees_row_index, column = 2)
        
        self.fees_row_index += 1
        
        self.fees.append([widget_text, widget_button, widget_calc, fee_name, fee_amount, fee_type, fee_calc_value])
        
    def remove_fee(self, widget_text):
        remove_entry = None
        for entry in self.fees:
            if entry[0] == widget_text:
                remove_entry = entry
                break
                
        if remove_entry == None:
            return
                
        remove_entry[0].grid_forget()
        remove_entry[1].grid_forget()
        remove_entry[2].grid_forget()
        
        self.fees.remove(entry)
        self.root.update()
        
        self.calculate_fees()
    
    def make_control(self):
        print('GUI: Drawing control..')
        
        ## info area
        self.frame_info = ttk.LabelFrame(self.frame_main, text = 'Information')
        self.frame_info_name = ttk.Label(self.frame_info, text = 'Select an operator or machine')
        self.frame_info_name.grid(row = 0, column = 0)
        self.frame_info_progress = ttk.Progressbar(self.frame_info, orient = 'horizontal', length = 250, mode = 'determinate', value = 0, maximum = 1)
        self.frame_info_progress.grid(row = 0, column = 1, sticky = 'e')
        self.frame_info.grid(row = 2, column = 0, columnspan = 2, sticky = 'ew')
        
        ## fees set area
        self.frame_control = ttk.LabelFrame(self.frame_main, text = 'Fees')
        self.frame_control.grid(row = 3, column = 0, sticky = 'nsw')
        
        self.fee_container(self.frame_control).grid(row = 0, column = 0, rowspan = 10)        
        
        self.fee_button_setone = ttk.Button(self.frame_control, text = 'Set fees for this machine', command = self.set_fee_one)
        self.fee_button_setall = ttk.Button(self.frame_control, text = 'Set fees for all machines under this operator', command = self.set_fee_all)
        self.fee_button_active = ttk.Button(self.frame_control, text = 'Toggle active/inactive state', command = self.force_machine_state)
        self.fee_button_products = ttk.Button(self.frame_control, text = 'Toggle product report for operator', command = self.toggle_product_report)
        self.fee_button_products_child = ttk.Button(self.frame_control, text = 'Toggle product report for all machines under operator', command = self.toggle_product_report_child)
        self.op_create_customer = ttk.Button(self.frame_control, text = 'Create new operator under this one', command = lambda: self.create_new_operator(type = [14, 'Customer (General)']))
        self.op_create_location = ttk.Button(self.frame_control, text = 'Create new location under this one', command = lambda: self.create_new_operator(type = [13, 'Location (General)']))
        
        self.fee_button_setone.grid(row = 0, column = 1, sticky = 'new')
        self.fee_button_setall.grid(row = 1, column = 1, sticky = 'new')
        self.fee_button_active.grid(row = 2, column = 1, sticky = 'new')
        self.fee_button_products.grid(row = 3, column = 1, sticky = 'new')
        self.fee_button_products_child.grid(row = 4, column = 1, sticky = 'new')
        self.op_create_customer.grid(row = 5, column = 1, sticky = 'new')
        self.op_create_location.grid(row = 6, column = 1, sticky = 'new')
        
        ## fees display area
        self.frame_calculate = ttk.LabelFrame(self.frame_main, text = 'Calculated fees (click to copy)')
        self.frame_calculate.grid(row = 3, column = 1, sticky = 'nsw')
        
        self.calc_total_sales = DoubleVar()
        self.calc_cash_sales = DoubleVar()
        self.calc_cash_count = IntVar()
        self.calc_card_sales = DoubleVar()
        self.calc_card_count = IntVar()
        self.calc_active_dtus = IntVar()
        self.calc_fees = DoubleVar()
        self.calc_refund = DoubleVar()
        self.calc_fees.set(0)
        
        ttk.Label(self.frame_calculate, text = 'Total sales').grid(row = 0, column = 0)
        ttk.Label(self.frame_calculate, text = 'Cash sales').grid(row = 1, column = 0)
        ttk.Label(self.frame_calculate, text = 'Cash transactions').grid(row = 2, column = 0)
        ttk.Label(self.frame_calculate, text = 'Card sales').grid(row = 3, column = 0)
        ttk.Label(self.frame_calculate, text = 'Card transactions').grid(row = 4, column = 0)        
        ttk.Label(self.frame_calculate, text = 'Active DTUs').grid(row = 5, column = 0)
        ttk.Label(self.frame_calculate, text = '  ').grid(row = 6, column = 0)
        ttk.Label(self.frame_calculate, text = 'Fees and commissions').grid(row = 7, column = 0)
        ttk.Label(self.frame_calculate, text = '  ').grid(row = 8, column = 0)
        ttk.Label(self.frame_calculate, text = 'Refund').grid(row = 9, column = 0)
        
        ## make the widgets
        widget_total_sales = ttk.Entry(self.frame_calculate, textvariable = self.calc_total_sales, state = 'readonly')
        widget_cash_sales = ttk.Entry(self.frame_calculate, textvariable = self.calc_cash_sales, state = 'readonly')
        widget_cash_count = ttk.Entry(self.frame_calculate, textvariable = self.calc_cash_count, state = 'readonly')
        widget_card_sales = ttk.Entry(self.frame_calculate, textvariable = self.calc_card_sales, state = 'readonly')
        widget_card_count = ttk.Entry(self.frame_calculate, textvariable = self.calc_card_count, state = 'readonly')
        widget_active_dtus = ttk.Entry(self.frame_calculate, textvariable = self.calc_active_dtus, state = 'readonly')
        widget_fees = ttk.Entry(self.frame_calculate, textvariable = self.calc_fees, state = 'readonly')
        widget_refund = ttk.Entry(self.frame_calculate, textvariable = self.calc_refund, state = 'readonly')
        
        ## do the layout
        widget_total_sales.grid(row = 0, column = 1)
        widget_cash_sales.grid(row = 1, column = 1)
        widget_cash_count.grid(row = 2, column = 1)
        widget_card_sales.grid(row = 3, column = 1)
        widget_card_count.grid(row = 4, column = 1)
        widget_active_dtus.grid(row = 5, column = 1)
        widget_fees.grid(row = 7, column = 1)
        widget_refund.grid(row = 9, column = 1)
        
        ## make them copy to clipboard when clicked
        widget_total_sales.bind("<ButtonRelease-1>", lambda x: self.clipboard_copy(self.calc_total_sales))
        widget_cash_sales.bind("<ButtonRelease-1>", lambda x: self.clipboard_copy(self.calc_cash_sales))
        widget_cash_count.bind("<ButtonRelease-1>", lambda x: self.clipboard_copy(self.calc_cash_count))
        widget_card_sales.bind("<ButtonRelease-1>", lambda x: self.clipboard_copy(self.calc_card_sales))
        widget_card_count.bind("<ButtonRelease-1>", lambda x: self.clipboard_copy(self.calc_card_count))
        widget_active_dtus.bind("<ButtonRelease-1>", lambda x: self.clipboard_copy(self.calc_active_dtus))
        widget_fees.bind("<ButtonRelease-1>", lambda x: self.clipboard_copy(self.calc_fees))
        widget_refund.bind("<ButtonRelease-1>", lambda x: self.clipboard_copy(self.calc_refund))        

        ## report actions
        self.frame_report = ttk.LabelFrame(self.frame_main, text = 'Actions')
        self.frame_report.grid(row = 3, column = 2, sticky = 'nesw')
        
        ttk.Button(self.frame_report, text = 'Save report as HTML', command = self.make_report).grid(row = 0, column = 0, sticky = 'ew')
        ttk.Button(self.frame_report, text = 'Save fee structure', command = self.save_fees).grid(row = 1, column = 0, sticky = 'ew')
        ttk.Button(self.frame_report, text = 'Load fee structure', command = self.load_fees).grid(row = 2, column = 0, sticky = 'ew')
        
        try:
            selected = int(self.view_tree.selection()[0])
        except IndexError:
            self.clear_info_view()
            return
        
        ## disable tree clicks while loading
        self.view_tree.configure(selectmode = 'none')
        self.clear_info_view()
        self.root.update()
        
        type = str(self.tree[selected].record_type).title()
        name = re.sub(r'\-(\d+)$', '', self.tree[selected].record_name)
        
        ## disable the set one button for operators
        #print('UI_TREE_INITIAL: ' + type + ' record - ' + name)
        if type == 'Operator':
            self.fee_button_setone.configure(state = 'disabled')
            self.fee_button_active.configure(state = 'disabled')
        else:
            self.fee_button_setone.configure(state = 'normal')
            self.fee_button_active.configure(state = 'normal')

        self.calculate_fees()
        self.frame_info_name.configure(text = type + ': ' + name)
            
        ## re-enable tree clicks
        self.view_tree.configure(selectmode = 'browse')
        self.root.update()   
    
    def clipboard_copy(self, widget):
        self.root.clipboard_clear()
        try:
            print('Copying to clipboard: ' + str(widget.get()))
            self.root.clipboard_append(str(widget.get()))
        except:
            print('Could not copy widget value to clipboard!')
       
        self.root.update()
    
    def calculate_fees(self):
        try:
            selected = int(self.view_tree.selection()[0])
        except IndexError:
            self.clear_info_view()
            return        
        
        #print('DEBUG: Updating fees for ' + str(self.tree[selected].record_type) + ' ' + str(self.tree[selected].record_name))
    
        ## work out sales figures for machine or operator
        sales_cash_amount = 0
        sales_card_amount = 0
        sales_cash_count = 0
        sales_card_count = 0
        total_fees = 0  
        child_count = 0
        child_fees = dict()
        calc_vars = []
        
        if self.tree[selected].record_type == 'machine':
            self.check_machine_active()
            self.refresh_fee_database()
        
            if self.tree[selected].active == True:
                sales_cash_amount = self.tree[selected].sales_cash_amount
                sales_cash_count = self.tree[selected].sales_cash_count
                sales_card_amount = self.tree[selected].sales_card_amount
                sales_card_count = self.tree[selected].sales_card_count
                child_count = 1
                
                last_fee = None
                
                ## work out fees                    
                for fee_entry in self.tree[selected].fees:
                    calc_var = fee_entry[6]
                    fee_name = fee_entry[3]
                    fee_amount = float(fee_entry[4])
                    fee_type = fee_entry[5]
                    
                    ## for fees against revenue, skip and calculate at the end
                    if fee_type == '% of total revenue (after other fees)':
                        if last_fee != None:
                            messagebox.showwarning('Multiple fees against revenue', 'There are multiple fees applied to revenue. Only the first fee will be used. Others will be ignored.')
                        else:
                            last_fee = fee_entry
                            continue
                    
                    ## for all other fees..
                    fee_calc = 0
                    if fee_type == '% of total income (before other fees)':
                        fee_calc = (sales_cash_amount + sales_card_amount) * (fee_amount / 100.0)
                    elif fee_type == 'dollars per transaction':
                        fee_calc = (sales_cash_count + sales_card_count) * fee_amount
                    elif fee_type == '% of CC sales income':
                        fee_calc = sales_card_amount * (fee_amount / 100.0)
                    elif fee_type == 'dollars per CC sale':
                        fee_calc = sales_card_count * fee_amount
                    elif fee_type == '% of cash sales income':
                        fee_calc = sales_cash_amount * (fee_amount / 100.0)
                    elif fee_type == 'dollars per cash sale':
                        fee_calc = sales_cash_count * fee_amount
                    elif fee_type == 'dollars per active DTU':
                        fee_calc = fee_amount
                    
                    self.db_cursor.execute('UPDATE fees SET value=? WHERE id=? AND name=? AND amount=? AND type=?', [fee_calc, self.tree[selected].name, fee_name, fee_amount, fee_type])
                    calc_var.set(fee_calc)
                    calc_vars.append(calc_var)
                    #print('DEBUG: Added machine fee \'' + fee_name + '\': $' + str(fee_calc))
        
                    total_fees += fee_calc
                    
                ## fees against revenue
                if last_fee != None:
                    calc_var = last_fee[6]
                    fee_name = last_fee[3]
                    fee_amount = float(last_fee[4])
                    fee_type = last_fee[5]
                
                    fee_calc = 0
                    if fee_type == '% of total revenue (after other fees)':                        
                        fee_calc = ((sales_cash_amount + sales_card_amount) - total_fees) * (fee_amount / 100.0)
                    
                    self.db_cursor.execute('UPDATE fees SET value=? WHERE id=? AND name=? AND amount=? AND type=?', [fee_calc, self.tree[selected].name, fee_name, fee_amount, fee_type])
                    calc_var.set(fee_calc)
                    calc_vars.append(calc_var)
                    #print('DEBUG: Added revenue machine fee \'' + fee_name + '\': $' + str(fee_calc))
                    total_fees += fee_calc           

        elif self.tree[selected].record_type == 'operator':        
            
            self.refresh_fee_database() 
            zeroed = False
            for lower in self.tree[selected].descendants:
                self.refresh_fee_database(lower.name)            
                if lower.active == True:
                    ## work out the sales for each machine beneath
                    sales_cash_amount += lower.sales_cash_amount
                    sales_card_amount += lower.sales_card_amount
                    sales_cash_count += lower.sales_cash_count
                    sales_card_count += lower.sales_card_count
                    total_fees_child = 0
                    child_count += 1  
                    
                    last_fee = None
                    
                    ## work out fees per descendant
                    for fee_entry in lower.fees:
                        calc_var = fee_entry[6]
                        fee_name = fee_entry[3]
                        fee_amount = float(fee_entry[4])
                        fee_type = fee_entry[5]
                        
                        ## for fees against revenue, skip and calculate at the end
                        if fee_type == '% of total revenue (after other fees)':
                            if last_fee != None:
                                messagebox.showwarning('Multiple fees against revenue', 'There are multiple fees applied to revenue. Only the first fee will be used. Others will be ignored.')
                            else:
                                last_fee = fee_entry
                                continue
                        
                        ## for all other fees..
                        fee_calc = 0
                        if fee_type == '% of total income (before other fees)':
                            fee_calc = (lower.sales_cash_amount + lower.sales_card_amount) * (fee_amount / 100.0)
                        elif fee_type == 'dollars per transaction':
                            fee_calc = (lower.sales_cash_count + lower.sales_card_count) * fee_amount
                        elif fee_type == '% of CC sales income':
                            fee_calc = lower.sales_card_amount * (fee_amount / 100.0)
                        elif fee_type == 'dollars per CC sale':
                            fee_calc = lower.sales_card_count * fee_amount
                        elif fee_type == '% of cash sales income':
                            fee_calc = lower.sales_cash_amount * (fee_amount / 100.0)
                        elif fee_type == 'dollars per cash sale':
                            fee_calc = lower.sales_cash_count * fee_amount
                        elif fee_type == 'dollars per active DTU':
                            fee_calc = fee_amount
                        
                        if zeroed == False:
                            calc_var.set(fee_calc)
                            calc_vars.append(calc_var)
                            zeroed = True
                        else:
                            calc_var.set(float(calc_var.get()) + fee_calc) 
                        #print('DEBUG: Added operator fee for machine ' + str(lower.record_name) + ' \'' + fee_name + '\': $' + str(fee_calc))
            
                        self.db_cursor.execute('UPDATE fees SET value=? WHERE id=? AND name=? AND amount=? AND type=?', [fee_calc, lower.name, fee_name, fee_amount, fee_type])
                        total_fees += fee_calc
                        total_fees_child += fee_calc
                        
                    ## fees against revenue
                    if last_fee != None:
                        calc_var = last_fee[6]
                        fee_name = last_fee[3]
                        fee_amount = float(last_fee[4])
                        fee_type = last_fee[5]
                        
                        fee_calc = 0
                        if fee_type == '% of total revenue (after other fees)':
                            fee_calc = ((lower.sales_cash_amount + lower.sales_card_amount) - total_fees_child) * (fee_amount / 100.0)

                        self.db_cursor.execute('UPDATE fees SET value=? WHERE id=? AND name=? AND amount=? AND type=?', [fee_calc, lower.name, fee_name, fee_amount, fee_type])
                        
                        if zeroed == False:
                            calc_var.set(fee_calc)
                            calc_vars.append(calc_var)
                            zeroed = True
                        else:
                            calc_var.set(float(calc_var.get()) + fee_calc) 
                        
                        #print('DEBUG: Added revenue operator fee for machine ' + str(lower.record_name) + ' \'' + fee_name + '\': $' + str(fee_calc))
                        total_fees += fee_calc
                            
                else:
                    for fee_entry in lower.fees:                        
                        fee_entry[6].set(0)
        
        ## commit fee changes to databse
        self.db_connection.commit()
        
        ## round counts
        for entry in calc_vars:
            entry.set('%.2f' % float(entry.get()))
        
        ## set totals
        #print('DEBUG: Total fees: $' + str(total_fees))
        self.calc_fees.set('%.2f' % total_fees)
        self.calc_refund.set('%.2f' % (sales_card_amount - total_fees))        
        
        ## sales figures
        self.calc_total_sales.set('%.2f' % (sales_cash_amount + sales_card_amount))
        self.calc_cash_sales.set('%.2f' % sales_cash_amount)
        self.calc_cash_count.set(sales_cash_count) 
        self.calc_card_sales.set('%.2f' % sales_card_amount)
        self.calc_card_count.set(sales_card_count)         
        self.calc_active_dtus.set(str(child_count))
        
        self.root.update()
    
    def save_fees(self):
        filename = filedialog.asksaveasfilename(title = "Save fees",filetypes = (("Fee file", "*.srfee"),("All files","*.*")))
        if filename == None or filename == '':
            return
        
        savefees = []
        for entry in self.fees:
            savefees.append([entry[3], entry[4], entry[5]])
        
        regexp_extension = re.search('\.srfee', filename)
        if not regexp_extension:
            filename = filename + '.srfee'
        
        try:
            fsock = open(filename, 'wb')
        except:
            messagebox.showerror('Save error', 'Could not open file for writing')
        
        try:
            pickle.dump(savefees, fsock)
            fsock.flush()
            fsock.close()
        except:
            messagebox.showerror('Save error', 'An error occurred while saving the fees')
        else:
            messagebox.showinfo('Fees saved', 'Fees saved to file successfully')
            
    def load_fees(self):
        filename =  filedialog.askopenfilename(title = "Select fees file to open",filetypes = (("Fee file","*.srfee"),("All files","*.*")))
        
        if filename == None or filename == '':
            return
            
        try:
            fsock = open(filename, 'rb')
        except:
            messagebox.showerror('Load error', 'Could not open file for reading')
        
        try:
            loadfees = pickle.load(fsock)
            fsock.close()
            ## clear out the old fees
            for entry in self.fees:
                self.remove_fee(entry[0])
            
            ## load in the new ones
            for entry in loadfees:
                self.add_fee(entry[0], entry[1], entry[2])
        except:
            messagebox.showerror('Load error', 'An error occurred while loading the fees')
        else:
            messagebox.showinfo('Fees loaded', 'Fees loaded from file successfully')
           
    def tree_click(self, event = None):
        #print('UI_TREE_CLICK event [' + str(event) + '] selection [' + str(self.view_tree.selection()) + ']')
        try:
            selected = int(self.view_tree.selection()[0])
        except IndexError:
            self.clear_info_view()
            return
        
        ## disable tree clicks while loading
        self.view_tree.configure(selectmode = 'none')
        self.clear_info_view()
        self.root.update()
        
        type = str(self.tree[selected].record_type).title()
        name = re.sub(r'\-(\d+)$', '', self.tree[selected].record_name)
        
        ## disable the set one button for operators
        if type == 'Operator':
            self.fee_button_setone.configure(state = 'disabled')
            self.fee_button_active.configure(state = 'disabled')
        else:
            self.fee_button_setone.configure(state = 'normal')
            self.fee_button_active.configure(state = 'normal')            
        
        if self.tree[selected].active == False:
            name += ' (INACTIVE)'
        
        self.frame_info_name.configure(text = type + ': ' + name)        
        self.calculate_fees()

        ## re-enable tree clicks
        self.view_tree.configure(selectmode = 'browse')
        self.root.update()
        
    def clear_info_view(self):
        self.frame_info_name.configure(text = 'Select an operator or machine')
        self.calc_total_sales.set('N/A')
        self.calc_cash_sales.set('N/A')
        self.calc_card_sales.set('N/A')
        self.calc_card_count.set('N/A')
        self.calc_active_dtus.set('N/A')
        self.calc_fees.set('N/A')
        self.calc_refund.set('N/A')
        
        self.root.update()
    
    def force_machine_state(self, id = None):
        if id == None:
            try:
                selected = int(self.view_tree.selection()[0])
            except IndexError:
                return
        else:
            selected = id
            
        self.tree[selected].active = not self.tree[selected].active
        self.view_tree.set(self.tree[selected].name, 'active', str(self.tree[selected].active))
        
        if self.tree[selected].active == True:
            self.calculate_fees()

    def toggle_product_report(self, id = None):
        if id == None:
            try:
                selected = int(self.view_tree.selection()[0])
            except IndexError:
                return
        else:
            if isinstance(id, list):
                selected = id
            else:
                selected = [id]
            
        
            
        self.fee_button_products.configure(state = 'disabled')
        self.fee_button_products_child.configure(state = 'disabled')
        
        do_report = False
        for id in selected:
            self.tree[id].get_product_sales = not self.tree[id].get_product_sales
            self.view_tree.set(self.tree[id].name, 'prodreport', str(self.tree[id].get_product_sales))
            if self.tree[id].get_product_sales == True:
                do_report = True
        
        previous_text = self.frame_info_name.cget("text")
        if do_report == True:
            self.populate_product_sales(selected)
            self.frame_info_name.configure(text = previous_text)
            self.root.update()
            
        self.fee_button_products.configure(state = 'normal')
        self.fee_button_products_child.configure(state = 'normal')
        
        
    def toggle_product_report_child(self, id = None):
        if id == None:
            try:
                selected = int(self.view_tree.selection()[0])
            except IndexError:
                return
        else:
            selected = id
        
        if self.tree[selected].record_type == 'machine':
            targets = self.tree[selected].parent.descendants
        else:
            targets = self.tree[selected].descendants

        child_count = 0
        self.frame_info_name.configure(text = 'Please wait. Getting product sales data...')
        self.frame_info_progress.configure(maximum = len(targets), value = 0)
        ## don't forget to do the root node
        self.toggle_product_report(id = selected)        
        for child in targets:
            self.frame_info_progress.configure(maximum = len(targets), value = (self.frame_info_progress['value'] + 1))
            self.root.update()           
            self.toggle_product_report(id = child.name)
            child_count += 1            
        
        self.tree_click()
        self.frame_info_progress.configure(maximum = 1, value = 0)
        self.root.update()
        messagebox.showinfo('Product sales data', 'Got product sales data for ' + str(len(targets)) + ' machine(s)/operators under ' + str(self.tree[selected].record_name))
    
    def set_fee_one(self, id = None, mass_call = False):
        if id == None:
            try:
                selected = int(self.view_tree.selection()[0])
            except IndexError:
                return
        else:
            selected = id
         
        # if self.tree[selected].record_type == 'operator':
            # return
        
        self.fee_button_setone.configure(state = 'disabled')
        self.fee_button_setall.configure(state = 'disabled')
        self.root.update()
        
        self.check_machine_active(selected)
        
        self.tree[selected].fees = self.fees
        self.refresh_fee_database(selected)
        #print('DEBUG: Set fees for ' + str(id) + ' to ' + str(self.tree[selected].fees))
        
        self.fee_button_setone.configure(state = 'normal')
        self.fee_button_setall.configure(state = 'normal')
        self.root.update()
        
        if mass_call == False:
            self.tree_click()
            
    def refresh_fee_database(self, id = None):
        if id == None:
            try:
                selected = int(self.view_tree.selection()[0])
            except IndexError:
                return
        else:
            selected = id

        self.db_cursor.execute('DELETE FROM fees WHERE id=?', [selected])
        
        for widget_text, widget_button, widget_calc, fee_name, fee_amount, fee_type, fee_calc_value in self.tree[selected].fees:
            self.db_cursor.execute('INSERT INTO fees (id, name, amount, type) VALUES (?, ?, ?, ?)', [selected, fee_name, fee_amount, fee_type])
        
        self.db_connection.commit()
    
    def check_machine_active(self, id = None):
        if id == None:
            try:
                selected = int(self.view_tree.selection()[0])
            except IndexError:
                return
        else:
            selected = id
            
        if self.tree[selected].active == None and self.tree[selected].record_type == 'machine':
            self.frame_info_name.configure(text = 'Please wait. Checking for active machines (' + str(self.tree[selected].record_name) + ')')
            self.root.update()
            id, payable = get_active(self.tree, self.auth_token, self.auth_cookies, self.tree[selected].name, self.start_date, self.end_date)
            self.tree[selected].active = payable
            self.view_tree.set(selected, 'active', str(payable))
    
    def set_fee_all(self):
        try:
            selected = int(self.view_tree.selection()[0])
        except IndexError:
            return
        
        if self.tree[selected].record_type == 'machine':
            targets = self.tree[selected].parent.descendants
        else:
            targets = self.tree[selected].descendants

        child_count = 0        
        for child in targets:
            self.frame_info_progress.configure(maximum = len(targets), value = (self.frame_info_progress['value'] + 1))
            if child.record_type == 'machine':
                
                self.set_fee_one(id = child.name, mass_call = True)
                child_count += 1            
        
        self.tree_click()
        self.frame_info_progress.configure(maximum = 1, value = 0)
        messagebox.showinfo('Fees set', 'Set fees for ' + str(child_count) + ' machine(s) under ' + str(self.tree[selected].record_name))
    
    def make_tree(self):
        print('GUI: Drawing tree..')
        self.container_tree = ttk.Frame(self.frame_main)        
        
        self.view_tree = ttk.Treeview(self.container_tree, selectmode = 'browse', columns=('serial', 'active', 'prodreport', 'cash', 'card'))
        self.view_tree.bind('<ButtonRelease-1>', self.tree_click)
        
        self.view_tree.heading('#0', text = 'Name')        
        self.view_tree.heading('serial', text = 'DTU serial')
        self.view_tree.heading('active', text = 'Active?')
        self.view_tree.heading('prodreport', text = 'Report product sales?')
        self.view_tree.heading('cash', text = 'Cash sales')
        self.view_tree.heading('card', text = 'Card sales')
      
        
        self.view_tree.column('#0', width = 500)
        self.view_tree.column('serial', width = 150)
        self.view_tree.column('active', width = 75)
        self.view_tree.column('prodreport', width = 120)
        self.view_tree.column('cash', width = 100)
        self.view_tree.column('card', width = 100)
        
        self.tree[self.root_node.name].gui_entry = self.view_tree.insert('', 'end', self.root_node.name, text = self.root_node.record_name)
        self.make_tree_child(self.root_node)
        
        self.view_tree_scroll_vertical = ttk.Scrollbar(self.container_tree, orient = 'vertical', command = self.view_tree.yview)
        self.view_tree_scroll_horizontal = ttk.Scrollbar(self.container_tree, orient = 'horizontal', command = self.view_tree.xview)
        self.view_tree.configure(yscrollcommand = self.view_tree_scroll_vertical.set, xscrollcommand = self.view_tree_scroll_horizontal.set)
        
        self.view_tree.grid(row = 0, column = 0, sticky = 'news')
        self.view_tree_scroll_vertical.grid(row = 0, column = 1, sticky = 'ns')
        self.view_tree_scroll_horizontal.grid(row = 1, column = 0, sticky = 'ew')        
        
        self.container_tree.grid(row=1, column=0, columnspan = 10, sticky = 'news')
        print('GUI: Tree drawn')
        
    def make_tree_child(self, root_node):    
        for child in root_node.children:
            if child.record_type == 'machine':
                regexp_serial = re.search(r'^(.+)\-(\d+)$', str(child.record_name))
                if regexp_serial:
                    name = str(regexp_serial.group(1))
                    serial = str(regexp_serial.group(2))
                else:
                    name = child.name
                    serial = 'N/A'
                    
                if child.sales_cash_amount == None:
                    child.sales_cash_amount = 0
                if child.sales_cash_count == None:
                    child.sales_cash_count = 0
                if child.sales_card_amount == None:
                    child.sales_card_amount = 0
                if child.sales_card_count == None:
                    child.sales_card_count = 0
                    
                try:
                    self.tree[child.name].gui_entry = self.view_tree.insert(root_node.name, 'end', child.name, text = name)
                    self.view_tree.set(child.name, 'serial', serial)
                    self.view_tree.set(child.name, 'cash', '$' + str('%.2f' % child.sales_cash_amount) + ' (' + str(child.sales_cash_count) + ')')
                    self.view_tree.set(child.name, 'card', '$' + str('%.2f' % child.sales_card_amount) + ' (' + str(child.sales_card_count) + ')')
                    if child.active == None:
                        self.view_tree.set(child.name, 'active', 'Unknown')
                    else:
                        self.view_tree.set(child.name, 'active', str(child.active))
                        
                    self.view_tree.set(child.name, 'prodreport', str(child.get_product_sales))
                except:
                    pass

            elif child.record_type == 'operator':
                sales_cash_amount = 0
                sales_cash_count = 0
                sales_card_amount = 0
                sales_card_count = 0
                for lower in child.descendants:
                    try:
                        sales_cash_amount += lower.sales_cash_amount
                        sales_cash_count += lower.sales_cash_count
                        sales_card_amount += lower.sales_card_amount
                        sales_card_count += lower.sales_card_count
                    except TypeError:
                        #print('No sales data for ' + child.record_name)
                        continue
                try:
                    self.view_tree[child.name].gui_entry = self.view_tree.insert(root_node.name, 'end', child.name, text = str(child.record_name))
                    self.view_tree.set(child.name, 'cash', '$' + str('%.2f' % sales_cash_amount) + ' (' + str(sales_cash_count) + ')')
                    self.view_tree.set(child.name, 'card', '$' + str('%.2f' % sales_card_amount) + ' (' + str(sales_card_count) + ')')
                    self.view_tree.set(child.name, 'prodreport', str(child.get_product_sales))
                except:
                    pass
                    
                self.make_tree_child(child) 
    
    ## get sales by product from nayax
    def get_product_sales(self, actor):
        if actor.record_type == 'machine':
            regexp_serial = re.search(r'^(.+)\-(\d+)$', str(actor.record_name))
            if regexp_serial:
                name = str(regexp_serial.group(1))        
            else:
                name = str(actor.record_name)
        else:
            name = str(actor.record_name)
        
        if actor.record_type == 'machine':
            url_cash = 'public/facade.aspx?responseType=json&model=reports/SalesSummary&action=SalesSummary_Report&&actor_id='+ str(actor.parent.name) +'&payment_method=3&num_of_rows=100000&with_cash=1&with_cashless_external=0&time_period=57&start_date='+ self.start_date + '&end_date=' + self.end_date + '&report_type=7&op_id=' + name
            url_card = 'public/facade.aspx?responseType=json&model=reports/SalesSummary&action=SalesSummary_Report&&actor_id='+ str(actor.parent.name) +'&payment_method=1&num_of_rows=100000&with_cash=0&with_cashless_external=0&time_period=57&start_date='+ self.start_date + '&end_date=' + self.end_date + '&report_type=7&op_id=' + name
        else:
            url_cash = 'public/facade.aspx?responseType=json&model=reports/SalesSummary&action=SalesSummary_Report&&actor_id='+ str(actor.name) +'&payment_method=3&num_of_rows=100000&with_cash=1&with_cashless_external=0&time_period=57&start_date='+ self.start_date + '&end_date=' + self.end_date + '&report_type=7'
            url_card = 'public/facade.aspx?responseType=json&model=reports/SalesSummary&action=SalesSummary_Report&&actor_id='+ str(actor.name) +'&payment_method=1&num_of_rows=100000&with_cash=0&with_cashless_external=0&time_period=57&start_date='+ self.start_date + '&end_date=' + self.end_date + '&report_type=7'
        
        sales_cash = make_request(url_cash, type = 'POST', headers = {'X-Nayax-Validation-Token': self.auth_token, 'Host': 'my.nayax.com', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://my.nayax.com', 'Referer': 'https://my.nayax.com/dcs/public/facade.aspx?model=reports/SalesSummary'}, cookies = self.auth_cookies)    
        sales_card = make_request(url_card, type = 'POST', headers = {'X-Nayax-Validation-Token': self.auth_token, 'Host': 'my.nayax.com', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://my.nayax.com', 'Referer': 'https://my.nayax.com/dcs/public/facade.aspx?model=reports/SalesSummary'}, cookies = self.auth_cookies)
        
        json_cash = json.loads(sales_cash.text)
        json_card = json.loads(sales_card.text)
        
        return actor, json_cash, json_card
    
    ## create a new operator
    def create_new_operator(self, type = [14, 'Customer (general)'], id = None):
        if id == None:
            try:
                selected = int(self.view_tree.selection()[0])
            except IndexError:
                return
        else:
            selected = id
        
        name = simpledialog.askstring('New operator', 'Operator name?', parent = self.root)
        if name == None or name == '':
            print('No name specified for new operator. Aborting')
            return
        else:
            name = re.sub('\n', '', name)
            
        if self.tree[selected].record_type == 'machine':
            print('Cannot create new operator under a machine')
            messagebox.showerror('Cannot create operator', 'Operators cannot be created under machines')
            return
        
        url = 'public/facade.aspx?model=administration/Actors&action=Actors_Update&&is_allowed_transaction_dispatcher=true&is_allowed_transaction=1&is_allowed_billing_report=false'
        
        xml_data = '<?xml version="1.0" encoding="utf-8"?><metadata result="SUCCESS"><root><group group_name="Vending Operator - VMO" group_id="3" checked="1" was_checked="0" node="0" selected="1"/><row action="new" actor_code="' + str(''.join(random.choices(string.digits, k=10))) + '" actor_code_dirty="1" actor_code_original="" parent_actor_name="' + str(self.tree[selected].record_name) + '" parent_actor_name_dirty="1" parent_actor_name_original="" parent_actor_id="' + str(self.tree[selected].name) + '" parent_actor_id_dirty="1" parent_actor_id_original="" actor_type_name="' + type[1] + '" actor_type_name_dirty="1" actor_type_name_original="" actor_type_id="' + str(type[0]) + '" actor_type_id_dirty="1" actor_type_id_original="" actor_description="' + str(name) + '" actor_description_dirty="1" actor_description_original="" status_id="1" status_id_dirty="1" status_id_original="" currency_id="7" currency_id_dirty="1" currency_id_original="" country_id="13" country_id_dirty="1" country_id_original="" time_zone_key="48" time_zone_key_dirty="1" time_zone_key_original="" is_enabled="0" get_night_dex_reads="0" get_night_dex_reads_dirty="1" get_night_dex_reads_original="" log_missing_crc="0" log_missing_crc_dirty="1" log_missing_crc_original="" is_extract_LA="0" is_extract_LA_dirty="1" is_extract_LA_original="" is_check_g85="0" is_check_g85_dirty="1" is_check_g85_original="" is_g85_cancel_parsing="0" is_g85_cancel_parsing_dirty="1" is_g85_cancel_parsing_original="" is_cash_equal_va_minus_da="0" is_cash_equal_va_minus_da_dirty="1" is_cash_equal_va_minus_da_original="" actor_address="" actor_contact="" day_light_savings="0" day_light_savings_dirty="1" day_light_savings_original="" route_manager="" route_manager_mobile="" actor_contract_info="" use_product_group_vat="0" use_product_group_vat_dirty="1" use_product_group_vat_original="" use_phone_transaction="0" use_phone_transaction_dirty="1" use_phone_transaction_original="" use_phone_contactless="0" use_phone_contactless_dirty="1" use_phone_contactless_original="" use_phone_contact="0" use_phone_contact_dirty="1" use_phone_contact_original="" send_constant_preautho="0" send_constant_preautho_dirty="1" send_constant_preautho_original=""/><AutoPpActorParams action="new" card_type_lut_id="33" card_type_lut_id_dirty="1" card_type_lut_id_original="" credit_type_code="0" credit_type_code_dirty="1" credit_type_code_original="" is_accumulated="0" is_accumulated_dirty="1" is_accumulated_original="" is_single_use="0" is_single_use_dirty="1" is_single_use_original="" is_revalue_card="0" is_revalue_card_dirty="1" is_revalue_card_original="" is_revalue_credit_card="0" is_revalue_credit_card_dirty="1" is_revalue_credit_card_original="" is_active="0" is_active_dirty="1" is_active_original="" search_object="" card_holder_name="" card_user_identity_id="" autopp_actor_id=""/></root></metadata>'
        
        
        new_operator = make_request(url, type = 'POST', headers = {'X-Nayax-Validation-Token': self.auth_token, 'Host': 'my.nayax.com', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://my.nayax.com', 'Referer': 'https://my.nayax.com/dcs/public/facade.aspx?model=reports/SalesSummary', 'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}, cookies = self.auth_cookies, data = xml_data)
        
        if re.search(r'result="SUCCESS"', str(new_operator.text)):
            print('Successfully created new operator')
            messagebox.showinfo('Operator created', 'Created new operator under ' + str(self.tree[selected].record_name) + ': ' + name)
        else:
            print('Error creating operator: ' + str(new_operator.text))
            messagebox.showerror('Error creating operator', str(new_operator.text))
    
    ## get sales by product and populate db
    def populate_product_sales(self, id_list):    
        self.frame_info_name.configure(text = 'Please wait. Requesting product sales data...')
        self.root.update()
        
        actors = []
        for id in id_list:
            try:
                actors.append(self.tree[id])
            except:
                print('DEBUG_PPS: Missing actor ' + str(id))
        
        ## weed out the ones we already have data for
        for actor in actors:
            self.db_cursor.execute('SELECT * FROM sales_product WHERE machine_id=?', [actor.name])
            if self.db_cursor.rowcount > 0:
                actors.remove(actor)
                print('Not requesting product sales for ' + name + ' - we already have that data!')
        
        executor = ThreadPoolExecutor(max_workers = 25)
        thread_list = []
        done = 0
        ## submit for execution
        for actor in actors:
            self.frame_info_progress.configure(maximum = (len(actors) * 2), value = actors.index(actor))
            self.frame_info_name.configure(text = 'Please wait. Querying Nayax (' + str(actor.name) + ')...')
            self.root.update()
            thread_list.append(executor.submit(self.get_product_sales, actor))
        
        ## get results
        json_data = []
        for thread_child in thread_list:
            self.frame_info_progress.configure(maximum = (len(thread_list) * 2), value = (len(thread_list) + actors.index(actor)))
            self.frame_info_name.configure(text = 'Please wait. Waiting for Nayax data (' + str(actor.record_name) + ')...')
            self.root.update()
            actor, json_cash, json_card = thread_child.result()
            json_data.append([actor, json_cash, json_card])
            
        ## process json data
        self.frame_info_progress.configure(maximum = (len(thread_list) * 2), value = (len(thread_list) - 1))
        self.frame_info_name.configure(text = 'Please wait. Processing product sales data...')
        self.root.update()
        for actor, json_cash, json_card in json_data:
            if actor.record_type == 'machine':
                regexp_serial = re.search(r'^(.+)\-(\d+)$', str(actor.record_name))
                if regexp_serial:
                    name = str(regexp_serial.group(1))        
                else:
                    name = str(actor.record_name)
            else:
                name = str(actor.record_name)
        
            try:
                for entry in json_cash['data'][1]:
                    try:
                        cash_amount = entry['total_amount']
                    except:
                        cash_amount = 0
                        
                    try:
                        cash_count = entry['total_count']
                    except:
                        cash_count = 0
                        
                    try:
                        product_name = entry['product_name']
                    except:
                        product_name = 'Unknown product'
                    
                    self.db_cursor.execute('UPDATE sales_product SET cash_amount=?, cash_count=? WHERE machine_id=? AND product=?', [cash_amount, cash_count, actor.name, product_name])
                    if self.db_cursor.rowcount == 0:
                        self.db_cursor.execute('INSERT INTO sales_product (machine_id, product, cash_amount, cash_count) VALUES (?,?,?,?)', [actor.name, product_name, cash_amount, cash_count])        
                    
                for entry in json_card['data'][1]:
                    try:
                        card_amount = entry['total_amount']
                    except:
                        card_amount = 0
                        
                    try:
                        card_count = entry['total_count']
                    except:
                        card_count = 0
                        
                    try:
                        product_name = entry['product_name']
                    except:
                        product_name = 'Unknown product'
                    
                    self.db_cursor.execute('UPDATE sales_product SET card_amount=?, card_count=? WHERE machine_id=? AND product=?', [card_amount, card_count, actor.name, product_name])
                    if self.db_cursor.rowcount == 0:
                        self.db_cursor.execute('INSERT INTO sales_product (machine_id, product, card_amount, card_count) VALUES (?,?,?,?)', [actor.name, product_name, card_amount, card_count])
                        
                print('Got product sales data for ' + name)
            except:
                print('Missing or corrupted product sales data for ' + name + '!')
                
        self.frame_info_progress.configure(maximum = 1, value = 0)
        self.root.update()
    
    def check_equal_list(self, iterator):
        ## from https://stackoverflow.com/a/3844832. for checking if all
        ## elements in a list are equal. works for nested lists.
        iterator = iter(iterator)
        try:
            first = next(iterator)
        except StopIteration:
            return True
        return all(first == rest for rest in iterator)        
    
    def make_report_product_table(self, child):
        html = ''
        if child.get_product_sales == True:
            html += '<div class="products"><table>'
            html += '<tr><th>Product name</th><th>Total sales</th><th>Total units</th><th>Cash sales</th><th>Cash units</th><th>Card sales</th><th>Card units</th></tr>'
            
            for row in self.db_cursor.execute('SELECT * FROM sales_product WHERE machine_id=? ORDER BY product ASC', [child.name]):
                product_name = str(row[1])
                
                product_sales_total_amount = row[2] + row[4]
                product_sales_total_count = row[3] + row[5]
                product_sales_cash_amount = row[2]
                product_sales_cash_count = row[3]
                product_sales_card_amount = row[4]
                product_sales_card_count = row[5]

                html += '<tr><td>' + product_name + '</td>'
                html += '<td>$' + str('%.2f' % product_sales_total_amount) + '</td><td>' + str(product_sales_total_count) + '</td>'
                html += '<td>$' + str('%.2f' % product_sales_cash_amount) + '</td><td>' + str(product_sales_cash_count) + '</td>'
                html += '<td>$' + str('%.2f' % product_sales_card_amount) + '</td><td>' + str(product_sales_card_count) + '</td>'
                
            html += '</table></div>'
            
        return html
    
    def make_report_fee_table(self, child):
        html = '<div class="feetable" id="fee-' + str(child.name) + '"><span class="img-close" onClick="hideTable(\'' + str(child.name) + '\')"></span><table><tr><th>'
        if child.record_type == 'operator':
            html += '<span class="img-operator"></span>Operator'
        else:
            html += '<span class="img-machine"></span>Machine'
        html += '</th><th colspan="2">' + str(child.record_name) + '</th></tr><tr><th>Description</th><th>Rate</th><th>Amount</th></tr>'
        total_fees = 0
        fee_entries = []
        fee_entries_values = []
        
        if child.record_type == 'operator':
            sales_cash_amount = 0
            sales_cash_count = 0
            sales_card_amount = 0
            sales_card_count = 0
            total_fees = 0
            
            ## fees for operators are just all child fees together (summary)            
            for lower in self.tree[child.name].descendants:
                fees_for_child = []
                for row in self.db_cursor.execute('SELECT fees.value, sales.cash_amount, sales.cash_count, sales.card_amount, sales.card_count, fees.name, fees.amount, fees.type FROM fees, sales WHERE fees.id=? AND fees.id=sales.id', [lower.name]):
                    total_fees += float(row[0])
                    sales_cash_amount += float(row[1])
                    sales_cash_count += float(row[2])
                    sales_card_amount += float(row[3])
                    sales_card_count += float(row[4])
                    
                    fees_for_child.append([row[5], float(row[6]), row[7]])
                    fee_entries_values.append([row[5], float(row[6]), row[7], row[0]])
                    
                for name, amount, type in fees_for_child:
                    fee_entries.append(fees_for_child)
                    
        else:
            sales_cash_amount = child.sales_cash_amount
            sales_cash_count = child.sales_cash_count
            sales_card_amount = child.sales_card_amount
            sales_card_count = child.sales_card_count       
                
        ## sales figures
        html += '<tr><td>Cash sales</td><td>' + str(int(sales_cash_count)) + ' sales</td><td>+$' + str('%.2f' % sales_cash_amount) + '</td></tr>'
        html += '<tr><td>Card sales</td><td>' + str(int(sales_card_count)) + ' sales</td><td>+$' + str('%.2f' % sales_card_amount) + '</td></tr>'
        
        ## fees for machines are verbose
        if child.record_type == 'machine':
            for row in self.db_cursor.execute('SELECT * FROM fees WHERE id=?', [child.name]):
                fee_name = row[1]
                fee_amount = float(row[2])
                fee_type = row[3]
                fee_calc = row[4]
                total_fees += fee_calc
                
                html += '<tr><td>' + fee_name + '</td><td>' + str(fee_amount) + ' ' + fee_type + '</td><td>-$' + str('%.2f' % fee_calc) + '</td></tr>'
        
        ## fees for operators are not unless common
        else:
            ## if fees are the same for all machines below, show them verbosely
            if self.check_equal_list(fee_entries):
                ## combine the fee values
                combined_fees = dict()
                for fee_name, fee_amount, fee_type, fee_value in fee_entries_values:
                    fee_html = '<td>' + fee_name + '</td><td>' + str(fee_amount) + ' ' + fee_type + '</td>'
                    if fee_html not in combined_fees:
                        combined_fees[fee_html] = fee_value
                    else:
                        combined_fees[fee_html] += fee_value
                        
                ## print the fees
                for entry in combined_fees.keys():
                    html += '<tr>' + str(entry) + '<td>-$' + str('%.2f' % combined_fees[entry]) + '</td></tr>'
            ## if the fees are not the same for all machines below, don't be verbose
            else:
                html += '<tr><td>Machine fees</td><td>See individual machines</td><td>-$' + str('%.2f' % total_fees) + '</td></tr>'
        
        html += '<tr><td>Cash collected by operator</td><td>&nbsp;</td><td>-$' + str('%.2f' % sales_cash_amount) + '</td></tr>'
        
        refund = sales_card_amount - total_fees
        if refund < 0:
            html += '<tr class="bill"><td>Bill</td><td></td><td>$' + str('%.2f' % (0 - refund)) + '</td></tr>'
        else:
            html += '<tr class="refund"><td>Refund</td><td></td><td>$' + str('%.2f' % refund) + '</td></tr>'
        
        html += '</table>'
        
        ## add product table (if we have the data)
        html += self.make_report_product_table(child)
        html += '</div>'
        
        return html
    
    def toggle_vis_command(self, target):        
        return 'toggleVis(\'' + str(target.name) + '\')'
    
    def make_report_child(self, root_node, out_file):
        
        for child in root_node.children:
            if child.record_type == 'operator': 
                
                out_file.write('\n<li id="li-' + str(child.name) + '">')                
                out_file.write('<a onClick="' + self.toggle_vis_command(child) + '"><span class="img-operator"></span>' + child.record_name + '</a>')                
                out_file.write(self.make_report_fee_table(child))
                out_file.write('<ul>')                
                self.make_report_child(child, out_file)
                out_file.write('</ul></li>')
            else:
                out_file.write('\n<li id="li-' + str(child.name) + '" onClick="' + self.toggle_vis_command(child) + '">')
                out_file.write('<a onClick="' + self.toggle_vis_command(child) + '"><span class="img-machine"></span>' + child.record_name + '</a></li>')  
                out_file.write(self.make_report_fee_table(child))
                
        out_file.flush()
            
    ## make a report for the given operator
    def make_report(self):
        ## return true if the report is generated, false plus a reason otherwise
        global css, javascript
        
        try:
            selected = int(self.view_tree.selection()[0])
            root_node = self.tree[selected]
        except:
            print('MAKE_REPORT: Could not get selected node')
            return

        path = filedialog.asksaveasfilename(title = 'Save report to', filetypes = (("Web page", "*.html"), ("All files","*.*")))
        
        regexp_extension = re.search('\.html', path)
        if not regexp_extension:
            path = path + '.html'
        
        if path == None or path == '':
            return

        try:
            out_file = open(path, 'w')
        except:
            print('MAKE_REPORT: Could not open for writing')
            messagebox.showerror('Report not saved', 'Could not write to ' + str(path))
            return False, 'Could not open the output file for writing'
    
        out_file.write('<!DOCTYPE html>\n<html><head><style type="text/css">' + str(css) + '</style><script type="text/javascript">' + str(javascript) + '</script><title>Sales report for ' + root_node.record_name + ' (' + str(self.start_date) + ' - ' + str(self.end_date) + ')</title></head><body>')
        ## first check that we know about the active state for all machines under this operator
        for child in root_node.descendants:
            if child.record_type == 'machine' and child.active == None:
                print('MAKE_REPORT: Unknown active state for children')
                messagebox.showerror('Report not saved', 'Could not determine the active state of all machines under this operator. Are you sure you set fees for all affected machines?')
                return False, 'Could not determine the active state of all machines under this operator. Are you sure you set fees for all affected machines?'
                
        ## make the tree of operators and machines
        print('MAKE_REPORT: Making report')
        out_file.write('<h1><a onClick="' + self.toggle_vis_command(root_node) + '">' + root_node.record_name + '</a></h1>\n')
        out_file.write(self.make_report_fee_table(root_node))
        out_file.write('<div id="dates">' + str(self.start_date) + ' to ' + str(self.end_date) + '</div>')
        out_file.write('<div id="info"><p>Click on a machine or operator to see sales/fees for that item.</p><p>Note that only active machines are shown. Machines are considered active if they were active during this period or had card sales during this period.</p></div>')
        self.make_report_child(root_node, out_file)
        
        ## end of file
        out_file.write('</body></html>')
        out_file.flush()
        out_file.close()
        print('MAKE_REPORT: Report done')
        messagebox.showinfo('Report saved', 'Report saved to ' + str(path))
    

## program start ##
       
ui = GUI()
ui.run()

print('All done!')