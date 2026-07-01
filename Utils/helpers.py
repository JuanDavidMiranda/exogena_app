import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime

def inicializar_encabezado(raiz, ano, formato, version, num_envio, cantidad_registros, valor_total):
    """
    Inicializa el nodo <Cab> requerido por la DIAN en los archivos XML Muisca.
    """
    cab = ET.SubElement(raiz, "Cab")
    ET.SubElement(cab, "Ano").text = str(ano)
    ET.SubElement(cab, "CodCpt").text = "1"
    ET.SubElement(cab, "Formato").text = str(formato)
    ET.SubElement(cab, "Version").text = str(version)
    ET.SubElement(cab, "NumEnvio").text = str(num_envio)
    ET.SubElement(cab, "FecEnvio").text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    ET.SubElement(cab, "FecInicial").text = f"{ano}-01-01"
    ET.SubElement(cab, "FecFinal").text = f"{ano}-12-31"
    ET.SubElement(cab, "ValorTotal").text = str(int(valor_total))
    ET.SubElement(cab, "CantReg").text = str(int(cantidad_registros))

def generar_xml_bytes(raiz):
    """
    Convierte el árbol de ElementTree en un string XML indentado y codificado en ISO-8859-1.
    """
    xml_string = ET.tostring(raiz, encoding="ISO-8859-1")
    reparsed = minidom.parseString(xml_string)
    return reparsed.toprettyxml(indent="  ").encode("ISO-8859-1")