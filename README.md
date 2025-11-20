# 🚀 GitHub CV Generator (SaaS Edition)

Genera automáticamente un CV profesional analizando tus repositorios de GitHub. Este servicio SaaS utiliza Inteligencia Artificial para crear descripciones atractivas de tus proyectos.

## 📖 Guía Rápida para Clientes

Para usar este generador en tu perfil de GitHub, solo necesitas agregar un archivo de workflow.

### 1. Requisitos Previos

Necesitas una **API Key** para usar este servicio.
- Contacta a [Candy García Zárate](https://github.com/CandyGZ) para adquirir tu licencia.

### 2. Instalación en tu Repositorio

1.  En tu repositorio (puede ser tu repositorio de perfil `username/username` o cualquier otro), crea un archivo en: `.github/workflows/update-cv.yml`
2.  Copia y pega el siguiente contenido:

```yaml
name: Update CV

on:
  # Permite ejecutarlo manualmente desde la pestaña Actions
  workflow_dispatch:

permissions:
  contents: write

jobs:
  generate-cv:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Generate CV
        uses: CandyGZ/cv-fromGit-SAAS@main
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          api_url: "https://cv-from-git-saas.vercel.app" # O la URL que te proporcionen
          api_key: ${{ secrets.CV_API_KEY }} # Tu clave comprada

      - name: Commit and Push CV
        run: |
          git config --global user.name 'GitHub Actions'
          git config --global user.email 'actions@github.com'
          git add cv.md
          git commit -m "Update CV [skip ci]" || echo "No changes to commit"
          git push
```

### 3. Configurar Secretos

Para mantener tu API Key segura:

1.  Ve a tu repositorio en GitHub.
2.  Clic en **Settings** > **Secrets and variables** > **Actions**.
3.  Clic en **New repository secret**.
4.  Nombre: `CV_API_KEY`
5.  Valor: (Pega aquí la clave que compraste).
6.  Clic en **Add secret**.

¡Listo! Ahora puedes actualizar tu CV manualmente cuando lo necesites.

## ⚙️ Inputs de la Action

| Input | Descripción | Requerido |
|-------|-------------|-----------|
| `github_token` | Token de GitHub (usa `${{ secrets.GITHUB_TOKEN }}`) | Sí |
| `api_url` | URL del servicio SaaS | Sí |
| `api_key` | Tu licencia de uso | Sí |
| `openai_api_key` | (Opcional) Tu propia key de OpenAI si deseas usar tu cuota | No |

## 📄 Resultado

La acción generará un archivo `cv.md` en la raíz de tu repositorio con tu CV profesional actualizado.
