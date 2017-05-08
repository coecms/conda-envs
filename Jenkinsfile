pipeline {
    agent {label "saw562.raijin"}
    
    stages {
        stage ('Build') {
            steps {
                sh """
                    module use /g/data3/hh5/public/modules
                    module load conda
                    conda env create -n 'test-\${BRANCH_NAME}' -f environment.yml
                    conda env export -n 'test-\${BRANCH_NAME}' -f deployed.yml
                    """
            }
        }

       stage ('Test') {
           steps {
               sh """
                   source activate 'test-${BRANCH_NAME}'
                   py.test
                   """
           }
       }
   }

   post {
       success {
           sh """
               echo conda env update -n '\${BRANCH_NAME}' -f deployed.yml
               """
       }

       always {
           sh """
               conda env remove -n 'test-\${BRANCH_NAME}'
               """
           archiveArtifacts artifacts: 'deployed.yml'
       }
   }
}
