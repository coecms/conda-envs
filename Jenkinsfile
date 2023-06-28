pipeline {
    agent {label "hh5_apps.gadi"}

    environment {
        ENV_NAME = "${env.JOB_BASE_NAME}"
    }

    stages {
        stage ('Update') {
            steps {
                sh '''
                   rm -f build_miniconda3.o*
                   jobid=$( qsub -N build_miniconda3 -lncpus=1,mem=20GB,walltime=2:00:00,jobfs=50GB,storage=gdata/hh5+scratch/hh5 -P kr06 -q copyq -j oe -Wblock=true install.sh )
                   echo $jobid
                   outfile=build_miniconda3.o"${jobid%.*}"
                   while ! [[ -e "${outfile}" ]]; do
                       sleep 10
                    done
                    cat "${outfile}"
                   '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'deployed.yml'
        }

        failure {
            mail to: 'dr4292', subject: "${env.ENV_NAME} update failed", body: """
Full results at ${env.BUILD_URL}
"""
        }
    }
}
