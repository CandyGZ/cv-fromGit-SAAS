from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import sys
import copy
from datetime import datetime
from collections import Counter
from github import Github
import json

# Importar OpenAI de forma opcional
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

app = FastAPI()

class CVRequest(BaseModel):
    github_token: str
    api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    username: Optional[str] = None

class GitHubCVGenerator:
    def __init__(self, github_token, username=None, openai_api_key=None):
        self.github = Github(github_token)
        self.user = self.github.get_user(username) if username else self.github.get_user()
        self.openai_client = None
        self.use_ai = False
        if OPENAI_AVAILABLE and openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=openai_api_key)
                self.use_ai = True
            except Exception as e:
                print(f"Warning: OpenAI error: {e}")

    def _format_date(self, date_obj, format_str='%Y-%m-%d'):
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            except:
                return date_obj
        if hasattr(date_obj, 'strftime'):
            return date_obj.strftime(format_str)
        return str(date_obj)

    def _enhance_description_with_ai(self, repo_name, original_description, languages, technologies, readme_content=None):
        if not self.use_ai or not self.openai_client:
            return original_description

        try:
            readme_info = ""
            if readme_content:
                readme_info = f"\n- README (extracto): {readme_content}"

            if not original_description or original_description == "Sin descripción":
                prompt = f"""Eres un experto redactor de CVs técnicos. Genera una descripción profesional y completa para un proyecto llamado "{repo_name}".
Información del proyecto:
- Lenguajes: {', '.join(languages) if languages else 'No especificado'}
- Tecnologías: {', '.join(technologies) if technologies else 'No especificado'}{readme_info}

La descripción debe:
1. Ser técnica pero accesible (2-3 frases)
2. Destacar el propósito y valor del proyecto
3. Mencionar las tecnologías clave y características principales
4. Incluir detalles técnicos relevantes del README si están disponibles
5. Estar en español
6. No incluir palabras como "Este proyecto" o "Este repositorio"
7. IMPORTANTE: Por privacidad de clientes, NO mencionar nombres específicos de empresas o clientes. Usar descripciones genéricas.

Responde SOLO con la descripción, sin explicaciones adicionales."""
            else:
                prompt = f"""Eres un experto redactor de CVs técnicos. Genera una descripción profesional y completa para un proyecto de CV.
Proyecto: {repo_name}
Descripción original: {original_description}
Lenguajes: {', '.join(languages) if languages else 'No especificado'}
Tecnologías: {', '.join(technologies) if technologies else 'No especificado'}{readme_info}

Genera una descripción que:
1. Sea profesional y atractiva (2-3 frases)
2. Destaque el valor, propósito y características técnicas del proyecto
3. Mencione tecnologías clave y funcionalidades principales
4. Aproveche la información del README para dar detalles técnicos relevantes
5. Esté en español
6. Sea completa pero concisa
7. IMPORTANTE: Por privacidad de clientes, NO mencionar nombres específicos de empresas o clientes. Reemplaza con descripciones genéricas.

Responde SOLO con la descripción mejorada, sin explicaciones adicionales."""

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto redactor de CVs técnicos."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            enhanced_description = response.choices[0].message.content.strip()
            return enhanced_description.strip('"').strip("'")
        except Exception as e:
            return original_description

    def get_repositories(self):
        repos = []
        for repo in self.user.get_repos():
            if not repo.fork:
                repos.append(repo)
        return repos

    def _get_readme_content(self, repo):
        try:
            readme_files = ['README.md', 'readme.md', 'README.MD', 'README', 'Readme.md']
            for readme_name in readme_files:
                try:
                    readme = repo.get_contents(readme_name)
                    content = readme.decoded_content.decode('utf-8')
                    if len(content) > 1500:
                        content = content[:1500] + "..."
                    return content
                except:
                    continue
            return None
        except:
            return None

    def analyze_repository(self, repo):
        languages = repo.get_languages()
        technologies = self._detect_technologies(repo)
        try:
            commits_count = repo.get_commits().totalCount
        except:
            commits_count = 0
        
        original_description = repo.description or 'Sin descripción'
        readme_content = self._get_readme_content(repo)
        
        enhanced_description = self._enhance_description_with_ai(
            repo_name=repo.name,
            original_description=original_description,
            languages=list(languages.keys()),
            technologies=technologies,
            readme_content=readme_content
        )

        return {
            'name': repo.name,
            'description': enhanced_description,
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
        technologies = set()
        try:
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
            contents = repo.get_contents("")
            for content in contents:
                if content.name in tech_files:
                    technologies.update(tech_files[content.name])
                if content.name == 'package.json':
                    try:
                        pkg_content = repo.get_contents('package.json').decoded_content
                        pkg_json = json.loads(pkg_content)
                        dependencies = {**pkg_json.get('dependencies', {}), **pkg_json.get('devDependencies', {})}
                        if 'react' in dependencies: technologies.add('React')
                        if 'vue' in dependencies: technologies.add('Vue.js')
                        if 'angular' in dependencies or '@angular/core' in dependencies: technologies.add('Angular')
                        if 'express' in dependencies: technologies.add('Express.js')
                        if 'next' in dependencies: technologies.add('Next.js')
                        if 'typescript' in dependencies: technologies.add('TypeScript')
                    except: pass
                elif content.name == 'requirements.txt':
                    try:
                        req_content = repo.get_contents('requirements.txt').decoded_content.decode()
                        if 'django' in req_content.lower(): technologies.add('Django')
                        if 'flask' in req_content.lower(): technologies.add('Flask')
                        if 'fastapi' in req_content.lower(): technologies.add('FastAPI')
                        if 'tensorflow' in req_content.lower(): technologies.add('TensorFlow')
                        if 'pytorch' in req_content.lower(): technologies.add('PyTorch')
                        if 'pandas' in req_content.lower(): technologies.add('Pandas')
                        if 'numpy' in req_content.lower(): technologies.add('NumPy')
                    except: pass
        except Exception:
            pass
        return list(technologies)

    def generate_cv_data(self):
        repos = self.get_repositories()
        analyzed_repos = []
        all_languages = Counter()
        all_technologies = set()

        for repo in repos:
            repo_data = self.analyze_repository(repo)
            analyzed_repos.append(repo_data)
            for lang, bytes_count in repo_data['languages'].items():
                all_languages[lang] += bytes_count
            all_technologies.update(repo_data['technologies'])

        analyzed_repos.sort(key=lambda x: x['updated_at'], reverse=True)
        total_bytes = sum(all_languages.values())
        language_percentages = {
            lang: round((bytes_count / total_bytes) * 100, 2)
            for lang, bytes_count in all_languages.most_common()
        }

        return {
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

    def generate_markdown_cv(self, cv_data):
        user = cv_data['user']
        md_content = f"""# {user['name']}

**GitHub**: [@{user['login']}](https://github.com/{user['login']})
"""
        if user['location']: md_content += f"**Ubicación**: {user['location']}  \n"
        if user['email']: md_content += f"**Email**: {user['email']}  \n"
        if user['blog']: md_content += f"**Website**: {user['blog']}  \n"

        md_content += f"\n**Repositorios públicos**: {user['public_repos']} | **Seguidores**: {user['followers']}\n\n"

        if user['bio']: md_content += f"## Sobre mí\n\n{user['bio']}\n\n"

        md_content += "## Lenguajes de Programación\n\n"
        for lang, percentage in list(cv_data['languages'].items())[:10]:
            md_content += f"- **{lang}**: {percentage}%\n"

        if cv_data['technologies']:
            md_content += "\n## Tecnologías y Herramientas\n\n"
            md_content += ", ".join(cv_data['technologies'])
            md_content += "\n"

        md_content += "\n## Proyectos Destacados\n\n"

        # LIMIT INCREASED TO 100
        for repo in cv_data['repositories'][:100]:
            md_content += f"### [{repo['name']}]({repo['url']})\n\n"
            md_content += f"{repo['description']}\n\n"
            if repo['languages']:
                langs = ', '.join(repo['languages'].keys())
                md_content += f"**Lenguajes**: {langs}  \n"
            if repo['technologies']:
                techs = ', '.join(repo['technologies'])
                md_content += f"**Tecnologías**: {techs}  \n"
            if repo['stars'] > 0:
                md_content += f"⭐ {repo['stars']} estrellas  \n"
            md_content += "\n---\n\n"

        md_content += f"\n*CV generado automáticamente desde GitHub*\n"
        return md_content

@app.get("/")
def read_root():
    return {"status": "ok", "message": "CV Generator API is running"}

@app.post("/api/generate")
def generate_cv(request: CVRequest):
    # Validación de API Key (Simple para MVP)
    # En producción, esto debería verificar una base de datos
    valid_keys = os.environ.get('ACCEPTED_API_KEYS', '').split(',')
    if valid_keys and valid_keys != [''] and request.api_key not in valid_keys:
        raise HTTPException(status_code=403, detail="Invalid API Key. Please purchase a license.")

    try:
        generator = GitHubCVGenerator(request.github_token, request.username, request.openai_api_key)
        cv_data = generator.generate_cv_data()
        markdown_cv = generator.generate_markdown_cv(cv_data)
        return {"markdown": markdown_cv}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
