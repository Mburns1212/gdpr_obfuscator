# GDPR Obfuscator

## Project Overview

This is a general-purpose tool to process data being ingested by AWS and intercept personally identifiable information (PII) to ensure data stored for analysis follows GDPR guidelines.

## Supported formats

- CSV
- JSON - works for all JSON formats including nested
- Parquet - flat data only

## Installation

Recommended to install this package in a virtual environment.

```bash
python -m venv venv
source venv/bin/activate
```

(Local) Package Only

```bash

pip install path_to_package[all]

```


(Remote) Package Only

```bash

pip install git+https://github.com/Mburns1212/gdpr_obfuscator.git#egg=gdpr_obfuscator[all]

```

If you are deploying in AWS where boto3 may be built in and don't want to install it run:

```bash

pip install git+https://github.com/Mburns1212/gdpr_obfuscator.git

```

For the full repo use git clone.

```bash

git clone https://github.com/Mburns1212/gdpr_obfuscator.git

```

## Example input

Example input for the obfuscator function.

```json

{
    "file_to_obfuscate": "s3://my_ingestion_bucket/new_data/file1.csv",
    "pii_fields": ["name", "email_address"]
}
```
Both of these keys are required and the file to obfuscate must be a valid s3 object URI.

## Capabilities

This tool will get a supported file object from s3, obfuscate all PIIs specified and output the obfuscated file as bytes.

## Quick Start

After following installation instructions create an object in s3 and use tool in this way to obfuscate your chosen pii_fields.

```py
from gdpr_obfuscator import obfuscator

obfuscated_csv = obfuscator({"file_to_obfuscate": "s3://example-bucket/file.csv", "pii_fields": ["name"]})
with open('obfuscated.pq', 'wb') as file:
    file.write(obfuscated_csv)

```

## Parquet Engine

- This tool uses fastparquet by default as it is more lightweight than pyarrow.
- However, there are parquet compressions which aren't supported by fastparquet and will require pyarrow to be installed.
- If you try to use the tool without the required engine you will get an ImportError giving instuctions on how to install required engine.