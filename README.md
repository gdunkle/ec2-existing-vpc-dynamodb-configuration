
# ec2-existing-vpc-dynamodb-configuration

Python CDK project to demonstrate how you can dynamically deploy ec2 instances to an existing vpc based on configuration in dynamodb

### Deployment

#### Prerequisites

- [AWS Command Line Interface](https://aws.amazon.com/cli/)
- [AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_install)
- Python 3.9 or later
- [Poetry](https://python-poetry.org/docs/)
- A dynamodb table named "ec2_instances" with the following attributes
  - instance_name - Unique key which serves as the name of the instance
  - instance_type_class - Class of the instace based on [ec2.InstanceClass](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.InstanceClass.html)
  - instance_type_size - Size of the instance based on [ec2.InstanceSize](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-ec2.InstanceSize.html)
  - machine_image_is_windows - Whether the instance is windows otherwise linux
  - machine_image_name - (can be 'LATEST')
  - user_data - (string set of commands)


To create a virtualenv on MacOS and Linux:

```
$ poetry install
```
Drop into the python virtual env
```
$ poetry shell
```


If you haven't already be sure to bootstrap your cdk environment
```
$ cdk bootstrap aws://$AWS_DEFAULT_ACCOUNT/$AWS_DEFAULT_REGION
```

At this point you can now deploy the solution by issuing the following command

```
$  cdk deploy -c DEFAULT_ACCOUNT=<THE DEFAULT AWS ACCOUNT TO DEPLOY TO IF NONE IS SPECIFIED> -c DEFAULT_REGION=<THE DEFAULT AWS REGION TO DEPLOY TO IF NONE IS SPECIFIED> -c DEV_ACCOUNT=<YOUR DEVELOPMENT ACCOUNT ID> -c VPC_ID=<A VPC ID TO DEPLOY TO> -c SECURITY_GROUP_ID=<A SECURITY GROUP TO ASSIGN TO THE INSTANCES> -c ROLE_ARN="<THE INSTANCE ROLE ARN TO ASSIGN TO THE INSTANCES>"

```
 The use of the context variables on the command line is not necessary you can (and probably should) define these values directly in the app.py along with different stacks for different environments

# Example

These values...
![](images/01.png)

Result in this deployment

![](images/02.png)
