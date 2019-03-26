## standard libraries
import re
import time
import queue
import threading
import json
from tkinter import *
from tkinter import ttk, font, messagebox, filedialog
import datetime
import os
import copy
from multiprocessing.pool import ThreadPool

## non-standard libraries
import requests
from PIL import Image, ImageTk

## number of workers for multithreaded requests
worker_count = 20

## global variables
machine_list = []
operator_list = []

## Machine object for storing machine information
class Machine():
    ## Initialise the machine object
    def __init__(self, id, parent, name):
        self.id = id
        self.parent = parent        
        self.name = name
        
        self.dtu = None
        self.vpos = None
        self.sim = None
        self.rssi = None
        self.fw_dtu = None
        self.fw_vpos = None
        self.type = 'machine'
        
        ## set to true if the machine indicates that it is currently active
        ## (used later to figure out active ranges)
        self.active_now = False
        self.active = None
        self.fees = []
        ## sales are 'source': [count, value]
        self.sales = {'cash': [None,None], 'card': [None,None]}
    
    ## Returns true if the machine has a VPOS touch, false otherwise
    def is_vpos_touch(self):
        if self.dtu == self.vpos and self.dtu != None:
            return True
        else:
            return False
    
    ## Returns cash sale count, amount
    def get_cash_sales(self):        
        return self.sales['cash'][0], self.sales['cash'][1]
        
    ## Returns card sale count, amount
    def get_card_sales(self):
        return self.sales['card'][0], self.sales['card'][1]

    ## get the parent of this operator
    def get_parent(self):    
        for operator in operator_list:
            if operator.id == self.parent:
                return operator
                
        return None        
    
## Fee object
class Fee():
    ## Initialise the fee object
    def __init__(self, actor, name, amount, applied):
        self.actor = actor
        self.name = name            
        self.amount = amount
        self.applied = self.convert_name(applied)
        self.value = 0
    
    ## Compare two fees to see if they can be combined
    def compare(self, fee):
        if self.name == fee.name and self.amount == fee.amount and self.applied == fee.applied:
            return True
        else:
            return False
    
    ## Converts text representation of fee to int and vice-versa
    def convert_name(self, name):
        text_types = ['dollars per active DTU', 'dollars per cash sale', '% of cash sales income', 'dollars per CC sale', '% of CC sales income', 'dollars per transaction', '% of total income (before other fees)', '% of total revenue (after other fees)']    
    
        ## number to text
        if type(name) is int:
            return text_types[name]
        ## text to number
        elif type(name) is str:
            return text_types.index(name)
        else:
            return None           
    
    ## Calculate the value of this fee object
    def calculate(self, actor = None):
        ## Fee applications:
        ##  0: Fixed fee
        ##  1: Per cash sale
        ##  2: Per cash sale value (percent)
        ##  3: Per card sale
        ##  4: Per card sale value (percent)
        ##  5: Total sales count
        ##  6: Total income (percent)
        ##  7: Total revenue (percent)
    
        if actor == None:
            actor = self.actor
    
        ## Get the sales values
        cash_sales_count, cash_sales_amount = actor.get_cash_sales()
        card_sales_count, card_sales_amount = actor.get_card_sales()
        total_sales_count = cash_sales_count + card_sales_count
        total_sales_count = cash_sales_count + card_sales_count
        total_sales_amount = cash_sales_amount + card_sales_amount
        
        ## Calculate the fee values
        if self.applied == 0:
            ## Fixed fee
            if actor.type == 'operator':
                ## for ops, get the number of active actors
                dtus = len(actor.get_machines(recursive = True, active_only = True))
            else:
                ## machines dont have get_actors, so the number will be one
                dtus = 1
            value = self.amount * dtus
            
            #print('DEBUG_FEE_CALC_DTU: Actor ' + str(actor.name) + ' (' + str(actor.type) + ') with ' + str(dtus) + ' DTUs has fee ' + str(value))
        elif self.applied == 1:
            ## Per cash sale
            value = self.amount * cash_sales_count
        elif self.applied == 2:
            ## Percent of cash sale value
            value = self.amount * (cash_sales_amount / 100)
        elif self.applied == 3:
            ## Per card sale
            value = self.amount * card_sales_count
        elif self.applied == 4:
            ## Percent of card sale value
            value = self.amount * (card_sales_amount / 100)
        elif self.applied == 5:
            ## Per sale
            value = self.amount * total_sales_count
        elif self.applied == 6:
            ## Percent of sale value
            value = self.amount * (total_sales_amount / 100)
        elif self.applied == 7:
            other_fees = 0
            ## Percent of total revenue (income after other fees).
            ## This method will result in calculating all fees twice, but
            ## this is an acceptable compromise given the low
            ## computational cost and code complexity.
            for fee in self.actor.fees:
                ## Exclude self
                if fee != self:
                    ## Add together other fees
                    other_fees += fee.calculate(actor = actor)
            
            ## work out revenue
            revenue = total_sales_amount - other_fees
            
            ## apply the fee to revenue
            value = self.amount * (revenue / 100)
        else:
            raise ValueError('Unknown fee application: ' + str(self.applied))
               
        return value
                        
## Operator object for storing operator information
class Operator():
    ## Initialise the operator object
    def __init__(self, id, parent, name):
        self.id = id
        self.parent = parent
        self.name = name
        self.type = 'operator'
        self.active_now = False
        
        ## lie for operators. this just fixes some display stuff
        self.active = True
        self.fees = []
        
    ## Find all machines and operators under this one
    def get_children(self, parent = None, type = 'all', recursive = False, active_only = False):
        global machine_list, operator_list
        ## if no ID was passed, we are looking for nodes with this one as a parent
        if parent == None:
            parent = self.id
        
        children = []
        
        ## go through the operator list and add matching operators
        for operator in operator_list:
            ## if the operator has this one as a parent, add it to the list
            if operator.parent == parent:
                ## only add the operator if we are looking for ops too, 
                ## otherwise just do children
                if type == 'all' or type == 'operator':
                    children.append(operator)
                
                ## if we are are recursive, go deeper
                if recursive == True:
                    children.extend(self.get_children(parent = operator.id, type = type, recursive = True, active_only = active_only))
                    
        ## if we are looking for all or machines..
        if type == 'all' or type == 'machine':
            ## go through the machine list and add matching machines
            for machine in machine_list:
                ## if the machine has this one as a parent, add it to the list
                if machine.parent == parent:
                    ## exclude inactive machines if specified
                    if (active_only == True and machine.active == True) or active_only == False:
                        children.append(machine)
                    
        return children

    ## convinience function - get all machines under this one
    def get_machines(self, parent = None, recursive = False, active_only = False):
        return self.get_children(parent = parent, type = 'machine', recursive = recursive, active_only = active_only)
        
    ## convinience function - get all operators under this one
    def get_operators(self, parent = None, recursive = False):
        return self.get_children(parent = parent, type = 'operator', recursive = recursive)

    ## get the parent of this operator
    def get_parent(self):    
        for operator in operator_list:
            if operator.id == self.parent:
                return operator
                
        return None
        
    ## Returns cash sale count, amount
    def get_cash_sales(self):
        sales_count = 0
        sales_amount = 0
        null_sales = True
        ## add up the sales for all children
        for actor in self.get_machines(recursive = True):
            count, amount = actor.get_cash_sales()
            if count != None:
                null_sales = False
                sales_count += count
                sales_amount += amount
        
        ## if there is no sales data for any child, return None
        if null_sales == True:
            return None, None
        else:
            return sales_count, sales_amount
            
        
    ## Returns card sale count, amount
    def get_card_sales(self):
        sales_count = 0
        sales_amount = 0
        null_sales = True
        ## Add up the sales for all children
        for actor in self.get_machines(recursive = True):
            count, amount = actor.get_card_sales()
            if count != None:
                null_sales = False
                sales_count += count
                sales_amount += amount
        
        ## If there is no sales data for any child, return None
        if null_sales == True:
            return None, None
        else:    
            return sales_count, sales_amount
                   
