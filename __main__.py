import pulumi
from src.modules.vpc import CreateVPC
from src.modules.eks import CreateEKS

# Initialize stack resources
vpc = CreateVPC()
eks = CreateEKS(vpc.get_vpc())

# Export core outputs
pulumi.export("cluster_name", eks.cluster_name)
pulumi.export("kubeconfig", eks.kubeconfig)

# Export instructions for accessing the cluster
kubeconfig_command = pulumi.Output.concat(
    "aws eks update-kubeconfig --name ",
    eks.cluster_name,
    " --region ",
    pulumi.Config("aws").require("region"),
)
pulumi.export("kubeconfig_command", kubeconfig_command)
