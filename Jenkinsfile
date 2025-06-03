pipeline {
    agent any

    environment {
        TIMESTAMP = "${new Date().format('yyyyMMdd_HHmmss')}"
        DOCKER_REGISTRY = 'ghcr.io'
        DOCKER_REPO = 'NovanM/MLOps'
        IMAGE_TAG = "${TIMESTAMP}"
    }

    stages {
        stage('Checkout Repository') {
            steps {
                echo "Repository checked out successfully"
                sh 'pwd && ls -la'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                python3 -m venv myenv
                . myenv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Data Preparation') {
            steps {
                sh '''
                . myenv/bin/activate
                python Script/data_preparation.py --data_dir Data/raw --data_new Data/clean --output_dir Model/preprocessor --target_col Survived --random_state 42 --columns_to_remove Cabin PassengerId Name --timestamp $TIMESTAMP
                '''
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                . myenv/bin/activate
                python Script/train_model.py --data_dir Data/clean --model_dir Model/model --timestamp $TIMESTAMP --model_name random_forest
                '''
            }
        }

        stage('Deploy Model') {
            steps {
                sh '''
                . myenv/bin/activate
                python Script/deploy_model.py --model_path Model/model/random_forest_$TIMESTAMP.pkl --model_dir Model/model --metadata_dir Model/metadata --timestamp $TIMESTAMP
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    try {
                        echo "=== Building Docker image ==="
                        sh "docker build -t mlops-local:${env.IMAGE_TAG} ."
                        sh "docker tag mlops-local:${env.IMAGE_TAG} mlops-local:latest"
                        
                        // Verify image created
                        sh "docker images | grep mlops-local"
                        echo "✅ Docker image built successfully"
                    } catch (Exception e) {
                        echo "❌ Docker build failed: ${e.getMessage()}"
                        throw e
                    }
                }
            }
        }

        stage('Test Docker Image') {
            steps {
                script {
                    try {
                        // Cleanup any existing test containers
                        echo "=== Cleaning up existing test containers ==="
                        sh '''
                        if docker ps -a --format "table {{.Names}}" | grep -q "^mlops-test$"; then
                            docker stop mlops-test || true
                            docker rm mlops-test || true
                        fi
                        '''

                        // Check port availability
                        sh '''
                        if lsof -i :3001; then
                            echo "Port 3001 is in use, attempting to free..."
                            lsof -ti :3001 | xargs -r kill -9 || true
                            sleep 2
                        fi
                        '''

                        // Start container with explicit host binding
                        echo "=== Starting test container ==="
                        sh "docker run -d --name mlops-test -p 0.0.0.0:3001:3000 mlops-local:latest"

                        // Wait longer for initialization (ML models might take time to load)
                        echo "=== Waiting for container to initialize (30 seconds) ==="
                        sleep(30)

                        // Verify container is running
                        def containerStatus = sh(
                            script: "docker inspect -f '{{.State.Status}}' mlops-test",
                            returnStdout: true
                        ).trim()
                        
                        if (containerStatus != "running") {
                            error("Container is not running (status: ${containerStatus})")
                        }

                        // Internal health check (from within the container)
                        echo "=== Performing internal health check ==="
                        def internalCheck = sh(
                            script: "docker exec mlops-test sh -c 'curl -s -o /dev/null -w \"%{http_code}\" http://localhost:3000 || echo 000'",
                            returnStdout: true
                        ).trim()
                        
                        if (internalCheck != "200") {
                            error("Internal health check failed (status: ${internalCheck})")
                        }

                        // External health check with retries
                        echo "=== Performing external health checks ==="
                        def healthCheckPassed = false
                        for (int i = 1; i <= 6; i++) {
                            echo "Health check attempt ${i}/6"
                            
                            def statusCode = sh(
                                script: "curl -s -o /dev/null -w '%{http_code}' http://localhost:3001 || echo 000",
                                returnStdout: true
                            ).trim()
                            
                            if (statusCode == "200") {
                                healthCheckPassed = true
                                break
                            } else {
                                echo "Status code: ${statusCode}"
                                if (i < 6) {
                                    echo "Waiting 10 seconds before retry..."
                                    sleep(10)
                                    sh "docker logs --tail 20 mlops-test"
                                }
                            }
                        }

                        if (!healthCheckPassed) {
                            error("Health checks failed after 6 attempts")
                        }

                        echo "✅ Container health checks passed successfully"

                    } catch (Exception e) {
                        echo "❌ Test failed: ${e.getMessage()}"
                        echo "=== Debugging information ==="
                        sh '''
                        echo "=== Container logs ==="
                        docker logs mlops-test || true
                        
                        echo "=== Network information ==="
                        docker inspect mlops-test | grep -A 10 -B 10 NetworkSettings
                        
                        echo "=== Port mapping ==="
                        docker port mlops-test || true
                        '''
                        throw e
                    } finally {
                        echo "=== Cleaning up test container ==="
                        sh '''
                        docker stop mlops-test || true
                        docker rm mlops-test || true
                        '''
                    }
                }
            }
        }

        stage('Deploy Application') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
                    try {
                        echo "=== Deploying production container ==="
                        
                        // Cleanup existing container
                        sh '''
                        if docker ps -a --format "table {{.Names}}" | grep -q "^mlops-app$"; then
                            docker stop mlops-app || true
                            docker rm mlops-app || true
                        fi
                        '''

                        // Check port availability
                        sh '''
                        if lsof -i :3000; then
                            echo "Port 3000 is in use, attempting to free..."
                            lsof -ti :3000 | xargs -r kill -9 || true
                            sleep 2
                        fi
                        '''

                        // Start production container
                        sh "docker run -d --name mlops-app --restart unless-stopped -p 0.0.0.0:3000:3000 mlops-local:latest"
                        
                        // Wait for initialization
                        sleep(30)
                        
                        // Verify deployment
                        def statusCode = sh(
                            script: "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 || echo 000",
                            returnStdout: true
                        ).trim()
                        
                        if (statusCode != "200") {
                            error("Production deployment health check failed (status: ${statusCode})")
                        }
                        
                        echo "🚀 Application successfully deployed at http://localhost:3000"
                        
                    } catch (Exception e) {
                        echo "❌ Production deployment failed: ${e.getMessage()}"
                        sh '''
                        echo "=== Production container logs ==="
                        docker logs mlops-app || true
                        '''
                        throw e
                    }
                }
            }
        }
    }

    post {
        always {
            echo "=== Pipeline cleanup ==="
            sh '''
            echo "=== Cleaning up old containers ==="
            docker ps -a --filter "name=mlops" --format "{{.Names}}" | xargs -r docker stop || true
            docker ps -a --filter "name=mlops" --format "{{.Names}}" | xargs -r docker rm || true
            
            echo "=== Cleaning up old images ==="
            docker images --filter "reference=mlops-local*" --format "{{.Repository}}:{{.Tag}}" | grep -v latest | grep -v "${IMAGE_TAG}" | head -n -2 | xargs -r docker rmi || true
            '''
        }
        success {
            echo '✅ Pipeline completed successfully!'
            sh '''
            echo "=== Deployment Summary ==="
            docker ps | grep mlops-app
            echo "Application should be available at: http://localhost:3000"
            '''
        }
        failure {
            echo '❌ Pipeline failed. Check logs for details.'
            sh '''
            echo "=== Failure Debugging ==="
            echo "=== Running containers ==="
            docker ps -a
            
            echo "=== Recent container logs ==="
            docker logs mlops-test --tail 50 2>/dev/null || true
            docker logs mlops-app --tail 50 2>/dev/null || true
            '''
        }
    }
}
