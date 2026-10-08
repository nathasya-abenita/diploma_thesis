import pandas as pd

class GHG_tweak:

    def __init__ (self, models=None):
        # Open data
        self.df_ghg = self.open_ghg()
        self.df_gwl = self.open_warming_level()

        # Define assessed models
        if models is None:
            self.models = ['CESM2-WACCM', 'GFDL-ESM4', 'EC-Earth3', 'NorESM2-MM', 'EC-Earth3-Veg-LR', 'CESM2', 'MPI-ESM1-2-LR', 'EC-Earth3-Veg', 'IPSL-CM6A-LR', 'ACCESS-ESM1-5', 'TaiESM1', 'FGOALS-f3-L', 'INM-CM5-0', 'KACE-1-0-G', 'EC-Earth3-AerChem', 'FGOALS-g3', 'AWI-CM-1-1-MR', 'BCC-CSM2-MR', 'CanESM5', 'MRI-ESM2-0', 'CMCC-CM2-SR5', 'INM-CM4-8', 'MPI-ESM1-2-HR', 'ACCESS-CM2']
            # self.models = ["EC-Earth3-Veg",  "MPI-ESM1-2-HR",  "NorESM2-MM"]

    def open_ghg (self):
        # Read data
        df_hist = pd.read_excel('./data/SUPPLEMENT_DataTables_Meinshausen_6May2020.xlsx', 
                                sheet_name='T2 - History Year 1750 to 2014',
                                skiprows=8)

        df_ssp = pd.read_excel('./data/SUPPLEMENT_DataTables_Meinshausen_6May2020.xlsx', 
                                sheet_name="T6 - SSP3-7.0 ",
                                skiprows=8)

        # Define greenhouse gas names
        ghg_name_list = ['Gas', 'CO2', 'CH4', 'N2O', 'CFC11', 'CFC12']
        self.ghg_name_list = ghg_name_list[1:]

        # Filter to assessed GHG
        df_hist = df_hist[ghg_name_list][3:].rename(columns={'Gas':'Year'})
        df_ssp = df_ssp[ghg_name_list][3:].rename(columns={'Gas':'Year'})
        df = pd.concat([df_hist, df_ssp])
        df = df.set_index(keys='Year')
        return df

    def open_warming_level (self):
        filename = r'./data/cmip6_warming_levels_all_ens_1850_1900.csv'
        df = pd.read_csv(filename, comment='#', sep=r",\s*", engine='python')
        return df

    def compute_ghg_climatology (self, year_start, year_end):
        df_filt = self.df_ghg.loc[year_start : year_end ]
        print(df_filt.index)
        df_filt = df_filt.mean()
        return df_filt

    def compute_gwl_year (self, gwl : float):
        ensemble = 'r1i1p1f1'
        scenario = 'ssp370'
        # Find start and end years
        df = self.df_gwl
        df_filt = df[
            (df['ensemble'] == ensemble) & \
            (df['exp'] == scenario) & \
            (df['warming_level'] == gwl) & \
            (df['model'].isin(self.models))
        ]
        df_filt = df_filt.set_index(keys='model')
        return df_filt

    def compute_ghg_model (self, gwl):
        # Compile start and end year for all models
        df_gwl_year = self.compute_gwl_year(gwl)

        # Compute climatology for each model
        df_ghg_climatology = pd.DataFrame()
        for model in self.models:
            row = df_gwl_year.loc[model]
            df_clima_model = self.compute_ghg_climatology(row['start_year'], row['end_year'])
            df_ghg_climatology = pd.concat([df_ghg_climatology, df_clima_model], axis=1)

        # Add index
        df_ghg_climatology = df_ghg_climatology.transpose()
        df_ghg_climatology['model'] = self.models
        df_ghg_climatology = df_ghg_climatology.set_index(keys='model')
        return df_ghg_climatology

if __name__ == '__main__':
    tweak = GHG_tweak()

    # Compute baseline
    df_clima_baseline = tweak.compute_ghg_climatology(1850, 1900)
    # print(df_clima_baseline)

    # Compute factual period
    # df_clima_fac = tweak.compute_ghg_climatology(2010, 2029)
    df_clima_fac = tweak.compute_ghg_climatology(2005, 2024)
    # print(df_clima_fac)

    # Compute +1.5 degree and +3.0 degree GWL period
    df_clima_gwl_1_5 = tweak.compute_ghg_model(1.5).median()
    df_clima_gwl_3_0 = tweak.compute_ghg_model(3.0).median()

    # Construct DataFrame
    index_list = ['fac-PI', 'fac-GWL+1.5', 'fac-GWL+3.0']
    df = pd.DataFrame(index=tweak.ghg_name_list)
    df[index_list[0]] = df_clima_baseline / df_clima_fac
    df[index_list[1]] = df_clima_gwl_1_5 / df_clima_fac
    df[index_list[2]] = df_clima_gwl_3_0 / df_clima_fac
    df = df.astype("float")
    print(df.round(1))