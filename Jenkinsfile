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
                        // Build Docker image
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
                        // Cleanup any existing test containers first
                        echo "=== Cleaning up existing test containers ==="
                        sh '''
                        if docker ps -a --format "table {{.Names}}" | grep -q "^mlops-test$"; then
                            echo "Stopping existing mlops-test container"
                            docker stop mlops-test || true
                            echo "Removing existing mlops-test container"
                            docker rm mlops-test || true
                        else
                            echo "No existing mlops-test container found"
                        fi
                        '''
                        
                        // Check if port 3001 is in use
                        sh '''
                        if netstat -tuln | grep -q ":3001 "; then
                            echo "⚠️  Port 3001 is already in use"
                            netstat -tuln | grep ":3001 "
                            echo "Trying to find and stop process using port 3001"
                            lsof -ti:3001 | xargs -r kill -9 || true
                            sleep 2
                        fi
                        '''
                        
                        // Start test container with better error handling
                        echo "=== Starting test container ==="
                        def runResult = sh(
                            script: "docker run -d --name mlops-test -p 3001:3000 mlops-local:latest",
                            returnStatus: true
                        )
                        
                        if (runResult != 0) {
                            error("Failed to start test container")
                        }
                        
                        // Wait for container to initialize
                        echo "=== Waiting for container to initialize ==="
                        sleep(15)
                        
                        // Check container status with better error handling
                        def containerExists = sh(
                            script: "docker ps -a --format '{{.Names}}' | grep -q '^mlops-test\$'",
                            returnStatus: true
                        ) == 0
                        
                        if (!containerExists) {
                            error("Container mlops-test does not exist after creation")
                        }
                        
                        sh '''
                        echo "=== Container Status ==="
                        docker ps -a | grep mlops-test
                        
                        echo "=== Container Logs ==="
                        docker logs mlops-test
                        '''
                        
                        // Check if container is running
                        def containerStatus = sh(
                            script: "docker inspect --format='{{.State.Status}}' mlops-test 2>/dev/null || echo 'not_found'",
                            returnStdout: true
                        ).trim()
                        
                        echo "Container status: ${containerStatus}"
                        
                        if (containerStatus == "running") {
                            // Health check with improved logic
                            echo "=== Testing application health ==="
                            
                            def healthCheckPassed = false
                            for (int i = 1; i <= 6; i++) {
                                echo "Health check attempt ${i}/6"
                                
                                def exitCode = sh(
                                    script: '''
                                    timeout 15 curl -f -s -o /dev/null -w "%{http_code}" http://localhost:3001/ 2>/dev/null
                                    ''',
                                    returnStatus: true
                                )
                                
                                if (exitCode == 0) {
                                    echo "✅ Health check successful on attempt ${i}"
                                    healthCheckPassed = true
                                    break
                                } else {
                                    echo "❌ Health check failed on attempt ${i} (exit code: ${exitCode})"
                                    if (i < 6) {
                                        echo "Waiting 10 seconds before retry..."
                                        sleep(10)
                                        
                                        // Show recent logs for debugging
                                        sh "docker logs --tail 10 mlops-test"
                                    }
                                }
                            }
                            
                            if (!healthCheckPassed) {
                                echo "=== Final debugging info ==="
                                sh '''
                                echo "=== Final container logs ==="
                                docker logs mlops-test
                                
                                echo "=== Network connectivity check ==="
                                netstat -tlnp | grep 3001 || echo "Port 3001 not listening"
                                
                                echo "=== Container processes ==="
                                docker exec mlops-test ps aux 2>/dev/null || echo "Cannot check container processes"
                                
                                echo "=== Container port mapping ==="
                                docker port mlops-test 2>/dev/null || echo "Cannot check port mapping"
                                
                                echo "=== Container inspect ==="
                                docker inspect mlops-test | grep -A 10 -B 10 "NetworkMode\\|PortBindings" || true
                                '''
                                error("Health check failed after 6 attempts")
                            }
                            
                        } else {
                            echo "=== Container failed to start properly ==="
                            sh '''
                            echo "Container logs:"
                            docker logs mlops-test 2>/dev/null || echo "No logs available"
                            
                            echo "Container inspect:"
                            docker inspect mlops-test 2>/dev/null || echo "Cannot inspect container"
                            '''
                            error("Container is not running (status: ${containerStatus})")
                        }
                        
                    } catch (Exception e) {
                        echo "❌ Test failed: ${e.getMessage()}"
                        sh '''
                        echo "=== Error debugging info ==="
                        docker logs mlops-test 2>/dev/null || echo "No test container logs available"
                        docker ps -a | grep mlops || echo "No MLOps containers found"
                        '''
                        throw e
                    } finally {
                        // Always cleanup test container
                        echo "=== Cleaning up test container ==="
                        sh '''
                        if docker ps -a --format "table {{.Names}}" | grep -q "^mlops-test$"; then
                            docker stop mlops-test 2>/dev/null || true
                            docker rm mlops-test 2>/dev/null || true
                            echo "Test container cleaned up"
                        fi
                        '''
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                script {
                    try {
                        // Stop existing production container
                        echo "=== Cleaning up existing production container ==="
                        sh '''
                        if docker ps -a --format "table {{.Names}}" | grep -q "^mlops-app$"; then
                            echo "Stopping existing mlops-app container"
                            docker stop mlops-app 2>/dev/null || true
                            echo "Removing existing mlops-app container"
                            docker rm mlops-app 2>/dev/null || true
                        else
                            echo "No existing mlops-app container found"
                        fi
                        '''
                        
                        // Check if port 3000 is in use
                        sh '''
                        if netstat -tuln | grep -q ":3000 "; then
                            echo "⚠️  Port 3000 is already in use"
                            netstat -tuln | grep ":3000 "
                            echo "Trying to find and stop process using port 3000"
                            lsof -ti:3000 | xargs -r kill -9 || true
                            sleep 2
                        fi
                        '''
                        
                        // Deploy new production container
                        echo "=== Deploying production container ==="
                        def deployResult = sh(
                            script: "docker run -d --name mlops-app -p 3000:3000 --restart unless-stopped mlops-local:latest",
                            returnStatus: true
                        )
                        
                        if (deployResult != 0) {
                            error("Failed to start production container")
                        }
                        
                        // Wait for application to start
                        echo "=== Waiting for application to start ==="
                        sleep(20)
                        
                        // Verify production deployment
                        echo "=== Verifying production deployment ==="
                        
                        def prodContainerExists = sh(
                            script: "docker ps -a --format '{{.Names}}' | grep -q '^mlops-app\$'",
                            returnStatus: true
                        ) == 0
                        
                        if (!prodContainerExists) {
                            error("Production container mlops-app does not exist after creation")
                        }
                        
                        sh '''
                        echo "=== Production Container Status ==="
                        docker ps -a | grep mlops-app
                        
                        echo "=== Production Container Logs ==="
                        docker logs mlops-app
                        '''
                        
                        // Production health check
                        def prodHealthPassed = false
                        for (int i = 1; i <= 5; i++) {
                            echo "Production health check attempt ${i}/5"
                            
                            def exitCode = sh(
                                script: 'timeout 15 curl -f -s http://localhost:3000/ 2>/dev/null',
                                returnStatus: true
                            )
                            
                            if (exitCode == 0) {
                                echo "✅ Production deployment successful"
                                prodHealthPassed = true
                                break
                            } else {
                                echo "❌ Production health check failed (exit code: ${exitCode})"
                                if (i < 5) {
                                    echo "Waiting 10 seconds before retry..."
                                    sleep(10)
                                    sh "docker logs --tail 10 mlops-app"
                                }
                            }
                        }
                        
                        if (!prodHealthPassed) {
                            echo "=== Production deployment debugging ==="
                            sh '''
                            echo "=== Final production logs ==="
                            docker logs mlops-app
                            
                            echo "=== Port check ==="
                            netstat -tlnp | grep 3000 || echo "Port 3000 not listening"
                            
                            echo "=== Container status ==="
                            docker inspect mlops-app | grep -A 5 -B 5 "Status\\|Health" || true
                            '''
                            error("Production deployment health check failed")
                        }
                        
                        echo "🚀 Application successfully deployed at http://localhost:3000"
                        
                    } catch (Exception e) {
                        echo "❌ Production deployment failed: ${e.getMessage()}"
                        sh '''
                        echo "=== Production failure debugging ==="
                        docker logs mlops-app 2>/dev/null || echo "No production container logs"
                        docker ps -a | grep mlops || echo "No MLOps containers running"
                        '''
                        throw e
                    }
                }
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
            sh '''
            echo "=== Deployment Summary ==="
            docker ps | grep mlops-app || echo "⚠️  No production container running"
            echo "Application should be available at: http://localhost:3000"
            
            echo "=== Final status check ==="
            curl -f -s http://localhost:3000/ >/dev/null && echo "✅ Application is responding" || echo "❌ Application not responding"
            '''
        }
        failure {
            echo '❌ Pipeline failed. Check logs for details.'
            sh '''
            echo "=== Failure cleanup and debugging info ==="
            echo "=== All MLOps containers ==="
            docker ps -a | grep mlops || echo "No MLOps containers found"
            
            echo "=== Container logs ==="
            docker logs mlops-test 2>/dev/null || echo "No test container logs"
            docker logs mlops-app 2>/dev/null || echo "No app container logs"
            
            echo "=== Port usage ==="
            netstat -tlnp | grep -E ":300[01] " || echo "Ports 3000/3001 not in use"
            
            echo "=== Cleaning up failed containers ==="
            docker stop mlops-app mlops-test 2>/dev/null || true
            docker rm mlops-app mlops-test 2>/dev/null || true
            echo "Cleanup completed"
            '''
        }
        always {
            sh '''
            echo "=== Cleaning up old images ==="
            docker image prune -f
            
            # Keep only latest and current timestamp images
            docker images mlops-local --format "{{.Repository}}:{{.Tag}}" | grep -v latest | grep -v "${IMAGE_TAG}" | head -n -2 | xargs -r docker rmi 2>/dev/null || true
            
            echo "=== Final system state ==="
            docker ps | grep mlops || echo "No MLOps containers running"
            docker images | grep mlops-local || echo "No MLOps images found"
            '''
        }
    }
}
