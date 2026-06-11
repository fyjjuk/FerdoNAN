import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
from security.filters.ingress import IngressFilter

def test_ingress_blocks_dangerous_pattern():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as f:
        f.write("rm -rf\nsudo\n")
        f.flush()
        ingress = IngressFilter(global_regex_path=f.name, enabled_layer2=False)
        agent = {"firewall_override": {}}
        
        assert ingress.evaluate("sudo apt update", agent) == False
        assert ingress.evaluate("hola mundo", agent) == True

def test_ingress_allows_safe_input():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as f:
        f.write("malo\n")
        f.flush()
        ingress = IngressFilter(global_regex_path=f.name, enabled_layer2=False)
        agent = {"firewall_override": {}}
        assert ingress.evaluate("comando seguro", agent) == True
