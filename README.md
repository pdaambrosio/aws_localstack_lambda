# AWS Metadata Collector

This project is a Python-based AWS Lambda function designed to collect metadata about VPCs (Virtual Private Clouds) from multiple AWS accounts. The metadata is stored in a MySQL database for further analysis.

## Features

- **AWS Secrets Manager Integration**: Retrieves AWS credentials securely from Secrets Manager.
- **Cross-Account Role Assumption**: Uses AWS STS to assume roles in other AWS accounts.
- **VPC Metadata Collection**: Fetches VPC IDs from AWS EC2 service.
- **MySQL Integration**: Stores collected metadata in a MySQL database.
- **LocalStack Support**: Can be run locally using LocalStack for testing AWS services.

## Project Structure

.env
.gitignore
docker-compose.yml
init-secrets.sh
lambda_function.py
local_test.py
localstack


### Key Files

- **`lambda_function.py`**: The main Lambda function code.
- **`docker-compose.yml`**: Sets up MySQL and LocalStack for local testing.
- **`init-secrets.sh`**: Script to initialize secrets in LocalStack's Secrets Manager.
- **`local_test.py`**: Script to test the Lambda function locally.

## Prerequisites

- Python 3.11
- Docker and Docker Compose
- LocalStack for local AWS service emulation
- MySQL client library (`pymysql`)

## Setup

1. **Clone the Repository**:

   ```bash
   git clone <repository-url>
   cd <repository-folder>
    ```

2. Install Dependencies: Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Set Up Environment Variables: Update the .env file with your configuration:

```bash
# .env
DB_HOST=localhost
DB_PORT=3306
DB_USER=testuser
DB_PASS=testpass
DB_NAME=aws_metadata
AWS_ENDPOINT_URL=http://localhost:4566
```

4. Start Docker Services: Use Docker Compose to start MySQL and LocalStack:

   ```bash
   docker-compose up -d
   ```

5. Initialize Secrets: Run the init-secrets.sh script to create a dummy secret in LocalStack:

   ```bash
    ./init-secrets.sh
    ```

## Usage

### Running Locally

1. Test the Lambda Function: Run the local_test.py script to invoke the Lambda function locally:

    ```bash
    python local_test.py
    ```

2. Check MySQL Database: Verify that the vpcs table in the MySQL database contains the collected VPC metadata.

### Deploying to AWS

1. Package the Lambda function and its dependencies.
2. Deploy the function to AWS Lambda using the AWS CLI or a deployment tool like AWS SAM.

### Code Overview

#### Main Components

**get_secret():** Retrieves AWS credentials from Secrets Manager.
**assume_role():** Assumes an IAM role in a target AWS account.
**get_vpcs():** Fetches VPC IDs from the EC2 service.
**connect_mysql():** Establishes a connection to the MySQL database.
**create_table_if_not_exists():** Ensures the vpcs table exists in the database.
**insert_vpcs():** Inserts VPC metadata into the database.
**lambda_handler():** The main entry point for the Lambda function.

#### Database Schema

The vpcs table has the following structure:

```sql
CREATE TABLE vpcs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id VARCHAR(20),
    vpc_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Testing

> Use LocalStack to emulate AWS services locally.
> Run local_test.py to test the Lambda function without deploying to AWS.

#### Troubleshooting

> MySQL Connection Issues: Ensure the database credentials in .env match the MySQL configuration in docker-compose.yml.
> LocalStack Issues: Verify that LocalStack is running and accessible at http://localhost:4566.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
