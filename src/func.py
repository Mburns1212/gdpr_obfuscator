import pandas
from boto3 import client
import json

def obfuscator(event):
    file = event['file_to_obfuscate']
    piis = event['pii_fields']
    s3_client = client('s3')
    bucket_name = file.split('/')[2]
    key = '/'.join(file.split('/')[3:])
    file_type = key.split('.')[-1]
    if file_type == 'csv':
        csv_df = pandas.read_csv(s3_client.get_object(Bucket=bucket_name, Key=key)['Body'])
        for column in csv_df:
            if column in piis:
                csv_df[column] = '***'
        byte_csv = csv_df.to_csv(index=False).encode('utf-8')
        return byte_csv
    if file_type == 'json':
        json_file = json.loads(s3_client.get_object(Bucket=bucket_name, Key=key)['Body'].read())
        if type(json_file) == list:
            for item in json_file:
                for field in item:
                    if field in piis:
                        item[field] = '***'
        if type(json_file) == dict:
            for key in json_file.keys():
                for item in json_file[key]:
                    for field in item:
                        if field in piis:
                            item[field] = '***'
        byte_json = json.dumps(json_file,indent=2).encode('utf-8')
        return byte_json
    



