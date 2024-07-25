import scapy.all as scapy

from utils.ipcfg import get_ipconfig_data

def scan_net(ip_range):
    try:
        ip = scapy.IP(dst=ip_range)
        for p in ip:
            result = scapy.send(p/scapy.ICMP(), verbose=False)
            print(result)
    except PermissionError as e:
        print(f"Permission error: {e}. Try running the script as an administrator.")
    except Exception as e:
        print(f"An error occurred: {e}")

def parse_ip_netmask(ip_address, netmask): # devuelve ip + mask format 192.168.1.0/24
    if "/" in netmask:
        cidr_suffix = netmask.split('/')[-1]
    else:
        cidr_suffix = sum(bin(int(x)).count('1') for x in netmask.split('.'))
    # Forma la dirección en el formato requerido
    ip_with_mask = f"{ip_address}/{cidr_suffix}"
    
    return ip_with_mask

def scan(ip):
    arp_req_frame = scapy.ARP(pdst = ip)

    broadcast_ether_frame = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")
    
    broadcast_ether_arp_req_frame = broadcast_ether_frame / arp_req_frame

    answered_list = scapy.srp(broadcast_ether_arp_req_frame, timeout = 1, verbose = False)[0]
    result = []
    for i in range(0,len(answered_list)):
        client_dict = {"ip" : answered_list[i][1].psrc, "mac" : answered_list[i][1].hwsrc}
        result.append(client_dict)

    return result

if __name__=="__main__":
    ip_dict = get_ipconfig_data()
    ip_device = next(iter(ip_dict))
    ip_dict = ip_dict[ip_device]
    ip = parse_ip_netmask(ip_dict["inet4"],ip_dict["netmask"])

    scan_net(ip)
