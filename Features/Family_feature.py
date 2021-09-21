import pandas as pd
import numpy as np
from pathing import filesets


def to_county(df: pd.DataFrame, county_name: str) -> pd.DataFrame:
    return df.loc[list(filter(lambda x: county_name in x, df.index))]


if __name__ == '__main__':
    low_end = 2012
    for year in range(low_end, 2018):
        print(year)
        county = 'Onondaga County'
        family_df = pd.read_csv(filesets.format(year=year) + 'Family income ' + str(year) + '.csv', na_values='N')
        index_name = family_df['Unnamed: 0'].loc[0]
        estimates = pd.Series(family_df.loc[0]).unique()[1:]
        family_df.drop(index=0, inplace=True)
        base_names = list(filter(lambda x: 'Unnamed' not in x, family_df.columns))
        family_index = pd.Series(list(map(str.strip, family_df['Unnamed: 0'])), name=index_name)
        family_df.drop(columns=['Unnamed: 0'], inplace=True)
        family_df.set_index(family_index, inplace=True)
        family_df = family_df.T
        workers_2_a = '2 workers husband and wife worked'
        workers_2_b = '2 workers other'
        workers_3_a = '3 or more workers husband and wife worked'
        workers_3_b = '3 or more workers other'
        family_df_2_a = family_df[workers_2_a].replace('-', 0).astype(float)
        family_df_2_b = family_df[workers_2_b].replace('-', 0).astype(float)
        family_df['2 Workers'] = np.round(family_df_2_a + family_df_2_b, 4)
        family_df_3_a = family_df[workers_3_a].replace('-', 0).astype(float)
        family_df_3_b = family_df[workers_3_b].replace('-', 0).astype(float)
        family_df['3+ Workers'] = np.round(family_df_3_a + family_df_3_b, 4)
        family_df.drop([workers_2_a, workers_2_b, workers_3_a, workers_3_b], axis=1, inplace=True)
        new_index = pd.Series([col + ': ' + estimate for col in base_names for estimate in estimates])
        family_df.set_index(new_index, inplace=True)
        family_df.to_csv(filesets.format(year=year) + 'Pandas Family income ' + str(year) + '.csv', na_rep='NA')
        print(family_df)
        print(any(pd.isna(family_df)))
