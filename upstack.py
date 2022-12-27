import datetime
import os

import pandas as pd


# create dataframes from tab-separated (tsv) files
rpm_raw = pd.read_csv('rpm_data.tsv', sep='\t')
sfdc_raw = pd.read_csv('sfdc_data.tsv', sep='\t')

# convert all date columns to YYYYMM format
rpm_raw.Added = pd.to_datetime(rpm_raw.Added).dt.strftime('%Y%m')
sfdc_raw.Date = pd.to_datetime(sfdc_raw.Date).dt.strftime('%Y%m')

# clean up revenue data by converting from strings to float and handling negative reported values (written in parentheses)
rpm_raw['Net billed'] = rpm_raw['Net billed'].replace('[\$,)]', '', regex=True).replace('[(]', '-', regex=True).astype(float)
sfdc_raw['Amount'] = sfdc_raw['Amount'].replace('[\$,)]', '', regex=True).replace('[(]', '-', regex=True).astype(float)

# group the dataframes to the appropriate level of granularity and sum the named value columns ('Net billed' and 'Amount')
rpm_grouped = rpm_raw.groupby(['Agency', 'Added'], as_index=False).agg({'Net billed': 'sum'})
sfdc_grouped = sfdc_raw.groupby(['Advisory Partner', 'Date'], as_index=False).agg({'Amount': 'sum'})

# rename the grouped dataframes to match requested column names in Upstack coding challenge README file
column_rename = {
    'Added': 'Month',
    'Advisory Partner': 'Supplier',
    'Agency': 'Supplier',
    'Amount': 'Registered',
    'Date': 'Month',
    'Net billed': 'Billed'
}
for df in [rpm_grouped, sfdc_grouped]:
    df.rename(columns=column_rename, inplace=True)

# join the dataframes into one using common columns 'Supplier' and 'Month' then reorder to match README
merged_df = rpm_grouped.merge(sfdc_grouped, on=['Supplier', 'Month'])
merged_df = merged_df[['Supplier', 'Registered', 'Billed', 'Month']]

# create timestamped output CSV file from merged dataframe and store in ./output folder
cwd = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(cwd, 'output', f'{datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")}.csv')
merged_df.to_csv(file_path, index=False)


# Answer Analytical Questions dynamically and print to console when script is executed.
print('Analytical Questions\n')

print('1. How many Suppliers were billed in August of 2022?')
august_2022 = rpm_grouped[rpm_grouped['Month'] == '202208']
print(f'''Number of Suppliers billed in August of 2022 = {len(august_2022)}\nSuppliers: {august_2022['Supplier'].values.tolist()}\n''')

print('2. Which Supplier in which month had the largest positive discrepancy between what was registered and what was billed?')
diff_df = merged_df.copy(deep=True)
diff_df['diff'] = diff_df['Registered'] - diff_df['Billed']
diff_df = diff_df.sort_values(by=['diff'], ascending=False).reset_index(drop=True)
if diff_df.at[0, 'diff'] != 0:
    print(f'''Supplier: {diff_df.at[0, 'Supplier']}\nMonth: {diff_df.at[0, 'Month']}''')
else:
    print('There are no *positive* discrepancies (where Registered > Billed). All Suppliers for all Months either have (Billed = Registered) OR (Billed > Registered)')


# Written Questions answered below as comments

# 1. What questions do you have for the business owner of this data?

'''
Do you foresee any future changes to the data that is currently being sent? Specifically in terms of granularity, column names, data types, and the like?
    Having knowledge of future changes to the data would allow the script to be refactored in a way that is futureproof before those changes
    create issues with data digestion and cause errors.

Could this data be aggregated first on the provider's end and then sent to Upstack?
    Much of the data currently being sent to Upstack is not necessary for the end product of this script. item IDs, agencies, customer names, etc. are
    simply being lost when the data is aggregated and rolled up into only three values (supplier, month, and $$$).
    Aggregating the data first would mean that smaller data files could be sent, reducing bandwith/overhead and would
    allow this script to be much more streamlined.

P.S. I appreciate the lightheartedness of the names used in the dummy data for this coding challenge (references to Spiderman, The Office, Law & Order, KFC, etc.)
'''

# 2. What technical work should be done for your solution before it can be deployed?

'''
The solution needs to be "wrapped" in the common syntax used in AWS lambda functions. The existing functionality
should be wrapped in a function called lambda_handler that passes in an "event" and a "context" at runtime. 
The two data files will likely be passed into the function as encoded objects in the body of the
passed-in event and they will need to be accessed using the json library, decoded, and made available to the
interior script. The current implementation (utilizing the pandas to_csv() method) assumes the TSV files will be
available at runtime in the same directory as the script itself for simplicity. Additionally, the production output
files would likely be stored in AWS S3 rather than saved to a local ./output directory.

Print statements near the end of this script that answer the provided Analytical Questions in a dynamic fashion would
most likely be replaced with some sort of actual logging (to DataDog or equivalent). Additionally, the results (or at
least a summary of the results) could be inserted into a database table so that a record of each run (once every 6 hours)
is retained in perpetuity and we can look back to see when SFDC data did not match RPM data.

There is a lot more that could be done in order to alert the end user of failures. Namely, error handling via try/except
blocks and being sure the script will alert and fail "loudly" in the event that data cannot be properly digested. For instance,
if data begins coming through in a slightly different format that cannot be properly handled using the existing regular
expressions or if the data provider decides to change the data they are sending (names of columns, data types, etc.).
'''
