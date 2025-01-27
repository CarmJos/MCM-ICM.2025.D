from dataclasses import dataclass

ONLY_DRIVES = True

DATA_FOLDER = '../data/'

ROUTES_FILE = DATA_FOLDER + 'Bus_Routes.csv'
STOPS_FILE = DATA_FOLDER + 'Bus_Stops.csv'
NODES_FILE = DATA_FOLDER + ('nodes_all.csv' if not ONLY_DRIVES else 'nodes_drive.csv')
EDGES_FILE = DATA_FOLDER + ('edges_all.csv' if not ONLY_DRIVES else 'edges_drive.csv')
TRAFFIC_DATA_FILE = DATA_FOLDER + 'MDOT_SHA_Annual_Average_Daily_Traffic_Baltimore.csv'

BUS_ROUTE_TYPE_MAPPER = {
    'BR': 'CityLink BROWN', 'BL': 'CityLink BLUE', 'GL': 'CityLink GOLD',
    'GR': 'CityLink GREEN', 'OR': 'CityLink ORANGE', 'PK': 'CityLink PINK',
    'PR': 'CityLink PURPLE', 'RD': 'CityLink RED', 'SV': 'CityLink SILVER',
    'YW': 'CityLink YELLOW', 'NV': 'CityLink NAVY'
}


@dataclass
class Coordinates:
    longitude: float
    latitude: float

    def distance(self, other: 'Coordinates') -> float:
        """Calculate the distance between two coordinates."""
        return ((self.longitude - other.longitude) ** 2 + (self.latitude - other.latitude) ** 2) ** 0.5
