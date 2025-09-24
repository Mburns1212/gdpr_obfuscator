import pandas
from boto3 import client

def obfuscator(event):
    file = event['file_to_obfuscate']
    piis = event['pii_fields']
    s3_client = client('s3')
    bucket_name = file.split('/')[2]
    key = '/'.join(file.split('/')[3:])
    file_type = key.split('.')[-1]
    csv_df = pandas.read_csv(s3_client.get_object(Bucket=bucket_name, Key=key)['Body'])
    for column in csv_df:
        if column in piis:
            csv_df[column] = '***'
    byte_csv = csv_df.to_csv(index=False).encode('utf-8')
    return byte_csv


