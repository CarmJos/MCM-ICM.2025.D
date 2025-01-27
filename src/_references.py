from dataclasses import dataclass

ONLY_DRIVES = False

SOURCE_DATA_FOLDER = '../data/source/'

NAMES_FILE = SOURCE_DATA_FOLDER + 'Edge_Names_With_Nodes.csv'
ROUTES_FILE = SOURCE_DATA_FOLDER + 'Bus_Routes.csv'
STOPS_FILE = SOURCE_DATA_FOLDER + 'Bus_Stops.csv'
NODES_FILE = SOURCE_DATA_FOLDER + ('nodes_all.csv' if not ONLY_DRIVES else 'nodes_drive.csv')
EDGES_FILE = SOURCE_DATA_FOLDER + ('edges_all.csv' if not ONLY_DRIVES else 'edges_drive.csv')
TRAFFIC_DATA_FILE = SOURCE_DATA_FOLDER + 'MDOT_SHA_Annual_Average_Daily_Traffic_Baltimore.csv'

BUS_ROUTE_TYPE_MAPPER = {
    'BR': 'CityLink BROWN', 'BL': 'CityLink BLUE', 'GL': 'CityLink GOLD',
    'GR': 'CityLink GREEN', 'OR': 'CityLink ORANGE', 'PK': 'CityLink PINK',
    'PR': 'CityLink PURPLE', 'RD': 'CityLink RED', 'SV': 'CityLink SILVER',
    'YW': 'CityLink YELLOW', 'NV': 'CityLink NAVY'
}
