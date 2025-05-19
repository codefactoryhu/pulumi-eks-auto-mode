import pulumi
from pulumi import Output
import pulumi_awsx as awsx
from typing import Any


class CreateVPC:
    """
    Creates and manages an AWS VPC with public and private subnets for running
    Kubernetes workloads on EKS.
    """
    
    def __init__(self):
        """
        Initialize the VPC using configuration from Pulumi config.
        """
        self._stack_name = pulumi.get_stack()
        self._project_name = pulumi.get_project()
        self._vpc_name = f"{self._stack_name}-{self._project_name}-vpc"

        # Load configuration
        vpc_config = pulumi.Config("vpc")
        self._vpc_ipv4_cidr_block = vpc_config.require("vpc_ipv4_cidr_block")
        self._vpc_enable_dns_hostnames = vpc_config.require_bool("vpc_enable_dns_hostnames")
        self._vpc_enable_dns_support = vpc_config.require_bool("vpc_enable_dns_support")

        # Create VPC resources
        self._vpc = self._create_vpc()
        
        # Export outputs
        self._export_vpc_outputs()

    def _create_vpc(self) -> awsx.ec2.Vpc:
        """
        Create the VPC with public and private subnets properly tagged for EKS.
        
        Returns:
            The created VPC instance
        """
        cluster_name = f"{self._stack_name}-{self._project_name}"
        
        return awsx.ec2.Vpc(
            self._vpc_name,
            cidr_block=self._vpc_ipv4_cidr_block,
            subnet_specs=[
                {
                    "type": awsx.ec2.SubnetType.PUBLIC,
                    "tags": {
                        f"kubernetes.io/cluster/{cluster_name}": "shared",
                        "kubernetes.io/role/elb": "1",
                    },
                },
                {
                    "type": awsx.ec2.SubnetType.PRIVATE,
                    "tags": {
                        f"kubernetes.io/cluster/{cluster_name}": "shared",
                        "kubernetes.io/role/internal-elb": "1",
                    },
                },
            ],
            enable_dns_hostnames=self._vpc_enable_dns_hostnames,
            enable_dns_support=self._vpc_enable_dns_support,
            subnet_strategy=awsx.ec2.SubnetAllocationStrategy.AUTO,
            tags={
                "Name": self._vpc_name,
                "Environment": self._stack_name,
                "ManagedBy": "Pulumi",
            },
        )
    
    def _export_vpc_outputs(self) -> None:
        """Export VPC-related values as Pulumi stack outputs"""
        pulumi.export("vpc_id", self._vpc.vpc_id)
        pulumi.export("public_subnet_ids", self._vpc.public_subnet_ids)
        pulumi.export("private_subnet_ids", self._vpc.private_subnet_ids)

    def get_vpc(self) -> awsx.ec2.Vpc:
        """
        Returns the created VPC instance
        
        Returns:
            The VPC instance
        """
        return self._vpc
    
    @property
    def vpc_id(self) -> Output[str]:
        """
        Returns the VPC ID
        
        Returns:
            Pulumi output containing the VPC ID
        """
        return self._vpc.vpc_id
    
    @property
    def public_subnet_ids(self) -> Output[Any]:
        """
        Returns the public subnet IDs
        
        Returns:
            Pulumi output containing the list of public subnet IDs
        """
        return self._vpc.public_subnet_ids
    
    @property
    def private_subnet_ids(self) -> Output[Any]:
        """
        Returns the private subnet IDs
        
        Returns:
            Pulumi output containing the list of private subnet IDs
        """
        return self._vpc.private_subnet_ids