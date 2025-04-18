# Receipt Processor Solution (Python)

This is a Python Flask implementation of the Receipt Processor API challenge.

## Features

- Processes receipts and assigns them unique IDs
- Calculates points for receipts according to the specified rules
- Provides a RESTful API with the required endpoints
- Includes validation for all input fields

## Running the Application

### Option 1: Run with Python

If you have Python installed (3.7 or higher recommended):

1. Clone the repository
2. Navigate to the project directory
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python app.py
   ```
5. The server will start on port 8080

### Option 2: Run with Docker

If you have Docker installed:

1. Clone the repository
2. Navigate to the project directory
3. Build the Docker image:
   ```
   docker build -t receipt-processor .
   ```
4. Run the Docker container:
   ```
   docker run -p 8080:8080 receipt-processor
   ```
5. The server will be accessible on port 8080

## API Usage

### Process a Receipt

```
POST /receipts/process
```

Example request:
```bash
curl -X POST http://localhost:8080/receipts/process \
  -H "Content-Type: application/json" \
  -d '{
    "retailer": "Target",
    "purchaseDate": "2022-01-01",
    "purchaseTime": "13:01",
    "items": [
      {
        "shortDescription": "Mountain Dew 12PK",
        "price": "6.49"
      }
    ],
    "total": "6.49"
  }'
```

Example response:
```json
{
  "id": "a9188250-d8a6-4687-96d3-f862e72e422a"
}
```

### Get Points for a Receipt

```
GET /receipts/{id}/points
```

Example request:
```bash
curl -X GET http://localhost:8080/receipts/a9188250-d8a6-4687-96d3-f862e72e422a/points
```

Example response:
```json
{
  "points": 28
}
```

## Testing

To run the tests:

```
pytest test_app.py
```

### Example Test Cases

The implementation has been tested with the example receipts provided in the challenge:

1. The Target receipt with multiple items (expected: 28 points)
2. The M&M Corner Market receipt (expected: 109 points)
3. Additional test cases for each point calculation rule

## Implementation Notes

- Data is stored in memory and will be lost when the application stops
- UUIDs are generated for receipt IDs
- The application follows the API spec as defined in the provided api.yml file
- Input validation is performed according to the API specification

## Point Calculation Rules

The implementation includes all the specified rules for calculating points:

- One point for every alphanumeric character in the retailer name
- 50 points if the total is a round dollar amount with no cents
- 25 points if the total is a multiple of 0.25
- 5 points for every two items on the receipt
- Special points for item descriptions that are multiples of 3 in length
- 6 points if the day in the purchase date is odd
- 10 points if the time of purchase is after 2:00pm and before 4:00pm