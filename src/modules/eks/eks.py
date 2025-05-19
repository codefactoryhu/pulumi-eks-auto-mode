import pulumi
from pulumi import Output
import pulumi_eks as eks
import pulumi_awsx as awsx
from typing import Dict, Any
from ..kms import KMS


class CreateEKS:
    """
    Creates and manages an EKS cluster with Auto Mode enabled along with
    necessary infrastructure components like KMS keys for encryption.
    """

    def __init__(self, vpc: awsx.ec2.Vpc):
        """
        Initialize and create an EKS cluster

        Args:
            vpc: The VPC where the EKS cluster will be deployed
        """
        self._vpc = vpc
        self._project_name = pulumi.get_project()
        self._stack_name = pulumi.get_stack()
        self._cluster_name = f"{self._stack_name}-{self._project_name}"

        # Load EKS configuration
        eks_config = pulumi.Config("eks")
        self._eks_version = eks_config.require("version")
        self._eks_cluster_log_types = eks_config.require_object("clusterLogging")
        self._eks_upgrade_policy = eks_config.get("upgradePolicy") or "STANDARD"

        # Create the cluster
        self._kms_key = self._create_kms_key()
        self._cluster = self._create_cluster()

        # Export outputs
        self._export_cluster_outputs()

    def _create_kms_key(self) -> KMS:
        """
        Create a KMS key for EKS cluster encryption

        Returns:
            The KMS instance for EKS encryption
        """
        return KMS(
            f"{self._cluster_name}-kms",
            "KMS key for EKS cluster encryption",
            "EKS cluster",
            deletion_window_in_days=15,  # Set a longer retention period for important infra components
        )

    def _create_cluster(self) -> eks.Cluster:
        """
        Create the EKS cluster with Auto Mode enabled

        Returns:
            The created EKS cluster instance
        """
        # Configure tags for cluster resources
        tags = {
            "Name": self._cluster_name,
            "Environment": self._stack_name,
            "ManagedBy": "Pulumi",
        }

        # Create EKS cluster with Auto Mode enabled
        return eks.Cluster(
            self._cluster_name,
            name=self._cluster_name,
            version=self._eks_version,
            authentication_mode=eks.AuthenticationMode.API,
            vpc_id=self._vpc.vpc_id,
            public_subnet_ids=self._vpc.public_subnet_ids,
            private_subnet_ids=self._vpc.private_subnet_ids,
            encryption_config_key_arn=self._kms_key.get_key_arn(),
            enabled_cluster_log_types=self._eks_cluster_log_types,
            auto_mode={
                "enabled": True,
            },
            tags=tags,
        )

    def _export_cluster_outputs(self) -> None:
        """Export EKS cluster-related values as Pulumi stack outputs"""
        pulumi.export("cluster_name", self._cluster_name)
        pulumi.export("kubeconfig", self._cluster.kubeconfig)
        # Access cluster endpoint from the kubeconfig
        self._cluster.kubeconfig.apply(
            lambda kc: pulumi.export(
                "cluster_endpoint", 
                kc.get("clusters", [{}])[0].get("cluster", {}).get("server", "")
            )
        )
        pulumi.export("cluster_version", self._eks_version)

    @property
    def cluster(self) -> eks.Cluster:
        """
        Returns the EKS cluster instance

        Returns:
            The EKS cluster instance
        """
        return self._cluster

    def get_cluster(self) -> eks.Cluster:
        """
        Returns the EKS cluster instance (legacy method)

        Returns:
            The EKS cluster instance
        """
        return self._cluster

    @property
    def endpoint(self) -> Output[str]:
        """
        Returns the EKS cluster endpoint

        Returns:
            Pulumi output containing the cluster endpoint
        """
        # Access cluster endpoint from the kubeconfig
        return self._cluster.kubeconfig.apply(
            lambda kc: kc.get("clusters", [{}])[0].get("cluster", {}).get("server", "")
        )
    
    @property
    def version(self) -> Output[str]:
        """
        Returns the EKS cluster version
        
        Returns:
            Pulumi output containing the cluster version
        """
        return Output.from_input(self._eks_version)
    
    @property
    def kubeconfig(self) -> Output[Dict[str, Any]]:
        """
        Returns the kubeconfig for connecting to the EKS cluster

        Returns:
            Pulumi output containing the kubeconfig
        """
        return self._cluster.kubeconfig

    @property
    def cluster_name(self) -> str:
        """
        Returns the EKS cluster name

        Returns:
            The cluster name
        """
        return self._cluster_name
