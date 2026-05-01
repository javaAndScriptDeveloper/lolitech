pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t vampire/spring-app:latest .'
            }
        }
        stage('Push') {
            steps {
                sh 'docker push vampire/spring-app:latest'
            }
        }
    }
}