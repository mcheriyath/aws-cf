# Converted from EC2InstanceSample.template located at:
# http://aws.amazon.com/cloudformation/aws-cloudformation-templates/
# Sample domain getting created i-795b0ee0.us-east-1.prokarmalab.com


import troposphere.ec2 as ec2
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
from troposphere.route53 import RecordSetType

template = Template()

template.add_mapping('RegionMap', {
    "us-east-1": {"AMI": "ami-4d87fc5a"},
})


ec2_instance_1 = template.add_resource(ec2.Instance(
    "Ec2Instance1",
    ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
    InstanceType="t1.micro",
    KeyName="mcheriyath",
    SecurityGroups=["mcheriyath-sg"],
    Tags=Tags(**{
        'Name': 'DevOpsDenver',
        'Owner': 'mithun@email.com'
        })
))

myDNSRecord = template.add_resource(RecordSetType(
    "myDNSRecord",
    HostedZoneName=Join("", ["example.com", "."]),
    Comment="DNS name for my instance.",
    Name=Join("", ["ops1", ".", "applicationname", ".",
              "example.com", "."]),
    Type="A",
    TTL="900",
    ResourceRecords=[GetAtt("Ec2Instance1", "PublicIp")],
))

template.add_output([
    Output(
        "InstanceId1",
        Description="InstanceId of the newly created EC2 instance",
        Value=Ref(ec2_instance_1),
    ),
    Output(
        "PublicIP1",
        Description="Public IP address of the newly created EC2 instance",
        Value=GetAtt(ec2_instance_1, "PublicIp"),
    ),
    Output(
        "PublicDNS1",
        Description="Public DNSName of the newly created EC2 instance",
        Value=GetAtt(ec2_instance_1, "PublicDnsName"),
    ),
    Output(
        "DomainName",
        Description="DomainName for the newly created instance",
        Value=Ref(myDNSRecord),
    ),

])

print(template.to_json())
