import re
import uuid
import math
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

receipts_store = {}
points_store = {}

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def validate_receipt(receipt):
    """Validates a receipt according to the API specification"""
    # Check required fields
    required_fields = ['retailer', 'purchaseDate', 'purchaseTime', 'items', 'total']
    for field in required_fields:
        if field not in receipt:
            raise ValidationError(f"Missing required field: {field}")
    
    # Validate retailer pattern (alphanumeric, spaces, hyphens, and ampersands)
    if not re.match(r'^[\w\s\-&]+$', receipt['retailer']):
        raise ValidationError("Invalid retailer name")
    
    # Validate purchase date format (YYYY-MM-DD)
    try:
        datetime.strptime(receipt['purchaseDate'], '%Y-%m-%d')
    except ValueError:
        raise ValidationError("Invalid purchase date format")
    
    # Validate purchase time format (HH:MM)
    try:
        datetime.strptime(receipt['purchaseTime'], '%H:%M')
    except ValueError:
        raise ValidationError("Invalid purchase time format")
    
    # Validate total format
    if not re.match(r'^\d+\.\d{2}$', receipt['total']):
        raise ValidationError("Invalid total format")
    
    # Validate items
    if not isinstance(receipt['items'], list) or len(receipt['items']) < 1:
        raise ValidationError("At least one item is required")
    
    for item in receipt['items']:
        # Check required item fields
        if 'shortDescription' not in item or 'price' not in item:
            raise ValidationError("Items must have shortDescription and price")
        
        # Validate short description pattern
        if not re.match(r'^[\w\s\-]+$', item['shortDescription']):
            raise ValidationError("Invalid item description")
        
        # Validate price pattern
        if not re.match(r'^\d+\.\d{2}$', item['price']):
            raise ValidationError("Invalid item price format")

def calculate_points(receipt):
    """Calculates points for a receipt according to the rules"""
    points = 0
    
    # Rule 1: One point for every alphanumeric character in the retailer name
    alphanumeric_count = sum(1 for char in receipt['retailer'] if char.isalnum())
    points += alphanumeric_count
    
    # Rule 2: 50 points if the total is a round dollar amount with no cents
    total_float = float(receipt['total'])
    if total_float == int(total_float):
        points += 50
    
    # Rule 3: 25 points if the total is a multiple of 0.25
    if total_float * 100 % 25 == 0:
        points += 25
    
    # Rule 4: 5 points for every two items on the receipt
    points += 5 * (len(receipt['items']) // 2)
    
    # Rule 5: If the trimmed length of the item description is a multiple of 3,
    # multiply the price by 0.2 and round up to the nearest integer
    for item in receipt['items']:
        trimmed_desc = item['shortDescription'].strip()
        if len(trimmed_desc) % 3 == 0 and len(trimmed_desc) > 0:
            price = float(item['price'])
            points_for_item = math.ceil(price * 0.2)
            points += points_for_item
    
    # Rule 6: 6 points if the day in the purchase date is odd
    purchase_date = datetime.strptime(receipt['purchaseDate'], '%Y-%m-%d')
    if purchase_date.day % 2 == 1:
        points += 6
    
    # Rule 7: 10 points if the time of purchase is after 2:00pm and before 4:00pm
    purchase_time = datetime.strptime(receipt['purchaseTime'], '%H:%M')
    purchase_hour = purchase_time.hour
    purchase_minute = purchase_time.minute
    purchase_minutes = purchase_hour * 60 + purchase_minute
    
    if 14 * 60 < purchase_minutes < 16 * 60:
        points += 10
    
    return points

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    """Processes a receipt and returns its ID"""
    try:
        receipt = request.json
        validate_receipt(receipt)
        receipt_id = str(uuid.uuid4())
        receipts_store[receipt_id] = receipt
        points_store[receipt_id] = calculate_points(receipt)
        
        return jsonify({"id": receipt_id})
    
    except ValidationError as e:
        return jsonify({"error": "The receipt is invalid."}), 400
    except Exception as e:
        return jsonify({"error": "The receipt is invalid."}), 400

@app.route('/receipts/<receipt_id>/points', methods=['GET'])
def get_points(receipt_id):
    """Returns the points for a receipt"""
    
    if receipt_id not in receipts_store:
        return jsonify({"error": "No receipt found for that ID."}), 404
    
    return jsonify({"points": points_store[receipt_id]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)