import unittest
import json
from app import app, calculate_points, validate_receipt, ValidationError

class TestReceiptProcessor(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_example_receipt_1_points(self):
        """Test the first example receipt from the README"""
        receipt = {
            "retailer": "Target",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [
                {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
                {"shortDescription": "Emils Cheese Pizza", "price": "12.25"},
                {"shortDescription": "Knorr Creamy Chicken", "price": "1.26"},
                {"shortDescription": "Doritos Nacho Cheese", "price": "3.35"},
                {"shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ", "price": "12.00"}
            ],
            "total": "35.35"
        }
        
        points = calculate_points(receipt)
        self.assertEqual(points, 28)
    
    def test_example_receipt_2_points(self):
        """Test the second example receipt from the README"""
        receipt = {
            "retailer": "M&M Corner Market",
            "purchaseDate": "2022-03-20",
            "purchaseTime": "14:33",
            "items": [
                {"shortDescription": "Gatorade", "price": "2.25"},
                {"shortDescription": "Gatorade", "price": "2.25"},
                {"shortDescription": "Gatorade", "price": "2.25"},
                {"shortDescription": "Gatorade", "price": "2.25"}
            ],
            "total": "9.00"
        }
        
        points = calculate_points(receipt)
        self.assertEqual(points, 109)
    
    def test_process_endpoint(self):
        """Test the /receipts/process endpoint"""
        receipt = {
            "retailer": "Target",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [
                {"shortDescription": "Mountain Dew 12PK", "price": "6.49"}
            ],
            "total": "6.49"
        }
        
        response = self.app.post('/receipts/process', 
                                json=receipt,
                                content_type='application/json')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', data)
        self.assertTrue(len(data['id']) > 0)
        
        # Now test getting points
        receipt_id = data['id']
        response = self.app.get(f'/receipts/{receipt_id}/points')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('points', data)
        self.assertIsInstance(data['points'], int)
    
    def test_invalid_receipt_validation(self):
        """Test validation of invalid receipts"""
        # Invalid retailer
        with self.assertRaises(ValidationError):
            validate_receipt({
                "retailer": "Target$", # Invalid character
                "purchaseDate": "2022-01-01",
                "purchaseTime": "13:01",
                "items": [{"shortDescription": "Test", "price": "1.00"}],
                "total": "1.00"
            })
        
        # Invalid date
        with self.assertRaises(ValidationError):
            validate_receipt({
                "retailer": "Target",
                "purchaseDate": "01-01-2022", # Wrong format
                "purchaseTime": "13:01",
                "items": [{"shortDescription": "Test", "price": "1.00"}],
                "total": "1.00"
            })
        
        # Invalid time
        with self.assertRaises(ValidationError):
            validate_receipt({
                "retailer": "Target",
                "purchaseDate": "2022-01-01",
                "purchaseTime": "1:01 PM", # Wrong format
                "items": [{"shortDescription": "Test", "price": "1.00"}],
                "total": "1.00"
            })
        
        # Invalid total
        with self.assertRaises(ValidationError):
            validate_receipt({
                "retailer": "Target",
                "purchaseDate": "2022-01-01",
                "purchaseTime": "13:01",
                "items": [{"shortDescription": "Test", "price": "1.00"}],
                "total": "1.0" # No cents
            })
        
        # No items
        with self.assertRaises(ValidationError):
            validate_receipt({
                "retailer": "Target",
                "purchaseDate": "2022-01-01",
                "purchaseTime": "13:01",
                "items": [],
                "total": "1.00"
            })
    
    def test_individual_point_rules(self):
        """Test each point calculation rule individually"""
        # Test retailer name points
        receipt = {
            "retailer": "ABCDEF123", # 9 alphanumeric chars
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [{"shortDescription": "Test", "price": "1.00"}],
            "total": "1.00"
        }
        points = calculate_points(receipt)
        self.assertGreaterEqual(points, 9)  # Should have at least 9 points for retailer name
        
        # Test round dollar amount
        receipt = {
            "retailer": "X",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [{"shortDescription": "Test", "price": "1.00"}],
            "total": "1.00" # Round dollar
        }
        points = calculate_points(receipt)
        self.assertGreaterEqual(points, 50)  # Should have at least 50 points for round dollar
        
        # Test multiple of 0.25
        receipt = {
            "retailer": "X",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [{"shortDescription": "Test", "price": "1.25"}],
            "total": "1.25" # Multiple of 0.25
        }
        points = calculate_points(receipt)
        self.assertGreaterEqual(points, 25)  # Should have at least 25 points for multiple of 0.25
        
        # Test odd day
        receipt = {
            "retailer": "X",
            "purchaseDate": "2022-01-01", # 1st is odd
            "purchaseTime": "13:01",
            "items": [{"shortDescription": "Test", "price": "1.00"}],
            "total": "1.00"
        }
        points = calculate_points(receipt)
        self.assertGreaterEqual(points, 6)  # Should have at least 6 points for odd day
        
        # Test time between 2:00pm and 4:00pm
        receipt = {
            "retailer": "X",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "15:30", # 3:30 PM
            "items": [{"shortDescription": "Test", "price": "1.00"}],
            "total": "1.00"
        }
        points = calculate_points(receipt)
        self.assertGreaterEqual(points, 10)  # Should have at least 10 points for afternoon time

if __name__ == '__main__':
    unittest.main()