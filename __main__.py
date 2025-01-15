from src.modules.vpc import vpc
from src.modules.eks import eks

vpc = vpc.CreateVPC()
eks = eks.CreateEKS(vpc.get_vpc())
