from dataclasses import dataclass
from typing import List, Optional
from _references import *

import pandas as pd

ROUTE_MAPPER = {
    'BR': 'CityLink BROWN', 'BL': 'CityLink BLUE', 'GL': 'CityLink GOLD',
    'GR': 'CityLink GREEN', 'OR': 'CityLink ORANGE', 'PK': 'CityLink PINK',
    'PR': 'CityLink PURPLE', 'RD': 'CityLink RED', 'SV': 'CityLink SILVER',
    'YW': 'CityLink YELLOW', 'NV': 'CityLink NAVY'
}

OpenStreetMapID = List[int]


@dataclass
class Coordinates:
    longitude: float
    latitude: float

    def distance(self, other: 'Coordinates') -> float:
        """Calculate the distance between two coordinates."""
        return ((self.longitude - other.longitude) ** 2 + (self.latitude - other.latitude) ** 2) ** 0.5


class DataLoader:
    """Central class to load and cache datasets with unified naming."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        """Load datasets with explicit dtype handling."""
        self.bus_routes = pd.read_csv(ROUTES_FILE, index_col='Route_Numb', low_memory=False)
        self.bus_stops = pd.read_csv(STOPS_FILE, index_col='stop_id', low_memory=False)
        self.nodes = pd.read_csv(NODES_FILE, index_col='osmid', low_memory=False)
        self.edges = pd.read_csv(EDGES_FILE, index_col=['u', 'v', 'key'], low_memory=False)
        self.traffic_data = pd.read_csv(TRAFFIC_DATA_FILE, low_memory=False)


class BusRoute:
    """Represents a bus route with flexible initialization and full data access."""

    def __init__(self, df: pd.DataFrame):
        self._data = df

    @classmethod
    def from_key(cls, identifier: str):
        return cls(DataLoader().bus_routes.loc[identifier])

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
            stop_ids = self.loader.bus_stops[
                self.loader.bus_stops['routes'].str.contains(self.key, na=False)
            ].index.tolist()
            self._stops = [BusStop(stop_id) for stop_id in stop_ids]
        return self._stops


class BusStop:
    """Represents a bus stop with spatial capabilities."""

    def __init__(self, frame: pd.DataFrame):
        self._data = frame
        self._node = None  # Lazy-loaded nearest node
        self._routes = None  # Lazy-loaded routes

    @classmethod
    def from_identifier(cls, identifier: str):
        return cls(DataLoader().bus_stops.loc[identifier])

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

    @property
    def routes(self) -> List[BusRoute]:
        """Get all routes passing through this stop."""
        if self._routes is None:
            self._routes = [BusRoute.from_key(ROUTE_MAPPER.get(key, key)) for key in self.routes_served]
        return self._routes

    def belongs_to(self, parent: BusRoute) -> bool:
        return parent.key in self._data['Routes_Ser']

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


class Node:
    """Represents a geographic node in the transportation network."""

    def __init__(self, frame: pd.DataFrame):
        self._data = frame

    @classmethod
    def from_id(cls, identifier: int):
        return cls(DataLoader().nodes.loc[identifier])

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
        edges_u = DataLoader().edges.xs(self.id, level='u')
        edges_v = DataLoader().edges.xs(self.id, level='v')
        return [Edge(u, v, key) for (u, v, key) in edges_u.index.append(edges_v.index)]

    @property
    def coordinates(self) -> Coordinates:
        """Get (longitude, latitude) point."""
        return Coordinates(self._data['x'], self._data['y'])


class Edge:
    """Represents a road segment with traffic analytics."""

    def __init__(self, u: int, v: int, key: int = 0):
        self.loader = DataLoader()
        self._data = self.loader.edges.loc[(u, v, key)]
        self._u = Node(u)
        self._v = Node(v)

    @property
    def u(self) -> Node:
        return self._u

    @property
    def v(self) -> Node:
        return self._v

    @property
    def key(self) -> int:
        return self._data.name[2]

    @property
    def osm_id(self) -> OpenStreetMapID:
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
    def traffic(self) -> Optional[pd.Series]:
        """Get traffic data for this edge."""
        traffic_df = self.loader.traffic_data
        mask = (traffic_df['node_start'] == self.u) & (traffic_df['node_end'] == self.v)
        return traffic_df[mask].iloc[0] if not traffic_df[mask].empty else None

    def aadt(self, year: Optional[int] = None) -> float:
        """Get Annual Average Daily Traffic."""
        if year:
            return self.traffic.get(f'aadt_{year}', None)
        return self.traffic.get('aadt_(current)', None)

    def aawdt(self, year: Optional[int] = None) -> float:
        """Get Annual Average Weekday Traffic."""
        if year:
            return self.traffic.get(f'aawdt_{year}', None)
        return self.traffic.get('aawdt_(current)', None)

    @property
    def geometry(self) -> str:
        """Get WKT representation of the edge geometry."""
        return self._data.get('geometry', '')
