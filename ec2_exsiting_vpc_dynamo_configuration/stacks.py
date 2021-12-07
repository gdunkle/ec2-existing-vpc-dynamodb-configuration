from aws_cdk import Stack, aws_ec2 as ec2, aws_iam as iam
from constructs import Construct
import boto3
from botocore.config import Config
from ec2_exsiting_vpc_dynamo_configuration import dynamo_to_ec2_props
from ec2_exsiting_vpc_dynamo_configuration.constructs import DynamicEc2


class DevStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc_id: str,
        subnet_selection: ec2.SubnetSelection,
        security_group_id: str,
        role_arn: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        config = Config(
            region_name=self.region,
            signature_version="v4",
            retries={"max_attempts": 10, "mode": "standard"},
        )

        client = boto3.client("dynamodb", config=config)
        paginator = client.get_paginator("scan")
        iterator = paginator.paginate(TableName="ec2_instances")
        vpc = ec2.Vpc.from_lookup(self, "vpc", vpc_id=vpc_id)

        instance_role = iam.Role.from_role_arn(self, "isntance_role", role_arn=role_arn)
        security_group = ec2.SecurityGroup.from_security_group_id(
            self, "security-group", security_group_id=security_group_id
        )

        for page in iterator:
            items = page["Items"]
            for item in items:
                props = dynamo_to_ec2_props(item)
                props.vpc = vpc
                props.subnet_selection = subnet_selection
                props.instance_role = instance_role
                props.security_group = security_group
                DynamicEc2(self, props.instance_name, props)
