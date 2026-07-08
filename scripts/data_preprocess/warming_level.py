import pandas as pd

# Read file
filename = r'./data/cmip6_warming_levels_all_ens_1850_1900.csv'
df = pd.read_csv(filename, comment='#', sep=r",\s*", engine='python')

# Define options
ensemble = 'r1i1p1f1'
scenario = 'ssp370'
level = 3

# Find start and end years
df_filt = df[
    (df['ensemble'] == ensemble) & \
    (df['exp'] == scenario) & \
    (df['warming_level'] == level)
]

# Find midpoint year
df_filt['mid_year'] = (df['start_year'] + df['end_year']) // 2 + 1
print(df_filt['mid_year'].mean())