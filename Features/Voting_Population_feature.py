import pandas as pd
from pathing import filesets, original
from Utilities.pathing_dir import national_demographics_path


def reformat(year: str, age_group: list):
    population_df_set = []
    for a in age_group:
        if '-' in a:
            pop = "Population " + a.replace('-', ' to ') + " years"
        else:
            pop = "Population 65 years and over"
        temp_df = pd.read_csv(original.format(year=year) + a + ' education ' + year + '.csv', index_col=0)
        base_names = list(filter(lambda x: 'Unnamed' not in x, temp_df.columns))
        if len(base_names) < len(temp_df.columns):
            estimates = pd.Series(temp_df.loc['Subject']).unique()
            temp_df.columns = [location + ': ' + estimate for location in base_names for estimate in estimates]
        else:
            estimates = pd.Series(temp_df.loc['Subject'])
            temp_df.columns = [location + ': ' + estimate for location, estimate in zip(base_names, estimates)]
        temp_df.drop(index='Subject', inplace=True)
        temp_df = temp_df.astype(float)
        temp_df.index = list(map(str.strip, temp_df.index))
        temp_df = temp_df.T
        population_df_set.append(pd.Series(temp_df[pop]))
    population_df = pd.concat(population_df_set, axis=1)
    population_df = population_df.astype(int)
    population_df.to_csv(filesets.format(year=year) + 'Pandas Voting Population.csv')


if __name__ == '__main__':
    low_end = 2012
    for y in range(low_end, 2018):
        reformat(str(y), ['18-24', '25-34', '35-44', '45-64', '65 and over'])
