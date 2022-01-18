"""This file is a container for global variables that are integral to a few key functions for this project."""

# Change these url's to update governors database
main_url = 'https://governance.algorand.foundation/governance-period-1/governors'
start_url = 'https://governance.algorand.foundation/api/periods/governance-period-1/governors/?cursor=cj0xJnA9MjAyMS0xMC0xNCsxNSUzQTU4JTNBMzQuMjM0MDA3JTJCMDAlM0EwMA%3D%3D&ordering=-registration_datetime&paginator=cursor'

# Webscraping headers
headers = {'User-Agent': 'Mozilla/5.0'}

# SQL Table Headers
table_headers = ['id', 'account_id', 'address', 'committed_algo', 'is_eligible', 'reason', 'registration_date',
                 'session_count', 'link_count']

# URL's pertaining to voting results:
measure1A_start = 'https://governance.algorand.foundation/api/topic-options/3424510351040185926/votes/?limit=20'
measure1B_start = 'https://governance.algorand.foundation/api/topic-options/3424510351040612964/votes/?limit=20'
measure2_start = ''

# Database path
database = r'C:/Users/jnwag/OneDrive/Documents/GitHub/AlgorandGovernance/AlgoDB.db'
