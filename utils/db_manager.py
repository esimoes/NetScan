import sqlite3

import nmap

# Función para crear la base de datos y la tabla
def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            mac TEXT PRIMARY KEY,
            ip TEXT NOT NULL,
            os TEXT,
            open_ports TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Función para insertar datos en la base de datos
def insert_data(db_name, devices):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for device in devices:
        cursor.execute('''
            INSERT INTO devices (mac, ip)
            VALUES (?, ?)
            ON CONFLICT(mac) DO UPDATE SET ip = excluded.ip
        ''', (device['mac'], device['ip']))
    conn.commit()
    conn.close()

def update_deep_scan(db_name, devices):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    for device in devices:
        print(f"deep scan for {device}")
        os, open_ports = deep_scan(device['ip'])
        cursor.execute('''
            UPDATE devices
            SET os = ?, open_ports = ?
            WHERE mac = ?
        ''', (os, ','.join(map(str, open_ports)), device['mac']))
    conn.commit()
    conn.close()

def deep_scan(ip):
    nm = nmap.PortScanner()
    nm.scan(ip, arguments='-O')  # -O para la detección del sistema operativo
    os = 'Unknown'
    open_ports = []
    
    # Verificar si la IP está en el resultado del escaneo
    if ip in nm.all_hosts():
        if 'osmatch' in nm[ip]:
            os = nm[ip]['osmatch'][0]['name']
        if 'tcp' in nm[ip]:
            open_ports = [port for port in nm[ip]['tcp'] if nm[ip]['tcp'][port]['state'] == 'open']
    
    return os, open_ports

if __name__=="__main__":
    create_database("db/mac_tables.db")