import requests
from bs4 import BeautifulSoup as soup
import re
import SQLiteFunctions as SQL
import time

main_url = 'https://governance.algorand.foundation/governance-period-1/governors'
start_url = 'https://governance.algorand.foundation/api/periods/governance-period-1/governors/?cursor=cj0xJnA9MjAyMS0xMC0xNCsxNSUzQTU4JTNBMzQuMjM0MDA3JTJCMDAlM0EwMA%3D%3D&ordering=-registration_datetime&paginator=cursor'

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


class LinkHandler:
    """Also known as the link fondler; this fondles all of the links"""

    def __init__(self):
        self.start_url = 'https://governance.algorand.foundation/api/periods/governance-period-1/governors/?cursor=cj0xJnA9MjAyMS0xMC0xNCsxNSUzQTU4JTNBMzQuMjM0MDA3JTJCMDAlM0EwMA%3D%3D&ordering=-registration_datetime&paginator=cursor'
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def navigate_link(self, nagivate_to=None):
        """Try/except block to catch DNS failure/other network failures"""
        if nagivate_to is None:
            nagivate_to = self.start_url
        try:
            return requests.get(nagivate_to, headers=headers)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def parse_link_request(self, link=None):
        if link is None:
            request = self.navigate_link()
        else:
            request = self.navigate_link(link)
        bsoup = soup(request.content, 'html.parser')
        return bsoup.text.replace('"', '')

    def get_next_link(self, text):
        split_text = text.split(',')
        raw_link = split_text[0]
        protocol = re.findall(r'(\w+)://', raw_link)

        if protocol:
            curated_link = raw_link.split('next:')
            curated_link = curated_link[1]
        else:
            print('Could not identify next link.')
            return
        #raw_link = re.findall(r'next:.*&paginator=cursor', text)

        '''try:
            raw_link = raw_link[0]
        except:
            print('stop')
        link = raw_link.replace('next:', '')
        return link'''
        return curated_link

    @staticmethod
    def get_link_data(text):
        all_ids = FetchGovernorData.fetch_ids(text)
        ids = all_ids[0]
        account_ids = all_ids[1]
        addresses = FetchGovernorData.fetch_addresses(text)
        algo = FetchGovernorData.fetch_committed_algo(text)
        eligibilities = FetchGovernorData.fetch_eligibility(text)
        all_reasons = FetchGovernorData.fetch_eligibility_reason(text)
        reg_dates = FetchGovernorData.fetch_registration_date(text)
        session_counts = FetchGovernorData.fetch_session_count(text)
        governors = list()
        for i in range(len(ids)):
            governor = Governor()
            governor.id = ids[i]
            governor.account = account_ids[i]
            governor.address = addresses[i]
            governor.committed_algo = algo[i]
            governor.is_eligible = eligibilities[i]
            governor.not_eligible_reason = all_reasons[i]
            governor.registration_datetime = reg_dates[i]
            governor.vote_session_count = session_counts[i]
            governors.append(governor)
        return governors


class FetchGovernorData:
    """This is a container for helper methods that fetch governor data"""

    @staticmethod
    def fetch_ids(text):
        all_ids = re.findall(r"id:\d*", text, re.MULTILINE)
        if len(all_ids) % 2 != 0:
            raise ValueError('Error parsing ids')
        all_ids = [single_id.replace('id:', '') for single_id in all_ids]
        ids = list(map(int, all_ids[0:len(all_ids):2]))
        account_ids = list(map(int, all_ids[1:len(all_ids):2]))
        return ids, account_ids

    @staticmethod
    def fetch_addresses(text):
        addresses = re.findall(r"address:\w*", text, re.MULTILINE)
        addresses = [address.replace('address:', '') for address in addresses]
        return addresses

    @staticmethod
    def fetch_committed_algo(text):
        algos = re.findall(r"committed_algo_amount:\d*", text, re.MULTILINE)
        algos = list(map(int, [algo.replace('committed_algo_amount:', '') for algo in algos]))
        return algos

    @staticmethod
    def fetch_eligibility(text):
        eligibile_list = re.findall(r"is_eligible:\w*", text, re.MULTILINE)
        eligibile_list = [eligibility.replace('is_eligible:', '') for eligibility in eligibile_list]
        eligibile_list = [1 if i == 'true' else 0 for i in eligibile_list]
        return eligibile_list

    @staticmethod
    def fetch_eligibility_reason(text):
        all_reasons = re.findall(r"not_eligible_reason:\w*", text, re.MULTILINE)
        all_reasons = [reason.replace('not_eligible_reason:', '') for reason in all_reasons]
        return all_reasons

    @staticmethod
    def fetch_registration_date(text):
        all_dates = re.findall(r"registration_datetime:\d{4}-\d{2}-\d{2}", text, re.MULTILINE)
        all_dates = [date.replace('registration_datetime:', '') for date in all_dates]
        return all_dates

    @staticmethod
    def fetch_session_count(text):
        all_counts = re.findall(r"voted_voting_session_count:\d*", text, re.MULTILINE)
        all_counts = list(map(int, [count.replace('voted_voting_session_count:', '') for count in all_counts]))
        return all_counts


class Governor:
    def __init__(self):
        self.id = None
        self.account = None
        self.address = None
        self.committed_algo = None
        self.is_eligible = None
        self.not_eligible_reason = None
        self.registration_datetime = None
        self.vote_session_count = None
        self.link_where_found = None
        self.link_id = None


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
link_handler = LinkHandler()
link_handler.start_url = start_url
link_handler.headers = headers
create_table_cmd = r'''CREATE TABLE IF NOT EXISTS Bananas (id integer PRIMARY KEY, account_id integer NOT NULL, address text NOT NULL, committed_algo integer NOT NULL, is_eligible integer NOT NULL, reason text, registration_date text, session_count integer, link_count integer NOT NULL);'''
'''Establish connection to database'''
list_of_links = LinkedList()
algo_db = SQL.SqliteDatabase()
algo_db.connect_database(r'C:/Users/jnwag/OneDrive/Documents/GitHub/AlgorandGovernance/AlgoDB.db')
algo_db.execute_command(create_table_cmd)
table_headers = ['id', 'account_id', 'address', 'committed_algo', 'is_eligible', 'reason', 'registration_date',
                 'session_count', 'link_count']
link_counter = 0

'''Get data from each website and insert into database table'''
# initialize data from start_url
link_data = link_handler.parse_link_request()
while link_handler.navigate_link() is not None:
    governors = LinkHandler.get_link_data(text=link_data)
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
