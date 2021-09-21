import matplotlib.pyplot as plt
import glob
import pickle
import numpy as np
import pandas as pd

from shapely.geometry import MultiPolygon
from Utilities.pathing_dir import maps_path, reference_path


class Country:
    def __init__(self, nation_name: str):
        self.__nation_name = nation_name
        self.__nation_abbreviation = self.__load_nation_abbreviations()
        self.__nation_path = maps_path
        print("Loading States...", end='\t')
        self.__state_names = self.__load_state_names()
        print(len(self.__state_names), 'Found', end='\t')
        print("Done.\nLoading State Adjacency...", end='\t')
        self.__state_adjacency = self.__load_state_adjacency()
        print("Done.\nLoading State Maps...", end='\t')
        self.__state_maps: dict = self.__load_state_maps()
        print(len(self.__state_maps), 'Found', end='\t')
        print("Done.\nLoading State Population...", end='\t')
        self.__nation_population_df = self.__load_nation_population_df()
        print('Done.\nNation ' + nation_name + ' Created', flush=True)

    def __load_nation_abbreviations(self) -> str:
        if self.__nation_name != 'United States of America':
            raise NotImplementedError
        return "USA"

    def __load_state_names(self) -> list:
        return list(map(lambda x: str(x).split('\\')[-2], list(glob.glob(self.__nation_path + '*\\'))))

    def __load_state_adjacency(self) -> pd.DataFrame:
        filename = self.__nation_path + self.__nation_name + ' State Adjacency.xlsx'
        try:
            return pd.read_excel(filename)
        except FileNotFoundError:
            country_level_adjacency = np.zeros((len(self.__state_names), len(self.__state_names)))
            state_abbr_df = pd.read_excel(reference_path + 'State Abbreviations.xlsx')
            with open(reference_path + 'State Adjacency.csv', 'r') as reader:
                for line in reader:
                    try:
                        details = line.removesuffix('\n').split(',')
                        query = state_abbr_df['Abbreviation'] == details[0]
                        current_state = state_abbr_df[query]['State'].values[0]
                        current_state_index = self.__state_names.index(current_state)
                        for i in range(1, len(details)):
                            if details[i] == '':
                                continue
                            query_i = state_abbr_df['Abbreviation'] == details[i]
                            neighbor_state = state_abbr_df[query_i]['State'].values[0]
                            neighbor_state_index = self.__state_names.index(neighbor_state)
                            country_level_adjacency[current_state_index, neighbor_state_index] = 1
                    except ValueError:
                        continue

            nation_adjacency_df = pd.DataFrame(country_level_adjacency, self.__state_names, self.__state_names)
            nation_adjacency_df.to_excel(filename)
            return nation_adjacency_df

    def __load_state_maps(self) -> dict:
        state_maps = {}
        state_map_files = list(glob.glob(self.__nation_path + '*\\*.pkl'))
        for state_map, state_name in zip(state_map_files, self.__state_names):
            with open(state_map, 'rb') as extract:
                state_maps[state_name] = pickle.load(extract)
        return state_maps

    @staticmethod
    def __load_nation_population_df() -> pd.DataFrame:
        return pd.read_excel(reference_path + 'County Census Counts 1900 - 1990.xlsx').drop(columns=['fips'])

    # Plot
    def plot_nation(self, save=False):
        if len(self.__state_maps) < len(self.__state_names):
            self.__state_maps = self.__load_state_maps()
        for state in self.__state_names:
            polygon = self.__state_maps[state]
            if polygon.geom_type == 'Polygon':
                plt.plot(*polygon.exterior.xy)
            elif polygon.geom_type == 'MultiPolygon':
                for poly in polygon:
                    plt.plot(*poly.exterior.xy)
        plt.axis('off')
        plt.title(self.__nation_name)
        if save:
            plt.savefig(self.__nation_path + self.__nation_name + ' .png')
        else:
            plt.show()
        plt.close('all')

    # Population
    def total_population(self, estimate: bool = False) -> pd.Series:
        states = [self.state_population(state, estimate) for state in self.__state_names]
        return pd.concat(states)

    def state_population(self, state_name: str, estimate: bool = False) -> pd.Series:
        county_df = self.__nation_population_df[self.__nation_population_df['State'] == state_name]
        temp_df = county_df.drop(columns=['State', 'Abbreviation', 'County']).reset_index(drop=True).transpose()
        if estimate:
            temp_df = self.__estimate(temp_df)
        temp_df = temp_df.squeeze().astype(int)
        temp_df.name = state_name
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
        return self.__nation_name

    @property
    def name(self) -> str:
        return self.__nation_name

    def states(self) -> list[str]:
        return self.__state_names
