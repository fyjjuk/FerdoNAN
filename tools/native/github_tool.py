#!/usr/bin/env python3
"""
Herramienta nativa para interactuar con GitHub API.
Soporta: list repos, create PR, list PRs, list issues, create issue
"""

import os
import json
import sys
from typing import Dict, Any, List, Optional

try:
    from github import Github, GithubException
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False


def get_github_client():
    """Obtiene cliente autenticado de GitHub."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN no configurada en variables de entorno")
    return Github(token)


def list_repos(limit: int = 10) -> List[Dict]:
    """Lista repositorios del usuario autenticado."""
    if not GITHUB_AVAILABLE:
        return [{"error": "PyGithub no instalado"}]
    
    client = get_github_client()
    repos = []
    for repo in client.get_user().get_repos()[:limit]:
        repos.append({
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "url": repo.html_url,
            "stars": repo.stargazers_count,
            "language": repo.language
        })
    return repos


def list_pull_requests(repo_name: str, state: str = "open") -> List[Dict]:
    """Lista pull requests de un repositorio."""
    if not GITHUB_AVAILABLE:
        return [{"error": "PyGithub no instalado"}]
    
    client = get_github_client()
    repo = client.get_repo(repo_name)
    prs = []
    for pr in repo.get_pulls(state=state):
        prs.append({
            "number": pr.number,
            "title": pr.title,
            "user": pr.user.login,
            "state": pr.state,
            "created_at": pr.created_at.isoformat(),
            "url": pr.html_url,
            "additions": pr.additions,
            "deletions": pr.deletions
        })
    return prs


def create_pull_request(repo_name: str, title: str, body: str, 
                        head: str, base: str = "main") -> Dict:
    """Crea un nuevo pull request."""
    if not GITHUB_AVAILABLE:
        return {"error": "PyGithub no instalado"}
    
    client = get_github_client()
    repo = client.get_repo(repo_name)
    try:
        pr = repo.create_pull(title=title, body=body, head=head, base=base)
        return {
            "success": True,
            "number": pr.number,
            "url": pr.html_url,
            "message": f"PR #{pr.number} creado exitosamente"
        }
    except GithubException as e:
        return {"success": False, "error": str(e)}


def list_issues(repo_name: str, state: str = "open") -> List[Dict]:
    """Lista issues de un repositorio."""
    if not GITHUB_AVAILABLE:
        return [{"error": "PyGithub no instalado"}]
    
    client = get_github_client()
    repo = client.get_repo(repo_name)
    issues = []
    for issue in repo.get_issues(state=state):
        issues.append({
            "number": issue.number,
            "title": issue.title,
            "user": issue.user.login,
            "state": issue.state,
            "created_at": issue.created_at.isoformat(),
            "url": issue.html_url,
            "comments": issue.comments
        })
    return issues


def create_issue(repo_name: str, title: str, body: str, 
                 labels: List[str] = None) -> Dict:
    """Crea un nuevo issue."""
    if not GITHUB_AVAILABLE:
        return {"error": "PyGithub no instalado"}
    
    client = get_github_client()
    repo = client.get_repo(repo_name)
    try:
        issue = repo.create_issue(title=title, body=body, labels=labels or [])
        return {
            "success": True,
            "number": issue.number,
            "url": issue.html_url,
            "message": f"Issue #{issue.number} creado exitosamente"
        }
    except GithubException as e:
        return {"success": False, "error": str(e)}


def run(input_data: Dict[str, Any]) -> Dict:
    """Punto de entrada para la herramienta nativa."""
    action = input_data.get("action", "list_repos")
    repo_name = input_data.get("repo_name")
    
    if action == "list_repos":
        limit = input_data.get("limit", 10)
        return {"repos": list_repos(limit)}
    
    elif action == "list_prs":
        if not repo_name:
            return {"error": "Se requiere repo_name"}
        state = input_data.get("state", "open")
        return {"pull_requests": list_pull_requests(repo_name, state)}
    
    elif action == "create_pr":
        if not all([repo_name, input_data.get("title"), input_data.get("head")]):
            return {"error": "Se requiere repo_name, title y head"}
        return create_pull_request(
            repo_name, 
            input_data["title"], 
            input_data.get("body", ""),
            input_data["head"],
            input_data.get("base", "main")
        )
    
    elif action == "list_issues":
        if not repo_name:
            return {"error": "Se requiere repo_name"}
        state = input_data.get("state", "open")
        return {"issues": list_issues(repo_name, state)}
    
    elif action == "create_issue":
        if not all([repo_name, input_data.get("title")]):
            return {"error": "Se requiere repo_name y title"}
        return create_issue(
            repo_name,
            input_data["title"],
            input_data.get("body", ""),
            input_data.get("labels", [])
        )
    
    else:
        return {"error": f"Acción desconocida: {action}"}


if __name__ == "__main__":
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    result = run(args)
    print(json.dumps(result, indent=2))
