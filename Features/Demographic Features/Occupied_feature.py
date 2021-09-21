import pandas as pd

from Features.pathing import filesets


def to_county(df: pd.DataFrame, county_name: str) -> pd.DataFrame:
    return df.loc[list(filter(lambda x: county_name in x, df.index))]


if __name__ == '__main__':
    low_end = 2012
    for year in range(low_end, 2018):
        fileset = filesets.format(year=year)
        county = 'Onondaga County'
        orig_occupied_df = pd.read_csv(fileset + 'Occupied rates ' + str(year) + '.csv')
        base_names = list(filter(lambda x: 'Unnamed' not in x, orig_occupied_df.columns))
        occupied_df = pd.DataFrame()
        total = 'Occupied housing units Estimate'
        owner = 'Owner-occupied housing units Estimate'
        renter = 'Renter-occupied housing units Estimate'
        locations = pd.Series(base_names)
        values = orig_occupied_df.values[1, :]
        estimates = pd.Series(orig_occupied_df.loc[0]).unique()
        for i in range(0, len(orig_occupied_df.columns), len(estimates)):
            occupied_df = occupied_df.append(pd.Series(values[i:i + len(estimates)]), ignore_index=True)
        occupied_df.columns = estimates
        occupied_df.set_index(locations, inplace=True)
        if any(map(lambda x: 'Percent' in x, occupied_df.columns)):
            occupied_df.columns = [total, 'Percent Owner Estimate', 'Percent Renter Estimate']
        else:
            occupied_df_totals = occupied_df[total].astype(float)
            occupied_df_owner = occupied_df[owner].astype(float)
            occupied_df_renter = occupied_df[renter].astype(float)
            occupied_df['Percent Owner Estimate'] = occupied_df_owner / occupied_df_totals
            occupied_df['Percent Renter Estimate'] = occupied_df_renter / occupied_df_totals
            occupied_df.drop(columns=[owner, renter], inplace=True)
        print(year)
        occupied_df.to_csv(fileset + 'Pandas Occupied rates ' + str(year) + '.csv')

