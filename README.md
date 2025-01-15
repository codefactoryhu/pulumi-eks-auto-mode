## Overview
This repository contains a Pulumi kit to create AWS resources written in Python.
Currently this code will create the following resources:
- VPC
    - 3 public subnets
    - 3 private subnets
    - Internet Gateway
    - NAT Gateway
    - Route tables
- KMS
    - KMS key
    - KMS key alias
- EKS Auto Mode

``` bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


``` bash
pulumi stack init

# stack name (dev):
# Enter your passphrase to protect config/secrets:
# Re-enter your passphrase to confirm:
# Created stack 'dev'
```

Copy variables from Pulumi.dev.template.yaml to Pulumi.dev.yaml. After run the following command:
```
pulumi up
```

```
aws eks update-kubeconfig --name dev-eks-auto-mode  --region eu-west-1
```

Enjoy your cluster! :)
