<div align="center" padding=25px>
    <img src="images/confluent.png" width=50% height=50%>
</div>

# <div align="center">Build Predictive Machine Learning Model Using Streaming Data Pipelines</div>
## <div align="center">Lab Guide</div>
<br>

## **Agenda**
1. [Log into Confluent Cloud](#step-1)
2. [Create an Environment and Cluster](#step-2)
3. [Create Flink Compute Pool](#step-3)
4. [Create Topics and walk through Confluent Cloud Dashboard](#step-4)
5. [Create Datagen Connectors for Customers and Credit Cards](#step-5)
6. [Create a Producer for transactions topic](#step-6)
7. [Clone the repository and configure the clients](#step-7)
8. [Add data contract to transactions topic](#step-8)
9. [Perform complex joins using Flink to combine the records into one topic](#step-9)
10. [Consume feature set topic and predict fraud transactions](#step-10)
11. [Connect Flink with Bedrock Model](#step-11)
12. [Flink Monitoring](#step-12)
13. [Clean Up Resources](#step-13)
14. [Confluent Resources and Further Testing](#step-14)
***

## **Prerequisites**
<br>

1. Create a Confluent Cloud Account.
    - Sign up for a Confluent Cloud account [here](https://www.confluent.io/confluent-cloud/tryfree/).
    - Once you have signed up and logged in, click on the menu icon at the upper right hand corner, click on “Billing & payment”, then enter payment details under “Payment details & contacts”. A screenshot of the billing UI is included below.

2. Install Python 3.8+
   > If you are using a Linux distribution, chances are you already have Python 3 pre-installed. To see which version of Python 3 you have installed, open a command prompt and run
   ```
    python3 --version
   ```

   If you need to install python3, [this may help](https://docs.python-guide.org/starting/install3/linux/)

3. Install python virtual environment: ```python3 -m pip install venv``` or ```python3 -m pip install virtualenv```
   > If ```/usr/bin/python3: No module named pip``` error shows up, install python3-pip using
   > ```
   > sudo apt-get install -y python3-pip
   > ```

4. Clone this repo:
   ```
   git clone git@github.com:confluentinc/commercial-workshops.git
   ```
   or
   ```
   git clone https://github.com/confluentinc/commercial-workshops.git
   ```

5. Install confluent cloud CLI based on your OS (https://docs.confluent.io/confluent-cli/current/install.html)

> **Note:** You will create resources during this workshop that will incur costs. When you sign up for a Confluent Cloud account, you will get free credits to use in Confluent Cloud. This will cover the cost of resources created during the workshop. More details on the specifics can be found [here](https://www.confluent.io/confluent-cloud/tryfree/).

<div align="center" padding=25px>
    <img src="images/billing.png" width=75% height=75%>
</div>

***

## **Objective**

<br>

Welcome to “Build Predictive Machine Learning Models Using Streaming Data Pipelines”! In this workshop, you will discover how to leverage the capabilities of Confluent Cloud to enable the development of predictive machine learning models using streaming data. We will focus on showcasing how Confluent Cloud, along with Apache Flink and Kafka, can facilitate the creation and deployment of effective data pipelines for real-time analytics.

By the end of this workshop, you'll have a clear understanding of how to utilize Confluent Cloud’s features to build a foundation for machine learning applications, empowering you to transform your streaming data into valuable predictions and insights.

<div align="center" padding=25px>
    <img src="images/arc.png" width=75% height=75%>
</div>

***


## <a name="step-1"></a>Log into Confluent Cloud

1. Log into [Confluent Cloud](https://confluent.cloud) and enter your email and password.

<div align="center" padding=25px>
    <img src="images/login.png" width=50% height=50%>
</div>

2. If you are logging in for the first time, you will see a self-guided wizard that walks you through spinning up a cluster. Please minimize this as you will walk through those steps in this workshop. 

***

## <a name="step-2"></a>Create an Environment and Cluster

An environment contains clusters and its deployed components such as Apache Flink, Connectors, ksqlDB, and Schema Registry. You have the ability to create different environments based on your company's requirements. For example, you can use environments to separate Development/Testing, Pre-Production, and Production clusters. 

1. Click **+ Add Environment**. Specify an **Environment Name** and Click **Create**. 

>**Note:** There is a *default* environment ready in your account upon account creation. You can use this *default* environment for the purpose of this workshop if you do not wish to create an additional environment.

<div align="center" padding=25px>
    <img src="images/environment.png" width=50% height=50%>
</div>

2. Now that you have an environment, click **Create Cluster**. 

> **Note:** Confluent Cloud clusters are available in 3 types: Basic, Standard, and Dedicated. Basic is intended for development use cases so you will use that for the workshop. Basic clusters only support single zone availability. Standard and Dedicated clusters are intended for production use and support Multi-zone deployments. If you are interested in learning more about the different types of clusters and their associated features and limits, refer to this [documentation](https://docs.confluent.io/current/cloud/clusters/cluster-types.html).

3. Chose the **Basic** cluster type. 

<div align="center" padding=25px>
    <img src="images/cluster-type.png" width=50% height=50%>
</div>

4. Click **Begin Configuration**. 
5. Choose your preferred Cloud Provider (AWS, GCP, or Azure), region, and availability zone. 
6. Specify a **Cluster Name**. For the purpose of this lab, any name will work here. 

<div align="center" padding=25px>
    <img src="images/create-cluster.png" width=50% height=50%>
</div>

7. View the associated *Configuration & Cost*, *Usage Limits*, and *Uptime SLA* information before launching. 
8. Click **Launch Cluster**. 

***

## <a name="step-4"></a>Create a Flink Compute Pool

1. On the navigation menu, select **Flink** and click **Create Compute Pool**.

<div align="center" padding=25px>
    <img src="images/create-flink-pool-1.png" width=50% height=50%>
</div>

2. Select **Region** and then **Continue**. (You have to use the region where the cluster was created in the previous step)
<div align="center" padding=25px>
    <img src="images/create-flink-pool-2.png" width=50% height=50%>
</div>

3. Name you Pool Name and set the capacity units (CFUs) to **5**. Click **Finish**.

<div align="center" padding=25px>
    <img src="images/create-flink-pool-3.png" width=50% height=50%>
</div>

> **Note:** The capacity of a compute pool is measured in CFUs. Compute pools expand and shrink automatically based on the resources required by the statements using them. A compute pool without any running statements scale down to zero. The maximum size of a compute pool is configured during creation. 

4. Flink Compute pools will be ready shortly. You can click **Open SQL workspace** when the pool is ready to use.

5. Change your workspace name by clicking **settings button**. Click **Save changes** after you update the workspace name.

<div align="center" padding=25px>
    <img src="images/flink-workspace-1.png" width=50% height=50%>
</div>

6. Set the Catalog as your environment name.

<div align="center" padding=25px>
    <img src="images/flink-workspace-2.png" width=50% height=50%>
</div>

7. Set the Database as your cluster name.

<div align="center" padding=25px>
    <img src="images/flink-workspace-3.png" width=50% height=50%>
</div>

***

## <a name="step-5"></a>Creates Topic and Walk Through Cloud Dashboard

1. On the navigation menu, you will see **Cluster Overview**. 

> **Note:** This section shows Cluster Metrics, such as Throughput and Storage. This page also shows the number of Topics, Partitions, Connectors, and ksqlDB Applications.

2. Click on **Cluster Settings**. This is where you can find your *Cluster ID, Bootstrap Server, Cloud Details, Cluster Type,* and *Capacity Limits*.
3. On the same navigation menu, select **Topics** and click **Create Topic**. 
4. Enter **customers** as the topic name, **3** as the number of partitions, skip the data contract and then click **Create with defaults**.'

<div align="center" padding=25px>
    <img src="images/create-topic.png" width=50% height=50%>
</div>

5. Repeat the previous step and create a second topic name **credit_cards** and **3** as the number of partitions and skip the data contract.

> **Note:** Topics have many configurable parameters. A complete list of those configurations for Confluent Cloud can be found [here](https://docs.confluent.io/cloud/current/using/broker-config.html). If you are interested in viewing the default configurations, you can view them in the Topic Summary on the right side. 

7. After topic creation, the **Topics UI** allows you to monitor production and consumption throughput metrics and the configuration parameters for your topics. When you begin sending messages to Confluent Cloud, you will be able to view those messages and message schemas.

***

## <a name="step-6"></a>Create Datagen Connectors for Customers and Credit Cards
The next step is to produce sample data using the Datagen Source connector. You will create two Datagen Source connectors. One connector will send sample customer data to **customers** topic, the other connector will send sample credit card data to **credit_cards** topic.

1. First, you will create the connector that will send data to **customers**. From the Confluent Cloud UI, click on the **Connectors** tab on the navigation menu. Click on the **Datagen Source** icon.

<div align="center" padding=25px>
    <img src="images/connectors.png" width=75% height=75%>
</div>

2. Click **Additional Configuration** button.
<div align="center" padding=25px>
    <img src="images/connectors-1.png" width=75% height=75%>
</div>

3. Choose **customers** topic.
<div align="center" padding=25px>
    <img src="images/connectors-2.png" width=75% height=75%>
</div>

4. Click **Generate API Key and Download** and give any description. The API key would be downloaded and would be available in the downloads folder in the system
<div align="center" padding=25px>
    <img src="images/connectors-3.png" width=75% height=75%>
</div>

5. Choose **JSON_SR** for select output record value format.
<div align="center" padding=25px>
    <img src="images/connectors-4.png" width=75% height=75%>
</div>

6. Click on **Provide Your Own Schema** and paste the following contents
```
{
  "type": "record",
  "name": "CustomerRecord",
  "namespace": "workshop_5",
  "fields": [
    {
      "name": "customer_id",
      "type": {
        "type": "int",
        "arg.properties": {
          "iteration": {
            "start": 100
          }
        }
      }
    },
    {
      "name": "customer_email",
      "type": {
        "type": "string",
        "arg.properties": {
          "options": [
            "alex.jose@gmail.com",
            "james.joe@gmail.com",
            "john.doe@gmail.com",
            "lisa.kudrow@gmail.com",
            "jeniffer.aniston@gmail.com",
            "ross.geller@gmail.com",
            "joey.tribbiani@gmail.com",
            "courtney.cox@gmail.com"
          ]
        }
      }
    },
    {
      "name": "average_spending_amount",
      "type": {
        "type": "int",
        "arg.properties": {
          "range": {
            "min": 1000,
            "max": 1500
          }
        }
      }
    }
  ]
}
```
7. Click on **Continue**, Sizing should be good, click on **Continue** again. You can name the connector anything or leave it as default and click on **Continue**.
<div align="center" padding=25px>
    <img src="images/connectors-5.png" width=75% height=75%>
</div>


8. After few seconds Connector would be provisioned and running. Check for messages in the **customers** topic by navigating to the topics section.
9. Repeat the same steps to create a connector for **credit_cards** topic by using the below schema but use existing API key this time.
```
{
  "type": "record",
  "name": "CreditCards",
  "namespace": "workshop_5",
  "fields": [
    {
      "name": "credit_card_number",
      "type": {
        "type": "long",
        "arg.properties": {
          "iteration": {
            "start": 4738273984732749,
            "step": 749384739937
          }
        }
      }
    },
    {
      "name": "customer_id",
      "type": {
        "type": "int",
        "arg.properties": {
          "iteration": {
            "start": 100
          }
        }
      }
    },
    {
      "name": "maximum_limit",
      "type": {
        "type": "int",
        "arg.properties": {
          "range": {
            "min": 10000,
            "max": 50000
          }
        }
      }
    }
  ]
}
```
<div align="center" padding=25px>
    <img src="images/connectors-6.png" width=75% height=75%>
</div>

<div align="center" padding=25px>
    <img src="images/connectors-7.png" width=75% height=75%>
</div>

> **Note:** If the connectors fails, there are a few different ways to troubleshoot the error:
> * Click on the *Connector Name*. You will see a play and pause button on this page. Click on the play button.
> * Click on the *Connector Name*, go to *Settings*, and re-enter your API key and secret. Double check there are no extra spaces at the beginning or end of the key and secret that you may have accidentally copied and pasted.
> * If neither of these steps work, try creating another Datagen connector.


11. You can view the sample data flowing into topics in real time. Navigate to  the **Topics** tab and then click on the **customers** and **credit_cards**. You can view the production and consumption throughput metrics here.

12. Click on **Messages**.

* You should now be able to see the messages within the UI. You can view the specific messages by clicking the icon.
***

## <a name="step-7"></a>Configure the clients.
The next step is to run the producer to produce transaction records to the **transactions** topic.

1. Open VS Code or any editor of your choice and open the github repository folder and run the following command
```bash
cd series-getting-started-with-cc/workshop-predictive-ai
```
3. Create a virtual environment for this project and activate it by running the following command
```bash
python3 -m venv _venv
source _venv/bin/activate
```
4. Install the dependencies by running the following commmand.
```bash
pip3 install -r requirements.txt
```
5. Create a ```client.properties``` and ```schema.properties``` files in the current folder. Let these be empty now we'll paste the configurations in the next step.

## <a name="step-8"></a>Create a Python Client for transactions topic
The next step is to produce sample data using a client. You will configure a python client for **transactions** topic.

1. From the Confluent Cloud UI, click on the **Clients** tab on the navigation menu. Click on the **Add new client** button on the top right.
<div align="center" padding=25px>
    <img src="images/producer-1.png" width=75% height=75%>
</div>

2. Choose **Python** in choose your language option.
<div align="center" padding=25px>
    <img src="images/producer-2.png" width=75% height=75%>
</div>

3. Click on  **Use existing API Key** in select an API key and fill out the downloaded API keys.
<div align="center" padding=25px>
    <img src="images/producer-3.png" width=75% height=75%>
</div>

4. Click on  **Use existing topic** in type **transactions**.
5. Copy the configuration snippet shown in the screen and paste in ```client.properties``` file.
```bash
# Required connection configs for Kafka producer, consumer, and admin
bootstrap.servers=pkc-p11xm.us-east-1.aws.confluent.cloud:9092
security.protocol=SASL_SSL
sasl.mechanisms=PLAIN
sasl.username=xxxxxxxxxxxx
sasl.password=xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Best practice for higher availability in librdkafka clients prior to 1.7
session.timeout.ms=45000

client.id=ccloud-python-client-3b98b537-adba-4c2d-b36f-79f964f031c0

```

6. Scroll down and click on **View Clients** button. However you can't see any clients yet as there are no applications currently talking to topics yet.
7. Click on **Environments** in the top left of the screen and choose your environment.
8. Scroll down at the right hand side of the screen, you'll see the stream governance details like below
<div align="center" padding=25px>
    <img src="images/client-1.png" width=75% height=75%>
</div>

9. Copy the endpoint of Stream Governance API and create a new credentials to access this by clicking on **Add Key**.
10. Paste the endpoint and API Keys in ```schema.properties``` file like below:
```bash
schema.registry.url=https://psrc-em25q.us-east-2.aws.confluent.cloud
schema.registry.username=xxxxxxxxxx
schema.registry.password=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
12. Run the admin client to create required topics.
```bash
python3 admin_client.py
```
You should be able to view the output something like this..
```bash
Topic transactions created
Topic fraudulent_transactions created
```
11. Run the ```producer.py``` file by running the following command.
```bash
python3 producer.py
```
You can see records being published to transactions topic.
> **Note:** If the producer fails, there are a few different ways to troubleshoot the error:
> * Click on the *Cluster Overiview*, go to *Cluster Settings*,. Double check there are no extra spaces at the beginning or end of the key and secret that you may have accidentally copied and pasted in ```client.properties``` file also verify the ```bootstrap.servers``` value by comparing it with the *Bootstrap Server* value in the Endpoints section in UI. Also verify the ```schema.properties```


## <a name="step-10"></a>Perform complex joins using Flink to combine the records into one topic
Kafka topics and schemas are always in sync with our Flink cluster. Any topic created in Kafka is visible directly as a table in Flink, and any table created in Flink is visible as a topic in Kafka. Effectively, Flink provides a SQL interface on top of Confluent Cloud.

1. From the Confluent Cloud UI, click on the **Environments** tab on the navigation menu. Choose your environment.
2. Click on *Flink* from the menu pane
3. Choose the compute pool created in the previous steps.
4. Click on **Open SQL workspace** button on the top right.
5. Create an **aggregated_transactions** table by running the following SQL query.
```sql
CREATE TABLE aggregated_transactions (
    transaction_id INT NOT NULL PRIMARY KEY NOT ENFORCED,
    credit_card_number BIGINT,
    customer_email STRING,
    total_amount INT,
    average_spending_amount INT,
    transaction_timestamp TIMESTAMP(3),
    WATERMARK FOR transaction_timestamp AS transaction_timestamp - INTERVAL '1' SECOND
) WITH (
    'changelog.mode' = 'upsert'
);
```

6. Add a new query by clicking on + icon in the left of previous query to Insert records to the above table by running the following query.
```sql
INSERT INTO aggregated_transactions
SELECT 
    t.transaction_id,
    t.credit_card_number,
    cust.customer_email,
    t.amount,
    cust.average_spending_amount,
    TO_TIMESTAMP(t.transaction_timestamp) AS transaction_timestamp
FROM transactions t
INNER JOIN credit_cards cc ON t.credit_card_number = cc.credit_card_number
INNER JOIN customers cust ON cc.customer_id = cust.customer_id
```
7. Now we will create a ```feature_set``` topic to put all the transactions in specific windows. To perform the same run the following query.
```sql
CREATE TABLE feature_set (
    credit_card_number BIGINT PRIMARY KEY NOT ENFORCED,
    customer_email STRING,
    total_amount INT,
    transaction_count BIGINT,
    average_spending_amount INT,
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3)
) WITH (
  'changelog.mode' = 'upsert',
  'value.format' = 'json-registry',
  'key.format' = 'json-registry'
)
```
```sql
INSERT INTO feature_set
  WITH windowed_transactions AS (
SELECT 
    credit_card_number,
    SUM(total_amount) AS total_amount,
    COUNT(transaction_id) AS transaction_count,
    window_start,
    window_end
FROM 
  TABLE(
    TUMBLE(TABLE aggregated_transactions, DESCRIPTOR(transaction_timestamp),INTERVAL '10' MINUTES)
  )
GROUP BY credit_card_number, window_start,window_end
)
SELECT DISTINCT
  t.credit_card_number,
  t.customer_email,
  wt.total_amount,
  wt.transaction_count,
  t.average_spending_amount,
  wt.window_start,
  wt.window_end
 FROM 
  aggregated_transactions t
 JOIN
   windowed_transactions wt
 ON
  wt.credit_card_number = t.credit_card_number
 AND
  t.transaction_timestamp BETWEEN wt.window_start AND wt.window_end
```

Windows are central to processing infinite streams. Windows split the stream into “buckets” of finite size, over which you can apply computations. This document focuses on how windowing is performed in Confluent Cloud for Apache Flink and how you can benefit from windowed functions.

Flink provides several window table-valued functions (TVF) to divide the elements of your table into windows, including:

a. [Tumble Windows](https://docs.confluent.io/cloud/current/flink/reference/queries/window-tvf.html#flink-sql-window-tvfs-tumble)
<br> 
b. [Hop Windows](https://docs.confluent.io/cloud/current/flink/reference/queries/window-tvf.html#flink-sql-window-tvfs-hop)
<br> 
c. [Cumulate Windows](https://docs.confluent.io/cloud/current/flink/reference/queries/window-tvf.html#flink-sql-window-tvfs-cumulate)
<br> 

## <a name="step-11"></a>Consume feature set topic and predict fraud transactions
The next step is to create a consumer for feature set topic and predict the fraudulent transaction.

1. Update ```client.properties``` file with an additional configuration at the end of the file like following.
```bash
auto.offset.reset=earliest
enable.auto.commit=false
group.id=FraudDetectorApplication
```

2. Run the ```fraud_detector.py``` to determine the fraudulent transactions from the feature set and produce the transactions to the topic created above.
```python
python3 fraud_detector.py
```

3. Now you can see few messages in the *fraudulent_transactions* topic. When you see ```Polling for messages...``` continously you can stop the consumer by clicking ```Ctrl+c```

> **Note:** This demonstration simulates a sample condition as a machine learning model to showcase the capabilities of real-time streaming with Confluent Cloud.
In this setup, a data engineer can extract the required features from various sources into separate topics. These topics enable data scientists to leverage the curated feature sets to develop and train machine learning models outside of the Confluent Cloud environment.
This illustrates the power of integrating Confluent Cloud for efficient data streaming and feature engineering in the ML workflow.

4. We shall see some fraudulent transactions under ***fraudulent_transactions*** topic by running the following command in flink
```sql
SELECT details FROM fraudulent_transactions
```
<div align="center" padding=25px>
    <img src="images/fraud_transactions.png" width=75% height=75%>
</div>

## <a name="step-12"></a>Connect Flink with Bedrock Model
The next step is to create a integrated model from AWS Bedrock with Flink on Confluent Cloud.

1. First, you will create the model connection using Confluent CLI. If you've never installed one, you could install it based on your OS (https://docs.confluent.io/confluent-cli/current/install.html) and login to confluent.
```bash
confluent login
```

2. Make sure you prepare your AWS API Key and Secret to create connection to the Bedrock. (Would be provided in the workshop)

3. Make sure you are using the right environment and right cluster to create the connection. Verify by performing the following.
```bash
confluent environment list
confluent environment use <env-id>
confluent kafka cluster list
confluent kafka cluster use <cluster-id>
```

> **Note:** If you doesn't have any user you could check the step below to create user with full access to Bedrock and creating API key and secret. You could skip this step if you already have user and api key with full access to bedrock.

>Go to **AWS IAM>User** and create User
<div align="center">
    <img src="images/bedrock0-1.png" width=100% height=100%>
</div>

>Create User with attach policies for Bedrock Full Access
<div align="center">
    <img src="images/bedrock0-2.png" width=100% height=100%>
</div>

<div align="center">
    <img src="images/bedrock0-3.png" width=100% height=100%>
</div>

>Create API Key by search your user that has been created and click on the "Create Access Key"
<div align="center">
    <img src="images/bedrock0-4.png" width=100% height=100%>
</div>

<div align="center">
    <img src="images/bedrock-1.png" width=100% height=100%>
</div>

<div align="center">
    <img src="images/bedrock-2.png" width=100% height=100%>
</div>

```bash
confluent flink connection create my-connection --cloud aws --region us-east-1 --type bedrock --endpoint https://bedrock-runtime.us-east-1.amazonaws.com/model/meta.llama3-8b-instruct-v1:0/invoke --aws-access-key <API Key> --aws-secret-key <API Secret>
```
3. After creating connection, we need to create the model in Flink before we could invoke on our query.
```sql
CREATE MODEL NotificationEngine
INPUT (details STRING)
OUTPUT (message STRING)
WITH (
  'task' = 'text_generation',
  'provider' = 'bedrock',
  'bedrock.connection' = 'my-connection'
);
```

5. Now let's invoke the model and get the results.

```sql
SELECT message FROM fraudulent_transactions, LATERAL TABLE(ML_PREDICT('NotificationEngine', details));
```
<div align="center" padding=25px>
    <img src="images/ai_messages.png" width=75% height=75%>
</div>
***

## <a name="step-13"></a>Flink Monitoring
1. Status of all the Flink Jobs is available under **Flink Statements** Tab.
   
<div align="center">
    <img src="images/flink-statements-status.png" width=75% height=75%>
</div>

2. Utilization information.
<div align="center">
    <img src="images/flink-compute-pool-tile.png" width=40% height=40%>
</div>

<br> 


***

## <a name="step-14"></a>Clean Up Resources

Deleting the resources you created during this workshop will prevent you from incurring additional charges. 

1. The first item to delete is the Apache Flink Compute Pool. Select the **Delete** button under **Actions** and enter the **Application Name** to confirm the deletion. 
<div align="center">
    <img src="images/flink-delete-compute-pool.png" width=50% height=50%>
</div>

2. Next, delete the Datagen Source connectors for **credit_cards_connector**, **customers_connector**. Navigate to the **Connectors** tab and select each connector. In the settings tab, you will see a **trash** icon on the bottom of the page. Click the icon and enter the **Connector Name**.
<div align="center">
    <img src="images/delete-connector.png" width=75% height=75%>
</div>

3. Next, under **Cluster Settings**, select the **Delete Cluster** button at the bottom. Enter the **Cluster Name** and select **Confirm**. 
<div align="center">
    <img src="images/delete-cluster.png" width=50% height=50%>
</div>

4. Finally, to remove all resource pertaining to this workshop, delete the environment **workshop**.
<div align="center">
    <img src="images/delete-environment.png" width=50% height=50%>
</div>
*** 

## <a name="step-15"></a>Confluent Resources and Further Testing

Here are some links to check out if you are interested in further testing:
- [Confluent Cloud Documentation](https://docs.confluent.io/cloud/current/overview.html)
- [Apache Flink 101](https://developer.confluent.io/courses/apache-flink/intro/)
- [Stream Processing with Confluent Cloud for Apache Flink](https://docs.confluent.io/cloud/current/flink/index.html)
- [Flink SQL Reference](https://docs.confluent.io/cloud/current/flink/reference/overview.html)
- [Flink SQL Functions](https://docs.confluent.io/cloud/current/flink/reference/functions/overview.html)

***
