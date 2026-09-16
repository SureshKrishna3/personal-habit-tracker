pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out HabitPulse source code...'
            }
        }

        stage('Test') {
            steps {
                echo 'Running application tests...'
                sh  sh '''
            python3 -m venv .ci-venv
            .ci-venv/bin/pip install --upgrade pip
            .ci-venv/bin/pip install -r requirements.txt
            .ci-venv/bin/pip install pytest
            .ci-venv/bin/pytest -v
        '''
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image...'
                sh 'docker build -t sureshkrishnasp/habitpulse:latest .'
            }
        }

        stage('Docker Hub Push') {
            steps {
                echo 'Pushing Docker image to Docker Hub...'

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin
                        docker push sureshkrishnasp/habitpulse:latest
                        docker logout
                    '''
                }
            }
        }

        stage('Terraform Deploy') {
            steps {
                echo 'Deploying to Kubernetes using Terraform...'
                sh '''
                    cd terraform
                    terraform init
                    terraform apply -auto-approve
                '''
            }
        }

        stage('Verify Kubernetes') {
            steps {
                echo 'Verifying Kubernetes deployment...'
                sh '''
                    kubectl get deployment habitpulse
                    kubectl get pods
                    kubectl get service habitpulse-service
                '''
            }
        }
    }

    post {
        success {
            echo 'HabitPulse CI/CD pipeline completed successfully!'
        }

        failure {
            echo 'HabitPulse CI/CD pipeline failed. Check the stage logs.'
        }
    }
}
