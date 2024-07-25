import subprocess
import re

def get_ipconfig_data():
    # Ejecuta el comando ipconfig y obtiene la salida
    result = subprocess.run(['ipconfig'], capture_output=True, text=True, encoding='cp850')
    
    # Divide la salida en líneas
    output = result.stdout.splitlines()
    
    # Diccionario para almacenar los datos
    ipconfig_data = {}
    
    # Expresiones regulares para extraer la información
    regexes = {
        'dns_suffix': re.compile(r'\s*Sufijo DNS específico para la conexión\. \. :\s*(\S*)'),
        'inet6': re.compile(r'\s*Vínculo: dirección IPv6 local. . . : ([ABCDEFabcdef\d\:\%]+)'),
        'inet4': re.compile(r'\s*Dirección IPv4. . . . . . . . . . . . . . : ([^\s\(]+)'),
        'netmask': re.compile(r'\s*Máscara de subred . . . . . . . . . . . . : ([^\s\(]+)'),
        'gateway': re.compile(r'\s*Puerta de enlace predeterminada . . . . . : ([^\s\(]+)')
    }
    
    # Variables temporales para almacenar los datos de cada adaptador
    current_adapter = None
    current_data = {}
    
    for line in output:
        # Si encuentra el nombre de un adaptador, guarda los datos del adaptador anterior y reinicia las variables
        if 'Adaptador' in line:
            if current_adapter:
                ipconfig_data[current_adapter] = current_data
            current_adapter = line.strip().replace('Adaptador de ', '')
            current_data = {}
        else:
            if line == '':
                continue
            for key, regex in regexes.items():
                match = regex.match(line)
                if match:
                    current_data[key] = match.group(1).strip()
    
    # Guarda los datos del último adaptador
    if current_adapter:
        ipconfig_data[current_adapter] = current_data
    
    return ipconfig_data

# Ejemplo de uso
if __name__ == "__main__":
    data = get_ipconfig_data()
    for adapter, info in data.items():
        print(f"Adapter: {adapter}")
        for key, value in info.items():
            print(f"  {key}: {value}")
