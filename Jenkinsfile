pipeline {
    agent any
    environment {
        AWS_DEFAULT_REGION = 'ap-south-1'
    }
    stages {
        stage('Clone') {
            steps {
                echo "Cloning code..."
                sh "pwd"
                sh "ls"
            }
        }

        stage('Docker Image'){
            steps{
                sh "docker --version"
               sh "docker build -t flask-todo-app:latest ."
            }
        }

        stage('Docker Image Push To DockerHub'){
            steps{
                echo "Pushing image to DockerHub"
                withCredentials([usernamePassword('credentialsId':"dockerHubCred",
                passwordVariable:"dockerHubPass",
                usernameVariable:"dockerHubUser")]){
                    sh "docker login -u ${env.dockerHubUser} -p ${env.dockerHubPass}"
                    sh "docker image tag flask-todo-app:latest ${env.dockerHubUser}/flask-todo-app:latest"
                    sh "docker push ${env.dockerHubUser}/flask-todo-app:latest"
                }
            }
        }

        stage('Plan') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh 'terraform init -upgrade'
                    sh 'terraform plan'
                    sh 'terraform apply -auto-approve'
                }
            }
        }

        stage('Get EC2 Public IP') {
            steps {
                script {
                    def ec2_ip = sh(
                        script: "terraform output -raw ec2_public_ip",
                        returnStdout: true
                    ).trim()
                    
                    env.EC2_IP = ec2_ip
                    echo "✅ EC2 Public IP: ${ec2_ip}"
                }
            }
        }

        stage('SSH to EC2 and Run container') {
            steps {
                sshagent(['ec2-ssh-key']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ubuntu@${env.EC2_IP} << 'EOF'
                            echo "Connected to EC2 instance: \$(hostname)"
        
                            # Update system
                            sudo apt-get update -y
        
                            # Install prerequisites
                            sudo apt-get install -y ca-certificates curl gnupg lsb-release
        
                            # Add Docker’s official GPG key
                            sudo mkdir -p /etc/apt/keyrings
                            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        
                            # Set up the Docker repository
                            echo "deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
                            https://download.docker.com/linux/ubuntu \$(lsb_release -cs) stable" \
                            | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
                            # Install Docker Engine
                            sudo apt-get update -y
                            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
                            # Pull and run container
                            sudo docker pull <username>/flask-todo-app:latest
                            sudo docker run -d --name flask-app -p 5000:5000 <username>/flask-todo-app:latest
EOF
                    """
                }
            }
        }



        stage('Destroy Approval') {
            steps {
                script {
                    timeout(time: 1, unit: 'HOURS') {
                        input message: 'Do you want to destroy the created resources?', ok: 'Yes, Destroy'
                    }
                }
            }
        }

        stage('Destroy Resources') {
            steps {
                withCredentials([
                    string(credentialsId: 'aws-access-key-id', variable: 'AWS_ACCESS_KEY_ID'),
                    string(credentialsId: 'aws-secret-access-key', variable: 'AWS_SECRET_ACCESS_KEY')
                ]) {
                    sh 'terraform destroy -auto-approve'
                }
            }
        }
    }
}
