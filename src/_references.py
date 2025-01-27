ONLY_DRIVES = False

DATA_FOLDER = '../data/'

ROUTES_FILE = DATA_FOLDER + 'Bus_Routes.csv'
STOPS_FILE = DATA_FOLDER + 'Bus_Stops.csv'
NODES_FILE = DATA_FOLDER + ('nodes_all.csv' if not ONLY_DRIVES else 'nodes_drive.csv')
EDGES_FILE = DATA_FOLDER + ('edges_all.csv' if not ONLY_DRIVES else 'edges_drive.csv')
TRAFFIC_DATA_FILE = DATA_FOLDER + 'MDOT_SHA_Annual_Average_Daily_Traffic_Baltimore.csv'
