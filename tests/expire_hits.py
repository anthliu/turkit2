
from utils import get_client

client = get_client(None)
print(client.get_account_balance())

existing_hits = client.list_hits()
counter = 0
for hit in existing_hits['HITs']:
    counter+=1
    print(f"counter: {counter}")
    response = client.update_expiration_for_hit(
    HITId=hit['HITId'],
    ExpireAt=0)
    # response = None
    # try:
    #     response = client.delete_hit(HITId=hit['HITId'])
    # except:
    #     print("catch", hit['HITStatus'])
    print(hit['HITStatus'], response)
