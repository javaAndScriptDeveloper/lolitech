# Infrastructure as Code — Lab Work

Modular Terraform configuration that provisions a complete AWS environment: networking, security, and a compute instance, split across three reusable modules.

**Stack:** Terraform · AWS (VPC · EC2 · Security Groups) · Nginx

---

## Structure

```
main.tf                  # Root module — wires the three child modules together
provider.tf              # AWS provider, region eu-west-2, default profile
variable.tf              # Instance name, AMI, key pair, instance type

network-resources/       # VPC + public subnet
security-resources/      # Security group
```

The root module uses the [terraform-aws-modules/ec2-instance](https://registry.terraform.io/modules/terraform-aws-modules/ec2-instance/aws) community module for the compute resource, and two local modules for networking and security.

---

## Modules

### `network-resources/`
Creates:
- A VPC with CIDR `10.0.0.0/16`.
- A public subnet `10.0.1.0/24` with `map_public_ip_on_launch = true`.

Outputs `vpc_id` and `public_subnet_id`, which the root module passes to the other two modules.

### `security-resources/`
Creates a security group inside the VPC that allows:
- Inbound SSH (port 22) from anywhere.
- Inbound HTTP (port 80) from anywhere.
- All outbound traffic.

Outputs `security_group_id`.

### EC2 instance (root module)
Uses `terraform-aws-modules/ec2-instance`:
- AMI: `ami-0d18e50ca22537278` (Amazon Linux, `eu-west-2`).
- Instance type: `t2.micro`.
- Placed in the public subnet with the security group from above.
- CloudWatch detailed monitoring enabled.
- `user_data` installs and starts Nginx on boot.

---

## Usage

```bash
terraform init
terraform plan
terraform apply
```

AWS credentials are read from the default profile (`~/.aws/credentials`). Override variables with `-var` flags or a `.tfvars` file.
