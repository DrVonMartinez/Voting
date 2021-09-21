import numpy as np
import pandas as pd
from pathing import filesets, original


def reformat(year: str):
    education_df = pd.read_csv(original.format(year=year) + age + ' education ' + year + '.csv', index_col=0)
    base_names = list(filter(lambda x: 'Unnamed' not in x, education_df.columns))
    if len(base_names) < len(education_df.columns):
        estimates = pd.Series(education_df.loc['Subject']).unique()
        education_df.columns = [location + ': ' + estimate for location in base_names for estimate in estimates]
    else:
        estimates = pd.Series(education_df.loc['Subject'])
        education_df.columns = [location.split('.')[0] + ': ' + estimate for location, estimate in zip(base_names, estimates)]
    education_df.drop(index='Subject', inplace=True)
    education_df = education_df.astype(float)
    education_df.index = list(map(str.strip, education_df.index))
    less_than_high_school = "Less than high school graduate"
    high_school_some_college = "High school graduate or Some College"
    high_school_plus = 'High school graduate or higher'
    bachelors_plus = "Bachelor's degree or higher"
    trim = list(education_df.index)
    if '-' in age:
        pop = "Population " + age.replace('-', ' to ') + " years"
    else:
        pop = "Population 65 years and over"
    if "Some college or associate's degree" in trim:
        high_school = 'High school graduate (includes equivalency)'
        some_college = "Some college or associate's degree"
        np_high_school = np.array(education_df.loc[high_school], dtype=float)
        np_some_college = np.array(education_df.loc[some_college], dtype=float)
        np_population = np.array(education_df.loc[pop], dtype=int)
        education_df.loc[high_school_some_college] = np_high_school + np_some_college
        if pd.DataFrame.max(education_df.loc[high_school_some_college]) > 1:
            np_less_than_high_school = np.array(education_df.loc[less_than_high_school], dtype=float)
            np_bachelors_plus = np.array(education_df.loc[bachelors_plus], dtype=float)
            education_df.loc[less_than_high_school] = np_less_than_high_school / np_population
            education_df.loc[bachelors_plus] = np_bachelors_plus / np_population
            education_df.loc[high_school_some_college] = (np_high_school + np_some_college) / np_population
            assert pd.DataFrame.max(education_df.loc[high_school_some_college]) <= 1
        education_df.drop(index=[high_school, some_college], inplace=True)
    elif high_school_plus in trim:
        np_population = np.array(education_df.loc[trim[0]], dtype=int)
        np_high_school_plus = np.array(education_df.loc[high_school_plus], dtype=float)
        one = np.ones_like(np_high_school_plus)
        np_bachelors_plus = np.array(education_df.loc[bachelors_plus], dtype=float)
        education_df.loc[less_than_high_school] = one - np_high_school_plus / np_population
        education_df.loc[high_school_some_college] = (np_high_school_plus - np_bachelors_plus) / np_population
        education_df.loc[bachelors_plus] = np_bachelors_plus / np_population
        education_df.drop(index=high_school_plus, inplace=True)

    assert pop in education_df.index, pop + '\n[' + ', '.join(map(str, education_df.index)) + ']'
    education_df = education_df.reindex(index=[pop, less_than_high_school, high_school_some_college, bachelors_plus])
    education_df = education_df.T
    columns = list(education_df.columns)
    col_dict = {col: float for col in columns}
    col_dict[columns[0]] = int
    education_df = education_df.astype(col_dict)
    education_df.to_csv(filesets.format(year=year) + 'Pandas ' + age + ' education.csv')


def to_county(df: pd.DataFrame, county_name: str) -> pd.DataFrame:
    return df.loc[list(filter(lambda x: county_name in x, df.index))]


if __name__ == '__main__':
    low_end = 2012
    for y in range(low_end, 2018):
        education = ['18-24', '25-34', '35-44', '45-64', '65 and over']
        county = 'Onondaga County'
        for age in education:
            print(y, age, sep=': ')
            reformat(str(y))
