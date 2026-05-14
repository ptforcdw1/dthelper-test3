pipeline {
    agent any

    parameters {
        choice(
            name: 'TASK',
            choices: ['log-ingest-k8s', 'auto-tagging', 'update-windows', 'host-alerts'],
            description: 'Select the configuration task/template to deploy'
        )
        string(
            name: 'TARGET_ENVIRONMENT',
            defaultValue: 'ylq89164',
            description: 'Environment name from manifest.yaml'
        )
        booleanParam(
            name: 'SKIP_DEPLOY',
            defaultValue: false,
            description: 'Run dry-run validation only, skip actual deployment'
        )
        // --- Task-specific parameters ---
        // [log-ingest-k8s]
        string(name: 'K8S_NAMESPACE', defaultValue: 'default', description: '[log-ingest-k8s] Kubernetes namespace to route to log storage')
        // [auto-tagging]
        string(name: 'TEAM_NAME', defaultValue: 'POC Team', description: '[auto-tagging] Ownership team display name')
        string(name: 'TEAM_IDENTIFIER', defaultValue: 'poc-team', description: '[auto-tagging] Unique team identifier (lowercase, no spaces)')
        // [update-windows]
        string(name: 'WINDOW_NAME', defaultValue: 'POC Update Window', description: '[update-windows] OneAgent update window name')
        // [host-alerts]
        string(name: 'ALERT_TITLE', defaultValue: 'POC Host CPU Alert', description: '[host-alerts] Davis anomaly detector title')
    }

    environment {
        MONACO_VERSION = '2.28.7'
    }

    stages {
        stage('Setup Monaco') {
            steps {
                sh """
                    BIN="monaco-\${MONACO_VERSION}"
                    if [ ! -f "\$BIN" ]; then
                        curl -fsSL -o "\$BIN" https://github.com/dynatrace-oss/dynatrace-monitoring-as-code/releases/download/v\${MONACO_VERSION}/monaco-linux-amd64
                        chmod +x "\$BIN"
                    fi
                    ln -sf "\$BIN" monaco
                    ./monaco --help | head -3
                """
            }
        }

        stage('Validate (Dry Run)') {
            steps {
                withCredentials([string(credentialsId: 'dynatrace-api-token', variable: 'DT_API_TOKEN')]) {
                    withEnv([
                        "K8S_NAMESPACE=${params.K8S_NAMESPACE}",
                        "TEAM_NAME=${params.TEAM_NAME}",
                        "TEAM_IDENTIFIER=${params.TEAM_IDENTIFIER}",
                        "WINDOW_NAME=${params.WINDOW_NAME}",
                        "ALERT_TITLE=${params.ALERT_TITLE}"
                    ]) {
                        sh "./monaco deploy manifest.yaml --environment ${params.TARGET_ENVIRONMENT} --project ${params.TASK} --dry-run"
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
                    withEnv([
                        "K8S_NAMESPACE=${params.K8S_NAMESPACE}",
                        "TEAM_NAME=${params.TEAM_NAME}",
                        "TEAM_IDENTIFIER=${params.TEAM_IDENTIFIER}",
                        "WINDOW_NAME=${params.WINDOW_NAME}",
                        "ALERT_TITLE=${params.ALERT_TITLE}"
                    ]) {
                        sh "./monaco deploy manifest.yaml --environment ${params.TARGET_ENVIRONMENT} --project ${params.TASK}"
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Monaco task '${params.TASK}' deployed to ${params.TARGET_ENVIRONMENT} successfully."
        }
        failure {
            echo "Monaco task '${params.TASK}' failed on ${params.TARGET_ENVIRONMENT}. Review the logs above."
        }
    }
}
