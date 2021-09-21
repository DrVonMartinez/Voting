import matplotlib.pyplot as plt
import glob
import pickle
import numpy as np
import pandas as pd
import shapely.geometry

from shapely.geometry import MultiPolygon
from Utilities.pathing_dir import maps_path, reference_path


class State:
    def __init__(self, state_name: str, silent=False):
        self.__state_name = state_name
        self.__state_abbreviation = self.__load_state_abbreviations()
        self.__state_path = maps_path + self.__state_name + '\\'
        if not silent:
            print("Loading Counties...", end='\t')
        self.__county_names = self.__load_county_names()
        if not silent:
            print("Done.\nLoading County Adjacency...", end='\t')
        self.__county_level_adjacency = self.__load_county_level_adjacency()
        if not silent:
            print("Done.\nLoading County Maps...", end='\t')
        self.__county_maps: dict = self.__load_county_maps()
        if not silent:
            print("Done.\nLoading State Population...", end='\t')
        self.__state_population_df = self.__load_state_population_df()
        if not silent:
            print('Done.\nState ' + state_name + ' Created', flush=True)

    def __load_state_abbreviations(self) -> str:
        state_abbr_df = pd.read_excel(reference_path + 'State Abbreviations.xlsx')
        state_abbr = state_abbr_df[state_abbr_df['State'] == self.__state_name]['Abbreviation'].values[0]
        return state_abbr

    def __load_county_names(self) -> list:
        return list(map(lambda x: str(x).split('\\')[-2], list(glob.glob(self.__state_path + '*\\'))))

    def __load_county_level_adjacency(self) -> pd.DataFrame:
        filename = self.__state_path + self.__state_name + ' County Adjacency.xlsx'
        try:
            return pd.read_excel(filename)
        except FileNotFoundError:
            county_level_adjacency = np.zeros((len(self.__county_names), len(self.__county_names)))
            county_adjacency_df = pd.read_excel(reference_path + 'County Adjacency.xlsx')
            query = county_adjacency_df['County State Abbreviation'] == self.__state_abbreviation
            county_adjacency_df = county_adjacency_df[query].dropna()
            query2 = county_adjacency_df['Adjacent County State Abbreviation'] == self.__state_abbreviation
            county_adjacency_df = county_adjacency_df[query2].dropna().reset_index(drop=True)
            for i in range(len(list(self.__county_names))):
                name_1 = self.__county_names[i]
                county_query = county_adjacency_df['County Name'] == name_1
                county_neighbors_df = county_adjacency_df[county_query].dropna().reset_index()
                for j in range(len(county_neighbors_df)):
                    try:
                        name_2 = county_neighbors_df.loc[j, 'Adjacent County Name']
                        if name_1 == name_2:
                            raise ValueError
                        county_level_adjacency[i, self.__county_names.index(name_2)] = 1
                    except ValueError:
                        continue
            state_county_adjacency_df = pd.DataFrame(county_level_adjacency, self.__county_names, self.__county_names)
            state_county_adjacency_df.to_excel(filename)
            return state_county_adjacency_df

    def __load_county_maps(self) -> dict:
        county_maps = {}
        county_map_files = list(glob.glob(self.__state_path + '\\*\\*.pkl'))
        for county_map, county_name in zip(county_map_files, self.__county_names):
            county_maps[county_name] = county_map
        return county_maps

    def __load_state_population_df(self) -> pd.DataFrame:
        national_df = pd.read_excel(reference_path + 'County Census Counts 1900 - 1990.xlsx').drop(columns=['fips'])
        return national_df[national_df['State'] == self.__state_name].dropna().reset_index(drop=True)

    # Plot
    def plot_state(self, save=False):
        if len(self.__county_maps) < len(self.__county_names):
            self.__county_maps = self.__load_county_maps()
        assert len(self.__county_maps) == len(self.__county_names)
        state_polygon = shapely.geometry.MultiPolygon()
        for county in self.__county_names:
            with open(self.__county_maps[county], 'rb') as extract:
                polygon = pickle.load(extract)
                state_polygon = state_polygon.union(polygon)
                if polygon.geom_type == 'Polygon':
                    plt.plot(*polygon.exterior.xy)
                elif polygon.geom_type == 'MultiPolygon':
                    for poly in polygon:
                        plt.plot(*poly.exterior.xy)
                del polygon
        with open(self.__state_path + self.__state_name + '.pkl', "wb+") as state_map:
            pickle.dump(state_polygon, state_map)
        del state_polygon
        plt.axis('off')
        plt.title(self.__state_name + ' Counties')
        if save:
            plt.savefig(self.__state_path + self.__state_name + ' Counties.png')
        else:
            plt.show()
        plt.close('all')

    # Population
    def total_population(self, estimate: bool = False) -> pd.Series:
        county_df: pd.Series = self.__state_population_df.drop(columns=['County', 'State', 'Abbreviation'])
        county_df.dropna(axis=1, inplace=True)
        county_df = county_df.astype(int).sum(axis=0)
        county_df.name = self.__state_name
        if estimate:
            county_df = self.__estimate(county_df)
        return county_df

    def county_population(self, county_name: str, estimate: bool = False) -> pd.Series:
        county_df = self.__state_population_df[self.__state_population_df['County'] == county_name]
        temp_df = county_df.drop(columns=['State', 'Abbreviation', 'County']).reset_index(drop=True).transpose()
        if estimate:
            temp_df = self.__estimate(temp_df)
        temp_df = temp_df.squeeze().astype(int)
        temp_df.name = county_name
        return temp_df

    @staticmethod
    def __estimate(county_df: pd.Series) -> pd.Series:
        for i in range(min(county_df.index), 2000):
            if i % 10 == 0:
                continue
            county_df[i] = np.nan
        return county_df.interpolate(method='from_derivatives').sort_index().dropna().astype(int)

    # Generic methods
    def __str__(self):
        return self.__state_name

    def __del__(self):
        del self.__state_population_df
        del self.__county_level_adjacency
        del self.__county_maps
        del self.__county_names
        del self.__state_abbreviation
        del self.__state_path

    @property
    def name(self) -> str:
        return self.__state_name

    def counties(self) -> list[str]:
        return self.__county_names
