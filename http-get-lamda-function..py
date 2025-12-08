import json

def lambda_handler(event, context):
    name = "World"
    if event.get('queryStringParameters'):
        name = event.get('queryStringParameters').get('name', name)

    response_data = {
        "message": f"Hello, {name}! Your request was successful.",
        "status": "success"
    }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response_data)
    }
