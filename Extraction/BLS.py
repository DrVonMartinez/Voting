import pandas as pd
import requests
import json
import prettytable

from Utilities.pathing_dir import data_path
from Utilities.Product_Key import bls_key


def list_surveys() -> list:
    headers = {'Content-type': 'application/json'}
    data = json.dumps({"startyear": "1900", "endyear": "2020", "registrationkey": bls_key})
    p = requests.post('https://api.bls.gov/publicAPI/v2/surveys', data=data, headers=headers)
    json_data = json.loads(p.text)
    cols = ['Survey Abbreviation', "Survey Name"]
    bls_survey_df = pd.DataFrame(json_data['Results']['survey'])
    bls_survey_df.columns = cols
    for survey in json_data['Results']['survey']:
        print(survey["survey_abbreviation"], survey["survey_name"], sep=':\t\t')
    print(bls_survey_df)
    bls_survey_df.to_csv(data_path + 'BLS Survey Details.csv', index=False)
    return list(bls_survey_df['Survey Abbreviation'].values)


def get_survey(survey_id: str):
    headers = {'Content-type': 'application/json'}
    data = json.dumps({"seriesid": [survey_id], "startyear": "1900", "endyear": "2020", "registrationkey": bls_key})
    p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
    json_data = json.loads(p.text)
    for series in json_data['Results']['series']:
        x = prettytable.PrettyTable(["series id", "year", "period", "value", "footnotes"])
        seriesId = series['seriesID']
        for item in series['data']:
            year = item['year']
            period = item['period']
            value = item['value']
            footnotes = ""
            for footnote in item['footnotes']:
                if footnote:
                    footnotes = footnotes + footnote['text'] + ','
            if 'M01' <= period <= 'M12':
                x.add_row([seriesId, year, period, value, footnotes[0:-1]])
        output = open(seriesId + '.txt', 'w')
        output.write(x.get_string())
        output.close()


list_surveys()
