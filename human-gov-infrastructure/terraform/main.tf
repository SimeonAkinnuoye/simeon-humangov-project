provider "aws" {
  region = "us-east-1"
}

module "network" {
  source = "./modules/network"
}

module "aws_human_gov_infrastructure" {
  source     = "./modules/application"
  for_each   = toset(var.states)
  state_name = each.value
  vpc_id     = module.network.vpc_id
  subnet_id  = module.network.subnet_id
}