import random
import time
from datetime import datetime, timedelta
from confluent_kafka import Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer

# List of Credit Cards and Locations
credit_card_numbers = [
    4774993836989662,
    4738273984732749,
    4739023369472686,
    4742020908432434,
    4743519677912308,
    4757008603231174,
    4751762910051615,
    4754760449011363,
    4760755526930859
]

locations = ["Tokyo", "Rio", "Berlin", "Oslo", "Stockholm", "Nairobi", "Spain", "Portugal"]

def read_schema():
    schema_config = {}
    with open("schema.properties") as sp:
     for line in sp:
        if len(line) != 0 and line[0] != "#":
           parameter, value = line.strip().split('=', 1)
           schema_config[parameter] = value.strip()
    return schema_config

def read_config():
  config = {}
  with open("client.properties") as fh:
    for line in fh:
      line = line.strip()
      if len(line) != 0 and line[0] != "#":
        parameter, value = line.strip().split('=', 1)
        config[parameter] = value.strip()
  return config

# JSON Schema for Transaction class
TRANSACTION_SCHEMA = """
    {
      "$schema": "http://json-schema.org/draft-07/schema#",
      "title": "Transaction",
      "description": "Credit card transaction",
      "type": "object",
      "properties": {
        "amount": {
            "connect.index": 3,
            "connect.type": "int32",
            "type": "integer"
        },
        "credit_card_number": {
            "connect.index": 2,
            "connect.type": "int64",
            "type": "integer"
        },
        "location": {
            "connect.index": 4,
            "type": "string"
        },
        "transaction_id": {
            "connect.index": 0,
            "connect.type": "int32",
            "type": "integer"
        },
        "transaction_timestamp": {
            "connect.index": 1,
            "type": "string"
        }
      }
    }
    """

# Transaction class definition
class Transaction(object):
    def __init__(self, transaction_id, transaction_timestamp, credit_card_number, amount, location):
        self.transaction_id = transaction_id
        self.transaction_timestamp = transaction_timestamp
        self.credit_card_number = credit_card_number
        self.amount = amount
        self.location = location

    def to_dict(self):
        # Serializes object to a dictionary for schema-based serialization
        return {
            "transaction_id": self.transaction_id,
            "transaction_timestamp": self.transaction_timestamp,
            "credit_card_number": self.credit_card_number,
            "amount": self.amount,
            "location": self.location
        }

# Configure the properties file
config = read_config()

# Configure the schema properties file
schema_config = read_schema()

# Set up Schema Registry client and JSON Serializer
schema_registry_client = SchemaRegistryClient({
   'url': schema_config["schema.registry.url"],
   'basic.auth.user.info':schema_config["schema.registry.username"]+":"+schema_config["schema.registry.password"]
})

json_serializer = JSONSerializer(TRANSACTION_SCHEMA, schema_registry_client)

# Kafka producer instance with StringSerializer for the key
producer = Producer(config)

# Kafka Broker and Schema Registry Configuration

KAFKA_TOPIC = 'transactions'  # Kafka topic for sending transaction data

# Function to send data to Kafka using JSON schema serialization
def send_to_kafka(transaction: Transaction):
    try:
        # Serialize the transaction object to JSON using the JSONSerializer
        serialized_transaction = json_serializer(transaction.to_dict(), SerializationContext(KAFKA_TOPIC, MessageField.VALUE))
        # Send serialized transaction to Kafka
        producer.produce(KAFKA_TOPIC, key=str(transaction.transaction_id), value=serialized_transaction)
        producer.flush()
        print(f"Sent transaction {transaction.transaction_id} to Topic.")
    except Exception as e:
        print(f"Failed to send transaction: {e}")

# Function to generate a random transaction amount
def generate_amount():
    return random.randint(500, 2000)  # Amount between $500 and $1000

# Function to generate fraudulent transactions
def generate_fraudulent_transactions(credit_card_number, start_time, num_transactions=3):
    transactions = []
    hour = random.randint(1,5)
    minute = random.randint(1,59)
    for i in range(num_transactions):
        amount = random.randint(5000, 10000)  # High-value transactions
        location = random.choice(locations)
        transaction_time = start_time + timedelta(hours=hour, minutes=minute + i * 3)  # Generate 3 transactions in 10 min span (every 3 minutes)
        transaction = Transaction(
            transaction_id=random.randint(1000000, 9999999),
            transaction_timestamp=' '.join(transaction_time.isoformat().split('T'))[:-3],
            credit_card_number=credit_card_number,
            amount=amount,
            location=location
        )
        transactions.append(transaction)
    return transactions

# Function to continuously generate transactions
def generate_transactions():
    last_fraud_time = None
    fraudulent_credit_card = None

    while True:
        # Randomly choose a credit card for normal transactions
        credit_card = random.choice(credit_card_numbers)

        # Normal transaction
        amount = generate_amount()
        location = random.choice(locations)
        transaction_time = datetime.now() + timedelta(hours=random.randint(1,10), minutes=random.randint(1,59))
        transaction = Transaction(
            transaction_id=random.randint(1000000, 9999999),
            transaction_timestamp=' '.join(transaction_time.isoformat().split('T'))[:-3],
            credit_card_number=credit_card,
            amount=amount,
            location=location
        )
        send_to_kafka(transaction)
        # print(transaction.to_dict())

        # Trigger fraudulent behavior
        random_num = random.random()
        if random_num < 0.1:  # 10% chance of initiating fraudulent transactions
                fraudulent_credit_card = random.choice(credit_card_numbers)
                last_fraud_time = datetime.now()

                # Generate fraudulent transactions
                fraudulent_transactions = generate_fraudulent_transactions(fraudulent_credit_card, last_fraud_time)
                for fraud_trans in fraudulent_transactions:
                    send_to_kafka(fraud_trans)
                    # print(fraud_trans.to_dict())
        # Sleep for 5 seconds before generating next transaction
        time.sleep(1)

# Start the transaction generation process
generate_transactions()
