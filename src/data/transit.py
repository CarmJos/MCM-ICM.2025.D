from shapely.geometry.point import Point

from _references import STOPS_FILE, ROUTES_FILE
from data import *

BUS_ROUTE_TYPE_MAPPER = {
    'BR': 'CityLink BROWN', 'BL': 'CityLink BLUE', 'GL': 'CityLink GOLD',
    'GR': 'CityLink GREEN', 'OR': 'CityLink ORANGE', 'PK': 'CityLink PINK',
    'PR': 'CityLink PURPLE', 'RD': 'CityLink RED', 'SV': 'CityLink SILVER',
    'YW': 'CityLink YELLOW', 'NV': 'CityLink NAVY'
}


class TransitSet:

    def __init__(self):
        self._table_bus_stops = read_geo(
            STOPS_FILE, 'stop_id',
            converter=(lambda data: [Point(xy) for xy in zip(data['X'], data['Y'])])
        )
        self._table_bus_routes = pd.read_csv(ROUTES_FILE, index_col='Route_Numb', low_memory=False)

        self._bus_routes = None
        self._bus_stops = None

    def load(self):
        self._bus_routes = load("| ROUTES", self._table_bus_routes, (lambda row: BusRoute(self, row)))
        self._bus_stops = load("|  STOPS", self._table_bus_stops, (lambda row: BusStop(self, row)))

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


class BusRoute:
    """Represents a bus route with flexible initialization and full data access."""

    def __init__(self, parent: TransitSet, df: pd.DataFrame):
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

    def __init__(self, parent: TransitSet, df: pd.DataFrame):
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
