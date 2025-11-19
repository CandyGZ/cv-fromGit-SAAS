#!/usr/bin/env python3
"""
GitHub CV Generator
Analiza repositorios de GitHub y genera un CV automático
"""

import os
import sys
import copy
from datetime import datetime
from collections import Counter
from github import Github
import json

class GitHubCVGenerator:
    def __init__(self, github_token, username=None):
        """
        Inicializa el generador de CV

        Args:
            github_token: Token de acceso personal de GitHub
            username: Usuario de GitHub (opcional, usa el usuario autenticado si no se proporciona)
        """
        self.github = Github(github_token)
        self.user = self.github.get_user(username) if username else self.github.get_user()

    @staticmethod
    def _format_date(date_obj, format_str='%Y-%m-%d'):
        """
        Formatea una fecha que puede ser string o datetime object

        Args:
            date_obj: String ISO o datetime object
            format_str: Formato de salida

        Returns:
            String con la fecha formateada
        """
        if isinstance(date_obj, str):
            # Si es string, parsearlo a datetime primero
            try:
                date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            except:
                return date_obj  # Si falla, devolver el string original

        # Si es datetime, formatearlo
        if hasattr(date_obj, 'strftime'):
            return date_obj.strftime(format_str)

        return str(date_obj)  # Fallback

    def get_repositories(self):
        """Obtiene todos los repositorios públicos del usuario (sin forks)"""
        repos = []
        for repo in self.user.get_repos():
            if not repo.fork:
                repos.append(repo)
        return repos

    def analyze_repository(self, repo):
        """
        Analiza un repositorio y extrae información relevante

        Returns:
            dict: Información del repositorio
        """
        # Obtener lenguajes
        languages = repo.get_languages()

        # Obtener tecnologías basadas en archivos
        technologies = self._detect_technologies(repo)

        # Calcular estadísticas
        try:
            commits_count = repo.get_commits().totalCount
        except:
            commits_count = 0

        return {
            'name': repo.name,
            'description': repo.description or 'Sin descripción',
            'url': repo.html_url,
            'created_at': repo.created_at,
            'updated_at': repo.updated_at,
            'languages': languages,
            'technologies': technologies,
            'stars': repo.stargazers_count,
            'commits': commits_count,
            'topics': repo.get_topics()
        }

    def _detect_technologies(self, repo):
        """Detecta tecnologías basándose en archivos en el repositorio"""
        technologies = set()

        try:
            # Mapeo de archivos a tecnologías
            tech_files = {
                'package.json': ['Node.js', 'npm'],
                'requirements.txt': ['Python', 'pip'],
                'Pipfile': ['Python', 'pipenv'],
                'pom.xml': ['Java', 'Maven'],
                'build.gradle': ['Java', 'Gradle'],
                'Cargo.toml': ['Rust', 'Cargo'],
                'go.mod': ['Go'],
                'composer.json': ['PHP', 'Composer'],
                'Gemfile': ['Ruby', 'Bundler'],
                'Dockerfile': ['Docker'],
                'docker-compose.yml': ['Docker Compose'],
                '.github/workflows': ['GitHub Actions'],
                'terraform': ['Terraform'],
                'ansible': ['Ansible'],
                'kubernetes': ['Kubernetes'],
                'k8s': ['Kubernetes']
            }

            # Frameworks específicos
            contents = repo.get_contents("")
            for content in contents:
                if content.name in tech_files:
                    technologies.update(tech_files[content.name])

                # Detectar frameworks específicos
                if content.name == 'package.json':
                    try:
                        pkg_content = repo.get_contents('package.json').decoded_content
                        pkg_json = json.loads(pkg_content)
                        dependencies = {**pkg_json.get('dependencies', {}),
                                      **pkg_json.get('devDependencies', {})}

                        if 'react' in dependencies:
                            technologies.add('React')
                        if 'vue' in dependencies:
                            technologies.add('Vue.js')
                        if 'angular' in dependencies or '@angular/core' in dependencies:
                            technologies.add('Angular')
                        if 'express' in dependencies:
                            technologies.add('Express.js')
                        if 'next' in dependencies:
                            technologies.add('Next.js')
                        if 'typescript' in dependencies:
                            technologies.add('TypeScript')
                    except:
                        pass

                elif content.name == 'requirements.txt':
                    try:
                        req_content = repo.get_contents('requirements.txt').decoded_content.decode()
                        if 'django' in req_content.lower():
                            technologies.add('Django')
                        if 'flask' in req_content.lower():
                            technologies.add('Flask')
                        if 'fastapi' in req_content.lower():
                            technologies.add('FastAPI')
                        if 'tensorflow' in req_content.lower():
                            technologies.add('TensorFlow')
                        if 'pytorch' in req_content.lower():
                            technologies.add('PyTorch')
                        if 'pandas' in req_content.lower():
                            technologies.add('Pandas')
                        if 'numpy' in req_content.lower():
                            technologies.add('NumPy')
                    except:
                        pass

        except Exception as e:
            # Ignorar errores en repositorios vacíos o sin acceso
            if "404" in str(e) or "empty" in str(e).lower():
                pass  # Repositorio vacío, es normal
            else:
                print(f"  [Warning] No se pudieron detectar tecnologías: {e}")

        return list(technologies)

    def generate_cv_data(self):
        """Genera los datos del CV analizando todos los repositorios"""
        print(f"Analizando repositorios de {self.user.login}...")

        repos = self.get_repositories()
        print(f"Encontrados {len(repos)} repositorios (sin forks)")

        analyzed_repos = []
        all_languages = Counter()
        all_technologies = set()

        for repo in repos:
            print(f"  Analizando: {repo.name}")
            repo_data = self.analyze_repository(repo)
            analyzed_repos.append(repo_data)

            # Acumular lenguajes y tecnologías
            for lang, bytes_count in repo_data['languages'].items():
                all_languages[lang] += bytes_count
            all_technologies.update(repo_data['technologies'])

        # Ordenar repositorios por fecha de actualización
        analyzed_repos.sort(key=lambda x: x['updated_at'], reverse=True)

        # Calcular porcentajes de lenguajes
        total_bytes = sum(all_languages.values())
        language_percentages = {
            lang: round((bytes_count / total_bytes) * 100, 2)
            for lang, bytes_count in all_languages.most_common()
        }

        cv_data = {
            'user': {
                'name': self.user.name or self.user.login,
                'login': self.user.login,
                'bio': self.user.bio,
                'location': self.user.location,
                'email': self.user.email,
                'blog': self.user.blog,
                'avatar_url': self.user.avatar_url,
                'public_repos': self.user.public_repos,
                'followers': self.user.followers,
                'following': self.user.following,
            },
            'repositories': analyzed_repos,
            'languages': language_percentages,
            'technologies': sorted(list(all_technologies)),
            'generated_at': datetime.now().isoformat()
        }

        return cv_data

    def generate_markdown_cv(self, cv_data, output_file='CV.md'):
        """Genera el CV en formato Markdown"""
        user = cv_data['user']

        md_content = f"""# {user['name']}

**GitHub**: [@{user['login']}](https://github.com/{user['login']})
"""

        if user['location']:
            md_content += f"**Ubicación**: {user['location']}  \n"
        if user['email']:
            md_content += f"**Email**: {user['email']}  \n"
        if user['blog']:
            md_content += f"**Website**: {user['blog']}  \n"

        md_content += f"\n**Repositorios públicos**: {user['public_repos']} | **Seguidores**: {user['followers']}\n\n"

        if user['bio']:
            md_content += f"## Sobre mí\n\n{user['bio']}\n\n"

        # Lenguajes de programación
        md_content += "## Lenguajes de Programación\n\n"
        for lang, percentage in list(cv_data['languages'].items())[:10]:
            md_content += f"- **{lang}**: {percentage}%\n"

        # Tecnologías y herramientas
        if cv_data['technologies']:
            md_content += "\n## Tecnologías y Herramientas\n\n"
            md_content += ", ".join(cv_data['technologies'])
            md_content += "\n"

        # Proyectos destacados
        md_content += "\n## Proyectos Destacados\n\n"

        # Mostrar top 10 proyectos más recientes
        for repo in cv_data['repositories'][:10]:
            md_content += f"### [{repo['name']}]({repo['url']})\n\n"
            md_content += f"{repo['description']}\n\n"

            if repo['languages']:
                langs = ', '.join(repo['languages'].keys())
                md_content += f"**Lenguajes**: {langs}  \n"

            if repo['technologies']:
                techs = ', '.join(repo['technologies'])
                md_content += f"**Tecnologías**: {techs}  \n"

            md_content += f"**Última actualización**: {self._format_date(repo['updated_at'])}  \n"

            if repo['stars'] > 0:
                md_content += f"⭐ {repo['stars']} estrellas  \n"

            md_content += "\n---\n\n"

        md_content += f"\n*CV generado automáticamente desde GitHub - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"✓ CV en Markdown generado: {output_file}")

    def generate_html_cv(self, cv_data, output_file='CV.html'):
        """Genera el CV en formato HTML"""
        user = cv_data['user']

        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV - {user['name']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}

        header {{
            text-align: center;
            padding: 40px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            margin-bottom: 30px;
        }}

        .avatar {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            border: 5px solid white;
            margin-bottom: 20px;
        }}

        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .contact-info {{
            margin: 20px 0;
            font-size: 1.1em;
        }}

        .contact-info a {{
            color: white;
            text-decoration: none;
            margin: 0 10px;
        }}

        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 20px;
        }}

        .stat {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 2em;
            font-weight: bold;
        }}

        section {{
            margin: 40px 0;
        }}

        h2 {{
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}

        .bio {{
            font-size: 1.2em;
            color: #555;
            font-style: italic;
            padding: 20px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }}

        .skills {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .skill {{
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
        }}

        .language-bar {{
            margin: 15px 0;
        }}

        .language-name {{
            font-weight: bold;
            margin-bottom: 5px;
        }}

        .bar {{
            background: #e0e0e0;
            height: 25px;
            border-radius: 12px;
            overflow: hidden;
        }}

        .bar-fill {{
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            display: flex;
            align-items: center;
            padding-left: 10px;
            color: white;
            font-size: 0.85em;
            font-weight: bold;
        }}

        .project {{
            background: #f8f9fa;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}

        .project h3 {{
            color: #333;
            margin-bottom: 10px;
        }}

        .project h3 a {{
            color: #667eea;
            text-decoration: none;
        }}

        .project h3 a:hover {{
            text-decoration: underline;
        }}

        .project-description {{
            color: #555;
            margin-bottom: 15px;
        }}

        .project-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            font-size: 0.9em;
            color: #666;
        }}

        .project-meta strong {{
            color: #333;
        }}

        .stars {{
            color: #f39c12;
        }}

        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid #ddd;
            margin-top: 40px;
        }}

        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <img src="{user['avatar_url']}" alt="{user['name']}" class="avatar">
            <h1>{user['name']}</h1>
            <div class="contact-info">
                <a href="https://github.com/{user['login']}" target="_blank">@{user['login']}</a>
