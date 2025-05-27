#!/usr/bin/env python3
"""
Simple Python Web App using Kubernetes API
Requires: pip install flask kubernetes
"""

from flask import Flask, render_template, jsonify
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# HTML template


def init_k8s_client():
    """Initialize Kubernetes client"""
    try:
        # Try to load in-cluster config first (when running in a pod)
        config.load_incluster_config()
        logger.info("Loaded in-cluster Kubernetes config")
    except config.ConfigException:
        try:
            # Fall back to local kubeconfig
            config.load_kube_config()
            logger.info("Loaded local Kubernetes config")
        except config.ConfigException as e:
            logger.error(f"Failed to load Kubernetes config: {e}")
            return None
    
    return client.ApiClient()

def get_age_string(creation_timestamp):
    """Convert creation timestamp to age string"""
    try:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        age = now - creation_timestamp.replace(tzinfo=timezone.utc)
        
        days = age.days
        hours, remainder = divmod(age.seconds, 3600)
        minutes = remainder // 60
        
        if days > 0:
            return f"{days}d"
        elif hours > 0:
            return f"{hours}h"
        else:
            return f"{minutes}m"
    except:
        return "Unknown"

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/cluster-info')
def cluster_info():
    """Get cluster information"""
    try:
        k8s_client = init_k8s_client()
        if not k8s_client:
            return jsonify({"error": "Failed to initialize Kubernetes client"})
        
        v1 = client.CoreV1Api(k8s_client)
        version_api = client.VersionApi(k8s_client)
        
        # Get version
        version_info = version_api.get_code()
        
        # Get counts
        nodes = v1.list_node()
        pods = v1.list_pod_for_all_namespaces()
        services = v1.list_service_for_all_namespaces()
        
        return jsonify({
            "version": f"{version_info.major}.{version_info.minor}",
            "node_count": len(nodes.items),
            "pod_count": len(pods.items),
            "service_count": len(services.items)
        })
    
    except ApiException as e:
        logger.error(f"Kubernetes API error: {e}")
        return jsonify({"error": f"Kubernetes API error: {e.reason}"})
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)})

@app.route('/api/nodes')
def get_nodes():
    """Get cluster nodes"""
    try:
        k8s_client = init_k8s_client()
        if not k8s_client:
            return jsonify({"error": "Failed to initialize Kubernetes client"})
        
        v1 = client.CoreV1Api(k8s_client)
        nodes = v1.list_node()
        
        node_list = []
        for node in nodes.items:
            # Get node status
            status = "NotReady"
            for condition in node.status.conditions:
                if condition.type == "Ready" and condition.status == "True":
                    status = "Ready"
                    break
            
            node_info = node.status.node_info
            node_list.append({
                "name": node.metadata.name,
                "status": status,
                "version": node_info.kubelet_version,
                "os": f"{node_info.os_image}",
                "cpu": node.status.capacity.get('cpu', 'Unknown'),
                "memory": node.status.capacity.get('memory', 'Unknown')
            })
        
        return jsonify({"nodes": node_list})
    
    except ApiException as e:
        logger.error(f"Kubernetes API error: {e}")
        return jsonify({"error": f"Kubernetes API error: {e.reason}"})
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)})

@app.route('/api/pods')
def get_pods():
    """Get cluster pods"""
    try:
        k8s_client = init_k8s_client()
        if not k8s_client:
            return jsonify({"error": "Failed to initialize Kubernetes client"})
        
        v1 = client.CoreV1Api(k8s_client)
        pods = v1.list_pod_for_all_namespaces()
        
        pod_list = []
        for pod in pods.items:
            # Calculate ready containers
            ready_containers = 0
            total_containers = len(pod.spec.containers)
            restart_count = 0
            
            if pod.status.container_statuses:
                for container_status in pod.status.container_statuses:
                    if container_status.ready:
                        ready_containers += 1
                    restart_count += container_status.restart_count
            
            pod_list.append({
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase,
                "ready": f"{ready_containers}/{total_containers}",
                "restarts": restart_count,
                "age": get_age_string(pod.metadata.creation_timestamp)
            })
        
        return jsonify({"pods": pod_list})
    
    except ApiException as e:
        logger.error(f"Kubernetes API error: {e}")
        return jsonify({"error": f"Kubernetes API error: {e.reason}"})
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)})

@app.route('/api/services')
def get_services():
    """Get cluster services"""
    try:
        k8s_client = init_k8s_client()
        if not k8s_client:
            return jsonify({"error": "Failed to initialize Kubernetes client"})
        
        v1 = client.CoreV1Api(k8s_client)
        services = v1.list_service_for_all_namespaces()
        
        service_list = []
        for service in services.items:
            # Format ports
            ports = []
            if service.spec.ports:
                for port in service.spec.ports:
                    port_str = str(port.port)
                    if port.target_port:
                        port_str += f":{port.target_port}"
                    if port.protocol and port.protocol != 'TCP':
                        port_str += f"/{port.protocol}"
                    ports.append(port_str)
            
            external_ip = service.status.load_balancer.ingress[0].ip if (
                service.status.load_balancer and 
                service.status.load_balancer.ingress
            ) else service.spec.external_i_ps[0] if service.spec.external_i_ps else "None"
            
            service_list.append({
                "name": service.metadata.name,
                "namespace": service.metadata.namespace,
                "type": service.spec.type,
                "cluster_ip": service.spec.cluster_ip,
                "external_ip": external_ip,
                "ports": ", ".join(ports) if ports else "None"
            })
        
        return jsonify({"services": service_list})
    
    except ApiException as e:
        logger.error(f"Kubernetes API error: {e}")
        return jsonify({"error": f"Kubernetes API error: {e.reason}"})
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": str(e)})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Kubernetes Dashboard on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)