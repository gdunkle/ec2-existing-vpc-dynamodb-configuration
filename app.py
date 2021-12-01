#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

# For consistency with TypeScript code, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core as cdk, aws_ec2 as ec2

from ec2_exsiting_vpc_dynamo_configuration.stacks import DevStack

app = cdk.App()
# I'm bringing in these values from the context b/c i can't check them into github
default_account = app.node.try_get_context("DEFAULT_ACCOUNT")
default_region = app.node.try_get_context("DEFAULT_REGION")
dev_account = app.node.try_get_context("DEV_ACCOUNT")
vpc_id = app.node.try_get_context("VPC_ID")
security_group_id = app.node.try_get_context("SECURITY_GROUP_ID")
role_arn = app.node.try_get_context("ROLE_ARN")

account = os.environ.get("AWS_DEFAULT_ACCOUNT", os.environ.get("CDK_DEFAULT_ACCOUNT"))
region = os.environ.get("AWS_DEFAULT_REGION", os.environ.get("CDK_DEFAULT_REGION"))
if region is not None and account is not None:
    env = cdk.Environment(account=account, region=region)
elif account is not None:
    env = cdk.Environment(account=account, region=default_region)
else:
    env = cdk.Environment(account=default_account, region=default_region)
is_dev = True if env.account == dev_account else False
if is_dev:
    DevStack(
        app,
        "ec2stack",
        vpc_id=vpc_id,
        subnet_selection=ec2.SubnetSelection(
            subnet_type=ec2.SubnetType.PUBLIC, one_per_az=True
        ),
        security_group_id=security_group_id,
        role_arn=role_arn,
        env=env,
    )

app.synth()
