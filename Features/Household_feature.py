import pandas as pd
from pathing import filesets


def to_county(df: pd.DataFrame, county_name: str) -> pd.DataFrame:
    return df.loc[list(filter(lambda x: county_name in x, df.index))]


if __name__ == '__main__':
    low_end = 2012
    for year in range(low_end, 2018):
        print(year)
        fileset = filesets.format(year=year)
        county = 'Onondaga County'
        household_df = pd.read_csv(fileset + 'Household income ' + str(year) + '.csv', na_values='N')
        index_name = household_df['Unnamed: 0'].loc[0]
        estimates = pd.Series(household_df.loc[0]).unique()[1:]
        household_df.drop(index=0, inplace=True)
        base_names = list(filter(lambda x: 'Unnamed' not in x, household_df.columns))
        household_index = pd.Series(list(map(str.strip, household_df['Unnamed: 0'])), name=index_name)
        household_df.drop(columns=['Unnamed: 0'], inplace=True)
        household_df.set_index(household_index, inplace=True)
        household_df = household_df.T
        new_index = pd.Series([col + ': ' + estimate for col in base_names for estimate in estimates])
        household_df.set_index(new_index, inplace=True)
        household_df.to_csv(fileset + 'Pandas Household income ' + str(year) + '.csv', na_rep='NA')
        print(household_df)
        print(any(pd.isna(household_df)))

