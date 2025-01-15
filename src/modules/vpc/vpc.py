import pulumi
import pulumi_awsx as awsx


class CreateVPC:
    def __init__(self):
        self._stack_name = pulumi.get_stack()
        self._project_name = pulumi.get_project()

        vpc_config = pulumi.Config("vpc")

        self._vpc_ipv4_cidr_block = vpc_config.require("vpc_ipv4_cidr_block")
        self._vpc_enable_dns_hostnames = vpc_config.require_bool(
            "vpc_enable_dns_hostnames"
        )
        self._vpc_enable_dns_support = vpc_config.require_bool("vpc_enable_dns_support")

        self._vpc = self._create_vpc()

    def _create_vpc(self):
        vpc_name = f"{self._stack_name}-{self._project_name}-vpc"
        return awsx.ec2.Vpc(
            vpc_name,
            cidr_block=self._vpc_ipv4_cidr_block,
            subnet_specs=[
                {
                    "type": awsx.ec2.SubnetType.PUBLIC,
                    "tags": {
                        "kubernetes_io_cluster_eks_auto_mode_demo": "shared",
                        "kubernetes_io_role_elb": "1",
                    },
                },
                {
                    "type": awsx.ec2.SubnetType.PRIVATE,
                    "tags": {
                        "kubernetes_io_cluster_eks_auto_mode_demo": "shared",
                        "kubernetes_io_role_internal_elb": "1",
                    },
                },
            ],
            enable_dns_hostnames=self._vpc_enable_dns_hostnames,
            enable_dns_support=self._vpc_enable_dns_support,
            subnet_strategy=awsx.ec2.SubnetAllocationStrategy.AUTO,
        )

    def get_vpc(self):
        return self._vpc
