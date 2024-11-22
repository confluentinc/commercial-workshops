
from confluent_kafka.admin import (AdminClient, NewTopic)

def read_config():
  config = {}
  with open("client.properties") as fh:
    for line in fh:
      line = line.strip()
      if len(line) != 0 and line[0] != "#":
        parameter, value = line.strip().split('=', 1)
        config[parameter] = value.strip()
  return config


config = read_config()
adminClient = AdminClient(conf=config)

def create_topics(topics):
    """ Create topics """

    new_topics = [NewTopic(topic, num_partitions=3, replication_factor=3) for topic in topics]
    # Call create_topics to asynchronously create topics, a dict
    # of <topic,future> is returned.
    fs = adminClient.create_topics(new_topics)

    # Wait for operation to finish.
    # Timeouts are preferably controlled by passing request_timeout=15.0
    # to the create_topics() call.
    # All futures will finish at the same time.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))


topics = ["transactions","fraudulent_transactions"]
create_topics(topics)