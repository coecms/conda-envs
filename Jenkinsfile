pipeline {
    agent {label "saw562.raijin"}
    
    stages {
        stage ('Build') {
            steps {
                sh """
                    module load conda
                    conda env create -f 'test-\${BRANCH_NAME}' environment.yml
                    conda env export -n 'test-\${BRANCH_NAME}' -f deployed.yml
                    """
            }
        }

       stage ('Test') {
           steps {
               sh """
                   module load conda
                   source activate 'test-${BRANCH_NAME}'
                   py.test
                   """
           }
       }
   }

   post {
       success {
           sh """
               module load conda
               echo conda env update -n '\${BRANCH_NAME}' -f deployed.yml
               """
       }

       always {
           sh """
               module load conda
               conda env remove -n 'test-\${BRANCH_NAME}'
               """
           archiveArtifacts artifacts: 'deployed.yml'
       }
   }
}
