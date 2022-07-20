pipeline {
    agent {label "hxw599.gadi"}

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
            mail to: 'hxw599', subject: "${env.ENV_NAME} update failed", body: """
Full results at ${env.BUILD_URL}
"""
            mail to: 'aph502', subject: "${env.ENV_NAME} update failed", body: """
Full results at ${env.BUILD_URL}
"""
        }
    }
}
