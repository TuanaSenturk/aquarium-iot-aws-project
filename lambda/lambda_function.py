import json
import os
from datetime import datetime, timezone
from decimal import Decimal

import boto3


TABLE_NAME = os.environ.get("TABLE_NAME", "AquariumSensorData")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    print("Received event:")
    print(json.dumps(event))

    device_id = event.get("deviceId")
    timestamp = event.get("timestamp")
    temperature = event.get("temperature")
    ph = event.get("ph")

    if not timestamp:
        timestamp = datetime.now(timezone.utc).isoformat()

    if device_id is None or temperature is None or ph is None:
        raise ValueError("Missing required fields: deviceId, temperature, ph")

    temperature = Decimal(str(temperature))
    ph = Decimal(str(ph))

    if ph < Decimal("7.0") or ph > Decimal("8.0"):
        status = "PH_ALERT"
        print(f"WARNING: pH value is out of safe range. pH={ph}")
    else:
        status = "NORMAL"

    item = {
        "deviceId": device_id,
        "timestamp": timestamp,
        "temperature": temperature,
        "ph": ph,
        "status": status
    }

    table.put_item(Item=item)

    print("Item saved to DynamoDB:")
    print(item)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Sensor data processed successfully",
            "deviceId": device_id,
            "status": status
        })
    }
