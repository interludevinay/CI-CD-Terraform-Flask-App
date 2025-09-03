output "ec2_public_ip" {
  value = aws_instance.slave-machine.public_ip
}