import json
import os
import random
import ssl
import time
from datetime import datetime, timezone

from dotenv import load_dotenv
from paho.mqtt import client as mqtt


load_dotenv()


AWS_IOT_ENDPOINT = os.getenv("AWS_IOT_ENDPOINT")
AWS_IOT_PORT = int(os.getenv("AWS_IOT_PORT", "8883"))
AWS_IOT_TOPIC = os.getenv("AWS_IOT_TOPIC")
DEVICE_ID = os.getenv("DEVICE_ID")

AWS_IOT_CERT_PATH = os.getenv("AWS_IOT_CERT_PATH")
AWS_IOT_KEY_PATH = os.getenv("AWS_IOT_KEY_PATH")
AWS_IOT_ROOT_CA_PATH = os.getenv("AWS_IOT_ROOT_CA_PATH")


def validate_environment():
    required_values = {
        "AWS_IOT_ENDPOINT": AWS_IOT_ENDPOINT,
        "AWS_IOT_TOPIC": AWS_IOT_TOPIC,
        "DEVICE_ID": DEVICE_ID,
        "AWS_IOT_CERT_PATH": AWS_IOT_CERT_PATH,
        "AWS_IOT_KEY_PATH": AWS_IOT_KEY_PATH,
        "AWS_IOT_ROOT_CA_PATH": AWS_IOT_ROOT_CA_PATH,
    }

    missing_values = [key for key, value in required_values.items() if not value]

    if missing_values:
        raise ValueError(f"Missing environment variables: {missing_values}")

    required_files = [
        AWS_IOT_CERT_PATH,
        AWS_IOT_KEY_PATH,
        AWS_IOT_ROOT_CA_PATH,
    ]

    for file_path in required_files:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")


def generate_sensor_data():
    temperature = round(random.uniform(24.0, 28.0), 2)
    ph = round(random.uniform(6.5, 8.5), 2)

    return {
        "deviceId": DEVICE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": temperature,
        "ph": ph,
    }


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("AWS IoT Core bağlantısı başarılı.")
    else:
        print(f"Bağlantı başarısız. Kod: {reason_code}")


def on_publish(client, userdata, mid, reason_code, properties):
    print(f"Mesaj AWS IoT Core'a gönderildi. Mesaj ID: {mid}")


def create_mqtt_client():
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=DEVICE_ID,
        protocol=mqtt.MQTTv311,
    )

    client.on_connect = on_connect
    client.on_publish = on_publish

    client.tls_set(
        ca_certs=AWS_IOT_ROOT_CA_PATH,
        certfile=AWS_IOT_CERT_PATH,
        keyfile=AWS_IOT_KEY_PATH,
        tls_version=ssl.PROTOCOL_TLS_CLIENT,
    )

    return client


def main():
    validate_environment()

    client = create_mqtt_client()

    print("AWS IoT Core'a bağlanılıyor...")
    client.connect(AWS_IOT_ENDPOINT, AWS_IOT_PORT, keepalive=60)

    client.loop_start()

    try:
        while True:
            sensor_data = generate_sensor_data()
            message = json.dumps(sensor_data)

            print(f"Gönderilen veri: {message}")

            result = client.publish(
                topic=AWS_IOT_TOPIC,
                payload=message,
                qos=1,
            )

            result.wait_for_publish()

            time.sleep(5)

    except KeyboardInterrupt:
        print("Simülatör durduruldu.")

    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()