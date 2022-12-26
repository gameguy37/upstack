import datetime
import os

import pandas as pd


# create dataframes from tab-separated (tsv) files
rpm_raw = pd.read_csv('rpm_data.tsv', sep='\t')
sfdc_raw = pd.read_csv('sfdc_data.tsv', sep='\t')

# convert all date columns to YYYYMM format
rpm_raw.Added = pd.to_datetime(rpm_raw.Added).dt.strftime('%Y%m')
sfdc_raw.Date = pd.to_datetime(sfdc_raw.Date).dt.strftime('%Y%m')

# clean up revenue data by converting from strings to float and handling negative values (written in parentheses)
rpm_raw['Net billed'] = rpm_raw['Net billed'].replace('[\$,)]', '', regex=True).replace('[(]', '-', regex=True).astype(float)
sfdc_raw['Amount'] = sfdc_raw['Amount'].replace('[\$,)]', '', regex=True).replace('[(]', '-', regex=True).astype(float)

# group the dataframes to the appropriate level of granularity and sum the named value columns ('Net billed' and 'Amount')
rpm_grouped = rpm_raw.groupby(['Agency', 'Added'], as_index=False).agg({'Net billed': 'sum'})
sfdc_grouped = sfdc_raw.groupby(['Advisory Partner', 'Date'], as_index=False).agg({'Amount': 'sum'})

# rename the dataframes to match requested column names in README file
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

# answer Analytical Questions dynamically
print('Analytical Questions\n')

print('1. How many Suppliers were billed in August of 2022?')
august_2022 = sfdc_grouped[sfdc_grouped['Month'] == '202208']
print(f'''Number of Suppliers billed in August of 2022 = {len(august_2022)}\nSuppliers: {august_2022['Supplier'].values.tolist()}\n''')

print('2. Which Supplier in which month had the largest positive discrepancy between what was registered and what was billed?')
diff_df = merged_df.copy(deep=True)
diff_df['diff'] = diff_df['Registered'] - diff_df['Billed']
diff_df = diff_df.sort_values(by=['diff'], ascending=False).reset_index(drop=True)
if diff_df.at[0, 'diff'] != 0:
    print(f'''Supplier: {diff_df.at[0, 'Supplier']}\nMonth: {diff_df.at[0, 'Month']}''')
else:
    print('There are no *positive* discrepancies (Registered > Billed). All Suppliers for all Months either have (Billed = Registered) OR (Billed > Registered)')
