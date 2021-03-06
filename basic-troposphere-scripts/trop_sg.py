from troposphere import Base64, Join
from troposphere import Parameter, Ref, Template
from troposphere import cloudformation
import troposphere.ec2 as ec2

import json
import boto3
import sys
import argparse
#from simplesecuritygroups.template import SecurityGroups, SecurityGroup
from troposphere import (Base64,
        cloudformation,
        FindInMap,
        GetAtt,
        GetAZs,
        Join,
        Parameter,
        Output,
        Ref,
        Tags,
Template)

# Loading the config file based on the argument passed
jsondata = ''
vpcdata = ''
sgs = ''
CidrIp = ''

# Fetching values from json given as argument while this python is executed
parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()
with open(args.filename) as file:
        jsondata = json.load(file)

t = Template()
t.add_version("2010-09-09")
t.add_description("CF to create Security Groups for %s" % jsondata['EnvInfo']['Name'])

#Get VPC ID based on the environment using boto3
boto_ec2 = boto3.resource('ec2',region_name='%s' % jsondata['Tags']['Region'])
vpcfilters = [{'Name':'tag-value', 'Values':['%s' % jsondata['Tags']['Name']]}]
try:
    vpcdata = list(boto_ec2.vpcs.filter(Filters=vpcfilters))[0]
except IndexError as e:
    print >> sys.stderr, ("Boto can't find the VPC. Is it there? [%s]" % e)
    sys.exit(0)

sgs = jsondata['securitygroups']

# Function to create ingress and egress rules from json
def make_securitygroup_rules(IpProtocol, FromPort, ToPort, CidrIp, ReferenceSecurityGroup):
    if ReferenceSecurityGroup == "":
        return(ec2.SecurityGroupRule(
            CidrIp = CidrIp,
            IpProtocol = IpProtocol,
            FromPort = FromPort,
            ToPort = ToPort
    ))
    else:
        return(ec2.SecurityGroupRule(
            SourceSecurityGroupId = Ref(ReferenceSecurityGroup),
            IpProtocol = IpProtocol,
            FromPort = FromPort,
            ToPort = ToPort
    ))

# Security Group Creation
# Ref: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-security-group-rule.html
for sg in sgs:
    sgname = sg['Name']
    t.add_resource(ec2.SecurityGroup(
        sgname,
        GroupDescription = sg['Description'],
        SecurityGroupIngress = [make_securitygroup_rules(**rules) for rules in sg['iRules']],
        SecurityGroupEgress = [make_securitygroup_rules(**rules) for rules in sg['eRules']],
        VpcId = vpcdata.vpc_id,
        Tags = Tags(**{
        'Name': '%s' % sg['Name'],
        'wltkkeas:environment': '%s' % jsondata['Tags']['Env']
        }) 
    ))

print(t.to_json())

