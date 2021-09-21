from Utilities.pathing_dir import national_demographics_path as path
import pandas as pd
from Extract_and_Stack import extract


def label():
    return 'Name,Year,Male Population 18-24: Less Than High School,Male Population 18-24: High School,' + \
           'Male Population 18-24: Bachelors or more,Male Population 25-34: Less Than High School' + \
           ',Male Population 25-34: High School,Male Population 25-34: Bachelors or more,' + \
           'Male Population 35-44: Less Than High School,Male Population 35-44: High School,Male' + \
           ' Population 35-44: Bachelors or more,Male Population 45-64: Less Than High School,Male ' + \
           'Population 45-64: High School,Male Population 45-64: Bachelors or more,Male Population 65+: ' + \
           'Less Than High School,Male Population 65+: High School,Male Population 65+: Bachelors or more, ' + \
           'Female Population 18-24: Less Than High School,Female Population 18-24: High School,Female Population ' + \
           '18-24: Bachelors or more,Female Population 25-34: Less Than High School,Female Population 25-34: High ' + \
           'School,Female Population 25-34: Bachelors or more,Female Population 35-44: Less Than High School,Female' + \
           ' Population 35-44: High School,Female Population 35-44: Bachelors or more,Female Population 45-64: Less ' + \
           'Than High School,Female Population 45-64: High School,Female Population 45-64: Bachelors or more,Female ' + \
           'Population 65: Less Than High School,Female Population 65+: High School,Female Population 65+: Bachelors' + \
           ' or more,Percent Owner,1-person,2-person,3-person,4+person,Percent Renter,1-person,2-person,3-person,' + \
           '4+person,No Workers,1 Worker,2 Workers,3+ Workers,Earnings,Retirement\n'


def to_county(df: pd.DataFrame, county_name: str) -> pd.DataFrame:
    return df.loc[list(filter(lambda x: county_name in x, df.index))]


if __name__ == '__main__':
    low_end = 2012
    for year in range(low_end, 2018):
        fileset = filesets.format(year=year)
        education = ['18-24', '25-34', '35-44', '45-64', '65 and over']
        county = 'Onondaga County'
        county_df_set = []
        age_df_set = []
        for file in education:
            file_df = pd.read_csv(fileset + 'Pandas ' + file + ' education.csv', index_col=0)
            param_columns = list(file_df.columns)
            file_df.columns = [param_columns[0].split(' ')[0] + ': ' + file] + [col + ': ' + file for col in
                                                                                param_columns[1:]]
            age_df_set.append(file_df)
        age_df = pd.concat(age_df_set, axis=1)


        def sort_col(a):
            col_order = ['P', 'L', 'H', 'B']
            return col_order.index(a[0]), a.split(' ')


        education_df = age_df.reindex(columns=sorted(age_df.columns, key=sort_col))
        occupied_df = pd.read_csv(fileset + 'Pandas Occupied rates ' + str(year) + '.csv', index_col=0)
        family_df = pd.read_csv(fileset + 'Pandas Family income ' + str(year) + '.csv', index_col=0)
        house_size_df = pd.read_csv(fileset + 'Pandas House size ' + str(year) + '.csv', index_col=0)
        household_df = pd.read_csv(fileset + 'Pandas Household income ' + str(year) + '.csv', index_col=0)

        city_set = ['Camillus', 'Cicero', 'Clay', 'De Witt', 'Elbridge', 'Fabius', 'Geddes', 'LaFayette', 'Lysander',
                    'Manlius', 'Marcellus', 'Onondaga', 'Otisco', 'Pompey', 'Salina', 'Skaneateles', 'Spafford',
                    'Syracuse', 'Tully', 'Van Buren']
        city_year = []
        for city in [county] + city_set:
            city_year.append(extract(city, year, education_df=education_df, family_df=family_df, occupied_df=occupied_df, household_df=household_df, house_size_df=house_size_df))
        city_year_df = pd.concat(city_year)
        city_year_df.to_csv(fileset + 'Pandas Stacked County.csv')
