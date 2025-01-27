import sys
from typing import List, Dict, Any, Callable, Union, Tuple

import geopandas as gpd
from geopandas import GeoDataFrame
from pandas import DataFrame
from shapely.geometry.point import Point
from tqdm import tqdm

from _references import *
from data import *


def read_geo(
        file_path: str, index_columns: Union[str, List[str]] = None,
        value_filter: Callable[[pd.DataFrame], bool] = None,
        converter: Callable[[pd.DataFrame], Any] = None
) -> GeoDataFrame:
    index_columns = index_columns if isinstance(index_columns, list) else [index_columns]
    df = pd.read_csv(file_path, index_col=index_columns, low_memory=False)
    if value_filter is not None:
        df = df[value_filter(df)]
    return gpd.GeoDataFrame(df, geometry=converter(df))


def load(
        desc: str, df: DataFrame,
        converter: Callable[[pd.Series], Any]
) -> Dict[Any, Any]:
    table: Dict[Any, Any] = {}
    for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc=desc):
        table[idx] = converter(row)
    return table


class Dataset:

    def __init__(self):
        self._table_traffic = pd.read_csv(TRAFFIC_DATA_FILE, index_col='GlobalID', low_memory=False)
        self._table_nodes = read_geo(
            NODES_FILE, 'osmid',
            (lambda data: (data['y'] >= 39.18) & (data['y'] <= 39.33) &
                          (data['x'] >= -76.71) & (data['x'] <= -76.45)),
            (lambda data: gpd.GeoSeries.from_wkt(data['geometry']))
        )
        self._table_edges = read_geo(
            EDGES_FILE, ['u', 'v', 'key'],
            (lambda data: (data.index.get_level_values(0).isin(self._table_nodes.index)) &
                          (data.index.get_level_values(1).isin(self._table_nodes.index))),
            converter=(lambda data: gpd.GeoSeries.from_wkt(data['geometry']))
        )

        self._table_bus_stops = read_geo(
            STOPS_FILE, 'stop_id',
            converter=(lambda data: [Point(xy) for xy in zip(data['X'], data['Y'])])
        )
        self._table_bus_routes = pd.read_csv(ROUTES_FILE, index_col='Route_Numb', low_memory=False)

        self._traffic = None
        self._nodes = None
        self._edges = None
        self._bus_routes = None
        self._bus_stops = None

    def load(self):
        self._traffic = load("|TRAFFIC", self._table_traffic, (lambda row: Traffic(self, row)))
        self._nodes = load("|  NODES", self._table_nodes, (lambda row: Node(self, row)))
        self._edges = load("|  EDGES", self._table_edges, (lambda row: Edge(self, row)))
        self._bus_routes = load("| ROUTES", self._table_bus_routes, (lambda row: BusRoute(self, row)))
        self._bus_stops = load("|  STOPS", self._table_bus_stops, (lambda row: BusStop(self, row)))

    @property
    def table_traffic(self) -> pd.DataFrame:
        return self._table_traffic

    @property
    def table_nodes(self) -> GeoDataFrame:
        return self._table_nodes

    @property
    def table_edges(self) -> GeoDataFrame:
        return self._table_edges

    @property
    def table_bus_routes(self) -> pd.DataFrame:
        return self._table_bus_routes

    @property
    def table_bus_stops(self) -> GeoDataFrame:
        return self._table_bus_stops

    def bus_routes(self) -> List['BusRoute']:
        return list(self._bus_routes.values())

    def bus_route(self, key: str) -> Optional['BusRoute']:
        return self._bus_routes.get(key)

    @property
    def bus_stops(self) -> List['BusStop']:
        return list(self._bus_stops.values())

    def bus_stop(self, key: int) -> Optional['BusStop']:
        return self._bus_stops.get(key)

    @property
    def nodes(self) -> List['Node']:
        return list(self._nodes.values())

    def node(self, key: int) -> Optional['Node']:
        return self._nodes.get(key)

    @property
    def edges(self) -> List['Edge']:
        return list(self._edges.values())

    def edge(self, key: Tuple[int, int, int]) -> Optional['Edge']:
        return self._edges.get(key)

    @property
    def traffic(self) -> List['Traffic']:
        return list(self._traffic.values())

    def traffic_data(self, key: int) -> Optional['Traffic']:
        return self._traffic.get(key)

    def memory_usage(self):
        return sum([sys.getsizeof(obj) for obj in [self._bus_routes, self._bus_stops, self._nodes, self._edges]])


