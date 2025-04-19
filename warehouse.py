class WarehouseLogistics:
    def __init__(self):
        self.stock_center_map = {}  # Maps stock to (center, unit_weight)
        self.transport_graph = {}   # Graph of center/destination connections
        self.destinations = set()  # All delivery destinations (L1, L2, etc.)
        
    def add_stock(self, stock_name, center, unit_weight):
        """Register a stock item with its center and unit weight"""
        self.stock_center_map[stock_name] = (center, unit_weight)
        
    def add_destination(self, *destinations):
        """Add one or more delivery destinations"""
        for dest in destinations:
            self.destinations.add(dest)
        
    def add_route(self, point1, point2, distance):
        """Connect two points with a transport route"""
        for point in [point1, point2]:
            if point not in self.transport_graph:
                self.transport_graph[point] = []
        
        self.transport_graph[point1].append((point2, distance))
        self.transport_graph[point2].append((point1, distance))
        
        # Auto-detect destinations (points starting with 'L')
        if point1.startswith('L'):
            self.destinations.add(point1)
        if point2.startswith('L'):
            self.destinations.add(point2)
    
    def calculate_center_loads(self, order):
        """
        Calculate total weight at each center based on order quantities
        Returns: {center: total_weight}
        """
        center_loads = {}
        
        for stock, quantity in order.items():
            if stock not in self.stock_center_map:
                raise ValueError(f"Unknown stock item: {stock}")
                
            center, unit_weight = self.stock_center_map[stock]
            center_loads[center] = center_loads.get(center, 0) + unit_weight * quantity
            
        return center_loads
    
    def find_min_transport_cost(self, order, destination='L1'):
        """
        Calculate minimum transport cost to deliver order to destination
        """
        if destination not in self.destinations:
            raise ValueError(f"Invalid destination: {destination}")
            
        center_loads = self.calculate_center_loads(order)
        # print(center_loads)
        # print(self.destinations)
        # print(self.stock_center_map)
        # print(self.transport_graph)
        active_centers = {c for c in center_loads if center_loads[c] > 0}
        # print(active_centers)
        # Base case: no centers to visit
        if not active_centers:
            return 0
            
        min_cost = float('inf')
        
        # Try starting from each center
        for start_center in active_centers:
            cost = self._calculate_route_cost(
                current=start_center,
                visited={start_center},
                remaining=active_centers - {start_center},
                current_weight=center_loads[start_center],
                destination=destination,
                center_loads=center_loads  # Pass the center_loads dictionary
            )
            # print(start_center,cost)
            min_cost = min(min_cost, cost)
            
        return min_cost if min_cost != float('inf') else 0
    
    def _calculate_route_cost(self, current, visited, remaining, current_weight, destination, center_loads):
        """
        Recursive helper to calculate transport cost for a specific route
        """
        # print(current,current_weight)
        # Determine transport cost factor based on weight
        cost_factor = 10 if current_weight <= 5 else 18
        
        # If we're at destination and all centers visited
        if current == destination and not remaining:
            return 0
            
        min_cost = float('inf')
        
        # Explore all connected points
        for neighbor, distance in self.transport_graph.get(current, []):
            transport_cost = distance * cost_factor
            
            # Case 1: Moving to destination (only allowed if all centers visited)
            if neighbor == destination:
                if not remaining:
                    total_cost = transport_cost + self._calculate_route_cost(
                        current=neighbor,
                        visited=visited,
                        remaining=remaining,
                        current_weight=0,
                        destination=destination,
                        center_loads=center_loads
                    )
                    min_cost = min(min_cost, total_cost)
            
            # Case 2: Moving to an unvisited center
            elif neighbor in remaining:
                new_weight = current_weight + center_loads.get(neighbor, 0)
                total_cost = transport_cost + self._calculate_route_cost(
                    current=neighbor,
                    visited=visited | {neighbor},
                    remaining=remaining - {neighbor},
                    current_weight=new_weight,
                    destination=destination,
                    center_loads=center_loads
                )
                min_cost = min(min_cost, total_cost)
                
        return min_cost


# Example Usage
if __name__ == "__main__":
    # Initialize system
    warehouse = WarehouseLogistics()
    
    # Configure stocks
    stocks = {
        'A': ('C1', 3), 'B': ('C1', 2), 'C': ('C1', 8),
        'D': ('C2', 12), 'E': ('C2', 25), 'F': ('C2', 15),
        'G': ('C3', 0.5), 'H': ('C3', 1), 'I': ('C3', 2)
    }
    for stock, (center, weight) in stocks.items():
        warehouse.add_stock(stock, center, weight)
    
    # Configure destinations and routes
    warehouse.add_destination('L1')
    routes = [
        ('C1', 'C2', 4), ('C1', 'L1', 3),
        ('C2', 'L1', 2.5), ('C2', 'C3', 3),
        ('C3', 'L1', 2)
    ]
    for point1, point2, dist in routes:
        warehouse.add_route(point1, point2, dist)
    
    # Calculate transport cost for an order
    order = {'A': 1, 'B': 1, 'D': 1}  # 1 unit each of A, B, D
    min_cost = warehouse.find_min_transport_cost(order)
    print(f"Minimum transport cost to L1: {min_cost}")