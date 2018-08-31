#https://www.digitalocean.com/community/tutorials/how-to-set-up-a-private-docker-registry-on-ubuntu-14-04
from docker import Client
import psutil
cli = Client(base_url='unix://var/run/docker.sock')
containers = cli.containers()


def get_cpu_times(pid):
    proc = psutil.Process(pid)
    return proc.cpu_percent(interval=1.0), proc.cpu_times() 
            
        
    
for container in containers:
    if container.get('State') == 'running':
        name= container.get('Names')[0]
        info = cli.inspect_container(name)
        pid = info['State']['Pid']
        cpu,l = get_cpu_times(pid)
        s = 'name:%s, state:%s, pid:%s, cpu:%s, %s'
        print(s % (container.get('Names')[0], container.get('State'), pid, cpu, l))