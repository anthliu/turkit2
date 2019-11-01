import boto3

prod_endpoint = 'https://mturk-requester.us-east-1.amazonaws.com'
sand_endpoint = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'

def get_client(profile='anthony', production=False):
    if production:
        endpoint = prod_endpoint
    else:
        endpoint = sand_endpoint

    if profile is not None:
        session = boto3.Session(profile_name=profile)
    else:
        session = boto3

    return session.client('mturk',
       region_name='us-east-1',
       endpoint_url = endpoint
    )

def get_s3(profile='anthony'):
    if profile is not None:
        session = boto3.Session(profile_name=profile)
    else:
        session = boto3

    return session.client(
        's3',
        region_name='us-east-2',
    )