class Node:
    """Represents a geographic node in the transportation network."""

    def __init__(self, parent: Dataset, data: pd.DataFrame):
        self._parent = parent
        self._data = data

    @property
    def id(self) -> int:
        """Get the unique OpenStreetMap ID."""
        return self._data.name

    @property
    def type(self) -> Optional[str]:
        """Indicates the type of road or path."""
        return self._data.get('highway', None)

    @property
    def ref(self) -> Optional[str]:
        """A reference code for the road, path, or other infrastructure."""
        return self._data.get('ref', None)

    @property
    def street_count(self) -> Optional[int]:
        """The number of streets (or ways) connected to a particular node. It can indicate intersections or endpoints."""
        return self._data.get('street_count', None)

    @property
    def railway(self) -> Optional[str]:
        """Specifies if the node or way is part of a railway."""
        return self._data.get('railway', None)

    @property
    def edges(self) -> List['Edge']:
        """Get all edges connected to this node."""
        return [edge for edge in self._parent.edges if edge.node_u == self or edge.node_v == self]

    @property
    def point(self) -> Point:
        return Point(self._data['x'], self._data['y'])


class Edge:
    """Represents a road segment with traffic analytics."""

    def __init__(self, parent: Dataset, frame: pd.DataFrame):
        self._parent = parent
        self._data = frame

    @property
    def u(self) -> int:
        return self._data.name[0]

    @property
    def v(self) -> int:
        return self._data.name[1]

    @property
    def node_u(self) -> Node:
        return self._parent.node(self.u)

    @property
    def node_v(self) -> Node:
        return self._parent.node(self.v)

    @property
    def key(self) -> int:
        return self._data.name[2]

    @property
    def osm_id(self) -> List[int]:
        # a single int or json int array
        if isinstance(self._data['osmid'], int):
            return [self._data['osmid']]
        return self._data['osmid']

    @property
    def access(self) -> str:
        return self._data.get('access', '')

    @property
    def highway(self) -> str:
        return self._data.get('highway', '')

    @property
    def name(self) -> str:
        return self._data['name']

    @property
    def lanes(self) -> int:
        return self._data.get('lanes', 1)

    @property
    def speed_limit(self) -> Optional[int]:
        return self._data['maxspeed'].str.extract(r'(\d+)').astype(float).iloc[0]

    @property
    def oneway(self) -> bool:
        """Indicates whether the road is one-way (yes or no).
         It may also include specific flow directions like -1 for reversed direction."""
        return self._data['oneway'] == 'TRUE'

    @property
    def ref(self) -> Optional[str]:
        return self._data.get('ref', None)

    @property
    def reversed(self) -> bool:
        return self._data['reversed'] == 'TRUE'

    @property
    def bridge(self) -> bool:
        """Indicates whether the segment is a bridge (yes or no).
         It may also include additional details about the bridge."""
        return self._data['bridge'] == 'yes'

    @property
    def junction(self) -> Optional[str]:
        """Provides details about the type of junction."""
        return self._data.get('junction', None)

    @property
    def width(self) -> Optional[str]:
        """The width of the road or pathway in meters."""
        return self._data.get('width', None)

    @property
    def tunnel(self) -> Optional[str]:
        return self._data.get('tunnel', None)

    @property
    def service(self) -> Optional[str]:
        """Describes the type of service associated with the road."""
        return self._data.get('service', None)

    @property
    def length(self) -> float:
        return self._data.get('length', 0)

    @property
    def geometry(self) -> str:
        """Get WKT representation of the edge geometry."""
        return self._data.get('geometry', '')


