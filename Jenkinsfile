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
                '''
            }
        }

        stage('Read Accuracy') {
            steps {
                script {
                    def metrics = readJSON file: 'app/artifacts/metrics.json'
                    env.NEW_ACCURACY = metrics.accuracy.toString()
                    echo "New Accuracy: ${env.NEW_ACCURACY}"
                }
            }
        }

        stage('Compare Accuracy') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'best-accuracy', variable: 'BEST_ACC')]) {
                        if (env.NEW_ACCURACY.toFloat() > BEST_ACC.toFloat()) {
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
