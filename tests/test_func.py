import pytest
from src.func import obfuscator
from moto import mock_aws
import os
import boto3
from unittest.mock import patch
import json
import io
from pandas.testing import assert_frame_equal
import pandas as pd
import re

@pytest.fixture(autouse=True)
def aws_creds():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture(scope="function")
def s3_client(aws_creds):
    with mock_aws():
        yield boto3.client("s3")

@pytest.fixture(scope="function")
def s3_client_with_bucket(s3_client):
    s3_client.create_bucket(Bucket="test-bucket")
    yield s3_client

@pytest.fixture(scope="function")
def s3_client_with_bucket_with_objects(s3_client_with_bucket):
    with open('tests/test_files/test.csv','rb') as file:
       s3_client_with_bucket.put_object(
           Bucket="test-bucket",
           Key="test.csv",
           Body=file.read()
        )
    with open('tests/test_files/test_obj.json','rb') as file:
        s3_client_with_bucket.put_object(
            Bucket="test-bucket",
            Key="test_obj.json",
            Body=file.read()
        )
    with open('tests/test_files/test_array.json','rb') as file:
        s3_client_with_bucket.put_object(
            Bucket="test-bucket",
            Key="test_array.json",
            Body=file.read()
        )
    with open('tests/test_files/test_nested.json','rb') as file:
        s3_client_with_bucket.put_object(
            Bucket="test-bucket",
            Key="test_nested.json",
            Body=file.read()
        )
    with open('tests/test_files/test.parquet','rb') as file:
        s3_client_with_bucket.put_object(
            Bucket="test-bucket",
            Key="test.parquet",
            Body=file.read()
        )

    yield s3_client_with_bucket


@patch('src.func.client')
def test_returns_bytestream_csv(mock_client, s3_client_with_bucket_with_objects):
    mock_client.return_value = s3_client_with_bucket_with_objects
    assert type(obfuscator({'file_to_obfuscate': 's3://test-bucket/test.csv', 'pii_fields': ['student_id']})) == bytes

@patch('src.func.client')
def test_returns_bytestream_json(mock_client, s3_client_with_bucket_with_objects):
    mock_client.return_value = s3_client_with_bucket_with_objects
    assert type(obfuscator({'file_to_obfuscate': 's3://test-bucket/test_array.json', 'pii_fields': ['student_id']})) == bytes

@patch('src.func.client')
def test_returns_bytestream_parquet(mock_client, s3_client_with_bucket_with_objects):
    mock_client.return_value = s3_client_with_bucket_with_objects
    assert type(obfuscator({'file_to_obfuscate': 's3://test-bucket/test.parquet', 'pii_fields': ['student_id']})) == bytes

@patch('src.func.client')
def test_obfuscates_piis_csv(mock_client, s3_client_with_bucket_with_objects):
    mock_client.return_value = s3_client_with_bucket_with_objects
    result = obfuscator({'file_to_obfuscate': 's3://test-bucket/test.csv', 'pii_fields': ['student_id','course']}).decode('utf-8')
    with open('tests/test_files/obfuscated.csv','rb') as file:
        expected = file.read().decode('utf-8')
    assert result == expected

@patch('src.func.client')
def test_obfuscates_piis_json_array(mock_client, s3_client_with_bucket_with_objects):
    mock_client.return_value = s3_client_with_bucket_with_objects
    result = obfuscator({'file_to_obfuscate': 's3://test-bucket/test_array.json', 'pii_fields': ['student_id']}).decode('utf-8')
    with open('tests/test_files/obfuscated_array.json','rb') as file:
        expected = file.read().decode('utf-8')
    assert json.loads(result) == json.loads(expected)

@patch('src.func.client')
def test_obfuscates_piis_json_obj(mock_client, s3_client_with_bucket_with_objects):
    mock_client.return_value = s3_client_with_bucket_with_objects
    result = obfuscator({'file_to_obfuscate': 's3://test-bucket/test_obj.json', 'pii_fields': ['student_id']}).decode('utf-8')
    with open('tests/test_files/obfuscated_obj.json','rb') as file:
        expected = file.read().decode('utf-8')
    assert json.loads(result) == json.loads(expected)

@patch('src.func.client')
def test_obfuscates_piis_nested_json(mock_client, s3_client_with_bucket_with_objects):
    mock_client.return_value = s3_client_with_bucket_with_objects
    result = obfuscator({'file_to_obfuscate': 's3://test-bucket/test_nested.json', 'pii_fields': ['name']}).decode('utf-8')
    with open('tests/test_files/obfuscated_nested.json','rb') as file:
        expected = file.read().decode('utf-8')
    assert json.loads(result) == json.loads(expected)

@patch('src.func.client')
def test_parquet(mock_client, s3_client_with_bucket_with_objects):
    mock_client.return_value = s3_client_with_bucket_with_objects
    result = pd.read_parquet(io.BytesIO(obfuscator({'file_to_obfuscate': 's3://test-bucket/test.parquet', 'pii_fields': ['student_id']})))
    expected = pd.read_parquet('tests/test_files/obfuscated.parquet')
    assert_frame_equal(result,expected)

@patch('src.func.client')
def test_invalid_file_type(mock_client, s3_client_with_bucket_with_objects):
    mock_client.return_value = s3_client_with_bucket_with_objects
    with pytest.raises(ValueError, match='txt files are not supported'):
        obfuscator({'file_to_obfuscate': 's3://test-bucket/test.txt', 'pii_fields': ['student_id']})

@patch('src.func.client')
def test_invalid_input_type(mock_client, s3_client_with_bucket_with_objects):
    mock_client.return_value = s3_client_with_bucket_with_objects
    with pytest.raises(TypeError, match='Input should be a dictionary'):
        obfuscator('incorrect_input')

@patch('src.func.client')
def test_input_missing_keys(mock_client, s3_client_with_bucket_with_objects):
    mock_client.return_value = s3_client_with_bucket_with_objects
    with pytest.raises(ValueError, match=re.escape("Missing key(s): {'pii_fields'}")):
        obfuscator({'file_to_obfuscate': 's3://test-bucket/test.csv'})