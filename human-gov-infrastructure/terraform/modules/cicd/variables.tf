variable "region" {
     type = string
      }
variable "ecr_repo_url" {
     type = string
      }
variable "cluster_name" {
     type = string
      }
# You will need to get this ARN manually one time from the AWS Console
variable "codestar_connection_arn" {
       type = string
      }