#!/bin/bash

aws --endpoint-url=http://localhost:4566 secretsmanager create-secret \
  --name aws/assume-role/creds \
  --secret-string '{"aws_access_key_id":"test-access-key","aws_secret_access_key":"test-secret-key"}'
