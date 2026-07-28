import pandas as pd

# Define years of interest (ratio is year2 divided by year1)

# [To pre-industrial]
# year1, year2 = 2031, 1875 # ensemble
# year1, year2 = 2012, 1875 # EC-Earth3-Veg
# year1, year2 = 2035, 1875 # MPI-ESM1-2-HR
# year1, year2 = 2047, 1875 # NorESM2-MM
# [To warming]
# year1, year2 = 2031, 2077 # ensemble
# year1, year2 = 2012, 2058 # EC-Earth3-Veg
year1, year2 = 2035, 2082 # MPI-ESM1-2-HR
# year1, year2 = 2047, 2091 # NorESM2-MM

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