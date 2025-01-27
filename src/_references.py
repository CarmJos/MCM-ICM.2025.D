from dataclasses import dataclass

ONLY_DRIVES = False

SOURCE_DATA_FOLDER = '../data/source/'

NAMES_FILE = SOURCE_DATA_FOLDER + 'Edge_Names_With_Nodes.csv'
ROUTES_FILE = SOURCE_DATA_FOLDER + 'Bus_Routes.csv'
STOPS_FILE = SOURCE_DATA_FOLDER + 'Bus_Stops.csv'
NODES_FILE = SOURCE_DATA_FOLDER + ('nodes_all.csv' if not ONLY_DRIVES else 'nodes_drive.csv')
EDGES_FILE = SOURCE_DATA_FOLDER + ('edges_all.csv' if not ONLY_DRIVES else 'edges_drive.csv')
TRAFFIC_DATA_FILE = SOURCE_DATA_FOLDER + 'MDOT_SHA_Annual_Average_Daily_Traffic_Baltimore.csv'
