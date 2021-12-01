from aws_cdk import core as cdk, aws_iam as iam, aws_ec2 as ec2
from ec2_exsiting_vpc_dynamo_configuration import DynamicEc2Props
from textwrap import dedent


class DynamicEc2(cdk.Construct):
    def __init__(
        self, scope: cdk.Construct, construct_id: str, props: DynamicEc2Props
    ) -> None:
        super().__init__(scope, construct_id)
        instance = ec2.Instance(
            self,
            construct_id,
            instance_type=props.instance_type,
            machine_image=props.machine_image,
            vpc=props.vpc,
            role=props.instance_role,
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(
                        30, encrypted=False, delete_on_termination=True
                    ),
                )
            ],
            instance_name=props.instance_name,
            security_group=props.security_group,
            vpc_subnets=props.subnet_selection,
        )
        cfn_instance = instance.node.default_child
        user_data = (
            ec2.UserData.for_windows() if props.is_windows else ec2.UserData.for_linux()
        )
        for command in props.user_data:
            user_data.add_commands(dedent(command))

        user_data_string = user_data.render()
        instance.add_user_data(user_data_string)
