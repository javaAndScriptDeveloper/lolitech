module "network-resources" {
  source = "./network-resources"
  vpc_id = module.network-resources.vpc_id
}

module "security-resources" {
  source = "./security-resources"
  vpc_id = module.network-resources.vpc_id
}


module "ec2_instance" {
  source = "terraform-aws-modules/ec2-instance/aws"

  name = var.name

  instance_type          = var.instance_type
  ami                    = var.ami_id
  key_name               = var.key_name
  monitoring             = true
  vpc_security_group_ids = [module.security-resources.security_group_id]
  subnet_id              = module.network-resources.public_subnet_id

  tags = {
    Terraform   = "true"
  }

  user_data = <<-EOF
#!/bin/bash
sudo yum update -y
sudo amazon-linux-extras install nginx1 -y
sudo systemctl enable nginx
sudo systemctl start nginx
EOF
}