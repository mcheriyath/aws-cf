# Converted from EC2InstanceSample.template located at:
# http://aws.amazon.com/cloudformation/aws-cloudformation-templates/

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

ec2_instance_2 = template.add_resource(ec2.Instance(
    "Ec2Instance2",
    ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
    InstanceType="t1.micro",
    KeyName="mcheriyath",
    SecurityGroups=["mcheriyath-sg"],
    Tags=Tags(**{
        'Name': 'DevOpsDenver',
        'Owner': 'mithun@email.com'
        })
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
        "InstanceId2",
        Description="InstanceId of the newly created EC2 instance",
        Value=Ref(ec2_instance_2),
    ),
    Output(
        "PublicIP2",
        Description="Public IP address of the newly created EC2 instance",
        Value=GetAtt(ec2_instance_2, "PublicIp"),
    ),
    Output(
        "PublicDNS2",
        Description="Public DNSName of the newly created EC2 instance",
        Value=GetAtt(ec2_instance_2, "PublicDnsName"),
    ),

])
  
print(template.to_json())
