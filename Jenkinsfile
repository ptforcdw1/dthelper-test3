pipeline {
    agent any

    parameters {
        string(
            name: 'TARGET_ENVIRONMENT',
            defaultValue: 'ylq89164',
            description: 'Environment name from manifest.yaml to deploy to'
        )
        booleanParam(
            name: 'SKIP_DEPLOY',
            defaultValue: false,
            description: 'Run dry-run validation only, skip actual deployment'
        )
    }

    environment {
        MONACO_VERSION = '2.14.0'
    }

    stages {
        stage('Setup Monaco') {
            steps {
                sh """
                    if [ ! -f monaco ]; then
                        curl -fsSL -o monaco https://github.com/dynatrace-oss/dynatrace-monitoring-as-code/releases/download/v\${MONACO_VERSION}/monaco-linux-amd64
                        chmod +x monaco
                    fi
                    ./monaco --version
                """
            }
        }

        stage('Validate (Dry Run)') {
            steps {
                withCredentials([string(credentialsId: 'dynatrace-api-token', variable: 'DT_API_TOKEN')]) {
                    sh "./monaco deploy manifest.yaml --environment ${params.TARGET_ENVIRONMENT} --dry-run"
                }
            }
        }

        stage('Deploy') {
            when {
                expression { return !params.SKIP_DEPLOY }
            }
            steps {
                withCredentials([string(credentialsId: 'dynatrace-api-token', variable: 'DT_API_TOKEN')]) {
                    sh "./monaco deploy manifest.yaml --environment ${params.TARGET_ENVIRONMENT}"
                }
            }
        }
    }

    post {
        success {
            echo "Monaco deployment to ${params.TARGET_ENVIRONMENT} completed successfully."
        }
        failure {
            echo "Monaco deployment to ${params.TARGET_ENVIRONMENT} FAILED. Review the logs above."
        }
    }
}
