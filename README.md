# Azure Cosmos DB SQL API client library for Python

Azure Cosmos DB is a globally distributed, multi-model database service that supports document, key-value, wide-column, and graph databases.

Use the Azure Cosmos DB SQL API SDK for Python to manage databases and the JSON documents they contain in this NoSQL database service.

* Create Cosmos DB **databases** and modify their settings
* Create and modify **containers** to store collections of JSON documents
* Create, read, update, and delete the **items** (JSON documents) in your containers
* Query the documents in your database using **SQL-like syntax**

Looking for source code or API reference?

* [SDK source code][source_code]
* [SDK reference documentation][ref_cosmos_sdk]

## Getting started

* Azure subscription - [Create a free account][azure_sub]
* Azure [Cosmos DB account][cosmos_account] - SQL API
* [Python 2.7 or 3.5.3+][python]


If you need a Cosmos DB SQL API account, you can create one with this [Azure CLI][azure_cli] command:

```Bash
az cosmosdb create --resource-group <resource-group-name> --name <cosmos-account-name>
```

## Installation

```bash
pip install azure-cosmos
```

### Configure a virtual environment (optional)

Although not required, you can keep your your base system and Azure SDK environments isolated from one another if you use a virtual environment. Execute the following commands to configure and then enter a virtual environment with [venv][venv]:

```Bash
python3 -m venv azure-cosmosdb-sdk-environment
source azure-cosmosdb-sdk-environment/bin/activate
```

## Key concepts

Interaction with Cosmos DB starts with an instance of the [CosmosClient][ref_cosmosclient] class. You need an **account**, its **URI**, and one of its **account keys** to instantiate the client object.

### Get credentials

Use the Azure CLI snippet below to populate two environment variables with the database account URI and its primary master key (you can also find these values in the Azure portal). The snippet is formatted for the Bash shell.

```Bash
RES_GROUP=<resource-group-name>
ACCT_NAME=<cosmos-db-account-name>

export ACCOUNT_URI=$(az cosmosdb show --resource-group $RES_GROUP --name $ACCT_NAME --query documentEndpoint --output tsv)
export ACCOUNT_KEY=$(az cosmosdb list-keys --resource-group $RES_GROUP --name $ACCT_NAME --query primaryMasterKey --output tsv)
```

### Create client

Once you've populated the `ACCOUNT_URI` and `ACCOUNT_KEY` environment variables, you can create the [CosmosClient][ref_cosmosclient].

```Python
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import azure.cosmos.http_constants as http_constants

import os
url = os.environ['ACCOUNT_URI']
key = os.environ['ACCOUNT_KEY']
client = cosmos_client.CosmosClient(url, {'masterKey': key})
```

## Usage

When you create a Cosmos DB Database Account, you specify the API you'd like to use when interacting with its documents: SQL, MongoDB, Gremlin, Cassandra, or Azure Table.

This SDK is used to interact with an SQL API database account.

Once you've initialized a [CosmosClient][ref_cosmosclient], you can interact with the primary resource types in Cosmos DB:

* Database: A Cosmos DB account can contain multiple databases. A database may contain a number of containers.

* Container: A container is a collection of JSON documents. You create (insert), read, update, and delete items in a container.

* Item: An Item is the dictionary-like representation of a JSON document stored in a container. Each Item you add to a container must include an `id` key with a value that uniquely identifies the item within the container.

For more information about these resources, see [Working with Azure Cosmos databases, containers and items][cosmos_resources].

## Examples

The following sections provide several code snippets covering some of the most common Cosmos DB tasks, including:

