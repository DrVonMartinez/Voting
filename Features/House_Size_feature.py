import pandas as pd

from Features.pathing import filesets


def to_county(df: pd.DataFrame, county_name: str) -> pd.DataFrame:
    return df.loc[list(filter(lambda x: county_name in x, df.index))]


if __name__ == '__main__':
    low_end = 2012
    for year in range(low_end, 2018):
        print(year)
        fileset = filesets.format(year=year)
        county = 'Onondaga County'
        house_size_df = pd.read_csv(fileset + 'House size ' + str(year) + '.csv', na_values='N', converters={'-': '0'})
        index_name = house_size_df['Unnamed: 0'].loc[0]
        estimates = pd.Series(house_size_df.loc[0]).unique()[1:]
        house_size_df.drop(index=0, inplace=True)
        base_names = list(filter(lambda x: 'Unnamed' not in x, house_size_df.columns))
        house_size_index = pd.Series(list(map(str.strip, house_size_df['Unnamed: 0'])), name=index_name)
        house_size_df.drop(columns=['Unnamed: 0'], inplace=True)
        house_size_df.set_index(house_size_index, inplace=True)
        house_size_df = house_size_df.T


        def percentage(x):
            if 'Percent' not in x:
                return 'Percent ' + x.lower()
            else:
                return x


        new_index = pd.Series([col + ': ' + percentage(estimate) for col in base_names for estimate in estimates])
        house_size_df.set_index(new_index, inplace=True)
        house_size_df.to_csv(fileset + 'Pandas House size ' + str(year) + '.csv', na_rep='NA')
        print(house_size_df)
        print(any(pd.isna(house_size_df)))
