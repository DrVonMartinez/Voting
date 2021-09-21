import glob
import progressbar
import pandas as pd
from Utilities.pathing_dir import reference_file2, national_demographics_path as path, maps_path, reference_path
import numpy as np

columns = ["GEO_ID", "Geographic Area Name", "County", "State", "Total"]
pop_df = pd.read_excel(path.format(demographic='Racial Demographics') + 'RACE.xlsx')[columns]
pop_df['Total'] = pop_df['Total'].astype(int)
pop_df["County"] = pop_df["County"].apply(lambda x: x.replace('.', ''))
geo_ref = pd.read_excel(reference_file2)
geo_ref["County"] = geo_ref["County"].apply(lambda x: x.replace('.', ''))


def extract_districts(county_name: str) -> pd.DataFrame:
    return pop_df[pop_df['County'] == county_name].dropna()


def name_districts(county_name: str, state_name: str) -> pd.DataFrame:
    census_df = pd.read_csv(reference_path + 'Async 2020 Census by Voting District.csv')
    census_df["County"] = census_df["County"].apply(lambda x: x.replace('.', ''))
    state_extract = census_df['State'] == state_name
    county_extract = census_df['County'] == county_name
    return census_df.loc[np.where(county_extract & state_extract)]


def build_county(county_name: str, state_name: str) -> bool:
    county_df = extract_districts(county_name).sort_values(['State', 'County', "Geographic Area Name"])
    county_df["VTD GeoId"] = county_df["GEO_ID"].apply(lambda x: x.split("US")[-1])
    district_df = name_districts(county_name, state_name)
    print(district_df.columns)
    state_list = list(district_df['State'].unique())
    state_path = maps_path + '{state}\\'.format(state=state_name)
    county_path = state_path + '{county}\\'.format(county=county_name)
    if len(state_list) < 1:
        with open(state_path + 'Missing County - ' + county_name + '.txt', 'w+') as writer:
            writer.write(county_name + ':\n')
        return False
    state_name = state_list[0]
    missing = list(filter(lambda x: x not in district_df['VTD GeoId'].values, county_df["VTD GeoId"].values))
    if len(missing) > 0:
        with open(state_path + 'Missing Paths - ' + county_name + ', ' + state_name + '.txt', 'w+') as writer:
            writer.write(county_name + ':\n\t')
            writer.write('\n\t'.join(missing))
    merge = ['GEO_ID', 'County', 'State']
    county_df = county_df.merge(district_df, how='outer', left_on=merge, right_on=merge).drop_duplicates()
    county_df.sort_values(by=['State', 'County', 'VTD GeoId'], inplace=True)
    county_state = county_name + ', ' + state_name
    county_df.to_excel(county_path + county_name + ' Pandas District Population.xlsx', sheet_name=county_state, index=False)
    return True


if __name__ == '__main__':
    all_counties = glob.glob(maps_path + '*\\*\\')
    success = 0
    build_county("Onondaga County", "New York")
    raise EnvironmentError
    with progressbar.ProgressBar(min_value=0, maxval=len(all_counties)) as bar:
        for county_file, i in zip(all_counties, range(len(all_counties))):
            state, county = str(county_file).split('\\')[-3:-1]
            success += build_county(county, state)
            bar.update(i)
    print(success, '/', len(all_counties), '\t', success/len(all_counties))
