pipeline {
    agent any

    parameters {
        string(
            name: 'TASK_ID',
            defaultValue: '',
            description: 'Subdirectory name under tasks/ (e.g. "task001"). Must contain config.yaml copied from templates/.'
        )
        string(
            name: 'TARGET_ENVIRONMENT',
            defaultValue: 'ylq89164',
            description: 'Environment name (must match an entry in the generated manifest)'
        )
        booleanParam(
            name: 'SKIP_DEPLOY',
            defaultValue: false,
            description: 'Run dry-run validation only — skip actual deployment (deploy tasks only)'
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
                    env.TASK_TYPE = sh(
                        script: """val=\$(grep '^task_type:' tasks/${params.TASK_ID}/config.yaml | awk '{print \$2}' | tr -d '"'); echo \${val:-deploy}""",
                        returnStdout: true
                    ).trim()
                    echo "Task type: ${env.TASK_TYPE}"
                }
            }
        }

        stage('Check OAuth Availability') {
            steps {
                script {
                    try {
                        withCredentials([string(credentialsId: 'dynatrace-oauth-client-id', variable: '_OAUTH_CHECK')]) {
                            env.HAS_OAUTH = 'true'
                            echo 'OAuth credentials detected — Grail-era schemas (e.g. builtin:davis.anomaly-detectors) will use OAuth.'
                        }
                    } catch (Exception e) {
                        env.HAS_OAUTH = 'false'
                        echo 'OAuth credentials NOT configured (dynatrace-oauth-client-id missing). Classic schemas will still deploy via API token. Grail-era schemas (e.g. builtin:davis.anomaly-detectors) will fail.'
                    }
                }
            }
        }

        stage('Resolve Names to IDs') {
            when {
                expression { return env.TASK_TYPE == 'deploy' }
            }
            steps {
                withCredentials([string(credentialsId: 'dynatrace-api-token', variable: 'DT_API_TOKEN')]) {
                    sh """
                        # --user installs into ~/.local (no root needed);
                        # --break-system-packages bypasses PEP 668 on Debian/Ubuntu.
                        python3 -m pip install --quiet --user --break-system-packages pyyaml
                        python3 scripts/resolve.py \\
                            --task-id ${params.TASK_ID} \\
                            --env-url https://${params.TARGET_ENVIRONMENT}.live.dynatrace.com
                        echo '---- tasks/${params.TASK_ID}/config.yaml after resolve ----'
                        cat tasks/${params.TASK_ID}/config.yaml
                    """
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
                script {
                    def oAuthBlock = ''
                    if (env.HAS_OAUTH == 'true') {
                        oAuthBlock = '''
          oAuth:
            clientId:
              name: DT_OAUTH_CLIENT_ID
            clientSecret:
              name: DT_OAUTH_CLIENT_SECRET
            tokenEndpoint:
              value: https://sso.dynatrace.com/sso/oauth2/token'''
                    }
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
            name: DT_API_TOKEN${oAuthBlock}
"""
                }
            }
        }

        stage('Validate (Dry Run)') {
            when {
                expression { return env.TASK_TYPE == 'deploy' }
            }
            steps {
                script {
                    def creds = [string(credentialsId: 'dynatrace-api-token', variable: 'DT_API_TOKEN')]
                    if (env.HAS_OAUTH == 'true') {
                        creds += [
                            string(credentialsId: 'dynatrace-oauth-client-id', variable: 'DT_OAUTH_CLIENT_ID'),
                            string(credentialsId: 'dynatrace-oauth-client-secret', variable: 'DT_OAUTH_CLIENT_SECRET')
                        ]
                    }
                    withCredentials(creds) {
                        sh './monaco deploy manifest-run.yaml --dry-run'
                    }
                }
            }
        }

        stage('Deploy') {
            when {
                allOf {
                    expression { return env.TASK_TYPE == 'deploy' }
                    expression { return !params.SKIP_DEPLOY }
                }
            }
            steps {
                script {
                    def creds = [string(credentialsId: 'dynatrace-api-token', variable: 'DT_API_TOKEN')]
                    if (env.HAS_OAUTH == 'true') {
                        creds += [
                            string(credentialsId: 'dynatrace-oauth-client-id', variable: 'DT_OAUTH_CLIENT_ID'),
                            string(credentialsId: 'dynatrace-oauth-client-secret', variable: 'DT_OAUTH_CLIENT_SECRET')
                        ]
                    }
                    withCredentials(creds) {
                        sh './monaco deploy manifest-run.yaml'
                    }
                }
            }
        }

        stage('Download') {
            when {
                expression { return env.TASK_TYPE == 'download' }
            }
            steps {
                script {
                    def creds = [string(credentialsId: 'dynatrace-api-token', variable: 'DT_API_TOKEN')]
                    if (env.HAS_OAUTH == 'true') {
                        creds += [
                            string(credentialsId: 'dynatrace-oauth-client-id', variable: 'DT_OAUTH_CLIENT_ID'),
                            string(credentialsId: 'dynatrace-oauth-client-secret', variable: 'DT_OAUTH_CLIENT_SECRET')
                        ]
                    }
                    withCredentials(creds) {
                        def schema = sh(
                            script: """grep 'schema:' tasks/${params.TASK_ID}/config.yaml | awk '{print \$2}' | tr -d '"'""",
                            returnStdout: true
                        ).trim()
                        env.DOWNLOAD_OUTPUT = sh(
                            script: """val=\$(grep 'outputFolder:' tasks/${params.TASK_ID}/config.yaml | awk '{print \$2}' | tr -d '"'); echo \${val:-output}""",
                            returnStdout: true
                        ).trim()
                        sh "./monaco download --manifest manifest-run.yaml --environment ${params.TARGET_ENVIRONMENT} --settings-schema ${schema} --output-folder tasks/${params.TASK_ID}/${env.DOWNLOAD_OUTPUT}"
                    }
                }
                archiveArtifacts artifacts: "tasks/${params.TASK_ID}/${env.DOWNLOAD_OUTPUT}/**/*", allowEmptyArchive: true
            }
        }
    }

    post {
        success {
            echo "Task '${params.TASK_ID}' completed successfully on ${params.TARGET_ENVIRONMENT}."
        }
        failure {
            echo "Task '${params.TASK_ID}' failed on ${params.TARGET_ENVIRONMENT}. Review the logs above."
        }
    }
}
