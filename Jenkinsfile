pipeline {
    agent any

    parameters {
        string(
            name: 'TASK_ID',
            defaultValue: '',
            description: 'Subdirectory name under tasks/ (e.g. "log-001"). Must contain config.yaml and template.json copied from templates/.'
        )
        string(
            name: 'TARGET_ENVIRONMENT',
            defaultValue: 'ylq89164',
            description: 'Environment name (must match an entry in the generated manifest)'
        )
        booleanParam(
            name: 'SKIP_DEPLOY',
            defaultValue: false,
            description: 'Run dry-run validation only — skip actual deployment'
        )
    }

    environment {
        MONACO_VERSION = '2.28.7'
    }

    stages {
        stage('Validate Task') {
            steps {
                script {
                    if (!params.TASK_ID?.trim()) {
                        error 'TASK_ID is required. Set it to the subdirectory name under tasks/.'
                    }
                    if (!fileExists("tasks/${params.TASK_ID}/config.yaml")) {
                        error "tasks/${params.TASK_ID}/config.yaml not found. Create the directory, copy a template from templates/, and push to git."
                    }
                }
            }
        }

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

        stage('Prepare Manifest') {
            steps {
                writeFile file: 'manifest-run.yaml', text: """\
manifestVersion: "1.0"
projects:
  - name: ${params.TASK_ID}
    path: tasks/${params.TASK_ID}
environmentGroups:
  - name: production
    environments:
      - name: ${params.TARGET_ENVIRONMENT}
        url:
          value: https://ylq89164.live.dynatrace.com
        auth:
          token:
            name: DT_API_TOKEN
"""
            }
        }

        stage('Validate (Dry Run)') {
            steps {
                withCredentials([string(credentialsId: 'dynatrace-api-token', variable: 'DT_API_TOKEN')]) {
                    sh './monaco deploy manifest-run.yaml --dry-run'
                }
            }
        }

        stage('Deploy') {
            when {
                expression { return !params.SKIP_DEPLOY }
            }
            steps {
                withCredentials([string(credentialsId: 'dynatrace-api-token', variable: 'DT_API_TOKEN')]) {
                    sh './monaco deploy manifest-run.yaml'
                }
            }
        }
    }

    post {
        success {
            echo "Task '${params.TASK_ID}' deployed to ${params.TARGET_ENVIRONMENT} successfully."
        }
        failure {
            echo "Task '${params.TASK_ID}' failed on ${params.TARGET_ENVIRONMENT}. Review the logs above."
        }
    }
}
