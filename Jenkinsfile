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
        // Verify this tag at: https://github.com/dynatrace-oss/dynatrace-monitoring-as-code/pkgs/container/dynatrace-monitoring-as-code%2Fmonaco
        MONACO_IMAGE = 'ghcr.io/dynatrace-oss/dynatrace-monitoring-as-code/monaco:v2.14.0'
    }

    stages {
        stage('Validate (Dry Run)') {
            steps {
                withCredentials([string(credentialsId: 'dynatrace-api-token', variable: 'DT_API_TOKEN')]) {
                    script {
                        docker.image(env.MONACO_IMAGE).inside('-e DT_API_TOKEN') {
                            sh "monaco deploy manifest.yaml --environment ${params.TARGET_ENVIRONMENT} --dry-run"
                        }
                    }
                }
            }
        }

        stage('Deploy') {
            when {
                expression { return !params.SKIP_DEPLOY }
            }
            steps {
                withCredentials([string(credentialsId: 'dynatrace-api-token', variable: 'DT_API_TOKEN')]) {
                    script {
                        docker.image(env.MONACO_IMAGE).inside('-e DT_API_TOKEN') {
                            sh "monaco deploy manifest.yaml --environment ${params.TARGET_ENVIRONMENT}"
                        }
                    }
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
