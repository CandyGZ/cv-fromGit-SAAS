import os
import sys
import requests

def main():
    print("="*60)
    print("CLIENTE DE GENERACIÓN DE CV")
    print("="*60)

    # Obtener variables de entorno
    github_token = os.environ.get('INPUT_GITHUB_TOKEN') or os.environ.get('GITHUB_TOKEN')
    api_url = os.environ.get('INPUT_API_URL') or os.environ.get('API_URL')
    api_key = os.environ.get('INPUT_API_KEY') or os.environ.get('API_KEY')
    openai_api_key = os.environ.get('INPUT_OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')
    
    if not github_token:
        print("Error: GITHUB_TOKEN es requerido")
        sys.exit(1)
        
    if not api_url:
        # Fallback temporal para pruebas locales o si no se define
        print("Warning: API_URL no definida. Asegúrate de configurarla en la Action.")
        sys.exit(1)

    # Asegurar que la URL termine en /api/generate
    if not api_url.endswith('/api/generate'):
        api_url = api_url.rstrip('/') + '/api/generate'

    print(f"Conectando a: {api_url}")

    try:
        payload = {
            "github_token": github_token,
            "api_key": api_key,
            "openai_api_key": openai_api_key
        }
        
        response = requests.post(api_url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            markdown_content = data.get('markdown')
            
            if markdown_content:
                with open('cv.md', 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                print("✓ cv.md generado exitosamente")
            else:
                print("Error: La respuesta no contiene el CV")
                sys.exit(1)
        else:
            print(f"Error del servidor: {response.status_code}")
            print(response.text)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error de conexión: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
