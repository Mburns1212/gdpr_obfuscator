# GDPR Obfuscator

## Project Overview

This is a general-purpose tool to process data being ingested by AWS and intercept personally identifiable information (PII) to ensure data stored for analysis follows GDPR guidelines.

## Supported formats

- CSV
- JSON - works for all JSON formats including nested
- Parquet - flat data only

## Example input

Example input for the obfuscator function.

```json

{
    "file_to_obfuscate": "s3://my_ingestion_bucket/new_data/file1.csv",
    "pii_fields": ["name", "email_address"]
}
```
Both of these keys are required and the file to obfuscate must be a valid s3 object ARN.

## Capabilities

This tool will get a supported file object from s3, obfuscate all PIIs specified and output the obfuscated file as bytes.
