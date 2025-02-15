import pytest
import yaml
from pathlib import Path

class TestKubernetesConfigs:
    @pytest.fixture
    def k8s_dir(self):
        return Path(__file__).parent.parent.parent / 'k8s'
    
    def test_deployment_config(self, k8s_dir):
        with open(k8s_dir / 'deployment.yml') as f:
            config = yaml.safe_load(f)
            
        assert config['kind'] == 'Deployment'
        assert config['spec']['replicas'] == 2
        
        container = config['spec']['template']['spec']['containers'][0]
        assert container['name'] == 'web'
        assert 'resources' in container
        assert 'limits' in container['resources']
        assert 'requests' in container['resources']
    
    def test_service_config(self, k8s_dir):
        with open(k8s_dir / 'service.yml') as f:
            config = yaml.safe_load(f)
            
        assert config['kind'] == 'Service'
        assert config['spec']['type'] == 'LoadBalancer'
        assert config['spec']['ports'][0]['port'] == 80
    
    def test_ingress_config(self, k8s_dir):
        with open(k8s_dir / 'ingress.yml') as f:
            config = yaml.safe_load(f)
            
        assert config['kind'] == 'Ingress'
        assert 'cert-manager.io/cluster-issuer' in config['metadata']['annotations']
        assert 'tls' in config['spec'] 