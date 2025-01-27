import sys
from typing import Tuple

from shapely.geometry.linestring import LineString
from shapely.geometry.point import Point

from _references import *
from data import *


class Dataset:

    def __init__(self):
        self._table_nodes = read_geo(
            NODES_FILE, 'osmid',
            (lambda data: (data['y'] >= 39.18) & (data['y'] <= 39.33) &
                          (data['x'] >= -76.71) & (data['x'] <= -76.45)),
            converter=(lambda data: gpd.GeoSeries.from_wkt(data['geometry']))
        )
        self._table_edges = read_geo(
            EDGES_FILE, ['u', 'v', 'key'],
            (lambda data: (data.index.get_level_values(0).isin(self._table_nodes.index)) &
                          (data.index.get_level_values(1).isin(self._table_nodes.index))),
            converter=(lambda data: gpd.GeoSeries.from_wkt(data['geometry']))
        )

        self._traffic = None
        self._nodes = None
        self._edges = None

    def load(self):
        self._nodes = load("|  NODES", self._table_nodes, (lambda row: Node(self, row)))
        self._edges = load("|  EDGES", self._table_edges, (lambda row: Edge(self, row)))

    @property
    def table_nodes(self) -> GeoDataFrame:
        return self._table_nodes

    @property
    def table_edges(self) -> GeoDataFrame:
        return self._table_edges

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
    def speed_limit(self) -> Optional[str]:
        return self._data.get('maxspeed', None)

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
    def geometry(self) -> LineString:
        """Get WKT representation of the edge geometry."""
        return self._data['geometry']