class Traffic:
    """Represents traffic analytics data for a road segment with temporal accessors."""

    def __init__(self, parent: Dataset, frame: pd.DataFrame):  # 注意这里实际是pd.Series而非DataFrame
        self._parent = parent
        self._data = frame

    # ------------------ Core Properties ------------------
    @property
    def node_start(self) -> List[int]:
        """OSMid list for road section start nodes."""
        raw = self._data.get('node start')
        return eval(raw) if pd.notna(raw) else []

    @property
    def node_end(self) -> List[int]:
        """OSMid list for road section end nodes."""
        raw = self._data.get('node(s) end')
        return eval(raw) if pd.notna(raw) else []

    @property
    def gis_object_id(self) -> int:
        return self._data['GIS Object ID']

    @property
    def station_id(self) -> Optional[str]:
        return self._data.get('Station ID')

    @property
    def road_name(self) -> Optional[str]:
        return self._data.get('Road Name')

    @property
    def route_prefix(self) -> Optional[str]:
        return self._data.get('Route Prefix')

    @property
    def route_number(self) -> Optional[str]:
        return self._data.get('Route Number')

    @property
    def k_factor(self) -> Optional[float]:
        return safe_float(self._data.get('K-Factor'))

    @property
    def d_factor(self) -> Optional[float]:
        return safe_float(self._data.get('D-Factor'))

    # ------------------ Temporal Data Accessors ------------------
    def aadt(self, year: int) -> Optional[float]:
        """处理混合数据类型（如示例中的空单元格）"""
        if year >= 2023:
            return safe_float(self._data.get('AADT (Current)'))
        return safe_float(self._data.get(f"AADT {year}"))

    def aawdt(self, year: int) -> Optional[float]:
        if year >= 2023:
            return safe_float(self._data.get('AAWDT (Current)'))
        return safe_float(self._data.get(f"AAWDT {year}"))

    # ------------------ Vehicle-Type Data Accessors ------------------
    def aadt_vehicle(self, vehicle_type: str) -> Optional[float]:
        """处理空值（如示例中某些车型数据为空白）"""
        return safe_float(self._data.get(f"AADT {vehicle_type}"))

    @property
    def aadt_motorcycle(self) -> Optional[float]:
        return self.aadt_vehicle('Motorcycle')

    @property
    def aadt_bus(self) -> Optional[float]:
        return self.aadt_vehicle('Bus')


class BusRoute:
    """Represents a bus route with flexible initialization and full data access."""

    def __init__(self, parent: Dataset, df: pd.DataFrame):
        self._parent = parent
        self._data = df
        self._stops = None

    @property
    def key(self) -> str:
        """Get the formal route key (e.g., 'Route 22' or 'CityLink PURPLE')."""
        return self._data.name

    @property
    def name(self) -> str:
        """Get the human-readable route name."""
        return self._data['Route_Name']

    @property
    def type(self) -> str:
        """Get the route type (e.g., 'Local', 'Express')."""
        return self._data['Route_Type']

    @property
    def shape_length(self) -> float:
        """Get the GIS length of the route."""
        return self._data.get('Shape__Length', 0)

    @property
    def stops(self) -> List['BusStop']:
        """Get all stops served by this route (lazy-loaded)."""
        if not hasattr(self, '_stops'):
            self._stops = [s for s in self._parent.bus_stops if s.serving(self)]
        return self._stops


class BusStop:
    """Represents a bus stop with spatial capabilities."""

    def __init__(self, parent: Dataset, df: pd.DataFrame):
        self._parent = parent
        self._data = df
        self._node = None  # Lazy-loaded nearest node
        self._routes = None  # Lazy-loaded routes

    @property
    def id(self) -> int:
        return int(self._data['stop_id'])

    @property
    def name(self) -> str:
        return self._data['stop_name']

    @property
    def mode(self) -> str:
        return self._data['Mode']

    @property
    def routes_served(self) -> List[str]:
        return self._data['Routes_Ser'].split(',')

    def serving(self, route: BusRoute) -> bool:
        return route.key in self.routes_served or BUS_ROUTE_TYPE_MAPPER.get(route.key, route.key) in self.routes_served

    @property
    def routes(self) -> List[BusRoute]:
        """Get all routes passing through this stop."""
        if not hasattr(self, '_routes'):
            self._routes = [route for route in self._parent.bus_routes() if self.serving(route)]
        return self._routes

    @property
    def rider_on(self) -> int:
        """Get daily riders on at this stop."""
        return self._data.get('Rider_On', 0)

    @property
    def rider_off(self) -> int:
        """Get daily riders off at this stop."""
        return self._data.get('Rider_Off', 0)

    @property
    def rider_stop(self) -> int:
        """Get daily riders stop at this stop."""
        return self._data.get('Stop_Rider', 0)

    @property
    def rider_total(self) -> int:
        """Get total daily riders at this stop."""
        return self._data.get('Rider_Total', 0)

    @property
    def shelter(self) -> bool:
        """Check if this stop has a shelter."""
        return self._data['Shelter'] == 'Yes'
