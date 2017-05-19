#Sample file which creates troposphere, Launches an instance with autoscaling, adds the hostname to route53 using ansible ran as userdata
from troposphere import Base64, Join
from troposphere import Parameter, Ref, Template, FindInMap
from troposphere import cloudformation, autoscaling
from troposphere.autoscaling import AutoScalingGroup, Tag
from troposphere.autoscaling import LaunchConfiguration
from troposphere.elasticloadbalancing import LoadBalancer
from troposphere.policies import (
    AutoScalingReplacingUpdate, AutoScalingRollingUpdate, UpdatePolicy
)
import troposphere.ec2 as ec2
import troposphere.elasticloadbalancing as elb

t = Template()

t.add_description("""Configures autoscaling group for api app""")

ScaleCapacity = t.add_parameter(Parameter(
        "ScaleCapacity",
        Default="1",
        Type="String",
        Description="Number of api servers to run",
))

EnvType = t.add_parameter(Parameter(
        "EnvType",
        Type="String",
        Description="The environment being deployed into",
))

t.add_mapping('RegionMap', {
    "us-east-1": {"AMI": "ami-4d87fc5a"}
})

LaunchConfiguration = t.add_resource(LaunchConfiguration(
        "LaunchConfiguration",
        UserData=Base64(Join('', [
                    "#!/bin/bash\n",
                    "sudo yum install httpd -y\n",
                    "sudo pip install https://s3.amazonaws.com/cloudformation-examples/",
                    "aws-cfn-bootstrap-latest.tar.gz\n",

                    "# Run cfn-init\n",
                    "/opt/aws/bin/cfn-init -v ",
                    "         --stack ", { "Ref": "AWS::StackName" },
                    "         --resource LaunchConfiguration ",
                    "         --region ", { "Ref" : "AWS::Region" }, "\n",

                    "/opt/aws/bin/cfn-signal -e $? ",
                    "    --resource AutoscalingGroup",
                    "    --stack ", Ref("AWS::StackName"),
                    "    --region ", Ref("AWS::Region"), "\n"


                ])),
        ImageId=FindInMap("RegionMap", Ref("AWS::Region"), "AMI"),
        KeyName="mcheriyath",
        BlockDeviceMappings=[
                            ec2.BlockDeviceMapping(
                            DeviceName="/dev/sda1",
                            Ebs=ec2.EBSBlockDevice(VolumeSize="8")
                            ),
                           ],
        SecurityGroups=["sg-b6de24cb"],
        InstanceType="t1.micro",
))

LoadBalancer = t.add_resource(LoadBalancer(
        "LoadBalancer",
        ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
                    Enabled=True,
                    Timeout=120,
                ),
        Subnets=["subnet-094ce924","subnet-c6bb2f8f"],
        HealthCheck=elb.HealthCheck(
                    Target="HTTP:80/",
                    HealthyThreshold="5",
                    UnhealthyThreshold="2",
                    Interval="20",
                    Timeout="15",
                ),
        Listeners=[
                    elb.Listener(
                                    LoadBalancerPort="80",
                                    InstancePort="80",
                                    Protocol="HTTP",
                                    InstanceProtocol="HTTP",
                                ),
                ],
        CrossZone=True,
        SecurityGroups=["sg-4cde2431"],
        LoadBalancerName="api-lb",
        Scheme="internet-facing",
))

AutoscalingGroup = t.add_resource(AutoScalingGroup(
        "AutoscalingGroup",
        DesiredCapacity=Ref(ScaleCapacity),
        Tags=[
                    Tag("Environment", Ref(EnvType), True)
                ],
        LaunchConfigurationName=Ref(LaunchConfiguration),
        MinSize=Ref(ScaleCapacity),
        MaxSize=Ref(ScaleCapacity),
        VPCZoneIdentifier=["subnet-0e4ce923","subnet-c7bb2f8e"],
        LoadBalancerNames=[Ref(LoadBalancer)],
        AvailabilityZones=["us-east-1a",
                           "us-east-1b"],
        HealthCheckType="EC2",
        UpdatePolicy=UpdatePolicy(
                    AutoScalingReplacingUpdate=AutoScalingReplacingUpdate(
                                    WillReplace=True,
                                ),
                    AutoScalingRollingUpdate=AutoScalingRollingUpdate(
                                    PauseTime='PT5M',
                                    MinInstancesInService="1",
                                    MaxBatchSize='1',
                                    WaitOnResourceSignals=True
                                )
                )
))

print(t.to_json())
