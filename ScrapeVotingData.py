import Governance
import SQLiteFunctions as SQL
import WebScraping
import settings
from Governance import get_link_data
import pandas as pd

# Generate http request using WebScraping and settings
algo_request = WebScraping.generate_request(settings.measure1A_start, settings.headers)
all_text = WebScraping.get_data(algo_request)
all_text = all_text.replace('"', '')

# Instantiate a link handler
link_handler = WebScraping.LinkHandler()
link_handler.start_url = settings.measure1A_start
link_handler.headers = settings.headers

# open database
algo_db = SQL.SqliteDatabase()
algo_db.connect_database(settings.database)

"""{all_data = algo_db.fetch_all('Measure1')
data_df = pd.DataFrame(all_data)
eligible_df = data_df.drop(data_df[data_df.iloc[:, 4] == 0].index)
dfA = data_df.drop(data_df[data_df.iloc[:, 8] == '"B"'].index)
dfB = eligible_df.drop(eligible_df[eligible_df.iloc[:, 8] == '"A"'].index)"""
# Step thru measure A votes first
# initialize data from start_url
Governance.insert_voting_results(algo_db=algo_db, link_handler=link_handler, vote='A', table_name='Measure1')

# B votes next!
link_handler.start_url = settings.measure1B_start
Governance.insert_voting_results(algo_db=algo_db, link_handler=link_handler, vote='B', table_name='Measure1')





