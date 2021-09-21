import numpy as np
import pandas as pd
import glob

path = 'D:\\County\\Population\\'
occupancy_status_data_files = glob.glob(path + 'Occupancy *\\*.csv')
print(occupancy_status_data_files)
headings = ['GEO_ID', 'Geographic Area Name', 'County', 'State', 'Total', 'Total Occupied', 'Total Vacant']

occupancy_status_df_set = []
for file in occupancy_status_data_files:
    print(file)
    temp = pd.read_csv(file, usecols=list(range(len(headings))))
    temp.columns = headings
    for i in range(4, len(headings)):
        temp[headings[i]] = temp[headings[i]].astype(int)
    one_col = headings[-2]
    two_col = headings[-1]
    assert np.array_equal(temp['Total'].values, (temp[one_col].values + temp[two_col].values))
    occupancy_status_df_set.append(temp)
occupancy_status_df = pd.concat(occupancy_status_df_set, ignore_index=True)
occupancy_status_df.sort_values(by=['State', 'County', 'Geographic Area Name'])
occupancy_status_df.to_csv(path + 'OCCUPANCY STATUS.csv', index=False)
