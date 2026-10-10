import re
from typing import Dict, List, Set, Tuple

# Comprehensive taxonomy and canonical mapping
SKILL_SYNONYMS: Dict[str, str] = {
    # Programming Languages
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python": "Python",
    "python3": "Python",
    "golang": "Go",
    "go": "Go",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "java": "Java",
    "ruby": "Ruby",
    "php": "PHP",
    "rust": "Rust",
    "scala": "Scala",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "bash": "Bash",
    "shell": "Shell Scripting",
    "powershell": "PowerShell",
    "r": "R",

    # Frontend Frameworks & Web
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "next": "Next.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "svelte": "Svelte",
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",
    "sass": "Sass",
    "scss": "Sass",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "redux": "Redux",
    "zustand": "Zustand",

    # Backend Frameworks
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "spring boot": "Spring Boot",
    ".net": ".NET",
    "dotnet": ".NET",
    "asp.net": "ASP.NET",
    "rails": "Ruby on Rails",
    "ruby on rails": "Ruby on Rails",
    "graphql": "GraphQL",
    "rest": "REST API",
    "restful": "REST API",
    "rest api": "REST API",
    "grpc": "gRPC",

    # Databases & Caching
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "cassandra": "Cassandra",
    "elasticsearch": "Elasticsearch",
    "dynamodb": "DynamoDB",
    "mariadb": "MariaDB",
    "neo4j": "Neo4j",
    "sql": "SQL",

    # Cloud & DevOps & Infra
    "aws": "Amazon Web Services (AWS)",
    "amazon web services": "Amazon Web Services (AWS)",
    "gcp": "Google Cloud Platform (GCP)",
    "google cloud": "Google Cloud Platform (GCP)",
    "azure": "Microsoft Azure",
    "ms azure": "Microsoft Azure",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "helm": "Helm",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    "linux": "Linux",
    "nginx": "Nginx",

    # AI / ML / Data Science
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "nlp": "Natural Language Processing (NLP)",
    "natural language processing": "Natural Language Processing (NLP)",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    "llm": "Large Language Models (LLM)",
    "llms": "Large Language Models (LLM)",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "keras": "Keras",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "huggingface": "Hugging Face",
    "hugging face": "Hugging Face",
    "transformers": "Transformers",
    "langchain": "LangChain",
    "llama-index": "LlamaIndex",
    "spacy": "spaCy",
    "nltk": "NLTK",
    "spark": "Apache Spark",
    "pyspark": "PySpark",
    "hadoop": "Hadoop",
    "kafka": "Apache Kafka",
    "tableau": "Tableau",
    "power bi": "Power BI",
    "powerbi": "Power BI",

    # Methodologies & Tools
    "git": "Git",
    "agile": "Agile",
    "scrum": "Scrum",
    "jira": "Jira",
    "microservices": "Microservices",
    "system design": "System Design",
    "tdd": "Test-Driven Development (TDD)",
    "unit testing": "Unit Testing",
}

# Pre-compile regex word boundary matches for known skills
_SKILL_PATTERNS = []
for syn, canonical in sorted(SKILL_SYNONYMS.items(), key=lambda x: len(x[0]), reverse=True):
    # Escape special regex chars like ++, #, .
    pattern_str = r'(?<!\w)' + re.escape(syn) + r'(?!\w)'
    if syn in ["c++", "c#", ".net"]:
        # Handle punctuation at boundary
        pattern_str = r'(?<![a-zA-Z0-9])' + re.escape(syn) + r'(?![a-zA-Z0-9])'
    _SKILL_PATTERNS.append((re.compile(pattern_str, re.IGNORECASE), canonical))


def canonicalize_skill(skill: str) -> str:
    """Normalizes a raw skill string to its canonical form if known."""
    cleaned = skill.strip().lower()
    return SKILL_SYNONYMS.get(cleaned, skill.strip())


def extract_skills_from_text(text: str) -> Dict[str, List[str]]:
    """
    Extracts skills from resume text, segmenting explicitly listed skills 
    from skills inferred through work experience or project mentions.
    """
    if not text:
        return {"explicit_skills": [], "inferred_skills": []}

    # Identify potential 'Skills' sections
    explicit_section_pattern = re.compile(
        r'(?:technical skills|skills|core competencies|proficiencies|technologies|tools & technologies)[:\s\n]+(.*?)(?=\n\s*(?:experience|work history|employment|education|projects|certifications|$))',
        re.IGNORECASE | re.DOTALL
    )

    explicit_match = explicit_section_pattern.search(text)
    explicit_text = explicit_match.group(1) if explicit_match else ""

    explicit_skills: Set[str] = set()
    all_skills: Set[str] = set()

    for pattern, canonical in _SKILL_PATTERNS:
        if explicit_text and pattern.search(explicit_text):
            explicit_skills.add(canonical)
        if pattern.search(text):
            all_skills.add(canonical)

    inferred_skills = all_skills - explicit_skills

    # If no distinct skills section was found, treat all detected as explicit to avoid empty lists
    if not explicit_skills and all_skills:
        explicit_skills = all_skills
        inferred_skills = set()

    return {
        "explicit_skills": sorted(list(explicit_skills)),
        "inferred_skills": sorted(list(inferred_skills)),
    }
