#!/usr/bin/env python3
from db.utils import *

import sys
#main
def main():
    #get modules from cli
    for arg in sys.argv[1:] :
        module_name = arg 
        print(f"********** module: {module_name} ***********")
        #get module connections
        module_connections = get_module_endpoints(module_name)
        if not module_connections:
            print(f"Module '{module_name}' not found or has no connections.")
            sys.exit(1)
        #print module connections
       # print(f"Connections for module '{module_name}':")
        for conn_type, conn_value in module_connections.items():
            if conn_value:
                print(f"{conn_type}: {conn_value}")
            else:
                print(f"{conn_type}: Not connected")
        module= get_module(module_name)
        print(f"Mounted_on: {module.get('mounted_on', 'N/A')}")
        print(f"Speed: {get_module_speed(module)}")
if __name__ == "__main__":
    main()