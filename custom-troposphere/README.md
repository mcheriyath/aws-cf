## Create Server Stack with Cloudformation using troposphere

Pre-requisites:
- Python Boto3
- AWS Credentials or ec2 instance with the suitable roles to create Cloudformation stack

```
python main.py config/amqp-federated-config.json > amqp-federated-2az-4nodes.template
aws cloudformation create-stack --stack-name amqp-cluster-2az --template-body file://amqp-federated-2az-4nodes.template
```
