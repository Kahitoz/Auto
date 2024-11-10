pipeline {
    agent any

    environment {
        KUBECONFIG = "/var/lib/jenkins/.kube/config"  // Path to your kubeconfig file on Jenkins server
        NAMESPACE = "personal"                          // Namespace where the deployment will occur
        IMAGE_NAME = "192.168.1.2:32000/filesprg"     // Updated image name
        MANIFESTS_PATH = "manifests"                  // Path to the manifests folder (no subfolders)
    }

    stages {
        stage('Build and Push Docker Image') {
            steps {
                script {
                    // Define variables
                    def dockerfile = 'Dockerfile'      // Dockerfile for building the image
                    def imageTag = 'latest'            // Always push with 'latest' tag

                    // Build and push Docker image to the registry
                    docker.withRegistry('http://192.168.1.2:32000') {
                        def dockerImage = docker.build("${IMAGE_NAME}:${imageTag}", "-f ${dockerfile} .")
                        dockerImage.push(imageTag)      // Push the image with 'latest' tag
                    }

                    // Save imageTag for later use in the pipeline
                    env.IMAGE_TAG = imageTag
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    def imageTag = env.IMAGE_TAG          // Use 'latest' tag for deployment

                    // Update the deployment manifest with the correct image and tag
                    sh """
                    sed -i 's|image:.*|image: ${IMAGE_NAME}:${imageTag}|' ${MANIFESTS_PATH}/deployment.yaml
                    """

                    // Apply the updated Kubernetes manifests
                    sh """
                    kubectl --kubeconfig=${KUBECONFIG} apply -f ${MANIFESTS_PATH}/ -n ${NAMESPACE}
                    """
                }
            }
        }

        stage('Force Rolling Restart') {
            steps {
                script {
                    // Restart the deployment to apply the new image
                    sh "kubectl --kubeconfig=${KUBECONFIG} rollout restart deployment/image-dp -n ${NAMESPACE}"
                }
            }
        }
    }
}
