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

                    env.NEW_R2 = metrics.R2.toString()
                    env.NEW_MSE = metrics.MSE.toString()

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

                        echo "NEW_R2 raw: '${env.NEW_R2}'"
                        echo "NEW_MSE raw: '${env.NEW_MSE}'"
                        echo "BEST_R2 raw: '${BEST_R2}'"
                        echo "BEST_MSE raw: '${BEST_MSE}'"

                        def newR2 = env.NEW_R2?.trim()?.toFloat()
                        def newMSE = env.NEW_MSE?.trim()?.toFloat()
                        def bestR2 = BEST_R2?.trim()?.toFloat()
                        def bestMSE = BEST_MSE?.trim()?.toFloat()

                        if (newR2 > bestR2 && newMSE < bestMSE) {
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
                    '''
                }
            }
        }

        stage('Pull Image'){
            steps{
                script{
                    sh '''
                        docker pull 2022bcs0008nivithanoble/wine_predict_2022bcs0008:${BUILD_NUMBER}
                    '''
                }
            }
        }

        stage('Run Container') {
            steps{
                script{
                    sh '''
                        docker run -d -p 8001:8000 --name bcs8_wine_test_jenkins 2022bcs0008nivithanoble/wine_predict_2022bcs0008:${BUILD_NUMBER}
                    '''
                }
            }
        }

        stage('Service Readiness') {
            steps {
                script {
                    sh '''
                        echo "Waiting for API to be ready..."

                        for i in 1 2 3 4 5 6 7 8 9 10 11 12
                        do
                            sleep 5

                            STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/docs || true)

                            echo "Attempt $i - Status: $STATUS"

                            if [ "$STATUS" = "200" ]; then
                                echo "Service is ready"
                                exit 0
                            fi
                        done

                        echo "Service did not become ready"
                        docker logs wine_test_container
                        exit 1
                    '''
                }
            }
        }
        

        stage('Valid Inference'){
            steps {
                script {
                    sh '''
                        RESPONSE=$(curl -s -X POST "http://localhost:8001/predict" \
                        -H "Content-Type: application/json" \
                        -d '{
                            "fixed_acidity":1,
                            "volatile_acidity":2,
                            "citric_acid":3,
                            "residual_sugar":4,
                            "chlorides":5,
                            "free_sulfur_dioxide":6,
                            "total_sulfur_dioxide":7,
                            "density":8,
                            "pH":9,
                            "sulphates":0,
                            "alcohol":1
                        }')

                        echo "Response: $RESPONSE"

                        echo $RESPONSE | grep prediction || exit 1
                    '''
                }
            }
        }

        stage('Invalid Response'){
            steps {
                script {
                    sh '''
                        STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
                        -X POST "http://localhost:8001/predict" \
                        -H "Content-Type: application/json" \
                        -d '{"invalid":"data"}')

                        echo "HTTP Status: $STATUS"

                        if [ "$STATUS" -eq 200 ]; then
                            echo "Invalid request did not fail"
                            exit 1
                        fi
                    '''
                }
            }
        }

        stage('Stop Container'){
            steps {
                script {
                    sh '''
                        docker stop bcs8_wine_test_jenkins || true
                        docker rm bcs8_wine_test_jenkins || true
                    '''
                }
            }
        }
    }
}
