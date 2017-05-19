# Converted from EC2InstanceSample.template located at:
# http://aws.amazon.com/cloudformation/aws-cloudformation-templates/
# Usage: python trop-ec2-sample.py
# Pre-requisites: Need to have a VPC, Subnet and SecurityGroup
# author: mithun@cheriyath.in

from troposphere import Base64, FindInMap, GetAtt
from troposphere import Parameter, Ref, Tags, Template, GetAtt, Join, Output
import troposphere.ec2 as ec2
import sys
import os
import boto3

template = Template()

template.add_mapping('RegionMap', {
    "us-east-1": {"AMI": "ami-29d0c53e"},
    "us-east-2": {"AMI": "ami-38e7bd5d"}
})

#Get VPCID, SecurityGroupID and SubnetID based on the environment using boto3

client = boto3.client('ec2')

vpcdata = client.describe_vpcs(
    Filters=[{'Name': 'tag-value','Values': ['uatdev']}]
    )

subnetdata = client.describe_subnets(
    Filters=[{'Name': 'vpc-id','Values': [vpcdata['Vpcs'][0]['VpcId']]},
             {'Name': 'tag-value','Values': ['Public','uatdev']}]
    )

sgdata = client.describe_security_groups(
    Filters=[{'Name': 'tag-value','Values': ['UatDevPublicSecurityGroup']}]
    )

ec2_instance = template.add_resource(ec2.Instance(
    "NagiosServer",
    ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
    KeyName='ec2deployuatdev',
    SubnetId=subnetdata['Subnets'][0]['SubnetId'],
    SecurityGroupIds=[sgdata['SecurityGroups'][0]['GroupId'],],
    Tenancy='default',
    InstanceType="t2.micro",
    BlockDeviceMappings=[
        ec2.BlockDeviceMapping(
            DeviceName="/dev/sda1",
            Ebs=ec2.EBSBlockDevice(
                VolumeType="gp2",
                VolumeSize="20"
            )
        ),
    ],
    Tags=Tags(**{
        'Name': 'NagiosServer',
        'Environment': 'uatdev',
        })
))

template.add_output([
    Output(
        "InstanceId",
        Description="InstanceId of the newly created EC2 instance",
        Value=Ref(ec2_instance),
    ),
    Output(
        "AZ",
        Description="Availability Zone of the newly created EC2 instance",
        Value=GetAtt(ec2_instance, "AvailabilityZone"),
    ),
    Output(
        "PrivateIP",
        Description="Private IP address of the newly created EC2 instance",
        Value=GetAtt(ec2_instance, "PrivateIp"),
    ),
])

print(template.to_json())
