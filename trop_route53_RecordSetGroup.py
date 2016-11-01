from troposphere import GetAtt, Join, Template
from troposphere.route53 import AliasTarget, RecordSetType, RecordSetGroup, RecordSet

t = Template()

myDNSRecord = t.add_resource(RecordSetGroup(
        "devdevopsdemoELBDNSARecord0",
        HostedZoneName=Join("", ["example.net", "."]),
        Comment="DNS Entry to point to the ELB for devopsdemo",
        RecordSets=[
            RecordSet(
                Name="devopsdemo.dev.example.net.",
                Type="A",
                AliasTarget=AliasTarget(
                    GetAtt("devdevopsdemoELB", "CanonicalHostedZoneNameID"),
                    GetAtt("devdevopsdemoELB", "CanonicalHostedZoneName"),
                ),
            ),
            RecordSet(
                Name="devopsdemo-dev.example.net.",
                Type="A",
                AliasTarget=AliasTarget(
                    GetAtt("devdevopsdemoELB", "CanonicalHostedZoneNameID"),
                    GetAtt("devdevopsdemoELB", "CanonicalHostedZoneName"),
                ),
            ),
        ],
    )
)

print t.to_json()
