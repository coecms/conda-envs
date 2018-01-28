pipeline {
    agent {label "saw562.raijin"}

    environment {
        ENV_NAME = "${env.JOB_BASE_NAME}"
    }

    stages {
        stage ('Update') {
            steps {
                sh """
                   bash install.sh
                   """
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'deployed.yml'
        }

        failure {
            mail to: 'saw562', subject: "${env.ENV_NAME} update failed", body: """
Full results at ${env.BUILD_URL}
"""
        }
    }
}
