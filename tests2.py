import nmap
import psutil
import socket
import windows_tools.antivirus
import platform
import sys
import io

def leer_html(path):
    with io.open(path, 'r', encoding='utf8') as archivo_html:
        contenido_html = archivo_html.read()
    return contenido_html




def port_scan(ip : str) -> dict:
    """
    Escanea los puertos abiertos en una dirección IP dada.

    Args:
        ip (str): La dirección IP a escanear.

    Returns:
        Un diccionario que contiene los puertos abiertos en la dirección IP dada.
    """

    #ip = "192.168.100.9/24"
    scanner = nmap.PortScanner()
    scanner.scan(ip)
    result = {}
    for host in scanner.all_hosts():
        if scanner[host].state() == 'up':
            result[host] = []
            for proto in scanner[host].all_protocols():
                lport = scanner[host][proto].keys()
                for port in lport:
                    result[host].append({"port": port, "protocol": proto})
    return result


def get_interface_info() -> dict:
    """
    Obtiene información de las interfaces de red y sus direcciones IP y máscaras de subred.

    Returns:
        Un diccionario donde las claves son los nombres de las interfaces de red y los valores son listas de tuplas
        que contienen las direcciones IP y máscaras de subred de cada interfaz.
    """
    net_ifs = psutil.net_if_addrs()
    result = {}
    for interface_name, interface_addresses in net_ifs.items():
        result[interface_name] = []
        for address in interface_addresses:
            if address.family == socket.AF_INET:
                result[interface_name].append({
                    "address": address.address,
                    "netmask": address.netmask
                })
            elif address.family == socket.AF_INET6:
                result[interface_name].append({
                    "address": address.address,
                    "netmask": address.netmask
                })
    return result


def get_antivirus() -> dict:
    """
    Obtiene el software antivirus instalado en el sistema.

    Returns:
        Un diccionario que contiene el software antivirus instalado en el sistema.
    """
    result = windows_tools.antivirus.get_installed_antivirus_software()
    return {"antivirus_software": result}



def get_system_info() -> dict:
    """
    Obtiene información del sistema.

    Returns:
        Un diccionario que contiene la información del sistema.
    """
    def linux_distribution() -> str:
        try:
            return platform.linux_distribution()
        except:
            return 'N/A'

    def dist() -> str:
        try:
            return platform.dist()
        except:
            return 'N/A'

    return {
        "python_version": sys.version.split('\n'),
        "dist": str(dist()),
        "linux_distribution": linux_distribution(),
        "system": platform.system(),
        "machine": platform.machine(),
        "platform": platform.platform(),
        "uname": platform.uname(),
        "version": platform.version(),
        "mac_ver": platform.mac_ver(),
    }



def get_local_ip() -> dict:
    """
    Obtiene la dirección IP local del sistema.

    Returns:
        Un diccionario con la dirección IP local del sistema.
    """
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    return IPAddr