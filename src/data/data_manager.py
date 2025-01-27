from data.data_types import *
from tqdm import tqdm

LOADER = DataLoader()  # Initialize

def all_bus_routes() -> List[BusRoute]:
    """Get all bus routes in the dataset."""
    return [BusRoute(route_id) for route_id in tqdm(LOADER.bus_routes.index, ncols=100, dynamic_ncols=False,  desc="ROUTES")]


def all_bus_stops() -> List[BusStop]:
    """Get all bus stops in the dataset."""
    return [BusStop(stop_id) for stop_id in tqdm(LOADER.bus_stops.index, ncols=100, dynamic_ncols=False,  desc="STOPS ")]


def all_nodes() -> List[Node]:
    """Get all nodes in the dataset."""
    return [Node(node_id) for node_id in tqdm(LOADER.nodes.index, ncols=100,  dynamic_ncols=False, desc="NODES ")]


def all_edges() -> List[Edge]:
    """Get all edges in the dataset."""
    return [Edge(u, v, key) for (u, v, key) in tqdm(LOADER.edges.index, ncols=100, dynamic_ncols=False, desc="EDGES ")]


