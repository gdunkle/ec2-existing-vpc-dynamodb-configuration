from aws_cdk import Stack, aws_iam as iam, aws_ec2 as ec2
import constructs
from textwrap import dedent
from distutils.util import strtobool


class DynamicEc2Props:
    def __init__(self, **kwargs):
        self.instance_name: str = kwargs["instance_name"]
        self.instance_type: ec2.InstanceType = kwargs["instance_type"]
        self.machine_image: ec2.MachineImage = kwargs["machine_image"]
        self.vpc: ec2.Vpc = kwargs.get("vpc", None)
        self.instance_role: iam.Role = kwargs.get("instance_role", None)
        self.subnet_selection: ec2.SubnetSelection = kwargs.get(
            "subnet_selection", None
        )
        self.security_group = kwargs.get("security_group", None)
        self.user_data: [str] = kwargs.get("user_data", None)
        self.is_windows: bool = kwargs.get("is_windows", None)
        self.key_name: str = kwargs.get("key_name", None)


def linux_init_script(stack: Stack, props: DynamicEc2Props):
    handle = ec2.InitServiceRestartHandle()

    cfn_auto_reloader_conf = dedent(
        f"""[cfn-auto-reloader-hook]
            triggers=post.update
            path=Resources.nginx.Metadata.AWS::CloudFormation::Init
            action=/opt/aws/bin/cfn-init -v --stack={stack.stack_name} --resource "{props.instance_name}"  --configsets default region={stack.region}
            runas=root
            """
    )
    cfn_hup_conf = dedent(
        f"""[main]
            stack={stack.stack_name}
            region={stack.region}
            """
    )
    return ec2.CloudFormationInit.from_config_sets(
        config_sets={"default": ["Install"]},
        configs={
            "Install": ec2.InitConfig(
                [
                    ec2.InitFile.from_string(
                        "/etc/cfn/cfn-hup.conf",
                        content=cfn_hup_conf,
                        group="root",
                        owner="root",
                        mode="000400",
                        service_restart_handles=[handle],
                    ),
                    ec2.InitFile.from_string(
                        "/etc/cfn/hooks.d/cfn-auto-reloader.conf",
                        content=cfn_auto_reloader_conf,
                        group="root",
                        owner="root",
                        mode="000400",
                        service_restart_handles=[handle],
                    ),
                    ec2.InitService.enable(
                        "cfn-hup",
                        enabled=True,
                        ensure_running=True,
                        service_restart_handle=handle,
                    ),
                ]
            )
        },
    )


def json_to_ec2_props(item: dict) -> DynamicEc2Props:
    instance_type_class = item["class"]
    instance_type_size = item["size"]
    instance_name = item["name"]
    machine_image_is_windows = item["is_windows"]
    machine_image_name = item["image_name"]
    user_data_list = []
    user_data_string_set = item["user_data"] if "user_data" in item else None
    key_name = item["key_name"]
    if user_data_string_set is not None:
        for line in user_data_string_set:
            user_data_list.append(line)
    return DynamicEc2Props(
        instance_name=instance_name,
        instance_type=ec2.InstanceType.of(
            ec2.InstanceClass[instance_type_class],
            instance_size=ec2.InstanceSize[instance_type_size],
        ),
        machine_image=get_machine_image(machine_image_name, machine_image_is_windows),
        user_data=user_data_list,
        is_windows=machine_image_is_windows,
        key_name=key_name,
    )


def get_machine_image(name: str, is_windows: bool) -> ec2.MachineImage:
    machine_image: ec2.MachineImage
    if "LATEST" == name:
        if is_windows:
            machine_image = ec2.MachineImage.latest_windows(
                version=ec2.WindowsVersion.WINDOWS_SERVER_2019_ENGLISH_FULL_BASE
            )
        else:
            machine_image = ec2.MachineImage.latest_amazon_linux(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            )
    else:
        ami_map = name.split(":")
        region = ami_map[0]
        ami = ami_map[1]
        if is_windows:
            machine_image = ec2.MachineImage.generic_windows({region: ami})
        else:
            machine_image = ec2.MachineImage.generic_linux({region: ami})

    return machine_image
