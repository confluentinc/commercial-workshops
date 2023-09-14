<div align="center">
    <img src="https://github.com/gsvamsikrishna/python-kafka-microservices/assets/73946498/b8adb476-2b70-4047-a378-4733a38a8f2e" width=75% height=75%>
</div>

# <img src="static/images/logo1.png" width="32" /> Building Event Driven Microservices with Confluent <img src="static/images/logo1.png" width="32" />
This is an example of a microservice ecosystem using the CQRS (Command and Query Responsibility Segregation) and Event Sourcing patterns, and nothing better to explain that by using as reference a pizza takeaway shop. Who doesn't love a pizza? :blush:


## <div align="center">Lab Guide</div>

## **Agenda**
[Prerequisites](#step-0a)<br>
[Use case details: Pizza Takeaway Shop](#step-0b)
1. [Log Into Confluent Cloud](#step-1)
1. [Create an Environment and Enable Stream Governance Essentials](#step-2)
1. [Create a Cluster](#step-3)
1. [Setup ksqlDB](#step-4)
2. [Create Topics using the Cloud UI](#step-5)
1. [Create an API Key Pair](#step-6)
1. [Prepare the config files and pre-requisites](#step-7)
1. [Cloud Dashboard Walkthrough](#step-8)
1. [Create Streams and Stream Processing ksqlDB](#step-9)
2. [Run the Microservices](#step-10)
1. [Using the webapp and chronology of events](#step-11)
2. [View Stream Lineage](#step-12)
1. [Stop the Demo](#step-13)
1. [Clean Up Resources](#step-14)
1. [Confluent Resources and Further Testing](#confluent-resources-and-further-testing)

***

## <a name="step-0a"></a>**Prerequisites**

1. Confluent Cloud Account
    * Sign-up for a Confluent Cloud account [here](https://www.confluent.io/confluent-cloud/tryfree/?utm_campaign=tm.fm-apac_cd.2023.09.14_APAC_ASIA_WS_Building-Event-Driven-Microservices-with-Confluent-Cloud&utm_source=splash&utm_medium=workshop).
      <!--    * You can also Sign-up through Cloud Marketplaces: [AWS Marketplace](https://docs.confluent.io/cloud/current/billing/ccloud-aws-payg.html) or [Azure Marketplace](https://docs.confluent.io/cloud/current/billing/ccloud-azure-payg.html) or [GCP Marketplace](https://docs.confluent.io/cloud/current/billing/ccloud-gcp-payg.html)
      -->
    * Once you have signed up and logged in, click on the menu icon at the upper right hand corner, click on “Billing & payment”. New signups receive $400 to spend during their first 30 days. No credit card required.

    > **Note:** You will create resources during this workshop that will incur costs. When you sign up for a Confluent Cloud account, you will get free credits to use in Confluent Cloud. This will cover the cost of resources created during the workshop. More details on the specifics can be found [here](https://www.confluent.io/confluent-cloud/tryfree/?utm_campaign=tm.fm-apac_cd.2023.09.14_APAC_ASIA_WS_Building-Event-Driven-Microservices-with-Confluent-Cloud&utm_source=splash&utm_medium=workshop).

From the system/ laptop/ instance where microservices are planned to run, setup the following

1. Ports `443` and `9092` need to be open to the public internet for outbound traffic. To check, try accessing the following from your web browser or using curl in the CLI.
    * portquiz.net:443
    * portquiz.net:9092

1. Install Python 3.8+
   > If you are using a Linux distribution, chances are you already have Python 3 pre-installed. To see which version of Python 3 you have installed, open a command prompt and run
   ```
    python3 --version
   ```

   If you need to install python3, [this may help](https://docs.python-guide.org/starting/install3/linux/)
<!--3. Install Docker-->
3. Install SQLite3
   To install, run
   ```
   sudo apt install sqlite3
   ```
   To check, run
   ```
   sqlite3
   ```
   Check [this external reference](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-sqlite-on-ubuntu-20-04) if required
5. Install python virtual environment: ```python3 -m pip install venv``` or ```python3 -m pip install virtualenv```
   > If ```/usr/bin/python3: No module named pip``` error shows up, install python3-pip using
   > ```
   > sudo apt-get install -y python3-pip
   > ```
7. Clone this repo:
   ```
   git clone git@github.com:confluentinc/commercial-workshops.git
   ```
   or
   ```
   git clone https://github.com/confluentinc/commercial-workshops.git
   ```

***

<!--
## CQRS vs Event Sourcing
While event sourcing can be used to implement CQRS, it does not necessarily imply event sourcing. In other words, CQRS is focused on the separation of write and read operations, while event sourcing is focused on storing the history of changes to a system as a sequence of events. CQRS and event sourcing can complement each other, but they are not the same thing.
-->
## <a name="step-0b"></a>Pizza Takeaway Shop

### <div align="center">High level view</div>
This pizza takeaway shop ecosystem was designed using Python and made simple for demo/learning purposes, basically the following are the app/microservices created:
- Web application using the Flask lib (```webapp.py```) so users can login to, customise their pizza, order and follow up the status of their order. This webapp will be the Command portion of the CQRS pattern. To make it simpler a SQLite3 state store* is being used as the materialised view between Command and Query, however in a real life scenario that could be an in-memory data store or ksqlDB
- Once the pizza is ordered it will go through four microservices (following the same flow of a real pizza shop):
  - Assemble the pizza as per order (```msvc_assemble.py```)
  - Bake the pizza (```msvc_bake.py```)
  - Have it delivered (```msvc_delivery.py```)
  - Process status (```msvc_status.py```): Whenever one of the previous microservices complete their task they will communicate with this microservice so it can update the web application. This microservice will be the Query portion of the CQRS pattern. It will have the materialised views stored in the aforementioned SQLite3 state store*
- All interprocess communication is via an Apache Kafka cluster

(*) By default SQLite3 will be used, but that can be changed via system configuration file (default is ```'config_sys/default.ini'```) by setting a different python class (the base/abstract class is defined on utils.db, class name is ```BaseStateStore```), see below the default system configuration:
```
[state-store-orders]
db_module_class = utils.db.sqlite

[state-store-delivery]
db_module_class = utils.db.sqlite
```

IMPORTANT: In order to keep consistency with Java based clients (using murmur2 partitioner), the producers will also set the topic partition using the murmur2 hash function, other than the standard CRC32 on librdkafka.

Webapp and four microservices in action:
![image](static/images/docs/service_flow.png)

### <div align="center">Low level view</div>
Detailed view of all microservices and to what Kafka topics their produce and are subscribed to:
![image](static/images/docs/gen_architecture.png)


This workshop will be utilizing kafka cluster and ksqlDB running on Confluent Cloud. Microservices (python) and HTTP server will be running on your local machines. 
***

## **Objective**

In this workshop you will learn how Confluent Cloud can enable you to design an Event Driven Microservices Application. During this workshop you’ll get hands-on experience with building out Confluent Cloud components; using a pre-built Python Microservices application to produce and consume data; transforming the data in real-time with ksqlDB. The use case will be centered around accepting Pizza order events and passing it on to the food preparation system and delivery system, updating the various levels of food preparation status to the customer and the delivery agent, update the orderstatus upon successful delivery.

By the end of this workshop, you will have a solid understanding of building microservices architectures with Kafka, enabling you to create scalable, robust, and event-driven systems.
You will also learn how to get started with Confluent Cloud, and the resources available to assist with development.

This workshop is perfect for those looking to build Event Driven Architecture use cases and to get started with Confluent Cloud. This is also a great session to ask the engineers your questions and participate in a forum with other attendees who already use Confluent Cloud or plan to use Confluent Cloud. In this workshop, Python will be used as programming language for building microservices. Python Knowledge is NOT Mandatory.


***

## <a name="step-1"></a>Step 1: Log Into Confluent Cloud

1. First, access Confluent Cloud sign-in by navigating [here](https://confluent.cloud).
1. When provided with the *username* and *password* prompts, fill in your credentials.
    > **Note:** If you're logging in for the first time you will see a wizard that will walk you through some tutorials. Minimize this as you will walk through these steps in this guide.

***

## <a name="step-2"></a>Step 2: Create an Environment and Enable Stream Governance Essentials

An environment contains Confluent clusters and its deployed components such as Connect, ksqlDB, and Schema Registry. You have the ability to create different environments based on your company's requirements. Confluent has seen companies use environments to separate Development/Testing, Pre-Production, and Production clusters.

1. Select **Environments** from the left side Navigation pane.
2. Click **+ Add cloud environment**.
    > **Note:** There is a *default* environment ready in your account upon account creation. You can use this *default* environment for the purpose of this workshop if you do not wish to create an additional environment.

3. Specify a meaningful `name` for your environment and then click **Create**.
    > **Note:** It will take a few minutes to assign the resources to make this new environment available for use.
    
4. Next page will show you "Stream Governance Packages". Select **Begin Configuration** under Essentials.
5. Choose cloud provider and region. You can select the nearest region which has $0/hr to keep the costs low for this workshop. Click on **Enable** at the bottom of the page.

In case, if you navigated away and want to use an existing environment, You can enable Stream Governance package by following the below steps:
1. Return to your environment by clicking on the **Environments** below the Confluent icon at the top left corner, and then clicking your environment tile.
2. On the right side pane, you will find **Stream Governance Package** grayed out. Click on "Enable Now".
3. Select **Begin Configuration** under Essentials.
4. Choose cloud provider and region. You can select the nearest region which has $0/hr to keep the costs low for this workshop. Click on **Enable** at the bottom of the page.

***

## <a name="step-3"></a>Step 3: Create a Cluster

1. Now that you have an environment, let's create a cluster. Select **Create Cluster on my own**.
    > **Note**: Confluent Cloud clusters are available in 3 types: **Basic**, **Standard**, and **Dedicated**. Basic is intended for development use cases so you should use that for this lab. Basic clusters only support single zone availability. Standard and Dedicated clusters are intended for production use and support Multi-zone deployments. If you’re interested in learning more about the different types of clusters and their associated features and limits, refer to this [documentation](https://docs.confluent.io/current/cloud/clusters/cluster-types.html).

    * Choose the **Basic** cluster type.

    * Click **Begin Configuration**.

    * Choose **AWS/ Azure/ GCP** as your Cloud Provider --> select your preferred **Region** --> Leave the Availability as **Single Zone**
        
    * Specify a meaningful **Cluster Name** and then review the associated *Configuration & Cost*, *Usage Limits*, and *Uptime SLA* before clicking **Launch Cluster**.

2. Once the cluster is ready to use, you will be on the "Cluster Overview" page. On the left side pane, click on **Cluster Settings** under **Cluster Overview**. Copy the Bootstrap server details for use in later steps.

***

## <a name="step-4"></a>Step 4: Setup ksqlDB

1. On the left-side navigation menu, select **ksqlDB** and click **Create cluster myself**.

1. Select **Global Access** and then **Continue**.

1. Name your ksqlDB application and set the cluster size to 1 CSU

    > **Note:** A streaming unit, also known as a Confluent Streaming Unit (CSU), is the unit of pricing for Confluent Cloud ksqlDB. A CSU is an abstract unit that represents the linearity of performance.

1. Click **Launch cluster**!

    > **Note:** It may take few minutes for the cluster to be ready. Meanwhile, you can continue with the next steps.
   ![image](https://github.com/gsvamsikrishna/python-kafka-microservices/assets/73946498/25047846-299c-45a5-ba2a-0171b618b7c5)

***

## <a name="step-5"></a>Step 5: Create Topics using the Cloud UI

1. On the left-side navigation menu, select **Topics** and click **+ Add Topic**.
    > **Note:** Refresh the page if your cluster is still spinning up.

2. Enter ```pizza-ordered``` as the Topic name and **1** as the Number of partitions
    > **Note:** Topics have many configurable parameters that dictate how Confluent handles messages. A complete list of those configurations for Confluent Cloud can be found [here](https://docs.confluent.io/cloud/current/using/broker-config.html).  If you’re interested in viewing the default configurations, you can view them in the *Topic Summary* on the right side.
   ```
   pizza-ordered
   ```

3. Click **Create with defaults**.
4. If **Define a data contract** pop-up appears, choose **Skip**

5. Repeat the above steps and create the following five topics with ```Number of partitions = 1```

   ```
   pizza-pending
   ```
   ```
   pizza-assembled
   ```
   ```
   pizza-baked
   ```
   ```
   pizza-delivered
   ```
   ```
   pizza-status
   ```

    > Topic creation can be autoamted using API/ CLI/ Terraform and ksqlDB queries. This is not covered in this workshop.

Your Topics page should like this now
![image](https://github.com/gsvamsikrishna/python-kafka-microservices/assets/73946498/562a8658-5e18-4406-94c4-80b65dabc2d7)


***


## <a name="step-6"></a>Step 6: Create an API Key Pair

1. Select **API keys** on the left-side navigation menu under **Cluster Overview**

1. Click **+ Add key** on the right side of the page

1. Select **Global Access**, then click Next.

1. Copy and Save your API key and secret - you will need these during the workshop.

1. CLick **Download and continue**. You will see this API key in the Confluent Cloud UI in the **API keys** tab. If you don’t see the API key populate right away, refresh the browser.

***

## <a name="step-7"></a>Step 7: Prepare the config files and pre-requisites

On the system/laptop/instance where the microservices are expected to run

- Go to the folder where the repo was cloned:
  ```
  cd commercial-workshops/series-getting-started-with-cc/workshop-microservices/
  ```
- Create a virtual environment:
  ```
  python3 -m venv _venv
  ```
- Activate the virtual environment:
  ```
  source _venv/bin/activate
  ```
- Install project requirements:
  ```
  python3 -m pip install -r requirements.txt
  ```

- ```{KAFKA_CONFIG_FILE}``` is a Kafka configuration file containing the properties to access the Apache Kafka cluster, this file must be located under the folder ```config_kafka/``` (see file ```config_kafka/example.ini``` for reference):
    - Use the details captured in earlier steps to fill in the details
```
    [kafka]
    bootstrap.servers = {{ host:port }}
    security.protocol = SASL_SSL
    sasl.mechanisms = PLAIN
    sasl.username = {{ CLUSTER_API_KEY }}
    sasl.password = {{ CLUSTER_API_SECRET }}
```

***

## <a name="step-8"></a>Step 8: Cloud Dashboard Walkthrough

This section will be conducted by the workshop instructor.  You can find additional information on the Cloud Dashboard [here](https://docs.confluent.io/cloud/current/overview.html) and [here](https://docs.confluent.io/cloud/current/client-apps/cloud-basics.html).

***

## <a name="step-9"></a>Step 9: Create Streams and Stream Processing ksqlDB

You can now easily build stream processing applications using ksqlDB. You are able to continuously transform, enrich, join, and aggregate your data using simple SQL syntax. You can gain value from your data directly from Confluent in real-time. Also, ksqlDB is a fully managed service within Confluent Cloud with a 99.9% uptime SLA. You can now focus on developing services and building your data pipeline while letting Confluent manage your resources for you.

With ksqlDB, you have the ability to leverage streams and tables from your topics in Confluent. A stream in ksqlDB is a topic with a schema and it records the history of what has happened in the world as a sequence of events. Tables are similar to traditional RDBMS tables. If you’re interested in learning more about ksqlDB and the differences between streams and tables, I recommend reading these two blogs [here](https://www.confluent.io/blog/kafka-streams-tables-part-3-event-processing-fundamentals/) and [here](https://www.confluent.io/blog/how-real-time-stream-processing-works-with-ksqldb/).

1. Navigate back to the ksqlDB tab and click on your ksqlDB Cluster name. This will bring us to the ksqlDB editor.

>**Note:** You can interact with ksqlDB through the Editor. You can create a stream by using the CREATE STREAM statement and a table using the CREATE TABLE statement.

To write streaming queries against topics, you will need to register the topics with ksqlDB as a stream and/or table.

2. Streams and tables are the two primary abstractions, they are referred to as collections. There are two ways of creating collections in ksqlDB:
- directly from Kafka topics (source collections)
- derived from other streams and tables (derived collections)

  *Insert the following queries into the ksqlDB editor and click ‘**Run query**’ to execute
**Source Collections**: The topics produced/consumed by the microservices need to be ingested by ksqlDB so they can be stream processed:
```SQL
CREATE STREAM IF NOT EXISTS PIZZA_ORDERED (
    order_id VARCHAR KEY,
    status INT,
    timestamp BIGINT,
    order STRUCT<
        extra_toppings ARRAY<STRING>,
        username STRING,
        customer_id STRING,
        sauce STRING,
        cheese STRING,
        main_topping STRING
    >
) WITH (
    KAFKA_TOPIC = 'pizza-ordered',
    VALUE_FORMAT = 'JSON',
    TIMESTAMP = 'timestamp'
);
```
The result should look like below with status = SUCCESS
![image](https://github.com/gsvamsikrishna/python-kafka-microservices/assets/73946498/7dbec68a-4171-49d0-8b1f-1f1bc64bcaed)

Now, clear the Editor contents and repeat the above steps with the below queries.

```SQL
CREATE STREAM IF NOT EXISTS PIZZA_ASSEMBLED (
    order_id VARCHAR KEY,
    status INT,
    baking_time INT,
    timestamp BIGINT
) WITH (
    KAFKA_TOPIC = 'pizza-assembled',
    VALUE_FORMAT = 'JSON',
    TIMESTAMP = 'timestamp'
);
```

```SQL
CREATE STREAM IF NOT EXISTS PIZZA_BAKED (
    order_id VARCHAR KEY,
    status INT,
    timestamp BIGINT
) WITH (
    KAFKA_TOPIC = 'pizza-baked',
    VALUE_FORMAT = 'JSON',
    TIMESTAMP = 'timestamp'
);
```

```SQL
CREATE STREAM IF NOT EXISTS PIZZA_DELIVERED (
    order_id VARCHAR KEY,
    status INT,
    timestamp BIGINT
) WITH (
    KAFKA_TOPIC = 'pizza-delivered',
    VALUE_FORMAT = 'JSON',
    TIMESTAMP = 'timestamp'
);
```

```SQL
CREATE STREAM IF NOT EXISTS PIZZA_PENDING (
    order_id VARCHAR KEY,
    status INT,
    timestamp BIGINT
) WITH (
    KAFKA_TOPIC = 'pizza-pending',
    VALUE_FORMAT = 'JSON',
    TIMESTAMP = 'timestamp'
);
```

```SQL
CREATE STREAM IF NOT EXISTS PIZZA_STATUS (
    order_id VARCHAR KEY,
    status INT,
    timestamp BIGINT
) WITH (
    KAFKA_TOPIC='pizza-status',
    VALUE_FORMAT='JSON',
    TIMESTAMP='timestamp'
);
```

If all the above six queries were executed correctly, you should see all the streams on the right-side of the page as shown below.
![image](https://github.com/gsvamsikrishna/python-kafka-microservices/assets/73946498/67cf9a90-cc51-4298-90f1-c5b0b1fe4cb7)


**Derived Collections**: With the source collections created (streams) we can now extract the status field of each event and have them merged into a single topic/stream by creating persistent queries:
```
INSERT INTO PIZZA_STATUS SELECT order_id, status, timestamp FROM PIZZA_ORDERED EMIT CHANGES;
INSERT INTO PIZZA_STATUS SELECT order_id, status, timestamp FROM PIZZA_ASSEMBLED EMIT CHANGES;
INSERT INTO PIZZA_STATUS SELECT order_id, status, timestamp FROM PIZZA_BAKED EMIT CHANGES;
INSERT INTO PIZZA_STATUS SELECT order_id, status, timestamp FROM PIZZA_DELIVERED EMIT CHANGES;
INSERT INTO PIZZA_STATUS SELECT order_id, status, timestamp FROM PIZZA_PENDING EMIT CHANGES;
```
You should see 5 SUCCESS messages after executing the above query.
Now, navigate to the **Flow** tab. You should see the topology as shown below. <br>

![image](https://github.com/gsvamsikrishna/python-kafka-microservices/assets/73946498/a92a4398-2f1a-4252-b947-ad2be9eee273)


***
## <a name="step-10"></a>Step 10: Run the Microservices

<!--
1. Run script to create topics*/ksqlDB streams: ```python3 run_me_first.py {KAFKA_CONFIG_FILE} {SYS_CONFIG_FILE}```
- If files names were not changes run ```python3 run_me_first.py example.ini default.ini```
-->

1. Start the demo: ```./start_demo.sh {KAFKA_CONFIG_FILE} {SYS_CONFIG_FILE}```

- If file names were not changed, run
  ```
  ./start_demo.sh example.ini default.ini
  ```
You should see an output similar to this
![image](https://github.com/gsvamsikrishna/python-kafka-microservices/assets/73946498/edfcd90a-6711-4926-9eea-afe40c6635a2)

- You may need to run below if there is "Permission denied" error.
  ```
  chmod +755 start_demo.sh stop_demo.sh
  ```
  
  
2. Open your browser and navigate to http://127.0.0.1:8000

>**Note:** In a real life scenario each microservice (consumer in a consumer group) could be instantiated for as many times as there are partitions to the topic, however that is just for demo/learning purposes, only one instance will be spawn. Also, for the simplicity of the demo, no Schema Registry is being used. That is not an ideal scenario as the "contract" between Producers and Consumers are "implicitly hard coded" other than being declared through the schema registry

***

## <a name="step-11"></a>Step 11: Using the webapp and chronology of events


1. After starting all scripts and access the landing page (http://127.0.0.1:8000), customise your pizza and submit your order:
![image](https://github.com/gsvamsikrishna/python-kafka-microservices/assets/73946498/730c5346-bcc3-4dfc-83c4-194cfaf61421)

<!--![image](static/images/docs/webapp_menu.png)-->

3. Once the order is submitted the webapp will produce an event to the Kafka topic ```pizza-ordered```:
```
(webapp) INFO 21:00:39.603 - Event successfully produced
 - Topic 'pizza-ordered', Partition #5, Offset #18
 - Key: b32ad
 - Value: {"status": 100, "timestamp": 1676235639159, "order": {"extra_toppings": ["Mushroom", "Black olives", "Green pepper"], "customer_id": "d94a6c43d9f487c1bef659f05c002213", "name": "Italo", "sauce": "Tomato", "cheese": "Mozzarella", "main_topping": "Pepperoni"}}
 ```

3. The webapp will display the status of the order:
![image](https://github.com/gsvamsikrishna/python-kafka-microservices/assets/73946498/50d94967-7523-42f7-b139-9f90f9c97846)

<!--![image](static/images/docs/webapp_order_confirmation.png)-->

4. The microservice **Deliver Pizza** (step 1/2) receives early warning about a new order by subscribing to topic ```pizza-ordered```. In a real life scenario it would get the ```customer_id``` data and query its data store (e.g., ksqlDB) and fetch the delivery address:
```
(msvc_delivery) INFO 21:00:18.516 - Subscribed to topic(s): pizza-ordered, pizza-baked
(msvc_delivery) INFO 21:00:39.609 - Early warning to deliver order 'b32ad' to customer_id 'd94a6c43d9f487c1bef659f05c002213'
```

5. The microservice **Assemble Pizza**, which is subscribed to the topic ```pizza-ordered```, receives the order and starts assembling the pizza. It will also estimate the baking time based on the ingredients chosen. Once the pizza is assembled, it will produce an event to the topic ```pizza-assembled``` as well as another to the topic ```pizza-status```:
```
(msvc_assemble) INFO 21:00:08.500 - Subscribed to topic(s): pizza-ordered
(msvc_assemble) INFO 21:00:39.604 - Preparing order 'b32ad', assembling time is 4 second(s)
(msvc_assemble) INFO 21:00:43.608 - Order 'b32ad' is assembled!
(msvc_assemble) INFO 21:00:43.923 - Event successfully produced
 - Topic 'pizza-assembled', Partition #5, Offset #15
 - Key: b32ad
 - Value: {"baking_time": 17}
(msvc_assemble) INFO 21:00:44.847 - Event successfully produced
 - Topic 'pizza-status', Partition #5, Offset #45
 - Key: b32ad
 - Value: {"status": 200}
 ```

6. The microservice **Process Status**, which is subscribed to the topic ```pizza-status```, receives the status change event and update the database with a materialised view of the status of the order:
```
(msvc_status) INFO 21:00:12.579 - Subscribed to topic(s): pizza-status
(msvc_status) INFO 21:00:44.851 - Order 'b32ad' status updated: Your pizza is in the oven (200)
 ```

7. The microservice **Bake Pizza**, which is subscribed to the topic ```pizza-assembled```, receives the notification the pizza is assembled along with the baking time, then it bakes the pizza accordingly. Once the pizza is baked, it will produce an event to the topic ```pizza-baked``` as well as another to the topic ```pizza-status```:
```
(msvc_bake) INFO 21:00:15.319 - Subscribed to topic(s): pizza-assembled
(msvc_bake) INFO 21:00:43.927 - Preparing order 'b32ad', baking time is 17 second(s)
(msvc_bake) INFO 21:01:00.929 - Order 'b32ad' is baked!
(msvc_bake) INFO 21:01:01.661 - Event successfully produced
 - Topic 'pizza-baked', Partition #5, Offset #15
 - Key: b32ad
 - Value:
(msvc_bake) INFO 21:01:02.645 - Event successfully produced
 - Topic 'pizza-status', Partition #5, Offset #46
 - Key: b32ad
 - Value: {"status": 300}
```

8. The microservice **Process Status**, which is subscribed to the topic ```pizza-status```, receives the status change event and update the database with a materialised view of the status of the order:
```
(msvc_status) INFO 21:00:12.579 - Subscribed to topic(s): pizza-status
(msvc_status) INFO 21:01:02.647 - Order 'b32ad' status updated: Your pizza is out for delivery (300)
 ```

9. The microservice **Deliver Pizza** (step 2/2), which is subscribed to the topic ```pizza-baked```, receives the notification the pizza is baked, then it delivers the pizza. It already had time to plan the delivery as it got an early warning as soon as the order was placed. Once the pizza is delivered, it will produce an event to the topic ```pizza-status```:
```
(msvc_delivery) INFO 21:00:18.516 - Subscribed to topic(s): pizza-ordered, pizza-baked
(msvc_delivery) INFO 21:01:01.662 - Deliverying order 'b32ad' for customer_id 'd94a6c43d9f487c1bef659f05c002213', delivery time is 10 second(s)
(msvc_delivery) INFO 21:01:11.665 - Order 'b32ad' delivered to customer_id 'd94a6c43d9f487c1bef659f05c002213'
(msvc_delivery) INFO 21:01:12.899 - Event successfully produced
 - Topic 'pizza-status', Partition #5, Offset #47
 - Key: b32ad
 - Value: {"status": 400}
```

10. The microservice **Process Status**, which is subscribed to the topic ```pizza-status```, receives the status change event and update the database with a materialised view of the status of the order:
```
(msvc_status) INFO 21:00:12.579 - Subscribed to topic(s): pizza-status
(msvc_status) INFO 21:01:12.902 - Order 'b32ad' status updated: Your pizza was delivered (400)
```

11. The flow is completed and, hopefully, we now have a happy customer for getting a delicious and nutritious pizza in such fast manner. The webapp, if on the order status page (in this case http://127.0.0.1:8000/orders/b32ad) will display in real time the status of the pizza, all of that thanks to the CQRS pattern. In a real life scenario that could be easily achieved by using frameworks such as ReactJS, however in this project it is used JQuery/AJAX async calls to accomplish that:
<!--![image](static/images/docs/webapp_order_delivered.png)-->
![image](https://github.com/gsvamsikrishna/python-kafka-microservices/assets/73946498/e5f2e39e-b8da-4f28-840f-b0800cd10187)



***
## <a name="step-12"></a>Step 12: View Stream Lineage

1. On the left-side navigation pane, click on **Stream Lineage**
Stream lineage provides a graphical UI of event streams and data relationships with both a bird’s eye view and drill-down magnification for answering questions like:
-Where did data come from?
-Where is it going?
-Where, when, and how was it transformed?

![image](https://github.com/gsvamsikrishna/python-kafka-microservices/assets/73946498/104d6c87-5175-44fd-a228-d60a27a07a48)


***
## <a name="step-13"></a>Step 13: Stop the Demo


1. To stop the demo: ```./stop_demo.sh```

### Graceful shutdown
One very important element of any Kafka consumer is by handling OS signals to be able to perform a graceful shutdown. Any consumer in a consumer group should inform the cluster it is leaving so it can rebalance itself other than wait for a timeout. All microservices used in this project have a graceful shutdown procedure in place, example:

```
(msvc_status) INFO 21:46:53.338 - Starting graceful shutdown...
(msvc_status) INFO 21:46:53.338 - Closing consumer in consumer group...
(msvc_status) INFO 21:46:53.372 - Consumer in consumer group successfully closed
(msvc_status) INFO 21:46:53.372 - Graceful shutdown completed

(msvc_assemble) INFO 21:46:54.541 - Starting graceful shutdown...
(msvc_assemble) INFO 21:46:54.541 - Closing consumer in consumer group...
(msvc_assemble) INFO 21:46:54.577 - Consumer in consumer group successfully closed
(msvc_assemble) INFO 21:46:54.577 - Graceful shutdown completed

(msvc_bake) INFO 21:46:55.968 - Starting graceful shutdown...
(msvc_bake) INFO 21:46:55.968 - Closing consumer in consumer group...
(msvc_bake) INFO 21:46:55.995 - Consumer in consumer group successfully closed
(msvc_bake) INFO 21:46:55.996 - Graceful shutdown completed

(msvc_delivery) INFO 21:46:57.311 - Starting graceful shutdown...
(msvc_delivery) INFO 21:46:57.311 - Closing consumer in consumer group...
(msvc_delivery) INFO 21:46:57.341 - Consumer in consumer group successfully closed
(msvc_delivery) INFO 21:46:57.341 - Graceful shutdown completed
```


2. Deactivate the virtual environment by running: ```deactivate```


***

## <a name="step-14"></a>Step 14: Clean Up Resources

Deleting the resources you created during this workshop will prevent you from incurring additional charges.

1. The first item to delete is the ksqlDB application. Select the Delete button under Actions and enter the Application Name to confirm the deletion.

2. Delete the Cluster by going to the **Settings** tab and then selecting **Delete cluster**

3. Delete the Environment by expanding the right hand menu and going to **Environments** tab and then clicking on **Delete** for the associated Environment you would like to delete

***


## <a name="confluent-resources-and-further-testing"></a>Confluent Resources and Further Testing

Here are some links to check out if you are interested in further testing:

* Confluent Cloud [Basics](https://docs.confluent.io/cloud/current/client-apps/cloud-basics.html)

* [Quickstart](https://docs.confluent.io/cloud/current/get-started/index.html) with Confluent Cloud

* Confluent Cloud ksqlDB [Quickstart](https://docs.confluent.io/cloud/current/get-started/ksql.html)

* Confluent Cloud [Demos/Examples](https://docs.confluent.io/platform/current/tutorials/examples/ccloud/docs/ccloud-demos-overview.html)

*  ksqlDB [Tutorials](https://kafka-tutorials.confluent.io/)

* Full repository of Connectors within [Confluent Hub](https://www.confluent.io/hub/)

***


#### **IMPORTANT 1**
Have you noticed the microservice **Deliver Pizza** is stateful as it has two steps?
- Step 1/2: Receive early warning that an order was placed (topic ```pizza-ordered```)
- Step 2/2: Receive notification the pizza is baked (topic ```pizza-baked```)

As that microservice is subscribed to two different topics, Apache Kafka cannot guarantee the order of events for the same event key. Hang on, but won't the early notification always arrive before the notification the pizza is baked (see the architecture diagram above)? The answer to that is: usually yes, as the first step happens before the second one, however what if for some reason the microservice **Deliver Pizza** is down and a bunch of events get pushed through the topics? When the microservice is brought up it will consume the events from the two topics and not necessarily in the same chronological order (for the same event key). For that reason microservice like that needs to take into account this kind of situations. On this project, if that happens the customer would first get the status "Bear with us we are checking your order, it won’t take long" (once the pizza is baked notification is processed), then would get the status "Your pizza was delivered" (once the early warning notification is processed).

#### **IMPORTANT 2**
The microservice **Process Status** is also stateful as it receives several notifications for the same event key. If that service was to be handled as stateless it would be a problem if a given order is not fully processed, for example, what if the baker decided to call it a day? The status of the order would get stuck forever as "Your pizza is in the oven". For example, it could be estimated the orders shouldn't take more than 'X minutes' between being ordered and baked and 'Y minutes' between being baked and not completed yet, creating then an SLA in between microservices, if that gets violated it could trigger a notification to state something got stuck (at least the pizza shop manager would get notified before the customer call to complain about the delay).<br><br>
What that microservice does is to spawn a new thread with an infinite loop to check the status of all orders in progress for every few seconds, like a watchdog.

Hope you enjoyed the Workshop :-) Thanks!


### Additional Troubleshooting

1. If ```The virtual environment was not created successfully because ensurepip is not available.``` Error comesup install python3-venv using 
    ```
    sudo  apt install python3.10-venv
    ```

