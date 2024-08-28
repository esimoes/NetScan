import sqlite3
from datetime import datetime
import nmap
import threading

# Función para crear la base de datos y la tabla
def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
                   mac TEXT PRIMARY KEY,
                   ip TEXT NOT NULL,
                   mac_vendor TEXT,
                   name TEXT,
                   type TEXT,
                   device_brand TEXT,
                   device_model TEXT,
                   os TEXT,
                   os_ver TEXT,
                   online BOOLEAN,
                   first_detect DATE,
                   open_ports TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Función para insertar datos en la base de datos
def insert_devices(db_name, devices):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Marcar todos los dispositivos como offline
    cursor.execute('''
        UPDATE devices
        SET online = False
    ''')
    now = datetime.now()
    format_date = now.strftime("%Y-%m-%d %H:%M:%S")
    # Insertar o actualizar los dispositivos pasados como parámetro
    for device in devices:
        cursor.execute('''
            INSERT INTO devices (mac, ip, online, first_detect)
            VALUES (?, ?, True,?)
            ON CONFLICT(mac) DO UPDATE SET ip = excluded.ip,  online = True
        ''', (device['mac'], device['ip'],format_date))

    conn.commit()
    conn.close()

def update_deep_scan(db_name, devices):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for device in devices:
        print(f"Deep scan for {device}")
        os, osgen, open_ports, vendor = deep_scan(device['ip'])

        # Actualizar solo si `device_os` es NULL
        cursor.execute('''
            UPDATE devices
            SET os = COALESCE(os, ?),
                os_ver = COALESCE(os_ver, ?),
                open_ports = ?,
                mac_vendor = COALESCE(mac_vendor, ?)    
            WHERE mac = ?
        ''', (os, osgen, ','.join(map(str, open_ports)), vendor, device['mac']))

    conn.commit()
    conn.close()

def deep_scan(ip):
    nm = nmap.PortScanner()
    nm.scan(ip, arguments='-O')  # -O para la detección del sistema operativo
    os = 'Unknown'
    osgen = 'Unknown'
    open_ports = []
    vendor = 'Unknown'
    # Verificar si la IP está en el resultado del escaneo
    if ip in nm.all_hosts():
        if 'osmatch' in nm[ip]:
            osmatch = nm[ip].get('osmatch', [])
            if osmatch:
                osclass = osmatch[0].get('osclass', [])
                if osclass:
                    os = osclass[0].get('osfamily', 'Unknown')
                    osgen = osclass[0].get('osgen', 'Unknown')
        if 'tcp' in nm[ip]:
            open_ports = [port for port in nm[ip]['tcp'] if nm[ip]['tcp'][port]['state'] == 'open']
        if 'mac' in nm[ip]['addresses']:
            mac = nm[ip]['addresses']['mac']
            #vendor = nm[ip]['vendor'][mac]
            vendor = nm[ip]['vendor'].get('mac', 'Unknown')
    
    return os, osgen, open_ports, vendor

if __name__=="__main__":
    create_database("db/devices.db")