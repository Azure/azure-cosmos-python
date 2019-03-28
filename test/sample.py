import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.documents as documents
import azure.cosmos.partition_key as partition_key
import azure.cosmos.auth as auth
import requests
import datetime
from six.moves.urllib.parse import quote as urllib_quote
import six
def test_sample():
    connectionPolicy = documents.ConnectionPolicy()
    #connectionPolicy.DisableSSLVerification = True
    #client = cosmos_client.CosmosClient(
    #    'https://localhost:8081',
    #    {'masterKey': 'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=='}, connection_policy=connectionPolicy)

    #db = client.get_database('mydb')
    #collection = db.create_container(id='mycoll', partition_key=partition_key.PartitionKey(path='id', kind='Hash'))

    base_url = "https://localhost:8081///"
    base_url_split = base_url.split(":");
    url = base_url_split[0] + ":" +  base_url_split[1] + ":" + base_url_split[2] .split("/")[0] + "//"
    print('\n' + url)
    '''
    c = client.get_database("mydb").get_container("mycoll-oldapi")
    i = c.create_item(body={'id':'1'})
    print(i)
    i = c.get_item('1', partition_key=partition_key.Empty)
    print(i)
    i = c.replace_item(i, {'id':'2'})
    print(i)
    i = c.upsert_item({'id':'1', 'updateField':'2'})
    print(i)
    i = list(c.query_items(query="Select * from c", partition_key=partition_key.Empty))
    print(i)
    i = c.delete_item('1', partition_key=partition_key.Empty)
    print(i)
    '''