* [Create a database](#create-a-database)
* [Create a container](#create-a-container)
* [Replace throughput for a container](#replace-throughput-for-a-container)
* [Get an existing container](#get-an-existing-container)
* [Insert data](#insert-data)
* [Delete data](#delete-data)
* [Query the database](#query-the-database)
* [Modify container properties](#modify-container-properties)

### Create a database

After authenticating your [CosmosClient][ref_cosmosclient], you can work with any resource in the account. You can use [CosmosClient.CreateDatabase][ref_cosmosclient_create_database] to create a database. 

```Python
database_name = 'testDatabase'
try:
    database = client.CreateDatabase({'id': database_name})
except errors.HTTPFailure:
    database = client.ReadDatabase("dbs/" + database_name)
```

### Create a container

This example creates a container with 400 RU/s as the throughput, using [CosmosClient.CreateContainer][ref_cosmosclient_create_container]. If a container with the same name already exists in the database (generating a `409 Conflict` error), the existing container is obtained instead.

```Python
import azure.cosmos.documents as documents
container_definition = {'id': 'products',
                        'partitionKey':
                                    {
                                        'paths': ['/productName'],
                                        'kind': documents.PartitionKind.Hash
                                    }
                        }
try:
    container = client.CreateContainer("dbs/" + database['id'], container_definition, {'offerThroughput': 400})
except errors.HTTPFailure as e:
    if e.status_code == http_constants.StatusCodes.CONFLICT:
        container = client.ReadContainer("dbs/" + database['id'] + "/colls/" + container_definition['id'])
    else:
        raise e
```


### Replace throughput for a container

A single offer object exists per container. This object contains information regarding the container's throughput.
This example retrieves the offer object using [CosmosClient.QueryOffers][ref_cosmosclient_query_offers], and modifies the offer object and replaces the throughput for the container using [CosmosClient.ReplaceOffer][ref_cosmosclient_replace_offer].
```Python
# Get the offer for the container
offers = list(client.QueryOffers("Select * from root r where r.offerResourceId='" + container['_rid'] + "'"))
offer = offers[0]
print("current throughput for " + container['id'] + ": " + str(offer['content']['offerThroughput']))

# Replace the offer with a new throughput
offer['content']['offerThroughput'] = 1000
client.ReplaceOffer(offer['_self'], offer)
print("new throughput for " + container['id'] + ": " + str(offer['content']['offerThroughput']))
```

### Get an existing container

Retrieve an existing container from the database using [CosmosClient.ReadContainer][ref_cosmosclient_read_container]:

```Python
database_id = 'testDatabase'
container_id = 'products'
container = client.ReadContainer("dbs/" + database_id + "/colls/" + container_id)
```

### Insert data

To insert items into a container, pass a dictionary containing your data to [CosmosClient.UpsertItem][ref_container_upsert_item]. Each item you add to a container must include an `id` key with a value that uniquely identifies the item within the container.

This example inserts several items into the container, each with a unique `id`:

```Python
for i in range(1, 10):
    client.UpsertItem("dbs/" + database_id + "/colls/" + container_id, {
            'id': 'item{0}'.format(i),
            'productName': 'Widget',
            'productModel': 'Model {0}'.format(i)
        }
    )
```

### Delete data

To delete items from a container, use [CosmosClient.DeleteItem][ref_container_delete_item]. The SQL API in Cosmos DB does not support the SQL `DELETE` statement.

```Python
for item in client.QueryItems("dbs/" + database_id + "/colls/" + container_id,
                              'SELECT * FROM products p WHERE p.productModel = "DISCONTINUED"',
                              {'enableCrossPartitionQuery': True}):
    client.DeleteItem("dbs/" + database_id + "/colls/" + container_id + "/docs/" + item['id'], {'partitionKey': 'Pager'})
```

### Query the database

A Cosmos DB SQL API database supports querying the items in a container with [CosmosClient.QueryItems][ref_container_query_items] using SQL-like syntax.

This example queries a container for items with a specific `id`:

```Python
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

# Enumerate the returned items
import json
for item in client.QueryItems("dbs/" + database_id + "/colls/" + container_id,
                              'SELECT * FROM ' + container_id + ' r WHERE r.id="item3"',
                              {'enableCrossPartitionQuery': True}):
    print(json.dumps(item, indent=True))
```

> NOTE: Although you can specify any value for the container name in the `FROM` clause, we recommend you use the container name for consistency.

Perform parameterized queries by passing a dictionary containing the parameters and their values to [CosmosClient.QueryItems][ref_container_query_items]:

```Python
discontinued_items = client.QueryItems("dbs/" + database_id + "/colls/" + container_id,
                                       {
                                            'query': 'SELECT * FROM root r WHERE r.id=@id',
                                            'parameters': [
                                                {'name': '@id', 'value': 'item3'}
                                            ]
                                       },
                                       {'enableCrossPartitionQuery': True})
for item in discontinued_items:
    print(json.dumps(item, indent=True))
```

For more information on querying Cosmos DB databases using the SQL API, see [Query Azure Cosmos DB data with SQL queries][cosmos_sql_queries].

### Modify container properties

Certain properties of an existing container can be modified. This example sets the default time to live (TTL) for items in the container to 10 seconds:

```Python
container = client.ReadContainer("dbs/" + database_id + "/colls/" + container_id)
container['defaultTtl'] = 10
modified_container = client.ReplaceContainer("dbs/" + database_id + "/colls/" + container_id, container)
# Display the new TTL setting for the container
print(json.dumps(modified_container['defaultTtl']))
```

For more information on TTL, see [Time to Live for Azure Cosmos DB data][cosmos_ttl].

## Troubleshooting

### General

When you interact with Cosmos DB using the Python SDK, errors returned by the service correspond to the same HTTP status codes returned for REST API requests:

[HTTP Status Codes for Azure Cosmos DB][cosmos_http_status_codes]

For example, if you try to create a container using an ID (name) that's already in use in your Cosmos DB database, a `409` error is returned, indicating the conflict. In the following snippet, the error is handled gracefully by catching the exception and displaying additional information about the error.

```Python
try:
    container = client.CreateContainer("dbs/" + database['id'], container_definition)
except errors.HTTPFailure as e:
    if e.status_code == http_constants.StatusCodes.CONFLICT:
        print("""Error creating container
HTTP status code 409: The ID (name) provided for the container is already in use.
The container name must be unique within the database.""")
    else:
        raise e
```

## Next steps

For more extensive documentation on the Cosmos DB service, see the [Azure Cosmos DB documentation][cosmos_docs] on docs.microsoft.com.

<!-- LINKS -->
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_portal]: https://portal.azure.com
[azure_sub]: https://azure.microsoft.com/free/
[cloud_shell]: https://docs.microsoft.com/azure/cloud-shell/overview
[cosmos_account_create]: https://docs.microsoft.com/azure/cosmos-db/how-to-manage-database-account
[cosmos_account]: https://docs.microsoft.com/azure/cosmos-db/account-overview
[cosmos_container]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-containers
[cosmos_database]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-databases
[cosmos_docs]: https://docs.microsoft.com/azure/cosmos-db/
[cosmos_http_status_codes]: https://docs.microsoft.com/rest/api/cosmos-db/http-status-codes-for-cosmosdb
[cosmos_item]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items#azure-cosmos-items
[cosmos_request_units]: https://docs.microsoft.com/azure/cosmos-db/request-units
[cosmos_resources]: https://docs.microsoft.com/azure/cosmos-db/databases-containers-items
[cosmos_sql_queries]: https://docs.microsoft.com/azure/cosmos-db/how-to-sql-query
[cosmos_ttl]: https://docs.microsoft.com/azure/cosmos-db/time-to-live
[python]: https://www.python.org/downloads/
[ref_container_delete_item]: https://docs.microsoft.com/python/api/azure-cosmos/azure.cosmos.cosmos_client.cosmosclient?view=azure-python#deleteitem-document-link--options-none-
[ref_container_query_items]: https://docs.microsoft.com/python/api/azure-cosmos/azure.cosmos.cosmos_client.cosmosclient?view=azure-python#queryitems-database-or-container-link--query--options-none--partition-key-none-
[ref_container_upsert_item]: https://docs.microsoft.com/python/api/azure-cosmos/azure.cosmos.cosmos_client.cosmosclient?view=azure-python#upsertitem-database-or-container-link--document--options-none-
[ref_cosmos_sdk]: https://docs.microsoft.com/python/api/azure-cosmos/azure.cosmos.cosmos_client?view=azure-python
[ref_cosmosclient_create_database]: https://docs.microsoft.com/python/api/azure-cosmos/azure.cosmos.cosmos_client.cosmosclient?view=azure-python#createdatabase-database--options-none-
[ref_cosmosclient_create_container]: https://docs.microsoft.com/python/api/azure-cosmos/azure.cosmos.cosmos_client.cosmosclient?view=azure-python#createcontainer-database-link--collection--options-none-
[ref_cosmosclient_read_container]: https://docs.microsoft.com/en-us/python/api/azure-cosmos/azure.cosmos.cosmos_client.cosmosclient?view=azure-python#readcontainer-collection-link--options-none-
[ref_cosmosclient_query_offers]: https://docs.microsoft.com/en-us/python/api/azure-cosmos/azure.cosmos.cosmos_client.cosmosclient?view=azure-python#queryoffers-query--options-none-
[ref_cosmosclient_replace_offer]: https://docs.microsoft.com/en-us/python/api/azure-cosmos/azure.cosmos.cosmos_client.cosmosclient?view=azure-python#replaceoffer-offer-link--offer-
[ref_cosmosclient]: https://docs.microsoft.com/python/api/azure-cosmos/azure.cosmos.cosmos_client.cosmosclient?view=azure-python
[ref_httpfailure]: https://docs.microsoft.com/python/api/azure-cosmos/azure.cosmos.errors.httpfailure?view=azure-python
[sample_database_mgmt]: https://github.com/Azure/azure-cosmos-python/tree/master/samples/DatabaseManagement
[sample_document_mgmt]: https://github.com/Azure/azure-cosmos-python/tree/master/samples/DocumentManagement
[source_code]: https://github.com/Azure/azure-cosmos-python
[venv]: https://docs.python.org/3/library/venv.html
[virtualenv]: https://virtualenv.pypa.io


# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
