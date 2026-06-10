import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
from security.filters.egress import EgressFilter

def test_egress_blocks_dangerous_command():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as cmd_f, \
         tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as tool_f:
        cmd_f.write("rm\n")
        cmd_f.flush()
        tool_f.write("danger\n")
        tool_f.flush()
        egress = EgressFilter(cmd_f.name, tool_f.name)
        route_config = {"firewall": {"egress_filter_enabled": True}}
        
        assert egress.evaluate("Ejecuta rm -rf /", route_config) == False
        assert egress.evaluate("Comando seguro", route_config) == True

def test_egress_disabled_by_default():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as cmd_f:
        cmd_f.write("rm\n")
        cmd_f.flush()
        egress = EgressFilter(cmd_f.name, "dummy.txt")
        route_config = {}  # sin habilitar
        assert egress.evaluate("rm -rf", route_config) == True
