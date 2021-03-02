#!/usr/bin/env python3
import uuid, os
from confluent_kafka import Consumer

consumer = Consumer({
    'bootstrap.servers': os.getenv('BOOTSTRAP_SERVERS'),
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'ssl.ca.location': 'probe',
    'sasl.username': os.getenv('API_KEY'),
    'sasl.password': os.getenv('API_SECRET'),
    'group.id': str(uuid.uuid1()),
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(['users'])
 
try:
    while True:
        msg = consumer.poll(0.1)
        if msg is None:
            continue
        print('consumed: {}'.format(msg.value()))
 
except KeyboardInterrupt:
    pass
 
finally:
    consumer.close()