## Class for Nayax functions        
class Nayax():
    ## Class initialisation. Set up variables and do the initial login
    def __init__(self, username, password):
        self.base_URL = 'https://my.nayax.com/DCS/'
        self.cookies = {}
        self.headers = {}
        self.logged_in = False
        self.sales_data_queue_in = queue.Queue()
        self.sales_data_queue_out = queue.Queue()
        self.product_map_queue_in = queue.Queue()
        self.product_map_queue_out = queue.Queue()
        self.request_queue_in = queue.Queue()
        self.request_queue_out = queue.Queue()
        
        self.login(username, password)
    
    ## Makes requests to the Nayax website for data
    def make_request(self, path, post = {}, json = {}, login_required = True):
        ## Figure out the URL to request
        url = self.base_URL + path
        request = None
        
        ## Error if we are not logged in, unless login_required is false       
        if login_required == True and self.logged_in == False:
            raise RuntimeError('Tried to make request for ' + path + ' but we are not logged in')
            return
        
        ## Wrap in a for loop so that we can do retries
        for i in range(3):
            ## Wrap in a try to catch connection issues        
            try:                
                ## If we have POST or JSON data, it's a POST request
                if post != {} or json != {}:
                    print('\n[NYX_REQUEST:POST/JSON] Requesting ' + str(url))
                    request = requests.post(url, cookies = self.cookies, headers = self.headers, data = post, json = json)
                ## If we don't have any, it's a GET request
                else:
                    print('\n[NYX_REQUEST:GET] Requesting ' + str(url))
                    request = requests.get(url, cookies = self.cookies, headers = self.headers)
                
                print('\n[NYX_REQUEST] Got ' + str(url))
            ## If there was a connection error, wait 1 second and then retry
            except requests.exceptions.ConnectionError:
                print('Request for ' + url + ' failed. Retrying (' + str(i+1) + '/3)...')
                time.sleep(1)
                continue
            ## If it worked, break the retry loop
            else:
                break
                
        ## Return the request object
        return request
    
    ## Log in to Nayax
    def login(self, username, password):
        nvtoken = None
        
        print('[' + str(time.time()) + '] Login: Getting login page...')
        ## Get the login page
        login_page = self.make_request('LoginPage.aspx', login_required = False)
        ## Find the signin token to be passed with the login attempt
        regexp_token = re.search(r'var token = \'(.+)\'\;', login_page.text)
        if regexp_token:
            signin_token = regexp_token.group(1)
        else:
            raise RuntimeError('Could not get the login page')
        
        print('[' + str(time.time()) + '] Login: Logging in...')        
        ## Do the login using the given login token to get the session cookies
        self.headers = {'signin-token': signin_token, 'Host': 'my.nayax.com', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://my.nayax.com'}
        login_post = self.make_request('LoginPage.aspx?ReturnUrl=%2fdcs%2fpublic%2fdefault.aspx', json = {'userName': username, 'password': password, 'action': 'signin', 'newPassword': '', 'oldPassword': '', 'verifyPassword': ''}, login_required = False)
        ## If the 'unknown credentials' error is present, the user/pass were wrong
        if re.search(r'UNKNOWNCREDS', login_post.text):
            raise RuntimeError('Incorrect login credentials')
        else:
            self.cookies = login_post.cookies
        
        print('[' + str(time.time()) + '] Login: Getting background request token...')        
        ## Get the dashboard using the authenticated login cookies so that we
        ## can get the background request validation token
        self.headers = {'Host': 'my.nayax.com', 'Origin': 'https://my.nayax.com'}
        dashboard = self.make_request('public/facade.aspx?model=reports/dashboard', login_required = False)
        ## Find the background request validation token
        regexp_nvtoken = re.search(r'var token = \'(.+)\'\;', dashboard.text)
        if regexp_nvtoken:
            nvtoken = regexp_nvtoken.group(1)
            ## Set the validation headers for all future requests
            self.headers = {'Host': 'my.nayax.com', 'X-Requested-With': 'XMLHttpRequest', 'Origin': 'https://my.nayax.com', 'X-Nayax-Validation-Token': nvtoken}
            ## Set the state to logged in
            self.logged_in = True
        else:
            raise RuntimeError('Logged in successfully, but could not get the request validation token')
            
        print('[' + str(time.time()) + '] Login: Login complete...')
    
    ## clean foreign characters from names
    def clean_name(self, name):
        name = re.sub('&amp;', '&', name)
        name = re.sub(r'[^\w\s\-\.\&\'\/\(\)]', '', name)
        return name
    
    ## Get the list of operators and machines
    def get_machine_list(self):
        global machine_list, operator_list
        machines = self.make_request('public/facade.aspx?model=operations/machine&action=Machine.Machines_Search')

        ## find machines
        for match in re.finditer(r'parent_id=\"(\d+)\" title=\"([^<>"]+)\" machine_id=\"(\d+)\"[^<>]+activity_color=\"color_((green)|(red)|(gray))\"', machines.text):
            ## parse out the information
            parent = str(match.group(1))
            name = self.clean_name(match.group(2))
            id = str(match.group(3))
            colour = match.group(4)
            machine = Machine(id, parent, name)
            
            ## work out if the machine is currently active
            if colour == 'green' or colour == 'red':
                machine.active_now = True
            else:
                machine.active_now = False
            
            ## add the machine to the list
            machine_list.append(machine)
            
        ## find operators        
        for match in re.finditer(r'id=\"(\d+)\" parent_id=\"(\d+)\" title=\"([^<>"]+)\" actor_type_id=\"\d+\"(\sdisabled=\"(1)\")?', machines.text):
            ## parse out the information
            parent = str(match.group(2))
            id = str(match.group(1))
            name = self.clean_name(match.group(3))
            inactive = match.group(5)
            
            ## add the operator to the list
            operator = Operator(id, parent, name)
            if inactive == '1':
                operator.active_now = False
            else:
                operator.active_now = True
                
            operator_list.append(operator)
            
    ## Find the root (highest) operator
    def find_root_operator(self):
        global operator_list
               
        ## Look at each operator
        for operator in operator_list:
        
            ## See if their parent is known. If not, this is the highest level
            parent = operator.parent
            is_root = True
            for op in operator_list:
                if op.id == parent:
                    is_root = False
                    
            if is_root == True:
                return operator
                
        raise RuntimeError('Unable to determine root operator')
    
    ## Reduce requests for stats so that they hit <500 machines at a time
    def reduce_tree(self, root = None):
        if root == None:
            ## Find the top of the tree
            root = self.find_root_operator()
        
        request_ops = []
        ## Get the operators under it
        sub_ops = root.get_operators(parent = root.id)
        ## If there are no ops under this, we have to request with it
        if len(sub_ops) == 0:
            request_ops.append(root)
        ## Otherwise we look at the sub operators
        else:
            for op in root.get_operators(parent = root.id):
                ## If they have less than 500 machines, we can do a request on them
                if len(root.get_machines(parent = op.id, recursive = True)) < 500:
                    request_ops.append(op)
                ## Otherwise we go deeper
                else:                
                    request_ops.extend(self.reduce_tree(root = op))
                
        ## Return the list of ops to request against
        return request_ops

    ## worker for getting product maps
    def get_product_map_json_worker(self):
        while True:
            machine = self.product_map_queue_in.get()
            
            ## If the machine is none, we are being terminated
            if machine == None:
                break
            
            ## Make the request
            print('[GPMJ_WORKER] Making request...')
            result = self.make_request('public/facade.aspx?responseType=json&model=operations/machine&action=InventoryStatus_Search&&machine_id=' + str(machine.id) + '&status_id=-1')
            
            ## Load the data in to a JSON object
            print('[GPMJ_WORKER] Loading JSON...')
            json_data = json.loads(result.text)
            
            ## Put the JSON in the out queue
            self.product_map_queue_out.put(json_data)
            
            ## Mark the task as done
            print('[GPMJ_WORKER] Complete...')
            self.product_map_queue_in.task_done()
            
    ## worker for performing multiple requests
    def request_worker(self):
        while True:
            data = self.request_queue_in.get()
            
            ## If the url is none, we are being terminated
            if data == None:
                break
            
            url = data[0]
            post = data[1]
            json = data[2]
            
            result = self.make_request(url, post = post, json = json)
            self.request_queue_out.put(result)
                                   
            ## Mark the task as done
            self.request_queue_in.task_done()
    
    ## Get the product maps JSON
    def get_product_map_json(self, targets, callback = None):
        global worker_count
        print('[GPMJ] Configuring workers..')
        
        ## If there is no callback, use print
        if callback == None:
            callback = print
        
        ## Set up a thread pool for multithreading
        worker_threads = []
        for i in range(worker_count):
            worker = threading.Thread(target = self.get_product_map_json_worker)
            worker.start()
            worker_threads.append(worker)        
        
        ## go through the list of machines
        for machine in targets:
            self.product_map_queue_in.put(machine)
        
        print('[GPMJ] Waiting for workers..')
        ## Wait for all the workers to finish
        while self.product_map_queue_in.empty() == False:
            remaining = self.product_map_queue_in.qsize()
            callback('Getting maps - ' + str(remaining + worker_count) + ' remaining..')
            time.sleep(0.1)
        
        ## Stop the worker threads
        callback('Waiting for final ' + str(worker_count) + '..')
        for i in range(worker_count):
            self.product_map_queue_in.put(None)
            
        for child in worker_threads:
            child.join(60)
        
        ## get the data from the workers
        print('[GPMJ] Getting worker output..')
        json_data = []
        while self.product_map_queue_out.empty() == False:
            ## Get the data from the JSON queue
            try:
                data = self.product_map_queue_out.get_nowait()
                json_data.append(data)
            ## Break if we can't get the data
            except:
                break
        
        print('[GPMJ] Done! Returning data.')        
        return json_data
       
    ## Remove unknown products from a machine
    def remove_unknown_products(self, targets, callback = None):
        global worker_count
        
        ## If no callback is defined, just make it print
        if callback == None:
            callback = print
        
        callback('Getting machine product maps...')
        json_data = self.get_product_map_json(targets, callback = callback)
        
        callback('Processing product maps...')
        ## Process the JSON data
        deletion_queue = []
        for data in json_data:
            
            ## go through each of the product entries
            for_deletion = []
            for product in data['data_products']:
                if str(product['product_id']) == '0':
                    ## add it to the list
                    for_deletion.append(product['machine_product_id'])
                    
            ## add the list to the deletion queue
            print('Found ' + str(len(for_deletion)) + ' unknown products for deletion in machine ' + str(data['data'][0]['operator_identifier']))
            deletion_queue.append([str(data['data'][0]['machine_id']), for_deletion])
        
        callback('Deleting unknown products...')        
        ## Set up workers again to do the deletions
        worker_threads = []
        for i in range(worker_count):
            worker = threading.Thread(target = self.request_worker)
            worker.start()
            worker_threads.append(worker)
        
        ## go through the list of machines
        del_machines = 0
        del_products = 0
        for entry in deletion_queue:
            ## ignore machines with no deletions
            if len(entry[1]) > 0:
                del_machines += 1
                del_products += len(entry[1])
                
                ## break up the data
                machine = str(entry[0])       
                deletions = ','.join(entry[1])
                request_url = 'public/facade.aspx?responseType=json&model=operations/machine&action=InventoryStatus.RemoveProducts&machine_id=' + machine + '&product_ids=' + deletions

                self.request_queue_in.put([request_url, None, None])
        
        ## Wait for all the workers to finish
        while self.request_queue_in.empty() == False:
            remaining = self.request_queue_in.qsize()
            callback('Deleting - ' + str(remaining + worker_count) + ' machines remaining..')
            time.sleep(0.1)
        
        ## Stop the worker threads
        callback('Waiting for final ' + str(worker_count) + '..')
        for i in range(worker_count):
            self.request_queue_in.put(None)
            
        for child in worker_threads:
            child.join(60)
        
        return del_machines, del_products
        callback('Task complete...')            
    
    ## Copy PA code to MDB code for products
    def pa_to_mdb(self, targets, callback = None, reverse = False):
        ## if called with reverse=true, we copy mdb->pa instead
    
        global worker_count
        
        ## If no callback is defined, just make it print
        if callback == None:
            callback = print
        
        upd_products = 0
        upd_machines = 0
        
        callback('Getting machine product maps...')
        json_data = self.get_product_map_json(targets, callback = callback)
        
        callback('Processing product maps...')
        ## Process the JSON data
        update_queue = []
        for data in json_data:
            update = False
            
            ## go through each of the product entries
            for product in data['data_products']:
                ## MDB to PA
                if reverse == True:
                    if str(product['pa_code']) == '' or str(product['pa_code']) == 'None':
                        product['pa_code'] = product['mdb_code']
                        upd_products += 1
                        update = True
                ## PA to MDB
                else:                
                    if str(product['mdb_code']) == '' or str(product['mdb_code']) == 'None':
                        product['mdb_code'] = product['pa_code']
                        upd_products += 1
                        update = True
            
            ## only queue for this machine if it needs an update
            if update == True:
                upd_machines += 1
                update_queue.append(data['data_products'])             
        
        callback('Copying code for products...')        
        ## Set up workers again to do the deletions
        worker_threads = []
        for i in range(worker_count):
            worker = threading.Thread(target = self.request_worker)
            worker.start()
            worker_threads.append(worker)
        
        ## go through the list of machines
        for entry in update_queue:
            machine = entry[0]['machine_id']            
            
            ## replace with new data
            self.request_queue_in.put(['public/facade.aspx?responseType=json&model=operations/machine&action=InventoryStatus.UpdateMachineProduct&machine_id=' + str(machine) + '&lastVisitUpdate=false', None, entry])
        
        ## Wait for all the workers to finish
        while self.request_queue_in.empty() == False:
            remaining = self.request_queue_in.qsize()
            callback('Updating - ' + str(remaining + worker_count) + ' machines remaining..')
            time.sleep(0.1)
        
        ## Stop the worker threads
        callback('Waiting for final ' + str(worker_count) + '..')
        for i in range(worker_count):
            self.request_queue_in.put(None)
            
        for child in worker_threads:
            child.join(60)
        
        return upd_machines, upd_products
        callback('Task complete...')   
    
    ## Dump JSON product data for a machine
    def dump_json_products(self, targets, callback = None):
        global worker_count
        
        ## If no callback is defined, just make it print
        if callback == None:
            callback = print
        
        callback('Getting machine product maps...')
        json_data = self.get_product_map_json(targets, callback = callback)
        
        callback('Processing product maps...')
        ## Process the JSON data
        deletion_queue = []
        for data in json_data:
            
            print('DEBUG_PM_JSON: ' + str(data['data_products']))
        
        callback('Task complete...')
        
    ## Gets sales data (plus a bunch of other data) for the machines - worker
    def get_sales_data_worker(self):
        ## Poll queue indefinitely
        while True:
            ## Get the next operator from the queue
            data = self.sales_data_queue_in.get()
            op = data[0]
            start = data[1]
            end = data[2]
            
            ## If operator is None, we have been stopped and need to break
            ## the queue polling
            if op == None:
                break
                
            actor = str(op.id)
            sales_cash = self.make_request('public/facade.aspx?responseType=json&model=reports/SalesSummary&action=SalesSummary_Report&&actor_id=' + actor + '&payment_method=3&num_of_rows=1000000&with_cash=1&with_cashless_external=0&time_period=57&start_date=' + start + 'T00%3A00%3A00&end_date=' + end + 'T23%3A59%3A59.997&report_type=2')
            sales_card = self.make_request('public/facade.aspx?responseType=json&model=reports/SalesSummary&action=SalesSummary_Report&&actor_id=' + actor + '&payment_method=1&num_of_rows=1000000&with_cash=0&with_cashless_external=0&time_period=57&start_date=' + start + 'T00%3A00%3A00&end_date=' + end + 'T23%3A59%3A59.997&report_type=2')
            
            json_cash = json.loads(sales_cash.text)
            json_card = json.loads(sales_card.text)  
            
            self.sales_data_queue_out.put([json_cash, json_card])
            
            self.sales_data_queue_in.task_done()
            
        
    ## Gets sales data (plus a bunch of other data) for the machines - control
    def get_sales_data(self, start, end, operator = None, callback = None):
        global worker_count
    
        if callback == None:
            callback = print
    
        ## Work out which operators to query
        callback('Reducing tree...')
        if operator == None:
            operator = self.find_root_operator()
            
        ops = self.reduce_tree(root = operator)        
        
        ## Set up a thread pool for multithreading
        callback('Preparing workers...')
        worker_threads = []
        for i in range(worker_count):
            worker = threading.Thread(target = self.get_sales_data_worker)
            worker.start()
            worker_threads.append(worker)
        
        callback('Employing workers...')
        ## Send the tasks to the worker threads
        for op in ops:
            self.sales_data_queue_in.put([op, start, end])
        
        callback('Waiting for workers to complete...')
        ## Wait for all the workers to finish
        while self.sales_data_queue_in.empty() == False:
            remaining = self.sales_data_queue_in.qsize()
            callback('Getting data - ' + str(remaining + worker_count) + ' remaining..')
            time.sleep(0.1)
        
        ## Stop the worker threads
        callback('Waiting for final ' + str(worker_count) + '..')
        for i in range(worker_count):
            self.sales_data_queue_in.put([None, None, None])
                
        for child in worker_threads:            
            child.join(60)
        
        ## Process the JSON data
        callback('Processing received data..')
        while self.sales_data_queue_out.empty() == False:
            ## Get the data from the JSON queue
            try:
                data = self.sales_data_queue_out.get_nowait()
            ## Break if we can't get the data
            except:
                break
            
            j_cash = data[0]
            j_card = data[1]
            
            ## Process the JSON data for cash
            for entry in j_cash['data'][1]:
                machine_id = int(entry['machine_id'])
                try:
                    cash_amount = entry['total_amount']
                except:
                    cash_amount = 0
                    
                try:
                    cash_count = entry['total_count']
                except:
                    cash_count = 0
                    
                ## Pull out some machine info, since that is supplied in the JSON too
                rssi = entry['ex_rssi']
                dtu = entry['ex_device_number']
                vpos = entry['ex_vpos_serial']
                fw_dtu = entry['ex_device_fw_existing']
                fw_vpos = entry['ex_vpos_fw_existing']
                sim = entry['ex_sim_card_serial']
                
                ## Add the sales data to the applicable machine
                for machine in machine_list:
                    if int(machine.id) == machine_id:
                        #callback('' + str(machine_id) + ' cash - $' + str(cash_amount) + ' (' + str(cash_count) + ')...')
                        machine.sales['cash'] = [cash_count, cash_amount]
                        
                        ## Add the info to the machine
                        machine.dtu = dtu
                        machine.fw_dtu = fw_dtu
                        machine.vpos = vpos
                        machine.fw_vpos = fw_vpos
                        machine.sim = sim
                        machine.rssi = rssi
                        
            ## Process the JSON data for cards
            for entry in j_card['data'][1]:
                machine_id = int(entry['machine_id'])
                try:
                    card_amount = entry['total_amount']
                except:
                    card_amount = 0
                    
                try:
                    card_count = entry['total_count']
                except:
                    card_count = 0                
                                
                ## Add the sales data to the applicable machine
                for machine in machine_list:
                    if int(machine.id) == machine_id:
                        #callback('' + str(machine_id) + ' card - $' + str(card_amount) + ' (' + str(card_count) + ')...')
                        machine.sales['card'] = [card_count, card_amount]
        
        ## If we get to here, processing of JSON data is complete
        callback('Data processing complete. Checking for active machines..')
        
        ## check for active machines (threaded)
        pool = ThreadPool(processes = worker_count)
        workers = []
        ## push out data to the workers
        for machine in operator.get_machines(recursive = True):
            workers.append([machine, pool.apply_async(self.is_machine_active, (machine, start, end, ))])            
            
        ## get the results
        for machine, child in workers:
            callback('Checking active machines (' + str(workers.index([machine, child])) + '/' + str(len(workers)) + ')...')
            active = child.get()
            #print(machine.name + ' active? ' + str(active))
            machine.active = active
            
        callback('Sales data loaded')
        
    ## Finds out if a machine was active during the specified sales period
    def is_machine_active(self, actor, start_date, end_date):
        ## we don't care about operators, only machines
        if actor.type != 'machine':
            return None
        
        ## data dates have to be specified
        try:
            start = datetime.datetime.strptime(start_date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
            end = datetime.datetime.strptime(end_date + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        except:
            print('Could not check if ' + str(actor.name) + ' was active because sales data dates were not specified!')
            return None
            
        ## machines with card sales are active
        if actor.sales['card'][0] != 0 and actor.sales['card'][0] != None:
            #print(str(actor.name) + ' active overridden because it has sales')
            return True  
    
        ## get the history tab
        response = self.make_request('public/facade.aspx?model=operations/machine&action=MachineHistory.Get&&machine_id=' + str(actor.id))
        
        event_list = []
        
        ## get the active/not active events
        for entry in re.finditer(r'<machineHistory[^<>]*changed_item="Status"[^<>]*changed_to="((Active)|(Not Active))" updated_at="(\d{4}\-\d{2}\-\d{2}T\d{2}:\d{2}:\d{2})[\.\d]*"', response.text):
            event = entry.group(1)
            stamp_dt = datetime.datetime.strptime(entry.group(4), '%Y-%m-%dT%H:%M:%S')
            event_list.append([stamp_dt, event])            

        ## the issue with Nayax event history is that they are often missing
        ## so we have to infer status from the absence of certain events, or
        ## the current status
         
        ## sort the event list by time and pull out the cloest events before and after our range
        event_list = sorted(event_list)
        history = [datetime.datetime.strptime('2000-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'), None]      
        future = [datetime.datetime.strptime('2100-01-01 00:00:00', '%Y-%m-%d %H:%M:%S'), None]
        active_in_period = False
        for stamp, event in event_list:
            #print('DEBUG_IMA ' + str(stamp) + ' event: ' + str(event))
            if stamp < start and stamp > history[0]:
                history = [stamp, event]
            elif stamp > end and stamp < future[0]:
                future = [stamp, event]
            else:
                active_in_period = True
            
        ## if we still dont think it's active, check the close events
        
        ## look for a transition to active before this period
        if str(history[1]) == 'Active':
            #print(str(actor.name) + ' active from past activity')
            active_in_period = True
        ## or a transition to not active after this period
        elif str(future[1]) == 'Not Active':
            #print(str(actor.name) + ' active from future inactivity')
            active_in_period = True            
        ## if there were no events, we just have to assume the current status
        ## is correct
        if len(event_list) == 0 and actor.active_now == True:
            #print(str(actor.name) + ' active assumed due to lack of events')
            active_in_period = True
        
        return active_in_period   
            
## GUI class
class GUI():
    ## Class initialisation
    def __init__(self):
        ## Local variables
        self.nayax = None       
    
        ## Root UI element
        self.root = Tk()
        self.root.title('Login')
        self.root.resizable(False, False)
        
        ## Image assets
        self.image_machine = ImageTk.PhotoImage(Image.open('icons/machine.png'))
        self.image_operator = ImageTk.PhotoImage(Image.open('icons/operator.png'))
        
        ## Login info storage variables
        self.input_username_value = StringVar()
        self.input_password_value = StringVar()
        self.login_error = StringVar()        
        
        ## Login info container frame
        self.frame_login = ttk.LabelFrame(self.root, text = 'Nayax login')
        self.frame_login.grid(row = 0, column = 0, sticky = 'news')
        
        ## Username and password labels and entry fields
        ttk.Label(self.frame_login, text = 'Username').grid(row = 0, column = 0)
        self.input_username = ttk.Entry(self.frame_login, textvariable = self.input_username_value)
        self.input_username.grid(row = 0, column = 1)
        
        ttk.Label(self.frame_login, text = 'Password').grid(row = 1, column = 0)
        self.input_password = ttk.Entry(self.frame_login, textvariable = self.input_password_value, show = '*')
        self.input_password.grid(row = 1, column = 1)
        self.input_password.bind('<Return>', self.login)
        
        ## Error display
        ttk.Label(self.frame_login, textvariable = self.login_error, foreground = 'red').grid(row = 2, column = 0, columnspan = 2)
        
        ## Submit button
        self.button_login = ttk.Button(self.frame_login, command = self.login, text = 'Login')
        self.button_login.grid(row = 3, column = 0, columnspan = 2)
        
    ## Run the GUI
    def run(self):
        self.root.update()
        self.root.mainloop()
    
    ## Do the Nayax login
    def login(self, event = None):
        ## Update the UI to indicate an operation in progress
        self.login_error.set('Logging in..')
        self.button_login.configure(state = 'disabled')        
        self.root.update()
        
        ## Get the username and password
        username = self.input_username_value.get()
        password = self.input_password_value.get()
        
        ## Make sure they are not blank
        if username == '' or password == '':
            self.login_error.set('Missing username or password')
            self.root.update()
        else:
            ## Do the login
            try:
                self.nayax = Nayax(username, password)
                self.login_error.set('Logged in!')
                self.input_username.configure(state = 'disabled')
                self.input_password.configure(state = 'disabled')
                self.root.update()
                self.load_initial()
                
            ## If there is an error, show it
            except RuntimeError as e:
                self.login_error.set('Login error: ' + str(e))
                self.root.update()                

        ## Restore the login button
        self.button_login.configure(state = 'normal')
        self.root.update()
        
    ## Load initial data and create the GUI
    def load_initial(self):
        ## Replace the login button with a progress bar
        self.button_login.grid_forget()       

        ## Get the machine list
        self.login_error.set('Downloading machine list..')
        self.root.update()
        self.nayax.get_machine_list()
        
        ## Get rid of the login form
        self.frame_login.grid_forget()
        
        ## Add the top menu
        self.create_top_menu()
        
        ## Create the tree view of machines and operators
        self.container_tree = ttk.Frame(self.root)        
        self.tree = ttk.Treeview(self.container_tree, selectmode = 'browse', columns = ('cash', 'card', 'total'))        
        self.tree.bind('<ButtonRelease-1>', self.actor_click_event)
        self.tree.heading('#0', text = 'Machine/operator name')
        self.tree.column('#0', width = 500)
        self.tree.heading('cash', text = 'Cash sales')
        self.tree.column('cash', width = 150)
        self.tree.heading('card', text = 'Card sales')
        self.tree.column('card', width = 150)
        self.tree.heading('total', text = 'Total sales')
        self.tree.column('total', width = 150)
        self.tree.grid(row = 0, column = 0, sticky = 'news')
        
        self.tree_scroll_vertical = ttk.Scrollbar(self.container_tree, orient = 'vertical', command = self.tree.yview)
        self.tree_scroll_horizontal = ttk.Scrollbar(self.container_tree, orient = 'horizontal', command = self.tree.xview)
        self.tree.configure(yscrollcommand = self.tree_scroll_vertical.set, xscrollcommand = self.tree_scroll_horizontal.set)
        self.tree_scroll_vertical.grid(row = 0, column = 1, sticky = 'ns')
        self.tree_scroll_horizontal.grid(row = 1, column = 0, sticky = 'ew')
        
        ## configure the contaiener so that the treeview can scale with window
        ## size changes
        self.container_tree.grid(row = 1, column = 0, sticky = 'news', columnspan = 3)
        self.root.grid_rowconfigure(1, weight=2)
        self.root.grid_columnconfigure(0, weight=2)
        self.container_tree.grid_rowconfigure(0, weight=2)
        self.container_tree.grid_columnconfigure(0, weight=2)
        
        ## populate the tree with machines/operators
        self.draw_actor_list()
        
        ## Add the sales date range fields
        self.create_sd_entry()
            
        ## give the tags meaning (active/inactive)        
        self.tree.tag_configure('active', foreground = 'black', font = font.Font(size = 10))
        self.tree.tag_configure('inactive', foreground = 'red', font = font.Font(size = 10, overstrike = 1))
        self.root.update()
        
        ## create the info area below the machine/op tree
        self.info_frame = ttk.LabelFrame(self.root, text = 'Information')
        self.info_frame.grid(row = 2, column = 0, sticky = 'nsew')       
        
        ## create vars to store machine/operator info
        self.info_name = StringVar()
        self.info_type = StringVar()
        self.info_signal = StringVar()
        self.info_serial_dtu = StringVar()
        self.info_serial_vpos = StringVar()
        self.info_serial_sim = StringVar()
        self.info_firmware_dtu = StringVar()
        self.info_firmware_vpos = StringVar()
        self.info_operator_operators = StringVar()
        self.info_operator_machines = StringVar()
        
        ## and sales info
        self.info_sales_cash_amount = StringVar()
        self.info_sales_cash_count = StringVar()
        self.info_sales_card_amount = StringVar()
        self.info_sales_card_count = StringVar()
        self.info_sales_total_amount = StringVar()
        self.info_sales_total_count = StringVar()        

        ## create the info display widgets       
        ttk.Label(self.info_frame, textvariable = self.info_name, font = ('Arial', 14, 'bold')).grid(row = 0, column = 0, columnspan = 2, sticky = 'w')
        
        self.info_frame_machine = ttk.Frame(self.info_frame)        
        ttk.Label(self.info_frame_machine, text = 'Nayax type').grid(row = 1, column = 0)
        self.info_field_type = ttk.Entry(self.info_frame_machine, textvariable = self.info_type, state = 'readonly', width = 30)
        self.info_field_type.grid(row = 1, column = 1)        
        ttk.Label(self.info_frame_machine, text = 'Signal strength').grid(row = 2, column = 0)
        self.info_field_signal = ttk.Entry(self.info_frame_machine, textvariable = self.info_signal, state = 'readonly', width = 30)
        self.info_field_signal.grid(row = 2, column = 1)
        ttk.Label(self.info_frame_machine, text = 'DTU serial').grid(row = 3, column = 0)
        self.info_field_serial_dtu = ttk.Entry(self.info_frame_machine, textvariable = self.info_serial_dtu, state = 'readonly', width = 30)
        self.info_field_serial_dtu.grid(row = 3, column = 1)        
        ttk.Label(self.info_frame_machine, text = 'VPOS serial').grid(row = 4, column = 0)
        self.info_field_serial_vpos = ttk.Entry(self.info_frame_machine, textvariable = self.info_serial_vpos, state = 'readonly', width = 30)
        self.info_field_serial_vpos.grid(row = 4, column = 1)
        ttk.Label(self.info_frame_machine, text = 'SIM card serial').grid(row = 5, column = 0)
        self.info_field_serial_sim = ttk.Entry(self.info_frame_machine, textvariable = self.info_serial_sim, state = 'readonly', width = 30)
        self.info_field_serial_sim.grid(row = 5, column = 1)
        ttk.Label(self.info_frame_machine, text = 'DTU version').grid(row = 6, column = 0)
        self.info_field_firmware_dtu = ttk.Entry(self.info_frame_machine, textvariable = self.info_firmware_dtu, state = 'readonly', width = 30)
        self.info_field_firmware_dtu.grid(row = 6, column = 1)
        ttk.Label(self.info_frame_machine, text = 'VPOS version').grid(row = 7, column = 0)
        self.info_field_firmware_vpos = ttk.Entry(self.info_frame_machine, textvariable = self.info_firmware_vpos, state = 'readonly', width = 30)
        self.info_field_firmware_vpos.grid(row = 7, column = 1)
        
        self.info_frame_operator = ttk.Frame(self.info_frame)        
        ttk.Label(self.info_frame_operator, text = 'Sub-operators').grid(row = 1, column = 0)
        self.info_field_operator_operators = ttk.Entry(self.info_frame_operator, textvariable = self.info_operator_operators, state = 'readonly', width = 20)
        self.info_field_operator_operators.grid(row = 1, column = 1)        
        ttk.Label(self.info_frame_operator, text = 'Machines').grid(row = 2, column = 0)
        self.info_field_operator_machines = ttk.Entry(self.info_frame_operator, textvariable = self.info_operator_machines, state = 'readonly', width = 20)
        self.info_field_operator_machines.grid(row = 2, column = 1)
        
        ## create sales display widget
        self.info_frame_sales = ttk.Frame(self.info_frame)        
        ttk.Label(self.info_frame_sales, text = 'Total sales').grid(row = 0, column = 0)
        self.info_field_sales_total_amount = ttk.Entry(self.info_frame_sales, textvariable = self.info_sales_total_amount, state = 'readonly', width = 12)
        self.info_field_sales_total_amount.grid(row = 0, column = 1)
        self.info_field_sales_total_count = ttk.Entry(self.info_frame_sales, textvariable = self.info_sales_total_count, state = 'readonly', width = 7)
        self.info_field_sales_total_count.grid(row = 0, column = 2) 

        ttk.Label(self.info_frame_sales, text = 'Cash sales').grid(row = 1, column = 0)
        self.info_field_sales_cash_amount = ttk.Entry(self.info_frame_sales, textvariable = self.info_sales_cash_amount, state = 'readonly', width = 12)
        self.info_field_sales_cash_amount.grid(row = 1, column = 1)
        self.info_field_sales_cash_count = ttk.Entry(self.info_frame_sales, textvariable = self.info_sales_cash_count, state = 'readonly', width = 7)
        self.info_field_sales_cash_count.grid(row = 1, column = 2)    

        ttk.Label(self.info_frame_sales, text = 'Card sales').grid(row = 2, column = 0)
        self.info_field_sales_card_amount = ttk.Entry(self.info_frame_sales, textvariable = self.info_sales_card_amount, state = 'readonly', width = 12)
        self.info_field_sales_card_amount.grid(row = 2, column = 1)
        self.info_field_sales_card_count = ttk.Entry(self.info_frame_sales, textvariable = self.info_sales_card_count, state = 'readonly', width = 7)
        self.info_field_sales_card_count.grid(row = 2, column = 2)
        
        ## make all of the entries copy-on-click
        self.info_field_type.bind('<ButtonRelease-1>', lambda x: self.clipboard_copy(self.info_type))
        self.info_field_signal.bind('<ButtonRelease-1>', lambda x: self.clipboard_copy(self.info_signal))
        self.info_field_serial_dtu.bind('<ButtonRelease-1>', lambda x: self.clipboard_copy(self.info_serial_dtu))
        self.info_field_serial_vpos.bind('<ButtonRelease-1>', lambda x: self.clipboard_copy(self.info_serial_vpos))
        self.info_field_serial_sim.bind('<ButtonRelease-1>', lambda x: self.clipboard_copy(self.info_serial_sim))
        self.info_field_firmware_dtu.bind('<ButtonRelease-1>', lambda x: self.clipboard_copy(self.info_firmware_dtu))
        self.info_field_firmware_vpos.bind('<ButtonRelease-1>', lambda x: self.clipboard_copy(self.info_firmware_vpos))
        self.info_field_operator_operators.bind('<ButtonRelease-1>', lambda x: self.clipboard_copy(self.info_operator_operators))
        self.info_field_operator_machines.bind('<ButtonRelease-1>', lambda x: self.clipboard_copy(self.info_operator_machines))
        self.info_field_sales_total_amount.bind('<ButtonRelease-1>', lambda x: self.clipboard_copy(self.info_sales_total_amount))
        self.info_field_sales_total_count.bind('<ButtonRelease-1>', lambda x: self.clipboard_copy(self.info_sales_total_count))
        self.info_field_sales_cash_amount.bind('<ButtonRelease-1>', lambda x: self.clipboard_copy(self.info_sales_cash_amount))
        self.info_field_sales_cash_count.bind('<ButtonRelease-1>', lambda x: self.clipboard_copy(self.info_sales_cash_count))
        self.info_field_sales_card_amount.bind('<ButtonRelease-1>', lambda x: self.clipboard_copy(self.info_sales_card_amount))
        self.info_field_sales_card_count.bind('<ButtonRelease-1>', lambda x: self.clipboard_copy(self.info_sales_card_count))
            
        
        ## set initial values for the machine info vars
        self.reset_selection_info()
        self.info_frame_sales.grid(row = 1, column = 1, sticky = 'nw')
        
        ## create the fee table
        self.create_fee_table()
        
        ## set the minimum window size to the current size and make it
        ## resizable again
        self.root.minsize(self.root.winfo_width(), self.root.winfo_height() + 200)
        self.root.resizable(True, True)
        self.root.title('Machine reporting')

    ## copy a widget variable value to the clipboard
    def clipboard_copy(self, widget):
        self.root.clipboard_clear()
        try:
            print('Copying to clipboard: ' + str(widget.get()))
            self.root.clipboard_append(str(widget.get()))
        except:
            print('Could not copy widget value to clipboard!')
       
        self.root.update()
        
    ## round monetary values to two decimal points and add a dollar sign
    def display_money(self, value):
        return '$' + str('{:,.2f}'.format(value))
        
    ## populate the treeview with machines and operators
    def draw_actor_list(self):
        ## Clear the existing tree (if present)
        self.tree.delete(*self.tree.get_children())
    
        ## Get the list of machines and operators
        root_op = self.nayax.find_root_operator()
        elements = root_op.get_children(recursive = True)
        
        ## Populate the root element first...
        self.tree.insert('', 'end', root_op.id, text = root_op.name, tag = ('active',))
        
        ## ...then everything else under that
        for entry in elements:
            ## tag elements to colour them
            if entry.active_now == False:
                tag = ('inactive',)
            else:
                tag = ('active',)
                
            ## choose the icon based on whether it is an operator or machine
            if entry.type == 'machine':
                icon = self.image_machine
            else:
                icon = self.image_operator
                
            ## check whether this entry should be hidden
            if entry.type == 'machine' and entry.active_now == False and self.menu_hide_inactive_machines.get() == True:
                continue
                
            if entry.type == 'operator':
                if entry.active_now == False and self.menu_hide_inactive_operators.get() == True:
                    continue
                elif len(entry.get_machines(recursive = True)) == 0 and self.menu_hide_empty_operators.get() == True:
                    continue               

            ## get the sales figures (if available)
            cash_count, cash_amount = entry.get_cash_sales()
            card_count, card_amount = entry.get_card_sales()
            
            ## work out the totals               
            if cash_count == None and card_count == None and entry.active == False:
                show_sales = False
            else:
                ## there might have been cash sales but not card or
                ## vice-versa. if so, set the other method to zero
                ## otherwise we might be overriden for an active actor
                if cash_count == None:
                    cash_count = 0
                    cash_amount = 0
                    
                if card_count == None:
                    card_count = 0
                    card_amount = 0     
                
                ## actually calculate the totals
                total_count = cash_count + card_count
                total_amount = cash_amount + card_amount
                show_sales = True
            
            ## insert the element if not hidden. wrap in a try in case the parent is hidden
            try:
                self.tree.insert(entry.parent, 'end', entry.id, text = entry.name, tags = tag, image = icon)
                
                ## if there are sales figures, populate them
                if show_sales == True:       
                    ## populate the figures with proper formatting
                    self.tree.set(entry.id, 'cash', self.display_money(cash_amount) + ' (' + str(cash_count) + ')')
                    self.tree.set(entry.id, 'card', self.display_money(card_amount) + ' (' + str(card_count) + ')')
                    self.tree.set(entry.id, 'total', self.display_money(total_amount) + ' (' + str(total_count) + ')')
                ## if not, put in placeholders
                else:
                    self.tree.set(entry.id, 'cash', '?')
                    self.tree.set(entry.id, 'card', '?')
                    self.tree.set(entry.id, 'total', '?')
            except:
                print('WARNING: Actor ' + entry.name + ' has hidden parent!')
                
        self.root.update()
        
    ## blank out the information section
    def reset_selection_info(self):
        for info_var in [self.info_name, self.info_type, self.info_signal, self.info_serial_dtu, self.info_serial_vpos, self.info_serial_sim, self.info_firmware_dtu, self.info_firmware_vpos, self.info_operator_operators, self.info_operator_machines, self.info_sales_cash_amount, self.info_sales_cash_count, self.info_sales_card_amount, self.info_sales_card_count, self.info_sales_total_amount, self.info_sales_total_count]:
            info_var.set('?')
            
        self.root.update()
    
    ## return the machine/operator object for a given id
    def find_object_for_id(self, id):
        global operator_list, machine_list
        for entry in operator_list:
            if entry.id == str(id):
                return entry
    
        for entry in machine_list:
            if entry.id == str(id):
                return entry
                
        return None
    
    ## called when an actor is clicked in the tree
    def actor_click_event(self, event = None):
        self.populate_selection_info()
        self.populate_fees()
    
    ## populate the information section for the given selection
    def populate_selection_info(self):
        ## clear the current info
        self.reset_selection_info()
        
        ## get the currently selected actor. bail out if not selected
        actor = self.get_selection()
        if actor == None:
            return
            
        ## convert the id to an object
        actor = self.find_object_for_id(actor)
        ## check we got an object again
        if actor == None:
            return
        
        ## common info
        if actor.active == False:
            self.info_name.set(str(actor.name) + ' (INACTIVE)')
        else:
            self.info_name.set(str(actor.name))
            
        ## common info - sales
        cash_count, cash_amount = actor.get_cash_sales()
        card_count, card_amount = actor.get_card_sales()
        
        ## work out the totals               
        if cash_count == None and card_count == None and actor.active == False:
            show_sales = False
        else:                
            ## there might have been cash sales but not card or
            ## vice-versa. if so, set the other method to zero
            ## otherwise we might be overriden for an active actor
            if cash_count == None:
                cash_count = 0
                cash_amount = 0
                
            if card_count == None:
                card_count = 0
                card_amount = 0                
            
            ## actually calculate the totals
            total_count = cash_count + card_count
            total_amount = cash_amount + card_amount
            show_sales = True
        
        if show_sales == True:
            self.info_sales_cash_amount.set(self.display_money(cash_amount))
            self.info_sales_card_amount.set(self.display_money(card_amount))
            self.info_sales_total_amount.set(self.display_money(total_amount))
            self.info_sales_cash_count.set(cash_count)
            self.info_sales_card_count.set(card_count)
            self.info_sales_total_count.set(total_count)
        else:
            self.info_sales_cash_amount.set('?')
            self.info_sales_card_amount.set('?')
            self.info_sales_total_amount.set('?')
            self.info_sales_cash_count.set('?')
            self.info_sales_card_count.set('?')
            self.info_sales_total_count.set('?')
        
        ## populate info for machines
        if actor.type == 'machine':        
            if actor.is_vpos_touch() == True:
                self.info_type.set('VPOS touch')
            else:
                self.info_type.set('VPOS + DTU')
        
            ## populate with info we have            
            if actor.rssi != None:
                ## correlate RSSI to performance
                if actor.rssi == None:
                    rssi = 'Unknown'
                elif int(actor.rssi) < 7:
                    rssi = str(actor.rssi) + ' (Unusable)'
                elif int(actor.rssi) < 11:
                    rssi = str(actor.rssi) + ' (Poor)'
                elif int(actor.rssi) < 15:
                    rssi = str(actor.rssi) + ' (Average)'
                elif int(actor.rssi) < 20:
                    rssi = str(actor.rssi) + ' (Good)'
                elif int(actor.rssi) != 31:
                    rssi = str(actor.rssi) + ' (Excellent)'
                else:
                    rssi = str(actor.rssi) + ' (Perfect or error)'
                
                self.info_signal.set(rssi)
            
            if actor.dtu != None:
                self.info_serial_dtu.set(str(actor.dtu))
            
            if actor.vpos != None:
                self.info_serial_vpos.set(str(actor.vpos))        
                
            if actor.sim != None:
                self.info_serial_sim.set(str(actor.sim))
                
            if actor.fw_dtu != None:
                self.info_firmware_dtu.set(str(actor.fw_dtu))
            
            if actor.fw_vpos != None:
                self.info_firmware_vpos.set(str(actor.fw_vpos))
            
            ## show the applicable info widgets
            self.info_frame_operator.grid_forget()
            self.info_frame_machine.grid(row = 1, column = 0, sticky = 'w')
        
        ## populate with info for operators
        else:
            ## recursively get number of operators and machines under this one
            
            ## figure out the total and active operators
            op_list = actor.get_operators(recursive = True)
            op_inactive = 0
            for op in op_list:
                ## changed active_now to active so we get data for the specified period
                if (op.active == None and op.active_now == False) or op.active == False:
                    op_inactive += 1
                    
            self.info_operator_operators.set(str(len(op_list) - op_inactive) + ' (plus ' + str(op_inactive) + ' inactive)')
            
            ## repeat for machines
            mac_list = actor.get_machines(recursive = True)
            mac_inactive = 0
            for mac in mac_list:
                ## changed active_now to active so we get data for the specified period
                if (mac.active == None and mac.active_now == False) or mac.active == False:
                    mac_inactive += 1
            self.info_operator_machines.set(str(len(mac_list) - mac_inactive) + ' (plus ' + str(mac_inactive) + ' inactive)')
 
            ## show the applicable info widgets
            self.info_frame_machine.grid_forget()
            self.info_frame_operator.grid(row = 1, column = 0, sticky = 'w')
        
        ## update the GUI
        self.root.update()
    
    ## get targets for a given selection
    def get_selection_targets(self, type = 'machine'):
        targets = []
        actor = self.find_object_for_id(self.get_selection())
        if actor == None:
            print('Could not find current selection!')
    
        ## figure out how many machines this will affect
        
        if actor.type == 'operator':
            targets = actor.get_children(recursive = True, type = type)
        else:
            targets = [actor]
            
        return targets
        
    ## remove unknown products callback for updating the GUI
    def rup_callback(self, message = ''):
        self.status.set('Removing unknown products: ' + str(message))
        self.root.update()
    
    ## debug: product json dump callback for updating the GUI
    def dp_callback(self, message = ''):
        self.status.set('Dumping product JSON: ' + str(message))
        self.root.update()
    
    ## get sales data callback for updating the GUI
    def gsd_callback(self, message = ''):
        self.status.set('Getting sales data: ' + str(message))
        self.root.update()
    
    ## remove unknown products for an actor or all machines under it
    def remove_unknown_products(self):
        targets = self.get_selection_targets(type = 'machine')
            
        ## confirm the action
        confirm = messagebox.askquestion('Confirm action', 'This will delete all unknown products for ' + str(len(targets)) + ' machines. Are you sure you want to continue?', icon = 'warning')
        if confirm == 'no':
            return
        else:
            machines, products = self.nayax.remove_unknown_products(targets, callback = self.rup_callback)
        
        messagebox.showinfo('Unknown products deleted', 'Deleted ' + str(products) + ' unknown products from ' + str(machines) + ' machines')
        
    ## copy PA code to MDB code for an actor or all machines under it
    def pa_to_mdb(self):
        targets = self.get_selection_targets(type = 'machine')
            
        ## confirm the action
        confirm = messagebox.askquestion('Confirm action', 'This will copy the PA code to the MDB code in the product map of ' + str(len(targets)) + ' machines. Are you sure you want to continue?', icon = 'warning')
        if confirm == 'no':
            return
        else:
            machines, products = self.nayax.pa_to_mdb(targets, callback = self.rup_callback)
        
        messagebox.showinfo('Codes copied', 'Copied PA codes to MDB codes for ' + str(products) + ' products in ' + str(machines) + ' machines')
        
    ## copy MDB code to PA code for an actor or all machines under it
    def mdb_to_pa(self):
        targets = self.get_selection_targets(type = 'machine')
            
        ## confirm the action
        confirm = messagebox.askquestion('Confirm action', 'This will copy the MDB code to the PA code in the product map of ' + str(len(targets)) + ' machines. Are you sure you want to continue?', icon = 'warning')
        if confirm == 'no':
            return
        else:
            machines, products = self.nayax.pa_to_mdb(targets, callback = self.rup_callback, reverse = True)
        
        messagebox.showinfo('Codes copied', 'Copied MDB codes to PA codes for ' + str(products) + ' products in ' + str(machines) + ' machines')
        
    ## debug: dump json products for an actor or all machines under it
    def dump_json_products(self):
        targets = self.get_selection_targets(type = 'machine')
            
        ## confirm the action
        confirm = messagebox.askquestion('Confirm action', 'This will dump JSON product data for ' + str(len(targets)) + ' machines. Are you sure you want to continue?', icon = 'warning')
        if confirm == 'no':
            return
        else:
            self.nayax.dump_json_products(targets, callback = self.dp_callback)
        
        messagebox.showinfo('Product JSON dumped', 'Dumped from ' + str(len(targets)) + ' machines')
    
    ## get the selected op/machine (as an id)
    def get_selection(self):
        try:
            return int(self.tree.selection()[0])
        except IndexError:
            return None       
    
    ## Create the menu across the top of the screen
    def create_top_menu(self):
        ## Create the root menu object
        self.menubar = Menu(self.root)
        
        ## Display menu
        self.menu_hide_inactive_machines = BooleanVar()
        self.menu_hide_inactive_operators = BooleanVar()
        self.menu_hide_empty_operators = BooleanVar()
        
        self.menu_display = Menu(self.menubar, tearoff = 0)
        self.menu_display.add_checkbutton(label = 'Hide inactive machines', onvalue = True, offvalue = False, variable = self.menu_hide_inactive_machines, command = self.draw_actor_list)
        self.menu_display.add_checkbutton(label = 'Hide inactive operators', onvalue = True, offvalue = False, variable = self.menu_hide_inactive_operators, command = self.draw_actor_list)
        self.menu_display.add_checkbutton(label = 'Hide operators with no machines', onvalue = True, offvalue = False, variable = self.menu_hide_empty_operators, command = self.draw_actor_list)
        self.menubar.add_cascade(label = 'Display', menu = self.menu_display)
        
        ## Export menu
        self.menu_export = Menu(self.menubar, tearoff = 0)
        self.menu_export.add_command(label = 'Export machine info to file', command = self.save_machine_info)
        self.menubar.add_cascade(label = 'Export', menu = self.menu_export)
        
        ## Product map menu
        self.menu_pm = Menu(self.menubar, tearoff = 0)
        self.menu_pm.add_command(label = 'Remove unknown products', command = self.remove_unknown_products)
        self.menu_pm.add_command(label = 'Copy PA codes to MDB codes', command = self.pa_to_mdb)
        self.menu_pm.add_command(label = 'Copy MDB codes to PA codes', command = self.mdb_to_pa)
        self.menubar.add_cascade(label = 'Product map', menu = self.menu_pm)
        
        ## Display the menu
        self.root.config(menu = self.menubar)
    
    ## save machine info to a file
    def save_machine_info(self):
        ## Get the path
        path = filedialog.asksaveasfilename(title = 'Export machine info to', filetypes = (("Web page", "*.html"), ("All files","*.*")))
        
        ## Check we got an answer
        if path == None or path == '':
            return
        
        ## Add an extension if not present
        regexp_extension = re.search('\.html', path)
        if not regexp_extension:
            path = path + '.html'       
    
        ## Export the data
        export = HTML(self)
        actor = self.find_object_for_id(self.get_selection())
        if actor == None:
            messagebox.showerror('No selection', 'Could not determine which actor was selected')
        html = export.machine_info_report(actor)
        try:
            export.save_file(path, html)
            messagebox.showinfo('Machine info saved', 'Machine information saved to ' + str(path))
        except:
            messagebox.showerror('Save failed', 'Could not write to ' + str(path))
            
    ## save machine sales/fees to a file
    def save_machine_sales(self):
        ## Get the path
        path = filedialog.asksaveasfilename(title = 'Export machine sales to', filetypes = (("Web page", "*.html"), ("All files","*.*")))
        
        ## Check we got an answer
        if path == None or path == '':
            return
        
        ## Add an extension if not present
        regexp_extension = re.search('\.html', path)
        if not regexp_extension:
            path = path + '.html'       
    
        ## Export the data
        export = HTML(self)
        actor = self.find_object_for_id(self.get_selection())
        if actor == None:
            messagebox.showerror('No selection', 'Could not determine which actor was selected')
        html = export.machine_sales_report(actor)
        try:
            export.save_file(path, html)
            messagebox.showinfo('Machine sales saved', 'Machine sales saved to ' + str(path))
        except:
            messagebox.showerror('Save failed', 'Could not write to ' + str(path))
    
    ## Puts in defaults for sales data dates if none are present
    def defaults_sd(self, event = None, force = None):
        ## Entries have default values in grey text if nothing is entered.
        ## Otherwise text is black
        if self.start_date.get() == '':
            self.start_date.set('YYYY-MM-DD')
            self.start_date_entry.config(foreground = 'grey')
        elif self.start_date.get() != 'YYYY-MM-DD' or force == 'start':
            self.start_date_entry.config(foreground = 'black')
            if force == 'start':
                self.start_date.set('')
            
        if self.end_date.get() == '':
            self.end_date.set('YYYY-MM-DD')
            self.end_date_entry.config(foreground = 'grey')
        elif self.end_date.get() != 'YYYY-MM-DD' or force == 'end':
            self.end_date_entry.config(foreground = 'black')
            if force == 'end':
                self.end_date.set('')
            
        self.root.update()
    
    ## Sales data date entry
    def create_sd_entry(self):
        ## Create variables for the start and end dates
        self.start_date = StringVar()
        self.end_date = StringVar()
        self.status = StringVar()
        self.status.set('Choose a date range and click the button to get sales data and machine info')
        
        ## Create a frame with entries for the dates, a confirmation button and status area
        self.frame_date = ttk.LabelFrame(self.root, text = 'Sales report date')
        ttk.Label(self.frame_date, text = 'Report range:').grid(row = 0, column = 0, sticky = 'e')
        self.start_date_entry = ttk.Entry(self.frame_date, textvariable = self.start_date)
        self.start_date_entry.grid(row = 0, column = 1)
        ttk.Label(self.frame_date, text = '  to  ').grid(row = 0, column = 2)
        self.end_date_entry = ttk.Entry(self.frame_date, textvariable = self.end_date)
        self.end_date_entry.grid(row = 0, column = 3)
        self.sd_get_button = ttk.Button(self.frame_date, text = 'Get sales data', command = self.get_sales_data)
        self.sd_get_button.grid(row = 0, column = 4)
        ttk.Label(self.frame_date, textvariable = self.status).grid(row = 0, column = 5, sticky = 'e')
        
        self.frame_date.grid(row = 0, column = 0, columnspan = 2, sticky = 'ew')
        
        self.start_date_entry.bind('<FocusOut>', self.defaults_sd)
        self.end_date_entry.bind('<FocusOut>', self.defaults_sd)
        self.start_date_entry.bind('<FocusIn>', lambda x: self.defaults_sd(force = 'start'))
        self.end_date_entry.bind('<FocusIn>', lambda x: self.defaults_sd(force = 'end'))
        self.defaults_sd(force = True)
        
    ## Get the sales data
    def get_sales_data(self):
        ## get the values
        start_date = self.start_date.get()
        end_date = self.end_date.get()
        self.status.set('')
        
        ## convert to (and check) as datestamps
        try:        
            datetime.datetime.strptime(start_date, '%Y-%m-%d')
            datetime.datetime.strptime(end_date, '%Y-%m-%d')
            
            ## disable the entries and buttons while we work
            self.start_date_entry.configure(state = 'disabled')
            self.end_date_entry.configure(state = 'disabled')
            self.sd_get_button.configure(state = 'disabled')
            self.status.set('Please wait. Getting sales data...')
        except ValueError:
            self.status.set('Invalid date format. Dates must be in the format YYYY-MM-DD, e.g. 2018-11-03')
            
        self.root.update()
        
        ## Populate the sales data
        self.nayax.get_sales_data(start_date, end_date, callback = self.gsd_callback)
        
        ## Redraw the tree with the new data
        self.draw_actor_list()
        
        ## Restore the entries
        self.status.set('')
        self.start_date_entry.configure(state = 'normal')
        self.end_date_entry.configure(state = 'normal')
        self.sd_get_button.configure(state = 'normal')
        
        self.root.update()
        
        ## This might have taken a while and the user isn't paying attention.
        ## Tell the user we are done with a dialog
        messagebox.showinfo('Sales data downloaded', 'Sales data has been downloaded for the specified period. Machines are now marked as active/inactive based on the specified period.')       

    ## creates the fee table section of the gui
    def create_fee_table(self):   
        self.ft_container = ttk.LabelFrame(self.root, text = 'Fees')
        self.ft_row = 2
        
        ## title row
        ft_fee = font.Font(family = 'Arial', size = 10, weight = 'bold')
        ttk.Label(self.ft_container, text = 'Name', font = ft_fee).grid(row = 0, column = 0)
        ttk.Label(self.ft_container, text = 'Amount', font = ft_fee).grid(row = 0, column = 1)
        ttk.Label(self.ft_container, text = 'Applied', font = ft_fee).grid(row = 0, column = 2)
        ttk.Label(self.ft_container, text = 'Value', font = ft_fee).grid(row = 0, column = 3)
        ttk.Label(self.ft_container, text = 'Action', font = ft_fee).grid(row = 0, column = 4)
        ttk.Button(self.ft_container, text = 'Clear fees', command = self.clear_fees).grid(row = 0, column = 5)
        
        ## new fee row
        self.f_name = StringVar()
        self.f_amount = DoubleVar()
        self.f_applied = StringVar()        
        ttk.Entry(self.ft_container, textvariable = self.f_name, width = 30).grid(row = 1, column = 0)
        ttk.Spinbox(self.ft_container, format = '%.2f', increment = 0.01, textvariable = self.f_amount).grid(row = 1, column = 1)
        ttk.Combobox(self.ft_container, values = ['% of total income (before other fees)', '% of total revenue (after other fees)', 'dollars per transaction', '% of CC sales income', 'dollars per CC sale', '% of cash sales income', 'dollars per cash sale', 'dollars per active DTU'], textvariable = self.f_applied, width = 30).grid(row = 1, column = 2)
        ttk.Button(self.ft_container, text = 'Add', command = self.commit_fee).grid(row = 1, column = 3)
        
        self.ft_container.grid(row = 2, column = 1, sticky = 'ew')
    
    ## clear out fees for a machine or operator
    def clear_fees(self, event = None):
        actor_id = self.get_selection()
        actor_obj = self.find_object_for_id(actor_id)
        
        ## we can't do anything if we dont know who it is
        if actor_id == None:
            messagebox.showerror('No selection', 'Select a machine or operator before trying to delete fees')
            return
            
        ## check if we're doing this to an operator. if so, target all machines
        ## under it
        targets = []
        if actor_obj.type == 'operator':
            targets = actor_obj.get_machines(recursive = True)
        ## otherwise just make the target the single machine
        else:
            targets = [actor_obj]
            
        ## add it to the fee list for all targets
        for actor_single in targets:
            actor_single.fees = []

        ## tell the user about it
        messagebox.showinfo('Cleared fees', 'Cleared fees for ' + str(len(targets)) + ' machines')
    
    
    ## called by the add button. adds the fee to the current object
    def commit_fee(self, event = None):
        global machine_list
        
        ## get all the info
        name = str(self.f_name.get())
        amount = float(self.f_amount.get())
        applied = str(self.f_applied.get())
        actor_id = self.get_selection()
        actor_obj = self.find_object_for_id(actor_id)
        
        ## we can't do anything if we dont know who it is
        if actor_id == None:
            messagebox.showerror('No selection', 'Select a machine or operator before trying to add new fees')
            return        
        
        ## check if we're doing this to an operator. if so, target all machines
        ## under it
        targets = []
        if actor_obj.type == 'operator':
            targets = actor_obj.get_children(recursive = True)
            
        ## for machines, just do them. for ops, add them to the list
        targets.append(actor_obj)
                  
        ## add it to the fee list for all targets
        for actor_single in targets:
            ## make the fee object. we need a new object for every actor to
            ## ensure independent calculation
            fobj = Fee(actor_obj, name, amount, applied)
            ## add the fee to the actor object
            actor_single.fees.append(fobj)
        
        ## add it to the GUI
        self.add_fee_row(targets, fobj)
        
        ## clear out the input variables
        self.f_name.set('')
        self.f_amount.set('')
        self.f_applied.set('')
        self.root.update()
    
    ## remove a row from the fee table
    def remove_fee_row(self, obj_list, fee_obj, delrow):
        ## remove the fee from all affected actors
        for actor in obj_list:
            actor.fees.remove(fee_obj)
    
        ## get all widgets on the row...
        for w in list(self.ft_container.grid_slaves(row = delrow)):
            ## ...and remove them
            w.grid_forget()
    
    ## populate the fee list
    def populate_fees(self):
        actor_id = self.get_selection()
        actor_obj = self.find_object_for_id(actor_id)
        
        ## clear the old fees first
        for i in range(2, self.ft_row+1):
            ## get all widgets on the row...
            for w in list(self.ft_container.grid_slaves(row = i)):
                ## ...and remove them
                w.grid_forget()
        
        ## we can't do anything if we dont know who it is
        if actor_id == None:
            return
            
        ## iterate through the fees
        for fobj in actor_obj.fees:
            ## and add them to the list
            self.add_fee_row([actor_obj], fobj)
    
    ## adds existing fee to table
    def add_fee_row(self, obj_list, fee_obj):
        ## get the fee attributes
        name = fee_obj.name
        amount = fee_obj.amount
        applied = fee_obj.applied
        
        ## create a deep copy of the row for later reference
        row = copy.deepcopy(self.ft_row)
        
        ## add the fee row
        ttk.Label(self.ft_container, text = name).grid(row = self.ft_row, column = 0)
        ttk.Label(self.ft_container, text = amount).grid(row = self.ft_row, column = 1)
        ttk.Label(self.ft_container, text = fee_obj.convert_name(applied)).grid(row = self.ft_row, column = 2)        
        ventry = ttk.Entry(self.ft_container)
        ventry.grid(row = self.ft_row, column = 3)
        ttk.Button(self.ft_container, text = 'Remove', command = lambda x: self.remove_fee_row(obj_list, fee_obj, row)).grid(row = self.ft_row, column = 4)        
        self.ft_row += 1
        
        ## put in the fee value then make it read only
        ventry.insert(0, self.display_money(fee_obj.calculate(actor = self.find_object_for_id(self.get_selection()))))
        ventry.configure(state = 'readonly')
               
        self.root.update()
        
        
## Class for outputting information as HTML
class HTML():
    ## Class initialisation. Pass it the Nayax object being used
    def __init__(self, nayax):
        self.nayax = nayax
    
    ## returns html header code
    def header(self, title):
        html = '<!DOCTYPE html>\n<html><head>\n<title>' + str(title) + '</title>'
        html += '<style type="text/css">\n'
        html += 'table {border-collapse: collapse;}\n'
        html += 'table tr * {border: 1px solid #000000;}\n'
        html += 'body {font-family: Arial;}\n'
        html += '</style>'
        html += '</head><body>'
        return html
    
    ## returns html footer code
    def footer(self):
        return '</body></html>'
    
    ## save a file
    def save_file(self, file_path, file_content):
        try:
            file_path = os.path.abspath(file_path)
        except:
            raise RuntimeError('Could not determine save path')
        
        ## open the file and write to it
        file_socket = open(file_path, 'w')
        file_socket.write(file_content)
        file_socket.flush()
        file_socket.close()        
    
    ## makes a report for the selected machine or all machines under the
    ## selected op
    def machine_info_report(self, operator):        
        html = self.header(title = 'Machine information report')
    
        ## targets for info are the current actor and all descendents
        targets = [operator]
        targets.extend(operator.get_children(recursive = True))
        
        html += '<table>'
        
        ## get info for each actor
        for actor in targets:
            ## for ops, we just show the name
            if actor.type == 'operator':
                html += '</table>\n<h1>' + actor.name + '</h1>'
                html += '<table><tr><th>Name</th><th>Device type</th><th>DTU serial</th><th>VPOS serial</th><th>SIM serial</th><th>RSSI</th><th>DTU firmware</th><th>VPOS firmware</th></tr>'
            ## for machines, we show a table of info
            elif actor.type == 'machine':
                html += '<tr><td>' + actor.name + '</td>'
                
                ## say if it's a VPOS touch
                if actor.is_vpos_touch() == True:
                    html += '<td>VPOS touch</td>'
                    
                ## if it's not a VPOS touch,it's a DTU+VPOS
                else:
                    html += '<td>DTU + VPOS</td>'
                
                html += '<td>' + str(actor.dtu) + '</td>'
                html += '<td>' + str(actor.vpos) + '</td>'
                html += '<td>' + str(actor.sim) + '</td>'
                
                ## correlate RSSI to performance
                if actor.rssi == None:
                    rssi = 'Unknown'
                elif int(actor.rssi) < 7:
                    rssi = str(actor.rssi) + ' (Unusable)'
                elif int(actor.rssi) < 11:
                    rssi = str(actor.rssi) + ' (Poor)'
                elif int(actor.rssi) < 15:
                    rssi = str(actor.rssi) + ' (Average)'
                elif int(actor.rssi) < 20:
                    rssi = str(actor.rssi) + ' (Good)'
                elif int(actor.rssi) != 31:
                    rssi = str(actor.rssi) + ' (Excellent)'
                else:
                    rssi = str(actor.rssi) + ' (Perfect or error)'
                    
                html += '<td>' + rssi + '</td>'
                
                html += '<td>' + str(actor.fw_dtu) + '</td>'
                html += '<td>' + str(actor.fw_vpos) + '</td></tr>'           

        html += '</table>'
        
        ## add the footer
        html += self.footer()
        
        ## return the generated html
        return html
        
    ## make a report for fees for the selected op/machine
    def machine_sales_report(self, operator):        
        html = self.header(title = 'Machine sales report')
    
        ## targets for info are the current actor and all descendents
        targets = [operator]
        targets.extend(operator.get_children(recursive = True))
        
        ## create the overall variables
        overall_cash_count, overall_cash_amount = operator.get_cash_sales()
        overall_card_count, overall_card_amount = operator.get_card_sales()
        overall_refund = 0
        overall_fees = []
        
        ## work out the fees       
        for actor in targets:
            ## for ops
            if actor.type == 'operator':
                ## go through its fees
                for fee in actor.fees:
                    ## see if it is an existing fee
                    for existing in overall_fees:
                        ## if it's existing, add the value of this one to it
                        if existing.compare(fee) == True:
                            existing.value += fee.calculate(actor = actor)
                        ## if not, add it to the list
                        else:
                            overall_fees.append(fee)
            ## for machines
            else:
                overall_fees = copy.deepcopy(actor.fees)
        
        ## table head and summary
        html += '<h1>' + str(actor.name) + '</h1>'
        html += '<table>'
        html += '<tr><th>Item</th><th>Applied</th><th>Rate</th><th>Value</th></tr>'
        html += '<tr><td>Total sales</td><td>&nbsp;</td><td>&nbsp;</td><td>$' + str(overall_cash_amount + overall_card_amount) + ' (' + str(overall_cash_count + overall_card_count) + ' sales)</td></tr>'
        html += '<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>'
        html += '<tr><td>Cash sales</td><td>&nbsp;</td><td>&nbsp;</td><td>$' + str(overall_cash_amount) + ' (' + str(overall_cash_count) + ' sales)</td></tr>'
        html += '<tr><td>Card sales</td><td>&nbsp;</td><td>&nbsp;</td><td>$' + str(overall_card_amount) + ' (' + str(overall_card_count) + ' sales)</td></tr>'
        
        ## fees
        for fobj in overall_fees:
            html += '<tr><td>' + fobj.name + '</td><td>' + fobj.applied + '</td><td>' + fobj.rate + '</td><td>-$' + fobj.value + '</td></tr>'
            
        ## take off cash sales - they took that
        html += '<tr><td>Cash taken by operator</td><td>&nbsp;</td><td>&nbsp;</td><td>$' + str(overall_cash_amount) + ' (' + str(overall_cash_count) + ' sales)</td></tr>'
                
        html += '</table>'
        
        ## add the footer
        html += self.footer()
        
        ## return the generated html
        return html
    
ui = GUI()
ui.run()        
        
