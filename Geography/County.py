import matplotlib.pyplot as plt
import glob
import pickle
import numpy as np
import pandas as pd
import shapely.geometry

from shapely.geometry import MultiPolygon
from Utilities.pathing_dir import maps_path, reference_path


class County:
    def __init__(self, county_name: str, state_name: str, silent=False):
        self.__county_name = county_name
        self.__state_name = state_name
        if not silent:
            print("Loading Districts...", end='\t')
        self.__county_path = maps_path + state_name + '\\' + county_name + '\\'
        self.__district_names: list = self.__gather_district_files()
        if not silent:
            print("Done.\nLoading District Adjacency...", end='\t')
        self.__district_level_adjacency = self.__load_district_level_adjacency()
        if not silent:
            print("Done.\nLoading District Population...", end='\t')
        self.__county_population_df = self.__total_population_df()
        if not silent:
            print('Done.\nCounty', county_name + ',', state_name, 'Created', flush=True)

    @property
    def name(self) -> str:
        return self.__county_name + ', ' + self.__state_name

    @property
    def state(self) -> str:
        return self.__state_name

    def __gather_district_files(self) -> list:
        return list(glob.glob(self.__county_path + '\\District Graph\\*.pkl'))

    def __load_district_level_adjacency(self) -> pd.DataFrame:
        filename = self.__county_path + self.__county_name + ' Adjacency.xlsx'
        try:
            return pd.read_excel(filename)
        except FileNotFoundError:
            districts: dict[MultiPolygon] = {district.split('\\')[-1][:-4]: self.__load_polygon(district)
                                             for district in self.__district_names}
            district_level_adjacency = np.zeros((len(self.__district_names), len(self.__district_names)))
            for i in range(len(list(districts))):
                name_1 = list(districts)[i]
                for j in range(i + 1, len(list(districts))):
                    name_2 = list(districts)[j]
                    if districts[name_1].intersects(districts[name_2]):
                        district_level_adjacency[i, j] = 1
                        district_level_adjacency[j, i] = 1
            district_df = pd.DataFrame(district_level_adjacency, self.__district_names, self.__district_names)
            district_df.to_excel(filename)
            return district_df

    '''
    def plot_counties(self, save=False):
        plt.axis('off')
        for county in self.__county_files:
            county_polygon = self.__group_districts(county)
            if county_polygon.geom_type == 'Polygon':
                plt.plot(*county_polygon.exterior.xy)
            elif county_polygon.geom_type == 'MultiPolygon':
                for poly in county_polygon:
                    plt.plot(*poly.exterior.xy)
        if save and include_districts:
            plt.savefig(self.__county_path + ' District Level.png')
        elif save and not include_districts:
            plt.savefig(self.__county_path + ' County Level.png')
        else:
            plt.show()
        plt.close('all')
    
    def __group_districts(self, county_name) -> MultiPolygon:
        county_polygon: MultiPolygon = MultiPolygon()
        for district in self.__county_files[county_name]:
            county_polygon = county_polygon.union(self.__load_polygon(district))
        return county_polygon
    '''

    def plot_districts(self, save=False):
        county_polygon = shapely.geometry.MultiPolygon()
        for district in self.__district_names:
            polygon = self.__load_polygon(district)
            county_polygon = county_polygon.union(polygon)
            if polygon.geom_type == 'Polygon':
                plt.plot(*polygon.exterior.xy)
            elif polygon.geom_type == 'MultiPolygon':
                for poly in polygon:
                    plt.plot(*poly.exterior.xy)
        with open(self.__county_path + self.__county_name + '.pkl', "wb+") as county_map:
            pickle.dump(county_polygon, county_map)
        del county_polygon
        plt.axis('off')
        plt.title(self.__county_name + ' Districts')
        if save:
            plt.savefig(self.__county_path + self.__county_name + ' Districts.png')
        else:
            plt.show()
        plt.close('all')

    def plot_county_map(self, show=True):
        county_polygon = shapely.geometry.MultiPolygon()
        for district in self.__district_names:
            polygon = self.__load_polygon(district)
            county_polygon = county_polygon.union(polygon)
        if county_polygon.geom_type == 'Polygon':
            plt.plot(*county_polygon.exterior.xy)
        elif county_polygon.geom_type == 'MultiPolygon':
            for poly in county_polygon:
                plt.plot(*poly.exterior.xy)
        if show:
            plt.title(self.__county_name)
            plt.axis('off')
            plt.show()
            plt.close('all')

    @property
    def district_level_adjacency(self) -> pd.DataFrame:
        return self.__district_level_adjacency

    @staticmethod
    def __load_polygon(filename) -> MultiPolygon:
        polygon: MultiPolygon
        with open(filename, "rb") as extract:
            polygon = pickle.load(extract)
        return polygon

    # Population
    def population(self, estimate: bool = False) -> pd.Series:
        cols = ['State', 'Abbreviation', 'County']
        temp_df = self.__county_population_df.drop(columns=cols).reset_index(drop=True).transpose()
        if estimate:
            temp_df = self.__estimate(temp_df)
        temp_df = temp_df.squeeze().astype(int)
        temp_df.name = self.__county_name
        return temp_df

    @staticmethod
    def __estimate(county_df: pd.Series) -> pd.Series:
        for i in range(min(county_df.index), 2000):
            if i % 10 == 0:
                continue
            county_df[i] = np.nan
        return county_df.interpolate(method='from_derivatives').sort_index().dropna().astype(int)

    def __total_population_df(self) -> pd.DataFrame:
        national_df = pd.read_excel(reference_path + 'County Census Counts 1900 - 1990.xlsx').drop(columns=['fips'])
        query = national_df['State'] == self.__state_name
        query2 = national_df['County'] == self.__county_name
        return national_df[query & query2].dropna().reset_index(drop=True)

    # Generic methods
    def __str__(self):
        return self.__county_name

    def __del__(self):
        del self.__county_population_df
        del self.__district_level_adjacency
        del self.__district_names
        del self.__county_path
        del self.__county_name
        del self.__state_name
