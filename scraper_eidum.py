import requests
from bs4 import BeautifulSoup
import json

# Lista de URLs de la web de las que quieres que beba el chatbot
URLS = [
    "https://www.um.es/web/eidum/..." # Añade aquí las páginas clave
]

conocimiento = []

for url in URLS:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Intentamos capturar solo el cuerpo del texto principal 
            # (evitando menús de navegación, headers y footers)
            # Ajusta el id o la clase según la estructura de la web
            contenido_principal = soup.find('div', id='content') or soup.find('main') or soup.body
            
            if contenido_principal:
                texto_limpio = ' '.join(contenido_principal.get_text(separator=' ').split())
                
                conocimiento.append({
                    "url": url,
                    "texto": texto_limpio[:4000] # Limitamos caracteres por seguridad de contexto
                })
    except Exception as e:
        print(f"Error al raspar {url}: {e}")

# Guardamos el resultado en el JSON que leerá el chatbot
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(conocimiento, f, ensure_ascii=False, indent=2)

print("¡Conocimiento actualizado con éxito!")
