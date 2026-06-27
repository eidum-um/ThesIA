import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse

# URL base desde la que empezará a rastrear
URL_SEMILLA = "https://www.um.es/web/eidum/"

# Configuración del rastreador
URLS_VISITADAS = set()
URLS_POR_VISITAR = [URL_SEMILLA]
conocimiento = []

# Encabezado para simular un navegador real y evitar bloqueos institucionales
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("Iniciando el rastreo automático de la web de la EIDUM...")

while URLS_POR_VISITAR:
    # Tomamos la siguiente URL de la lista
    url_actual = URLS_POR_VISITAR.pop(0)
    
    if url_actual in URLS_VISITADAS:
        continue
        
    print(f"Raspando: {url_actual}")
    URLS_VISITADAS.add(url_actual)
    
    try:
        # Hacemos la petición web
        response = requests.get(url_actual, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. EXTRAER EL TEXTO PRINCIPAL DE LA PÁGINA ACTUAL
            # En la web de la UMU, el contenido suele estar dentro del div con id 'contenido' o la etiqueta 'main'
            contenido_principal = soup.find('div', id='contenido') or soup.find('div', id='content') or soup.find('main') or soup.body
            
            if contenido_principal:
                # Limpiamos el texto eliminando espacios en blanco extra y saltos de línea repetidos
                texto_limpio = ' '.join(contenido_principal.get_text(separator=' ').split())
                
                # Solo guardamos la página si realmente tiene contenido útil
                if len(texto_limpio) > 100:
                    conocimiento.append({
                        "url": url_actual,
                        "texto": texto_limpio[:5000] # Guardamos hasta 5000 caracteres por subpágina
                    })
            
            # 2. ENCONTRAR NUEVOS ENLACES (SUBPÁGINAS)
            for enlace in soup.find_all('a', href=True):
                href = enlace['href']
                # Construimos la URL absoluta por si el enlace es relativo (ej: "/web/eidum/matricula")
                url_absoluta = urljoin(url_actual, href)
                
                # Reglas estrictas para que el robot no se salga de la web oficial de la EIDUM
                if "web/eidum" in url_absoluta and url_absoluta not in URLS_VISITADAS and url_absoluta not in URLS_POR_VISITAR:
                    # Evitamos rastrear enlaces a archivos pesados (PDFs, ZIPs, etc.) directos en este JSON
                    if not any(url_absoluta.lower().endswith(ext) for ext in ['.pdf', '.zip', '.rar', '.doc', '.docx', '.jpg', '.png']):
                        # Limpiamos posibles fragmentos de la URL (ej: #seccion1) para no repetir páginas
                        url_limpia = url_absoluta.split('#')[0]
                        if url_limpia not in URLS_VISITADAS and url_limpia not in URLS_POR_VISITAR:
                            URLS_POR_VISITAR.append(url_limpia)
                            
        # Pequeña pausa de seguridad de medio segundo para no saturar el servidor institucional
        time.sleep(0.5)
        
    except Exception as e:
        print(f"Error al procesar {url_actual}: {e}")

# Guardamos todo el almacén de datos estructurado en tu archivo JSON
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(conocimiento, f, ensure_ascii=False, indent=2)

print(f"\n¡Proceso finalizado! Se han rastreado con éxito {len(conocimiento)} subpáginas de la EIDUM.")
print("El archivo 'data.json' ya no estará vacío y está listo para subirse a GitHub.")
