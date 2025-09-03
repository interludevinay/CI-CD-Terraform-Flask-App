# Key-pair
resource "aws_key_pair" "jenkins_key" {
  key_name   = "Jenkins-key"
  public_key = file("jenkins-ec2.pub")
}

# VPC & Security group
resource "aws_default_vpc" "terraform-vpc" {

}
resource "aws_security_group" "terraform-sg" {
  name        = "terraform-slave-sg"
  vpc_id      = aws_default_vpc.terraform-vpc.id
  description = "Slave machine terraform implementation sg"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH open rule"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP open rule"
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Flask open rule"
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = -1
    cidr_blocks = ["0.0.0.0/0"]   # Allow all outbound internet access
  }
  tags = {
    name = "terraform-slave-sg"
  }
}


# EC2
resource "aws_instance" "slave-machine" {
  ami               = "ami-0f918f7e67a3323f0"
  availability_zone = "ap-south-1a"
  instance_type     = "t2.micro"
  root_block_device {
    volume_size = 8
    volume_type = "gp3"
  }
  key_name        = aws_key_pair.jenkins_key.key_name
  security_groups = [aws_security_group.terraform-sg.name]
  tags = {
    name = "terraform-slave-sg"
  }
}
