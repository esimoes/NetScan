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
                   mac_brand TEXT,
                   name TEXT,
                   type TEXT,
                   device_brand TEXT,
                   device_model TEXT,
                   device_os TEXT,
                   device_os_ver TEXT,
                   online BOOLEAN,
                   first_detect DATE,
                   open_ports TEXT
        )
    ''')
    conn.commit()
    conn.close()