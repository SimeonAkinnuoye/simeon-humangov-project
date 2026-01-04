output "vpc_id" {
  value = aws_vpc.main_vpc.id
}

#output "subnet_id" {
  #value = aws_subnet.public_subnet.id
#}

output "public_subnets" {
  value = [aws_subnet.public_subnet.id, aws_subnet.public_subnet_2.id]
}