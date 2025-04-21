#!/bin/bash

awslocal secretsmanager create-secret \
  --name aws/assume-role/creds \
  --secret-string '{"aws_access_key_id":"dummy-access-key", "aws_secret_access_key":"dummy-secret-key"}'
