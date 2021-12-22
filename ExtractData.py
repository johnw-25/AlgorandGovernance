import SQLiteFunctions as SQL
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# Create new database object and connect to database
algo_db = SQL.SqliteDatabase()
algo_db.connect_database(r'C:/Users/jnwag/OneDrive/Documents/GitHub/AlgorandGovernance/AlgoDB.db')
table_headers = ['id', 'account_id', 'address', 'committed_algo', 'is_eligible', 'reason', 'registration_date',
                 'session_count', 'link_count']

# Fetch governor data from db
test = algo_db.fetch_all('Governors')

# convert table data into dataframe and keep only the eligible users
df = pd.DataFrame(test, columns=table_headers)
eligible_df = df.drop(df[df.is_eligible == 0].index)

# Convert to numpy float array
all_algo = eligible_df.committed_algo.values
all_algo = np.array([all_algo])
all_algo = all_algo.astype(float)
algo_log = np.log10(all_algo)

# define edges for our hist bins
start = -1
stop = 14
num_samples = (stop - start) * 2
h_edges = np.linspace(-1, 14, num=num_samples)

# Bin committed algo based on min/max of data
hist, edges = np.histogram(algo_log, bins=h_edges)
#fig = plt.figure(figsize=(7, 3))

# Set some configurations for the chart
plt.figure(figsize=[10, 5])
plt.xlim(min(h_edges), max(h_edges))
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Edge Values', fontsize=20)
plt.ylabel('Histogram Values', fontsize=20)
plt.title('Histogram Chart', fontsize=25)

# Create the chart
plt.bar(h_edges[:-1], hist, width=0.5, color='blue')
# Display the chart

plt.show()
print('done')