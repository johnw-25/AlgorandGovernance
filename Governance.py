import re
import hashlib


class FetchGovernorData:
    """This is a container for helper methods that fetch governor data"""

    @staticmethod
    def fetch_ids(text):
        all_ids = re.findall(r'[\[,]{id:\d{19}', text, re.MULTILINE)
        all_ids = [single_id.replace('id:', '') for single_id in all_ids]
        all_ids = [single_id.replace('[{', '') for single_id in all_ids]
        all_ids = [single_id.replace(',{', '') for single_id in all_ids]
        ids = list(map(int, all_ids))
        return ids

    @staticmethod
    def fetch_acct_ids(text):
        all_ids = re.findall(r'account:{id:\d{19}', text, re.MULTILINE)
        all_ids = [single_id.replace('account:{id:', '') for single_id in all_ids]
        ids = list(map(int, all_ids))
        return ids

    @staticmethod
    def fetch_tx_ids(text):
        all_ids = re.findall(r',transaction_id:\w{52}', text, re.MULTILINE)
        all_ids = [single_id.replace(',transaction_id:', '') for single_id in all_ids]
        tx_ids = list(map(str, all_ids))
        return tx_ids

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
        eligible_list = re.findall(r"is_eligible:\w*", text, re.MULTILINE)
        eligible_list = [eligibility.replace('is_eligible:', '') for eligibility in eligible_list]
        eligible_list = [1 if i == 'true' else 0 for i in eligible_list]
        return eligible_list

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
        self.tx_id = None
        self.address = None
        self.committed_algo = None
        self.is_eligible = None
        self.not_eligible_reason = None
        self.registration_datetime = None
        self.vote_session_count = None
        self.link_where_found = None
        self.link_id = None
        self.voting_result = None


def get_link_data(text):
    ids = FetchGovernorData.fetch_ids(text)
    account_ids = FetchGovernorData.fetch_acct_ids(text)
    tx_ids = FetchGovernorData.fetch_tx_ids(text)
    addresses = FetchGovernorData.fetch_addresses(text)
    algo = FetchGovernorData.fetch_committed_algo(text)
    eligibility = FetchGovernorData.fetch_eligibility(text)
    all_reasons = FetchGovernorData.fetch_eligibility_reason(text)
    reg_dates = FetchGovernorData.fetch_registration_date(text)

    '''Don't need this currently.
    session_counts = FetchGovernorData.fetch_session_count(text)'''

    governors = list()
    for i in range(len(ids)):
        governor = Governor()
        governor.id = ids[i]
        governor.account = account_ids[i]
        governor.tx_id = tx_ids[i]
        governor.address = addresses[i]
        governor.committed_algo = algo[i]
        governor.is_eligible = eligibility[i]
        governor.not_eligible_reason = all_reasons[i]
        governor.registration_datetime = reg_dates[i]
        governors.append(governor)
    return governors


def insert_voting_results(algo_db=None, link_handler=None, vote=None, table_name=None):
    # Large function that handles database insertion of governor data for a voting session. Could probably break this down into smaller functions.
    if algo_db is None or link_handler is None:
        return

    link_data = link_handler.parse_link_request(link=link_handler.start_url)
    link_counter = 0
    while link_data is not None:
        governors = get_link_data(text=link_data)
        for governor in governors:
            # Use features of governance transaction to hash a string (P-key) for the sqlite database.
            hstring = governor.tx_id + governor.registration_datetime + str(governor.is_eligible) + str(link_counter)
            hash_id = hashlib.sha1(hstring.encode("utf-8")).hexdigest()

            # Check for existence of data in SQLite using the hash
            is_row = algo_db.check_row(hash_id, table_name=table_name, col_name='hash_id')
            governor.voting_result = vote
            governor.link_id = link_counter
            if not is_row:
                # Insert into database if data is new
                row = [hash_id, governor.tx_id, governor.id, governor.account, governor.address,
                       governor.committed_algo, governor.is_eligible,
                       governor.not_eligible_reason, governor.registration_datetime, governor.link_id,
                       governor.voting_result]
                algo_db.sqlite_insert(table=table_name, num_vals='?,?,?,?,?,?,?,?,?,?,?', row=row)
            else:
                print('Row already exists in database. Skipping to next possible entry...')

        print('Navigating to next link...')
        link_counter += 1

        # Grab next link and the data from it
        next_link = link_handler.get_next_link(link_data)
        link_data = link_handler.parse_link_request(link=next_link)
