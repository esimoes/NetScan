import scapy.all as scapy
import ifcfg

def scan_net(ip):
    ip=scapy.IP(dst=ip)
    for p in ip:
        print(p)

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

def get_system_net(): # devuelve ip + mask format 192.168.1.0/24
    nets_dict = {}
    for name, interface in ifcfg.interfaces().items():
        # Obtiene el nombre del dispositivo
        device_name = interface['device']
        # Obtiene la dirección IPv4 y la máscara de red
        ip_address = interface.get('inet')
        netmask = interface.get('netmask')
        if ip_address and netmask:
            # Convierte la máscara de red en formato de sufijo CIDR
            if "/" in netmask:
                cidr_suffix = netmask.split('/')[-1]
            else:
                cidr_suffix = sum(bin(int(x)).count('1') for x in netmask.split('.'))
            # Forma la dirección en el formato requerido
            ip_with_mask = f"{ip_address}/{cidr_suffix}"
            nets_dict[device_name] = ip_with_mask
    
    return nets_dict

if __name__=="__main__":
    ip = get_system_net()
    scan_net('192.168.100.0/24')