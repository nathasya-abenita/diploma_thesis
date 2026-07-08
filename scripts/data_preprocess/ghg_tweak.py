import pandas as pd

# Define years of interest (ratio is year2 divided by year1)
year1, year2 = 2031, 1875

# Read data
df_hist = pd.read_excel('./data/SUPPLEMENT_DataTables_Meinshausen_6May2020.xlsx', 
                        sheet_name='T2 - History Year 1750 to 2014',
                        skiprows=8)

df_ssp = pd.read_excel('./data/SUPPLEMENT_DataTables_Meinshausen_6May2020.xlsx', 
                        sheet_name="T6 - SSP3-7.0 ",
                        skiprows=8)


# Define greenhouse gas names
ghg_name_list = ['Gas', 'CO2', 'CH4', 'N2O', 'CFC11', 'CFC12']
print(df_hist[ghg_name_list][3:])

# Filter to assessed GHG
df_hist = df_hist[ghg_name_list][3:].rename(columns={'Gas':'Year'})
df_ssp = df_ssp[ghg_name_list][3:].rename(columns={'Gas':'Year'})
df = pd.concat([df_hist, df_ssp])
df = df.set_index(keys='Year')

# Filter to chosen years
ratio = df.loc[year2] / df.loc[year1]
print(df.loc[[year1, year2]])
print(ratio)