"""

        if user['location']:
            html_content += f"                <span>📍 {user['location']}</span>\n"
        if user['email']:
            html_content += f"                <a href='mailto:{user['email']}'>📧 {user['email']}</a>\n"
        if user['blog']:
            html_content += f"                <a href='{user['blog']}' target='_blank'>🌐 Website</a>\n"

        html_content += f"""            </div>
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{user['public_repos']}</div>
                    <div>Repositorios</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{user['followers']}</div>
                    <div>Seguidores</div>
                </div>
            </div>
        </header>
"""

        if user['bio']:
            html_content += f"""        <section>
            <h2>Sobre mí</h2>
            <p class="bio">{user['bio']}</p>
        </section>
"""

        # Lenguajes
        html_content += """        <section>
            <h2>Lenguajes de Programación</h2>
"""

        for lang, percentage in list(cv_data['languages'].items())[:10]:
            html_content += f"""            <div class="language-bar">
                <div class="language-name">{lang}</div>
                <div class="bar">
                    <div class="bar-fill" style="width: {percentage}%">{percentage}%</div>
                </div>
            </div>
"""

        html_content += """        </section>
"""

        # Tecnologías
        if cv_data['technologies']:
            html_content += """        <section>
            <h2>Tecnologías y Herramientas</h2>
            <div class="skills">
