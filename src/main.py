from data.data_manager import *

if __name__ == '__main__':
    print("Loading dataset...")
    bus_routes = all_bus_routes()
    bus_stops = all_bus_stops()
    nodes = all_nodes()
    edges = all_edges()

    print("COUNT: ")
    print(f"- bus_routes: {len(bus_routes)}")
    print(f"- bus_stops: {len(bus_stops)}")
    print(f"- nodes: {len(nodes)}")
    print(f"- edges: {len(edges)}")
