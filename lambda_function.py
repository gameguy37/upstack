import pandas as pd

# create dataframes from tab-separated (tsv) files
rpm_raw = pd.read_csv('rpm_data.tsv', sep='\t')
sfdc_raw = pd.read_csv('sfdc_data.tsv', sep='\t')

# convert all dates to YYMMMM format
rpm_raw.Added = pd.to_datetime(rpm_raw.Added).dt.strftime('%Y%m')
sfdc_raw.Date = pd.to_datetime(sfdc_raw.Date).dt.strftime('%Y%m')

# clean up revenue data by converting from strings to float and handling negative values (written in parentheses)
rpm_raw['Net billed'] = rpm_raw['Net billed'].replace('[\$,)]', '', regex=True).replace('[(]', '-', regex=True).astype(float)
sfdc_raw['Amount'] = sfdc_raw['Amount'].replace('[\$,)]', '', regex=True).replace('[(]', '-', regex=True).astype(float)

# group the dataframes to the appropriate level of granularity
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

# join the dataframes
merged_df = rpm_grouped.merge(sfdc_grouped, on=['Supplier', 'Month'])

# merged_df['diff'] = merged_df['Registered'] - merged_df['Billed']
# merged_df.sort_values(by=['diff'])
print(merged_df)

# def lambda_handler(event, context):
#
#     print(event)
#     print(context)
#     print('hello')

