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
                   ### Create named pipe
                   named_pipe=$( mktemp -u )
                   mkfifo $named_pipe
                   exec 10<>$named_pipe
                   ### Submit job
                   qsub -N build_miniconda3 -lncpus=1,mem=20GB,walltime=2:00:00,jobfs=50GB,storage=gdata/hh5+scratch/hh5 -P kr06 -q copyq -j oe -Wblock=true install.sh >&10 &
                   pid=$!
                   ### Get jobid
                   read -u 10 jobid
                   echo $jobid
                   ### Create a trap that cats job output file on exit
                   outfile=build_miniconda3.o"${jobid%.*}"
                   trap "while ! [[ -e ${outfile} ]]; do sleep 1; done; cat ${outfile}; exec 10>&-; rm -f $named_pipe;" EXIT
                   wait $pid
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
