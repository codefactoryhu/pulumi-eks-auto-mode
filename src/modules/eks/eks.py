import pulumi
import pulumi_eks as eks
from ..kms import kms


class CreateEKS:
    def __init__(self, vpc):
        self._vpc = vpc
        self._project_name = pulumi.get_project()
        self._stack_name = pulumi.get_stack()
        self._cluster_name = f"{self._stack_name}-{self._project_name}"

        eks_config = pulumi.Config("eks")

        self._eks_version = eks_config.require("version")
        self._eks_cluster_log_types = eks_config.require_object("clusterLogging")

        self._cluster = self._create_cluster()

    def _create_kms_key(self):
        return kms.KMS(
            f"{self._cluster_name}-kms",
            "KMS key for EKS cluster",
            "EKS cluster",
        )

    def _create_cluster(self):
        return eks.Cluster(
            self._cluster_name,
            name=self._cluster_name,
            version=self._eks_version,
            authentication_mode=eks.AuthenticationMode.API,
            vpc_id=self._vpc.vpc_id,
            public_subnet_ids=self._vpc.public_subnet_ids,
            private_subnet_ids=self._vpc.private_subnet_ids,
            encryption_config_key_arn=self._create_kms_key().get_key_arn(),
            enabled_cluster_log_types=self._eks_cluster_log_types,
            auto_mode={
                "enabled": True,
            },
        )

    def get_cluster(self):
        return self._cluster
