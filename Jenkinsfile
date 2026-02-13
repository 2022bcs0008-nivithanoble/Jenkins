pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                    . venv/bin/activate
                    python train.py

                    echo "Workspace content:"
                    pwd
                    ls -R
                '''
            }
        }

        stage('Read Metrics') {
            steps {
                script {
                    def metrics = readJSON file: 'outputs/metrics/results.json'

                    env.NEW_R2 = metrics.r2.toString()
                    env.NEW_MSE = metrics.mse.toString()

                    echo "New R2: ${env.NEW_R2}"
                    echo "New MSE: ${env.NEW_MSE}"
                }
            }
        }

        stage('Compare Metrics') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'best-r2', variable: 'BEST_R2'),
                        string(credentialsId: 'best-rmse', variable: 'BEST_MSE')
                    ]) {

                        if (env.NEW_R2.toFloat() > BEST_R2.toFloat() &&
                            env.NEW_MSE.toFloat() < BEST_MSE.toFloat()) {

                            env.MODEL_IMPROVED = "true"
                            echo "Model improved"

                        } else {
                            env.MODEL_IMPROVED = "false"
                            echo "Model did not improve"
                        }
                    }
                }
            }
        }

        stage('Build and Push Docker Image') {
            when {
                expression { env.MODEL_IMPROVED == "true" }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker build -t $DOCKER_USER/wine_predict_2022bcs0008:${BUILD_NUMBER} .
                        docker tag $DOCKER_USER/wine_predict_2022bcs0008:${BUILD_NUMBER} $DOCKER_USER/wine_predict_2022bcs0008:v03
                        docker push $DOCKER_USER/wine_predict_2022bcs0008:${BUILD_NUMBER}
                        docker push $DOCKER_USER/wine_predict_2022bcs0008:v03
                    '''
                }
            }
        }
    }
}
