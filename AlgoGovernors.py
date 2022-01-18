"""Deprecated script! Going to remove this in hopefully the near future."""
import requests
from bs4 import BeautifulSoup as soup
import re
import SQLiteFunctions as SQL
import time
import WebScraping
import settings
from Governance import FetchGovernorData, Governor, get_link_data

main_url = settings.main_url
start_url = settings.start_url

headers = {'User-Agent': 'Mozilla/5.0'}
algo_request = requests.get(start_url, headers=headers)
bsoup = soup(algo_request.content, 'html.parser')
all_text = bsoup.text.replace('"', '')
'''
Classes and functions for scraping and storing algorand wallet data
'''


class Node(object):
    def __init__(self, link=None, list_of_governors=None, next_node=None, previous_node=None):
        self.link = link
        self.list_of_governors = list_of_governors
        self.next_node = next_node
        self.previous_node = previous_node

    def get_data(self):
        return self.link, self.list_of_governors

    def get_next(self):
        return self.next_node

    def set_next(self, new_next):
        self.next_node = new_next


class LinkedList(object):
    def __init__(self, head=None):
        self.head = head

    def insert(self, link, governors):
        # declare new node to add to head of linked list
        new_node = Node(link=link, list_of_governors=governors)
        # set old head node as the new node's next and previous for new node as none
        new_node.set_next(self.head)
        new_node.previous_node = None
        # now set the new head as new nodesize(self):
        if self.head is not None:
            self.head.previous_node = new_node
        self.head = new_node

    def size(self):
        current = self.head
        count = 0
        while current:
            count += 1
            current = current.get_next()
        return count

    def search(self, data):
        current = self.head
        found = False
        while current and found is False:
            if current.get_data() == data:
                found = True
            else:
                current = current.get_next()
        if current is None:
            raise ValueError('Data not found in list.')
        return current

    def delete(self, data):
        current = self.head
        previous = None
        found = False
        while current and found is False:
            if current.get_data() == data:
                found = True
            else:
                previous = current
                current = current.get_next()
        if current is None:
            raise ValueError('Data not found in list.')
        if previous is None:
            self.head = current.get_next()
        else:
            previous.set_next(current.get_next())
        return current







# Parameters for a table of governor data
governor_params = [SQL.SQLParameter(var_type='integer', name='id', constraint='NOT NULL', is_primary=True),
                   SQL.SQLParameter(var_type='integer', name='account_id', constraint='NOT NULL'),
                   SQL.SQLParameter(var_type='text', name='address', constraint='NOT NULL'),
                   SQL.SQLParameter(var_type='text', name='committed_algo', constraint='NOT NULL'),
                   SQL.SQLParameter(var_type='integer', name='is_eligible', constraint='NOT NULL'),
                   SQL.SQLParameter(var_type='text', name='reason'),
                   SQL.SQLParameter(var_type='text', name='registration_date'),
                   SQL.SQLParameter(var_type='integer', name='session_count'),
                   SQL.SQLParameter(var_type='integer', name='link_count', constraint='NOT NULL')]

'''First test our link handler'''
link_handler = WebScraping.LinkHandler()
link_handler.start_url = start_url
link_handler.headers = headers
list_of_links = LinkedList()
algo_db = SQL.SqliteDatabase()
algo_db.connect_database(r'C:/Users/jnwag/OneDrive/Documents/GitHub/AlgorandGovernance/AlgoDB.db')
table_headers = ['id', 'account_id', 'address', 'committed_algo', 'is_eligible', 'reason', 'registration_date',
                 'session_count', 'link_count']
link_counter = 0

'''Get data from each website and insert into database table'''
# initialize data from start_url
link_data = link_handler.parse_link_request()
while link_handler.navigate_link() is not None:
    governors = get_link_data(text=link_data)
    # list_of_links.insert(link=next_link, governors=governors)
    start = time.time()
    for governor in governors:
        governor.link_id = link_counter
        is_row = algo_db.check_row(governor.id, table_name='Governors')
        if not is_row:
            row = [governor.id, governor.account, governor.address, governor.committed_algo, governor.is_eligible,
                   governor.not_eligible_reason, governor.registration_datetime, governor.vote_session_count,
                   governor.link_id]
            algo_db.sqlite_insert(table='Governors', num_vals='?,?,?,?,?,?,?,?,?', row=row)
            print('Insert successful.')
        else:
            print('Row already exists in database. Skipping to next possible entry...')
    end = time.time()
    print('Time taken to parse link: ' + str(end - start) + ' seconds')
    link_counter += 1
    print('Navigating to next link...')
    try:
        next_link = link_handler.get_next_link(link_data)
    except:
        print('Error?')
    link_data = link_handler.parse_link_request(link=next_link)

algo_db.connection.close()
print(list_of_links)
