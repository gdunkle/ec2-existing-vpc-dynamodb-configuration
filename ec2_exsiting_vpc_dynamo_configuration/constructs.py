from aws_cdk import Stack, aws_iam as iam, aws_ec2 as ec2
from constructs import Construct
from ec2_exsiting_vpc_dynamo_configuration import DynamicEc2Props
from textwrap import dedent


class DynamicEc2(Construct):
    def __init__(
        self, scope: Construct, construct_id: str, props: DynamicEc2Props
    ) -> None:
        super().__init__(scope, construct_id)
        instance = ec2.Instance(
            self,
            construct_id,
            instance_type=props.instance_type,
            machine_image=props.machine_image,
            vpc=props.vpc,
            role=props.instance_role,
            instance_name=props.instance_name,
            security_group=props.security_group,
            vpc_subnets=props.subnet_selection,
            key_name=props.key_name,
        )
        cfn_instance = instance.node.default_child
        user_data = (
            ec2.UserData.for_windows() if props.is_windows else ec2.UserData.for_linux()
        )
        for commands in props.user_data:
            if commands is not None:
                for command in commands:
                    if command is not None:
                        user_data.add_commands(dedent(command))

        user_data_string = user_data.render()
        instance.add_user_data(user_data_string)
