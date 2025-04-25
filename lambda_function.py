import boto3
import os
import json
import pymysql
# from datetime import datetime

TEST_ACCOUNTS = [
    {"account_id": "1234123513", "role_name": "test-role"}
]

def get_secret():
    """
    Retrieves AWS access key and secret access key from AWS Secrets Manager.

    The function connects to the AWS Secrets Manager using the endpoint URL
    specified in the `AWS_ENDPOINT_URL` environment variable. It fetches the
    secret with the ID `aws/assume-role/creds` and extracts the access key
    and secret access key from the secret's JSON string.

    Returns:
        tuple: A tuple containing the AWS access key ID and secret access key.
    """
    client = boto3.client('secretsmanager', endpoint_url=os.getenv("AWS_ENDPOINT_URL"))
    response = client.get_secret_value(SecretId='aws/assume-role/creds')
    secret = json.loads(response['SecretString'])
    return secret['aws_access_key_id'], secret['aws_secret_access_key']

def assume_role(account_id: str, role_name: str, base_session) -> boto3.Session:
    sts = base_session.client('sts')
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
    resp = sts.assume_role(RoleArn=role_arn, RoleSessionName="SyncSession")
    creds = resp['Credentials']
    return boto3.Session(
        aws_access_key_id=creds['AccessKeyId'],
        aws_secret_access_key=creds['SecretAccessKey'],
        aws_session_token=creds['SessionToken']
    )

def get_vpcs(session: boto3.Session) -> list:
    ec2 = session.client('ec2')
    vpcs = ec2.describe_vpcs()
    return [vpc['VpcId'] for vpc in vpcs['Vpcs']]

def connect_mysql() -> pymysql.connections.Connection:
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME'),
        port=int(os.getenv('DB_PORT', 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

def create_table_if_not_exists(conn, sql: str) -> None:
    with conn.cursor() as cursor:
        cursor.execute(sql)
    conn.commit()

# def insert_vpcs(conn, account_id, vpc_ids):
#     with conn.cursor() as cursor:
#         for vpc_id in vpc_ids:
#             cursor.execute(
#                 "INSERT INTO vpcs (account_id, vpc_id) VALUES (%s, %s)",
#                 (account_id, vpc_id)
#             )
#     conn.commit()

def insert_items(conn: pymysql.connections.Connection, table_name: str, items: list, columns: list) -> None:
    placeholders = ', '.join(['%s'] * len(columns))
    columns_str = ', '.join(columns)

    with conn.cursor() as cursor:
        sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        for item in items:
            values = tuple(item[col] for col in columns)
            cursor.execute(sql, values)
    conn.commit()

def lambda_handler(event, context):
    access_key, secret_key = get_secret()

    base_session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    conn = connect_mysql()
    vpc_table_sql: str = """
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        account_id VARCHAR(20),
        vpc_id VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    create_table_if_not_exists(conn, vpc_table_sql.format(table_name='vpcs'))

    for account in TEST_ACCOUNTS:
        account_id = account['account_id']
        role_name = account['role_name']

        # Assume role in the target account
        session = assume_role(account_id, role_name, base_session)

        # Retrieve VPC IDs
        vpc_ids = get_vpcs(session)

        # Insert VPC IDs into MySQL database
        items = [{'account_id': account_id, 'vpc_id': vpc_id} for vpc_id in vpc_ids]
        insert_items(conn, 'vpcs', items, ['account_id', 'vpc_id'])

    conn.close()

    return {
        'statusCode': 200,
        'body': json.dumps('VPC IDs inserted successfully!')
    }
