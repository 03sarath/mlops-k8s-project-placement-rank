# Kubernetes-placement-app
project folder for ML model deployment using Kubernetes 



This is repo for project for demonstration of deployment of ML model (containerized) using Kubernetes(k8s)

The Docker image is uploaded on https://hub.docker.com . The image can be pulled using

$ docker pull 03sarath/placement-rank

The details of folder/files in the project folder is as follows :

 (1) Notebooks folder - jupyter noteboook for data cleaning , model building with model and Dictvectorizer(encoding of cat columns) as output

 (2) Data - contains train and test data .

 (3) predict.py - python script to prodice an API for model prediction using flask framework

 (4) predict-test.py - python test script with test features for testing the model prediction . It uses requests libary to access REST API.
                       Please keep in mind to enter correct URL in the script for testing the application (depends on loca/rremote testing)

  (5) Pipfile and Pipfile.lock - pipenv generated dependencies files

  (6) Dockerfile - for building Docker image

  (7) kubeconfig folder - contains deployment.yaml and service.yaml for deploying the container on k8s
