import com.cloudbees.jenkins.GitHubRepositoryName
import com.cloudbees.jenkins.GitHubPushCause

def SKIP_PATTERN = ".*?ci.skip.*"
def CAUSE = 'default'
def DOCKER_IMG = ''
def COMPOSE_PROJECT = ''

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
					branch = BRANCH_NAME.replace("_", "-")
                    branch = branch.replace(".", "-")
                    branch = branch.toLowerCase()
					base_docker_image = "docker-staging.imio.be/iadelib/pm-ws:${branch}"
					DOCKER_IMG = "${base_docker_image}-${BUILD_ID}"
					echo "Docker image is ${DOCKER_IMG}"
                    COMPOSE_PROJECT = "docker-compose-pm-ws-${branch}"
                    echo "docker compose project is ${COMPOSE_PROJECT}"
					sh "wget -O docker-compose.yml https://raw.githubusercontent.com/IMIO/buildout.pm/master/docker/docker-compose-jenkins.yml"
				}
			}
		}
        stage('Docker build') {
			when {
				expression { skip == false }
			}
            steps {
                sh "docker build -t ${DOCKER_IMG} --no-cache --force-rm --pull ."
            }
        }
        stage('Push test image') {
			when {
				expression { skip == false }
			}
            steps {
                script {
                    sh "docker push ${DOCKER_IMG}"
                }
            }
        }
        stage('Set up tests') {
			when {
				expression { skip == false }
			}
            steps {
                script {
					escapedDockerImage = DOCKER_IMG.replace("/", "\\/")
					sh "sed -ie 's/imiobe\\/iadelib:dev/${escapedDockerImage}/g' docker-compose.yml"
                    sh "docker compose -p ${COMPOSE_PROJECT} -f docker-compose.yml down -v --remove-orphans || exit 0"
                    sh "echo Docker compose project : cleaned"
                    sh "docker compose -p ${COMPOSE_PROJECT} -f docker-compose.yml pull"
                    sh "echo Docker compose project : image pulled"
                    sh "docker compose -p ${COMPOSE_PROJECT} -f docker-compose.yml up --no-start"
                    sh "echo Docker compose project : network recreated"
                    sh "docker compose -p ${COMPOSE_PROJECT} -f docker-compose.yml start loffice"
                    sh "echo Docker compose project : LibreOffice started"
                }
            }
        }
        stage('Run tests') {
            parallel{
                stage('Test') {
                    when {
                        expression { skip == false }
                    }
                    steps {
                        script {
                            sh("docker compose -p ${COMPOSE_PROJECT} -f docker-compose.yml run instance bin/test")
                        }
                    }
                }
                stage('Test Coverage') {
                    when {
                        expression { skip == false }
                    }
                    steps {
                        withCredentials([string(credentialsId: 'COVERALLS_REPO_TOKEN', variable: 'COVERALLS_REPO_TOKEN')]) {
                            script {
                                command = "docker compose -p ${COMPOSE_PROJECT} -f docker-compose.yml run"
                                sh(command + ' -e COVERALLS_REPO_TOKEN=${COVERALLS_REPO_TOKEN} --entrypoint bash instance bin/test-coverage.sh')
                            }
                        }
                    }
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
        }
        regression{
            mail to: 'pm-interne@imio.be',
                 subject: "Broken Pipeline: ${currentBuild.fullDisplayName}",
                 body: "The pipeline ${env.JOB_NAME} ${env.BUILD_NUMBER} is broken (${env.BUILD_URL})"
        }
        fixed{
            mail to: 'pm-interne@imio.be',
                 subject: "Fixed Pipeline: ${currentBuild.fullDisplayName}",
                 body: "The pipeline ${env.JOB_NAME} ${env.BUILD_NUMBER} is back to normal (${env.BUILD_URL})"
        }
        failure{
            mail to: 'pm-interne@imio.be',
                 subject: "Failed Pipeline: ${currentBuild.fullDisplayName}",
                 body: "The pipeline${env.JOB_NAME} ${env.BUILD_NUMBER} failed (${env.BUILD_URL})"
        }
        cleanup{
            deleteDir()
        }
    }
}
