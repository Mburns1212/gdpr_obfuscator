import pandas
from boto3 import client
import json
import io
from .json_obfuscate import json_obfuscate


def obfuscator(event):
    if not isinstance(event, dict):
        raise TypeError('Input should be a dictionary')

    required_keys = {'file_to_obfuscate', 'pii_fields'}
    provided_keys = set(event.keys())
    missing = required_keys - provided_keys
    if missing:
        raise ValueError(f'Missing key(s): {missing}')

    file = event['file_to_obfuscate']
    piis = event['pii_fields']
    s3_client = client('s3')
    bucket_name = file.split('/')[2]
    key = '/'.join(file.split('/')[3:])
    file_type = key.split('.')[-1]

    if file_type == 'csv':
        csv_file = s3_client.get_object(Bucket=bucket_name, Key=key)['Body']
        csv_df = pandas.read_csv(csv_file)
        for column in csv_df:
            if column in piis:
                csv_df[column] = '***'
        byte_csv = csv_df.to_csv(index=False).encode('utf-8')
        return byte_csv

    if file_type == 'json':
        json_obj = s3_client.get_object(Bucket=bucket_name,
                                        Key=key)['Body'].read()
        json_file = json.loads(json_obj)
        json_obfuscate(json_file, piis)
        byte_json = json.dumps(json_file, indent=2).encode('utf-8')
        return byte_json

    if '.parquet' in key:
        parquet_file = s3_client.get_object(Bucket=bucket_name,
                                            Key=key)['Body'].read()
        try:
            parquet_df = pandas.read_parquet(io.BytesIO(parquet_file),
                                            engine='fastparquet')
        except (ValueError):
            parquet_df = pandas.read_parquet(io.BytesIO(parquet_file),
                                            engine='pyarrow')
        for column in parquet_df:
            if column in piis:
                parquet_df[column] = '***'
        byte_parquet = parquet_df.to_parquet(engine='fastparquet')
        return byte_parquet

    raise ValueError(f'{file_type} files are not supported')
