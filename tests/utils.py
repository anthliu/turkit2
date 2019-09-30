import boto3

prod_endpoint = 'https://mturk-requester.us-east-1.amazonaws.com'
sand_endpoint = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

def get_client(production=False):
    '''
    Note: need to set awscli configuration!
    '''
    if production:
        endpoint = prod_endpoint
    else:
        endpoint = sand_endpoint

    return boto3.client('mturk',
       region_name= 'us-east-1',
       endpoint_url = endpoint
    )
