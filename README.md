# 🚀 GitHub CV Generator

Genera automáticamente un CV profesional basado en tus repositorios de GitHub. El sistema analiza todos tus repositorios públicos (excluyendo forks), extrae información relevante sobre lenguajes de programación, tecnologías utilizadas, y genera un CV atractivo en formatos Markdown y HTML.

## ✨ Características

- 📊 **Análisis automático** de todos tus repositorios públicos
- 🚫 **Excluye forks** automáticamente
- 💻 **Detección de lenguajes** y porcentajes de uso
- 🔧 **Detección inteligente de tecnologías** (frameworks, herramientas, etc.)
- 📝 Generación de CV en **Markdown** y **HTML**
- 🎨 **Diseño profesional** y responsive para el CV en HTML
- ⏰ **Ejecución automática diaria** mediante GitHub Actions
- 🔄 **Actualización automática** con commits automáticos

## 🎯 Tecnologías Detectadas

El sistema puede detectar automáticamente:

### Lenguajes de Programación
- Python, JavaScript, TypeScript, Java, Go, Rust, PHP, Ruby, etc.

### Frameworks y Librerías
- **Frontend**: React, Vue.js, Angular, Next.js
- **Backend**: Express.js, Django, Flask, FastAPI
- **Data Science**: TensorFlow, PyTorch, Pandas, NumPy

### Herramientas
- Docker, Docker Compose
- Kubernetes
- GitHub Actions
- Terraform, Ansible
- npm, pip, Maven, Gradle, Cargo, Composer, Bundler

## 🚀 Uso

### Configuración Inicial

1. **Fork este repositorio** o crea uno nuevo con estos archivos

2. **Habilitar GitHub Actions**:
   - Ve a la pestaña "Actions" en tu repositorio
   - Si es la primera vez, haz clic en "I understand my workflows, go ahead and enable them"

3. **Configurar permisos** (importante):
   - Ve a Settings → Actions → General
   - En "Workflow permissions", selecciona "Read and write permissions"
   - Marca "Allow GitHub Actions to create and approve pull requests"
   - Guarda los cambios

4. **Ejecutar manualmente** (primera vez):
   - Ve a Actions → "Generate CV from GitHub"
   - Haz clic en "Run workflow"
   - Selecciona la rama y ejecuta

### Ejecución Local

Si deseas generar el CV localmente:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar token de GitHub
export GITHUB_TOKEN="tu_token_de_github"

# Opcionalmente, especificar un usuario diferente
export GITHUB_USERNAME="usuario_de_github"

# Ejecutar el generador
python generate_cv.py
```

**Nota**: Para obtener un token de GitHub:
1. Ve a Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Genera un nuevo token con el scope `public_repo`
3. Copia el token (no podrás verlo de nuevo)

## 📅 Ejecución Automática

El workflow de GitHub Actions está configurado para:

- ✅ Ejecutarse **diariamente a las 00:00 UTC**
- ✅ Ejecutarse **manualmente** cuando lo desees
- ✅ Ejecutarse al hacer **push a main/master**

Puedes modificar la frecuencia editando el archivo `.github/workflows/generate-cv.yml`:

```yaml
schedule:
  - cron: '0 0 * * *'  # Diario a las 00:00 UTC
  # - cron: '0 0 * * 1'  # Semanal (cada lunes)
  # - cron: '0 0 1 * *'  # Mensual (día 1 de cada mes)
```

## 📄 Archivos Generados

El script genera tres archivos:

1. **CV.md**: Curriculum en formato Markdown
   - Ideal para GitHub, fácil de leer en texto plano
   - Compatible con cualquier visor de Markdown

2. **CV.html**: Curriculum en formato HTML
   - Diseño profesional y atractivo
   - Responsive (se adapta a móviles)
   - Listo para imprimir o publicar

3. **cv_data.json**: Datos en formato JSON
   - Contiene toda la información estructurada
   - Útil para procesamiento adicional o debugging

## 🎨 Personalización

### Modificar el diseño del CV en HTML

Edita el método `generate_html_cv()` en `generate_cv.py` para personalizar:
- Colores (cambia el gradient en el CSS)
- Fuentes
- Estructura de secciones
- Información mostrada

### Añadir más detecciones de tecnologías

Edita el método `_detect_technologies()` en `generate_cv.py` para añadir:
- Más archivos de configuración
- Frameworks específicos
- Herramientas personalizadas

### Filtrar repositorios

Puedes modificar `get_repositories()` para filtrar repositorios por:
- Lenguaje principal
- Estrellas mínimas
- Fecha de actualización
- Topics específicos

## 📊 Ejemplo de Salida

El CV generado incluye:

- ✅ Información personal (nombre, ubicación, contacto)
- ✅ Estadísticas de GitHub (repos, seguidores)
- ✅ Lenguajes de programación con porcentajes
- ✅ Tecnologías y herramientas utilizadas
- ✅ Proyectos destacados con descripciones
- ✅ Última fecha de actualización de cada proyecto

## 🔧 Solución de Problemas

### El workflow no se ejecuta automáticamente

1. Verifica que GitHub Actions esté habilitado
2. Asegúrate de tener permisos de escritura configurados
3. Revisa la pestaña Actions para ver errores

### Error: "Resource not accessible by integration"

- Ve a Settings → Actions → General
- Habilita "Read and write permissions"

### El CV no se actualiza

- Verifica que hay cambios en tus repositorios
- Ejecuta manualmente el workflow para probar
- Revisa los logs en Actions

### Error al instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 📝 Licencia

MIT License - Siéntete libre de usar, modificar y compartir.

## 🤝 Contribuciones

Las contribuciones son bienvenidas:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 💡 Ideas para Mejoras

- [ ] Soporte para más formatos (PDF, LaTeX)
- [ ] Análisis de contribuciones a proyectos
- [ ] Gráficos y visualizaciones
- [ ] Múltiples plantillas de diseño
- [ ] Soporte para múltiples idiomas
- [ ] Integración con LinkedIn
- [ ] Análisis de commits y actividad

## 📧 Contacto

Si tienes preguntas o sugerencias, abre un issue en este repositorio.

---

*Generado con ❤️ por GitHub CV Generator*
