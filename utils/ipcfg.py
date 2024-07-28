import subprocess
import re
import locale

def get_regex_lng():
    lang = locale.getdefaultlocale()
    encoder = lang[1]
    try:
        result = subprocess.run(
            ["powershell", "-Command", "[CultureInfo]::InstalledUICulture.Name"],
            capture_output=True,
            text=True
        )
        cmd_language = result.stdout.strip()
        print(f"Idioma de la consola: {cmd_language}")
    except Exception as e:
        print(f"No se pudo obtener el idioma de la consola: {e}")

    regex = ""
    if "en" in cmd_language:
        regex = {
        'dns_suffix': re.compile(r'\s*Connection-specific DNS Suffix  \. :\s*(\S*)'),
        'inet6': re.compile(r'\s*IPv6 Address. . . . . . . . . . . : ([ABCDEFabcdef\d\:\%]+)'),
        'inet4': re.compile(r'\s*IPv4 Address. . . . . . . . . . . : ([^\s\(]+)'),
        'netmask': re.compile(r'\s*Subnet Mask . . . . . . . . . . . : ([^\s\(]+)'),
        'gateway': re.compile(r'\s*Default Gateway . . . . . . . . . : ([^\s\(]+)')
        }
        adapter = "adapter"
    elif "es" in cmd_language:
        regex = {
        'dns_suffix': re.compile(r'\s*Sufijo DNS específico para la conexión\. \. :\s*(\S*)'),
        'inet6': re.compile(r'\s*Vínculo: dirección IPv6 local. . . : ([ABCDEFabcdef\d\:\%]+)'),
        'inet4': re.compile(r'\s*Dirección IPv4. . . . . . . . . . . . . . : ([^\s\(]+)'),
        'netmask': re.compile(r'\s*Máscara de subred . . . . . . . . . . . . : ([^\s\(]+)'),
        'gateway': re.compile(r'\s*Puerta de enlace predeterminada . . . . . : ([^\s\(]+)')
        }
        adapter = 'Adaptador'
    return regex, adapter, encoder

def get_ipconfig_data():
    # Expresiones regulares para extraer la información
    regexes, adapter, encoder = get_regex_lng()

    # Ejecuta el comando ipconfig y obtiene la salida
    result = subprocess.run(['ipconfig'], capture_output=True, text=True, encoding=encoder)
    
    # Divide la salida en líneas
    output = result.stdout.splitlines()
    
    # Diccionario para almacenar los datos
    ipconfig_data = {}
    
    # Variables temporales para almacenar los datos de cada adaptador
    current_adapter = None
    current_data = {}
    
    for line in output:
        # Si encuentra el nombre de un adaptador, guarda los datos del adaptador anterior y reinicia las variables
        if adapter in line:
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
