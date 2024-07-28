import asyncio
from scapy.all import IP, ICMP, sr1
import ipaddress
from ipaddress import IPv4Network

from utils.ipcfg import get_ipconfig_data

def get_network_address(ip, netmask):
    # Crear un objeto IPv4Network usando la dirección IP y la máscara de red
    network = ipaddress.IPv4Network(f'{ip}/{netmask}', strict=False)
    return network.with_prefixlen

async def ping(ip):
    ip_str = str(ip)
    print(f"Pinging.. {ip_str}")
    pkt = IP(dst=ip_str) / ICMP()
    response = sr1(pkt, timeout=1, verbose=0)
    if response:
        print(f"{ip_str} is up")
    else:
        print(f"{ip_str} is down")

async def scan_net(ip_range):
    tasks = [ping(ip) for ip in ip_range]
    await asyncio.gather(*tasks)

def parse_ip_netmask(ip_address, netmask): # devuelve ip + mask format 192.168.1.0/24
    if "/" in netmask:
        cidr_suffix = netmask.split('/')[-1]
    else:
        cidr_suffix = sum(bin(int(x)).count('1') for x in netmask.split('.'))
    # Forma la dirección en el formato requerido
    ip_with_mask = f"{ip_address}/{cidr_suffix}"
    
    return ip_with_mask

if __name__=="__main__":
    ip_dict = get_ipconfig_data() #obtengo las ip del sistema
    ip_device = next(iter(ip_dict)) #me quedo con la del primer adaptador
    ip_dict = ip_dict[ip_device] #guardo la del primer adaptador en otro dict
    ip_net = get_network_address(ip_dict["inet4"],ip_dict["netmask"]) #obtengo la ip de red
    ip_net = IPv4Network(ip_net)
    ip_range = ip_net.hosts()
    asyncio.run(scan_net(ip_range))