"""
            for tech in cv_data['technologies']:
                html_content += f"""                <span class="skill">{tech}</span>
"""
            html_content += """            </div>
        </section>
"""

        # Proyectos
        html_content += """        <section>
            <h2>Proyectos Destacados</h2>
"""

        for repo in cv_data['repositories'][:10]:
            html_content += f"""            <div class="project">
                <h3><a href="{repo['url']}" target="_blank">{repo['name']}</a></h3>
                <p class="project-description">{repo['description']}</p>
                <div class="project-meta">
"""

            if repo['languages']:
                langs = ', '.join(repo['languages'].keys())
                html_content += f"""                    <span><strong>Lenguajes:</strong> {langs}</span>
"""

            if repo['technologies']:
                techs = ', '.join(repo['technologies'])
                html_content += f"""                    <span><strong>Tecnologías:</strong> {techs}</span>
"""

            html_content += f"""                    <span><strong>Actualizado:</strong> {self._format_date(repo['updated_at'])}</span>
"""

            if repo['stars'] > 0:
                html_content += f"""                    <span class="stars">⭐ {repo['stars']} estrellas</span>
"""

            html_content += """                </div>
            </div>
"""

        html_content += f"""        </section>

        <footer>
            CV generado automáticamente desde GitHub - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </footer>
    </div>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✓ CV en HTML generado: {output_file}")


def main():
    """Función principal"""
    # Obtener token de GitHub desde variable de entorno
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("Error: Se requiere la variable de entorno GITHUB_TOKEN")
        sys.exit(1)

    # Usuario opcional (si no se proporciona, usa el usuario autenticado)
    username = os.environ.get('GITHUB_USERNAME')

    try:
        # Generar CV
        generator = GitHubCVGenerator(github_token, username)
        cv_data = generator.generate_cv_data()

        # Generar CV en Markdown y HTML primero (usa datetime objects)
        generator.generate_markdown_cv(cv_data)
        generator.generate_html_cv(cv_data)

        # Guardar datos en JSON después (convierte a strings)
        with open('cv_data.json', 'w', encoding='utf-8') as f:
            # Convertir datetime a string para JSON
            cv_data_copy = copy.deepcopy(cv_data)
            for repo in cv_data_copy['repositories']:
                repo['created_at'] = repo['created_at'].isoformat()
                repo['updated_at'] = repo['updated_at'].isoformat()
            json.dump(cv_data_copy, f, indent=2, ensure_ascii=False)

        print("\n✓ ¡CV generado exitosamente!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
