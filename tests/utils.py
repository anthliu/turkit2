import boto3

prod_endpoint = 'https://mturk-requester.us-east-1.amazonaws.com'
sand_endpoint = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

def read_key_file(argf):
    with open(argf) as f:
        key_id, access_key, *_ = f.read().split()

    return key_id.strip(), access_key.strip()

def get_client(argf, production=False):
    key_id, access_key = read_key_file(argf)

    if production:
        endpoint = prod_endpoint
    else:
        endpoint = sand_endpoint

    return boto3.client('mturk',
       aws_access_key_id = key_id,
       aws_secret_access_key = access_key,
       region_name= 'us-east-1',
       endpoint_url = endpoint
    )
