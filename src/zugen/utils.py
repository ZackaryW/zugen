import os

def _resolve_path(path: str, useCacher: bool = False):
    if os.path.exists(path):
        return path

    if not useCacher:
        return

    from zuu.usrapp.gh_repo_cache import GhRepoCache

    cache = GhRepoCache()
    return cache.resolve_path_asc(path)

def resolve_path(path: str, useCacher: bool = False):
    path = _resolve_path(path, useCacher)
    if path:
        return os.path.abspath(path)

def resolve_template_type(path: str):
    extension = os.path.splitext(path)[1]
    match extension:
        case ".md":
            return "markdown"
        case ".tex":
            return "latex"
        case ".docx":
            return "docx"
        case ".pptx":
            return "pptx"
        case _:
            return None
