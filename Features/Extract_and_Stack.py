import pandas as pd


def to_location(df: pd.DataFrame, location_name: str) -> pd.DataFrame:
    if 'County' not in location_name:
        return df.loc[list(filter(lambda x: location_name in x and 'County' not in x, df.index))]
    return df.loc[list(filter(lambda x: location_name in x, df.index))]


def extract(location, year, education_df, occupied_df, family_df, house_size_df, household_df):
    location_education_df = to_location(education_df, location)
    location_occupied_df = to_location(occupied_df, location)
    location_family_df = to_location(family_df, location)
    location_house_size_df = to_location(house_size_df, location)
    location_household_df = to_location(household_df, location)

    def owner(x):
        return 'owner' in x.lower()

    def renter(x):
        return 'renter' in x.lower()

    def male(x):
        return 'Male' in x

    def female(x):
        return 'Female' in x

    def estimate(x):
        return 'total estimate' in x.lower()

    location_owner_size = location_house_size_df.loc[list(filter(owner, location_house_size_df.index))]
    location_owner_size.index = [location]
    location_owner = location_occupied_df[list(filter(owner, location_occupied_df.columns))]
    location_owner.index = [location]
    location_owner_df = [location_owner, location_owner_size]

    location_renter_size = location_house_size_df.loc[list(filter(renter, location_house_size_df.index))]
    location_renter_size.index = [location]
    location_renter = location_occupied_df[list(filter(renter, location_occupied_df.columns))]
    location_renter.index = [location]
    location_renter_df = [location_renter, location_renter_size]

    location_family_size = location_family_df.loc[list(filter(estimate, location_family_df.index))]
    location_family_size = location_family_size[['No workers', '1 worker', '2 Workers', '3+ Workers']]
    location_family_size.index = [location]
    location_household_earnings = location_household_df.loc[list(filter(estimate, location_household_df.index))]
    location_household_earnings.index = [location]
    earnings_col = ['With earnings', 'With cash public assistance income', 'With retirement income']
    location_household_earnings = location_household_earnings[earnings_col]
    location_household_earnings.index = [location]

    location_df_male: pd.DataFrame = location_education_df.loc[list(filter(male, location_education_df.index))]
    location_df_male = location_df_male[[col for col in filter(lambda x: 'Pop' not in x, location_df_male.columns)]]
    location_df_male.columns = ['Male: ' + col for col in location_df_male.columns]
    location_df_male.index = [location]

    location_df_female: pd.DataFrame = location_education_df.loc[list(filter(female, location_education_df.index))]
    location_df_female = location_df_female[[col for col in filter(lambda x: 'Pop' not in x, location_df_female.columns)]]
    location_df_female.columns = ['Female: ' + col for col in location_df_female.columns]
    location_df_female.index = [location]

    location_df = pd.DataFrame([year], index=[location], columns=['Year'], dtype=int)
    location_housing = location_owner_df + location_renter_df
    location_earnings = [location_family_size, location_household_earnings]
    location_list = [location_df, location_df_male, location_df_female] + location_housing + location_earnings
    location_df = pd.concat(location_list, axis=1)
    try:
        location_df.set_index(pd.Series([location]), inplace=True)
    except ValueError:
        location_df.to_csv('text.csv')
        assert False
    print(location_df)
    return location_df
