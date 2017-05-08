pipeline {
    agent {label "saw562.raijin"}

    environment {
        ENV_NAME = "${env.JOB_BASE_NAME}"
    }

    stages {
        stage ('Build') {
            steps {
                sh """
                    module use /g/data3/hh5/public/modules
                    module load conda
                    conda env create -n "test-\${ENV_NAME}" -f environment.yml
                    conda env export -n "test-\${ENV_NAME}" -f deployed.yml
                    """
            }
        }

        stage ('Test') {
            steps {
                sh """
                    module use /g/data3/hh5/public/modules
                    module load conda
                    source activate "test-\${ENV_NAME}"
                    py.test
                    """
            }
        }
    }

    post {
        success {
            sh """
                module use /g/data3/hh5/public/modules
                module load conda
                conda env update -n "\${ENV_NAME}" -f deployed.yml
                """
        }

        always {
            sh """
                module use /g/data3/hh5/public/modules
                module load conda
                conda env remove -y -n "test-\${ENV_NAME}"
                """
            archiveArtifacts artifacts: 'deployed.yml'
        }

        failure {
            mail to: 'climate_help', subject: "${env.ENV_NAME} update failed", body: """
Full results at ${env.BUILD_URL}
"""
        }
    }
}
