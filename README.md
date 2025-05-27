# k8s-api

## Running the original app
On a machine with network access to login to your Kubernetes Control Plane and a Kubeconfig file or a POD running inside a Kubernetes cluster (Will try both to login)

 - git clone https://github.com/tkrausjr/k8s-api.git
 - kubectl vsphere login --server 192.168.201.130 --vsphere-username administrator@vsphere.local --insecure-skip-tls-verify / --tanzu-kubernetes-cluster-namespace test-ns-1 --tanzu-kubernetes-cluster-name k8s-129-01
 - cd ./k8s-api
 - ./k8s-info-web-app.py 
   -- INFO:__main__:Starting Kubernetes Dashboard on port 5000
   -- * Serving Flask app 'k8s-info-web-app'
   -- * Debug mode: off
   -- INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
   -- * Running on all addresses (0.0.0.0)
   -- * Running on http://127.0.0.1:5000
   -- * Running on http://10.160.53.40:5000
   -- INFO:werkzeug:Press CTRL+C to quit
 - In a browser, open up http://127.0.0.1:5000 / You should see a webpage with your Cluster information with the title "Kubernetes Cluster Dashboard"
 
## Running the my version app
On a machine with network access to login to your Kubernetes Control Plane and a Kubeconfig file or a POD running inside a Kubernetes cluster (Will try both to login)
 - The my-k8s-web-app.py uses the ./templates/my-k8s-web-app-page.html  html template.
 - cd ./k8s-api
 - ./k8s-info-web-app.py 
   -- INFO:__main__:Starting Kubernetes Dashboard on port 5000
   -- * Serving Flask app 'k8s-info-web-app'
   -- * Debug mode: off
   -- INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
   -- * Running on all addresses (0.0.0.0)
   -- * Running on http://127.0.0.1:5000
   -- * Running on http://10.160.53.40:5000
   -- INFO:werkzeug:Press CTRL+C to quit
 - In a browser, open up http://127.0.0.1:5000 \ You should see a webpage with your Cluster information with the title "Kubernetes Cluster Dashboard"
