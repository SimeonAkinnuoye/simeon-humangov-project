
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "humangov-cluster" 
  cluster_version = "1.29"             

  # Networking
  vpc_id                   = var.vpc_id
  subnet_ids               = var.subnet_ids
  control_plane_subnet_ids = var.subnet_ids

  # Security: Allow you to access it from the internet (public endpoint)
  cluster_endpoint_public_access = true

  # Grant Admin permissions to the user running Terraform
  enable_cluster_creator_admin_permissions = true

  # Node Groups (The "t3.medium" workers)
  eks_managed_node_groups = {
    standard_workers = {           # Matches your --nodegroup-name
      min_size     = 1
      max_size     = 2
      desired_size = 1             # Matches your --nodes 1

      instance_types = ["t3.medium"] # Matches your --node-type
      capacity_type  = "ON_DEMAND"
    }
  }

  tags = {
    Environment = "dev"
    Project     = "humangov"
  }
}

module "lb_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "5.0"

  role_name = "humangov-eks-lb-role"

  attach_load_balancer_controller_policy = true
  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:aws-load-balancer-controller"]
    }
  }
  tags = {
    Project     = "humangov-eks-lb-role"
  }
}