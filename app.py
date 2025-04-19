from flask import Flask, request, jsonify
from warehouse import WarehouseLogistics  # Assuming your class is in this file

app = Flask(__name__)

# A welcome message
@app.route('/')
def home():
    return "🚀 This Warehouse Logistics API was built by a PSITian! Use /calculate_cost to access the API."

# Initialize the warehouse system (you could move this to a config file)
def initialize_warehouse():
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
    
    return warehouse

# Global warehouse instance
warehouse = initialize_warehouse()

@app.route('/calculate_cost', methods=['POST'])
def calculate_cost():
    """
    Endpoint that accepts JSON order data and returns transport cost
    Example input: {"A": 1, "B": 2, "D": 1}
    """
    try:
        # Get JSON data from request
        order_data = request.get_json()
        
        if not order_data:
            return jsonify({"error": "No order data provided"}), 400
        
        # Calculate minimum transport cost
        min_cost = warehouse.find_min_transport_cost(order_data)
        
        # Prepare response
        response = {
            "order": order_data,
            "minimum_transport_cost": min_cost,
            "destination": "L1"  # Default destination
        }
        
        return jsonify(response), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)