output "codebuild_role_arn" {
  description = "The ARN of the IAM Role used by CodeBuild"
  value       = aws_iam_role.codebuild_role.arn
}

output "codepipeline_arn" {
  description = "The ARN of the Pipeline"
  value       = aws_codepipeline.humangov_pipeline.arn
}