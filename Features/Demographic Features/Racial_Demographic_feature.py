import numpy as np
import pandas as pd
import glob
from Utilities.pathing_dir import national_demographics_path as path

race_data_files = glob.glob(path.format(demographic="Racial Demographics") + 'Race *\\*.csv')
print(path.format(demographic="Racial Demographic"))
print(race_data_files)
headings = ['GEO_ID', 'Geographic Area Name', 'County', 'State', 'Total', 'Total Population of One race',
            'Total Population of one race: White',
            'Total Population of one race: Black or African American',
            'Total Population of one race: American Indian and Alaska Native',
            'Total Population of one race: Asian',
            'Total Population of one race: Native Hawaiian and Other Pacific Islander',
            'Total Population of one race: Some Other Race', 'Total Population of Two or More Races']

race_df_set = []
for file in race_data_files:
    print(file)
    temp = pd.read_csv(file, usecols=list(range(len(headings))))
    temp.columns = headings
    for i in range(4, len(headings)):
        temp[headings[i]] = temp[headings[i]].astype(int)
    one_col = 'Total Population of One race'
    two_col = 'Total Population of Two or More Races'
    assert np.array_equal(temp['Total'].values, (temp[one_col].values + temp[two_col].values))
    race_df_set.append(temp)
race_df = pd.concat(race_df_set, ignore_index=True)
race_df[headings[1]] = pd.Series(race_df[headings[1]], dtype=str).apply(str.title)
race_df.sort_values(by=['State', 'County', 'Geographic Area Name'])
race_df.to_csv(path.format(demographic="Racial Demographics") + 'RACE.csv', index=False)
