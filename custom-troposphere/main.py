from troposphere import cloudformation
from troposphere import Base64, FindInMap, GetAtt
from troposphere import Parameter, Ref, Tags, Template, GetAtt, Join, Output
import troposphere.ec2 as ec2
from troposphere.route53 import RecordSetType
import argparse
import sys
import os
import boto3
import json

# Declaring variable to which everything is loaded from the config json file(argument)
jsondata = ''
instances = ''
# Fetching values from json given as argument while this python is executed
parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()
with open(args.filename) as file:
         jsondata = json.load(file)

t = Template()
t.add_version("2010-09-09")
t.add_description("CF to create %s EC2 instance(s) for %s environment" % (jsondata['NetworkInfo']['ServerName'], jsondata['NetworkInfo']['Env']))

# Get ZoneID, VPCID, SecurityGroupID and SubnetID based on the environment using boto3
client = boto3.client('ec2', region_name='us-east-1')
route53client = boto3.client('route53')

vpcdata = client.describe_vpcs(
    Filters=[{'Name': 'tag-value', 'Values': [jsondata['NetworkInfo']['VPCName']]}]
)

# Function to get the subnet id
def get_subnet_id(VpcId, Type, AvailabilityZone):
    subnetdata = client.describe_subnets(Filters=[
        {'Name': 'vpc-id', 'Values': [VpcId]},
        {'Name': 'tag-value', 'Values': [Type]},
        {'Name': 'availability-zone', 'Values': [AvailabilityZone]}
    ])
    return subnetdata['Subnets'][0]['SubnetId']

# Function to get the security group id using the group tag name
def get_securitygroup_id(SecurityGroupTagName):
    sgdata = client.describe_security_groups(
        Filters=[{'Name': 'tag-value', 'Values': [SecurityGroupTagName]}]
    )
    return sgdata['SecurityGroups'][0]['GroupId']


# Get the private hosted zone id
def get_domain_data():
    response = route53client.list_hosted_zones_by_name(
        DNSName='us-east-1.staging-nonprod.aws',
    )
    return response


allzones = get_domain_data()

# Get all instance details from json
instances = jsondata['Instances']


# Creating instances
for instance in instances:
    servername = instance['ServerName']
    t.add_resource(ec2.Instance(
        servername,
        ImageId=instance['ImageId'],
        KeyName=instance['KeyPairName'],
        SubnetId=get_subnet_id(vpcdata['Vpcs'][0]['VpcId'], jsondata['NetworkInfo']['Type'], instance['AZ']),
        SecurityGroupIds=[get_securitygroup_id(instance['SecurityGroupTagName']), ],
        Tenancy=instance['Tenancy'],
	IamInstanceProfile=jsondata['NetworkInfo']['Role'],
        InstanceType=instance['InstanceType'],
        BlockDeviceMappings=[
            ec2.BlockDeviceMapping(
                DeviceName="/dev/xvda",
                Ebs=ec2.EBSBlockDevice(
                    VolumeType="gp2",
                    VolumeSize=instance['VolumeSize']
                )
            ),
        ],
        UserData=Base64(Join('', [
            '#!/bin/bash\n',
            'sudo pip install https://s3.amazonaws.com/cloudformation-examples/',
            'aws-cfn-bootstrap-latest.tar.gz\n',
            '/bin/echo \'', instance['DomainName'], '-', jsondata['ServerTags']['Env'], '\'.us-east-1.staging-nonprod.aws > /etc/hostname  \n',
            '/bin/echo $(curl http://169.254.169.254/latest/meta-data/local-ipv4) \'', instance['DomainName'], '-',   jsondata['ServerTags']['Env'],
            '\'.us-east-1.staging-nonprod.aws\'', instance['DomainName'], '-', jsondata['ServerTags']['Env'], '\' >> /etc/hosts \n',
            '/bin/hostname \'', instance['DomainName'], '-', jsondata['ServerTags']['Env'], '\'\n',
            'cfn-init -s \'', Ref('AWS::StackName'),
            '\' -r Ec2Instance -c ascending\n'
        ])),
        Tags=Tags(**{
            'Name': '%s' % instance['ServerName'],
            'Env': '%s' % jsondata['ServerTags']['Env'],
            'Category': '%s' % jsondata['ServerTags']['Category'],
            'Owner': '%s' % jsondata['ServerTags']['Owner']
        })
    ))

# Creating Route53 A records
for i in instances:
    domainname = i['DomainName']
    t.add_resource(RecordSetType(
        domainname,
        HostedZoneId=allzones['HostedZones'][0]['Id'],  # 0 for prod; 1 for stage and dev.
        Comment="DNS A record for %s" % i['ServerName'],
        Name=Join("", [i['DomainName'], "-", jsondata['ServerTags']['Env'], ".",
                  "us-east-1.staging-nonprod.aws", "."]),
        Type="A",
        TTL="300",
        ResourceRecords=[GetAtt(i['ServerName'], "PrivateIp")],  # http://docs.aws.amazon.com/AWSCloudFormation/      latest/UserGuide/intrinsic-function-reference-getatt.html
    ))

print(t.to_json())
