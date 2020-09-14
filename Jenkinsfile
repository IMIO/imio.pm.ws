import com.cloudbees.jenkins.GitHubRepositoryName
import com.cloudbees.jenkins.GitHubPushCause

def SKIP_PATTERN = ".*?ci.skip.*"
def CAUSE = 'default'

def skip = false

def get_cause(){
    node {
        def UpstreamCause = currentBuild.rawBuild.getCause(hudson.model.Cause$UpstreamCause)
        def UserIdCause = currentBuild.rawBuild.getCause(hudson.model.Cause$UserIdCause)
        def RemoteCause = currentBuild.rawBuild.getCause(hudson.model.Cause$RemoteCause)
        def TimerTriggerCause = currentBuild.rawBuild.getCause(hudson.triggers.TimerTrigger$TimerTriggerCause)
        def SCMTriggerCause = currentBuild.rawBuild.getCause(hudson.triggers.SCMTrigger$SCMTriggerCause)
        def GitHubPushCause = currentBuild.rawBuild.getCause(GitHubPushCause)
        def BranchEventCause = currentBuild.rawBuild.getCause(jenkins.branch.BranchEventCause)

        if (UpstreamCause != null) {
          return 'UPSTREAM'
        } else if (SCMTriggerCause != null || GitHubPushCause != null || BranchEventCause != null) {
          return 'SCM'
        } else if (UserIdCause != null) {
          return 'USER'
        } else if (RemoteCause != null) {
          return 'REMOTE'
        } else if (TimerTriggerCause != null) {
          return 'TIMER'
        }

        return 'UNKNOWN'
    }
}

pipeline {
    agent any

    triggers {
        upstream(upstreamProjects: "IMIO-github-Jenkinsfile/Products.MeetingCommunes/master", threshold: hudson.model.Result.SUCCESS)
    }

    options {
        disableConcurrentBuilds()
        parallelsAlwaysFailFast()
    }

    stages {
		stage('Initialize') {
			steps {
				script {
					CAUSE = get_cause()
					commitMessage = sh(script: "git log --oneline -1", returnStdout: true)
					commitMessage = commitMessage.trim()
					echo "CAUSE = ${CAUSE} - commitMessage = '${commitMessage}'"
					skip = CAUSE != "UPSTREAM"
					echo "CAUSE != 'UPSTREAM = ${skip}"
					skip = commitMessage ==~ SKIP_PATTERN
					echo "'${commitMessage}' match '${SKIP_PATTERN}' : ${skip}"
					skip = CAUSE != "UPSTREAM" && commitMessage ==~ SKIP_PATTERN
					echo "skip = ${skip}"
					if (skip == true) {
						currentBuild.result = 'NOT_BUILT'
					}
				}
			}
		}
        stage('Build') {
			when {
				expression { skip == false }
			}
            steps {
                cache(maxCacheSize: 850, caches: [[$class: 'ArbitraryFileCache', excludes: '', path: "${WORKSPACE}/eggs"]]){
                    script {
                        sh "make bootstrap"
                        sh "bin/python bin/buildout -c jenkins.cfg"
                    }
                }
            }
        }
        stage('Code Analysis') {
            when {
				expression { skip == false }
			}
            steps {
		        script {
		            sh "bin/python bin/code-analysis"
		            warnings canComputeNew: false, canResolveRelativePaths: false, parserConfigurations: [[parserName: 'Pep8', pattern: '**/parts/code-analysis/flake8.log']]
                }
            }
        }
        stage('Test Coverage') {
            when {
				expression { skip == false }
			}
            steps {
                script {
					def zServerPort = new Random().nextInt(10000) + 30000
					sh "env ZSERVER_PORT=${zServerPort}  bin/coverage run --source=imio.pm.ws bin/test"
                    sh 'bin/python bin/coverage xml -i'
                }
            }
        }
	    
	stage('Publish Coverage') {
            when {
				expression { skip == false }
			}
            steps {
                catchError(buildResult: null, stageResult: 'FAILURE') {
                    cobertura (
                        coberturaReportFile: '**/coverage.xml',
                        conditionalCoverageTargets: '70, 50, 20',
                        lineCoverageTargets: '80, 50, 20',
                        maxNumberOfBuilds: 1,
                        methodCoverageTargets: '80, 50, 20',
                        onlyStable: false,
                        sourceEncoding: 'ASCII'
                    )
                }
            }
        }
    }
    post{
        always{
            chuckNorris()
        }
        aborted{
            mail to: 'pm-interne@imio.be',
                 subject: "Aborted Pipeline: ${currentBuild.fullDisplayName}",
                 body: "The pipeline ${env.JOB_NAME} ${env.BUILD_NUMBER} was aborted (${env.BUILD_URL})"

            slackSend channel: "#jenkins",
                      color: "#C0C0C0",
                      message: "Aborted ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
        regression{
            mail to: 'pm-interne@imio.be',
                 subject: "Broken Pipeline: ${currentBuild.fullDisplayName}",
                 body: "The pipeline ${env.JOB_NAME} ${env.BUILD_NUMBER} is broken (${env.BUILD_URL})"

            slackSend channel: "#jenkins",
                      color: "#ff0000",
                      message: "Broken ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
        fixed{
            mail to: 'pm-interne@imio.be',
                 subject: "Fixed Pipeline: ${currentBuild.fullDisplayName}",
                 body: "The pipeline ${env.JOB_NAME} ${env.BUILD_NUMBER} is back to normal (${env.BUILD_URL})"

            slackSend channel: "#jenkins",
                      color: "#00cc44",
                      message: "Fixed ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
        failure{
            mail to: 'pm-interne@imio.be',
                 subject: "Failed Pipeline: ${currentBuild.fullDisplayName}",
                 body: "The pipeline${env.JOB_NAME} ${env.BUILD_NUMBER} failed (${env.BUILD_URL})"

            slackSend channel: "#jenkins",
                      color: "#ff0000",
                      message: "Failed ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
        cleanup{
            deleteDir()
        }
    }
}
