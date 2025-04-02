import pytest
from pathlib import Path
import tempfile
import shutil
import git
from git.exc import GitCommandError
import json

from gitparse import GitRepo, ExtractionConfig


@pytest.fixture
def temp_repo():
    """Create a temporary directory with some test files."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create a simple repo structure
    (temp_dir / "README.md").write_text("# Test Repo\nThis is a test repository.")
    (temp_dir / "src").mkdir()
    (temp_dir / "src" / "main.py").write_text("print('hello world')")
    (temp_dir / "src" / "utils").mkdir()
    (temp_dir / "src" / "utils" / "helper.py").write_text("def help(): pass")
    (temp_dir / "docs").mkdir()
    (temp_dir / "docs" / "index.md").write_text("# Documentation")
    (temp_dir / "large_file.bin").write_bytes(b"0" * (11 * 1024 * 1024))  # 11MB file
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def git_repo():
    """Create a temporary Git repository."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Initialize Git repo
    repo = git.Repo.init(temp_dir)
    
    # Create some files
    (temp_dir / "README.md").write_text("# Git Test Repo")
    (temp_dir / "main.py").write_text("print('hello git')")
    
    # Add and commit
    repo.index.add(["README.md", "main.py"])
    repo.index.commit("Initial commit")
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


def test_gitrepo_init_local(temp_repo):
    """Test GitRepo initialization with local path."""
    repo = GitRepo(str(temp_repo))
    assert repo.source == str(temp_repo)
    assert isinstance(repo.config, ExtractionConfig)
    assert not repo._is_remote


def test_gitrepo_init_remote():
    """Test GitRepo initialization with remote URL."""
    url = "https://github.com/user/repo"
    repo = GitRepo(url)
    assert repo.source == url
    assert repo._is_remote
    assert repo._temp_dir is not None


def test_gitrepo_init_invalid_path():
    """Test GitRepo initialization with invalid local path."""
    with pytest.raises(ValueError, match="Repository path does not exist"):
        GitRepo("/path/does/not/exist")


def test_gitrepo_get_readme(temp_repo):
    """Test README retrieval."""
    repo = GitRepo(str(temp_repo))
    readme = repo.get_readme()
    assert readme is not None
    assert readme.startswith("# Test Repo")


def test_gitrepo_get_readme_no_readme(temp_repo):
    """Test README retrieval when no README exists."""
    # Remove README
    (temp_repo / "README.md").unlink()
    
    repo = GitRepo(str(temp_repo))
    assert repo.get_readme() is None


def test_get_file_tree_flattened(temp_repo):
    """Test flattened file tree output."""
    repo = GitRepo(str(temp_repo))
    tree = repo.get_file_tree(style="flattened")
    
    assert isinstance(tree, list)
    assert set(tree) == {
        "README.md",
        "src/main.py",
        "src/utils/helper.py",
        "docs/index.md"
    }
    # large_file.bin should be excluded due to size


def test_get_file_tree_markdown(temp_repo):
    """Test markdown file tree output."""
    repo = GitRepo(str(temp_repo))
    tree = repo.get_file_tree(style="markdown")
    
    assert isinstance(tree, list)
    expected = [
        "- README.md",
        "- docs/",
        "  - index.md",
        "- src/",
        "  - main.py",
        "  - utils/",
        "    - helper.py"
    ]
    assert tree == expected


def test_get_file_tree_structured(temp_repo):
    """Test structured (dict) file tree output."""
    repo = GitRepo(str(temp_repo))
    tree = repo.get_file_tree(style="structured")
    
    assert isinstance(tree, dict)
    expected = {
        "README.md": None,
        "docs": {
            "index.md": None
        },
        "src": {
            "main.py": None,
            "utils": {
                "helper.py": None
            }
        }
    }
    assert tree == expected


def test_get_file_tree_with_patterns(temp_repo):
    """Test file tree with include/exclude patterns."""
    config = ExtractionConfig(
        include_patterns=["*.py"],
        exclude_patterns=["**/utils/*"]
    )
    repo = GitRepo(str(temp_repo), config=config)
    tree = repo.get_file_tree(style="flattened")
    
    assert isinstance(tree, list)
    assert tree == ["src/main.py"]  # Only main.py should be included


def test_get_file_tree_invalid_style(temp_repo):
    """Test file tree with invalid style."""
    repo = GitRepo(str(temp_repo))
    with pytest.raises(ValueError, match="Unsupported tree style"):
        repo.get_file_tree(style="invalid")


def test_gitrepo_with_git(git_repo):
    """Test GitRepo with a Git repository."""
    repo = GitRepo(str(git_repo))
    info = repo.get_repository_info()
    
    assert info["name"] == git_repo.name
    assert info["default_branch"] == "master"
    assert "head_commit" in info
    assert isinstance(info["remotes"], list)
    assert info["is_bare"] is False


def test_gitrepo_without_git(temp_repo):
    """Test GitRepo with a non-Git directory."""
    repo = GitRepo(str(temp_repo))
    info = repo.get_repository_info()
    
    assert info["name"] == temp_repo.name
    assert len(info) == 1  # Only name should be present


@pytest.mark.skip("Requires network access")
def test_gitrepo_clone_remote():
    """Test cloning a remote repository."""
    url = "https://github.com/python/cpython"
    repo = GitRepo(url)
    
    assert repo._is_remote
    assert repo._repo_path is not None
    assert repo._repo_path.exists()
    assert (repo._repo_path / "README.rst").exists()
    
    info = repo.get_repository_info()
    assert info["name"] == "cpython"
    assert "head_commit" in info 


@pytest.fixture
def repo_with_deps():
    """Create a repository with various dependency files."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create requirements.txt
    reqs = """
# Comments should be ignored
requests>=2.28.0
flask==2.0.1
python-dotenv~=0.19.0
invalid==requirement==here
    """
    (temp_dir / "requirements.txt").write_text(reqs.strip())
    
    # Create pyproject.toml
    pyproject = """
[tool.poetry]
name = "test-project"
version = "0.1.0"
description = "Test project"

[tool.poetry.dependencies]
python = "^3.8"
requests = "^2.28.0"
pydantic = {version = "^2.0.0", extras = ["email"]}

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
black = "^24.0.0"
    """
    (temp_dir / "pyproject.toml").write_text(pyproject.strip())
    
    # Create package.json
    package_json = {
        "name": "test-project",
        "version": "1.0.0",
        "dependencies": {
            "express": "^4.17.1",
            "lodash": "^4.17.21"
        },
        "devDependencies": {
            "jest": "^27.0.6",
            "typescript": "^4.5.4"
        }
    }
    (temp_dir / "package.json").write_text(json.dumps(package_json, indent=2))
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


def test_parse_requirements_txt(repo_with_deps):
    """Test parsing requirements.txt file."""
    repo = GitRepo(str(repo_with_deps))
    deps = repo.get_dependencies()
    
    assert "requirements.txt" in deps
    reqs = deps["requirements.txt"]["dependencies"]
    
    # Should find 3 valid requirements (one is invalid)
    assert len(reqs) == 3
    
    # Check specific requirements
    req_names = {r["name"] for r in reqs}
    assert req_names == {"requests", "flask", "python-dotenv"}
    
    # Check version specifiers
    flask_req = next(r for r in reqs if r["name"] == "flask")
    assert flask_req["specifier"] == "==2.0.1"


def test_parse_poetry_toml(repo_with_deps):
    """Test parsing pyproject.toml with Poetry dependencies."""
    repo = GitRepo(str(repo_with_deps))
    deps = repo.get_dependencies()
    
    assert "pyproject.toml" in deps
    poetry_deps = deps["pyproject.toml"]
    
    # Check main dependencies
    main_deps = poetry_deps["dependencies"]
    assert len(main_deps) == 2  # python dependency is excluded
    
    # Check pydantic with extras
    pydantic = next(d for d in main_deps if d["name"] == "pydantic")
    assert pydantic["version"] == "^2.0.0"
    assert pydantic["extras"] == ["email"]
    
    # Check dev dependencies
    dev_deps = poetry_deps["dev-dependencies"]
    assert len(dev_deps) == 2
    dev_names = {d["name"] for d in dev_deps}
    assert dev_names == {"pytest", "black"}


def test_parse_package_json(repo_with_deps):
    """Test parsing package.json dependencies."""
    repo = GitRepo(str(repo_with_deps))
    deps = repo.get_dependencies()
    
    assert "package.json" in deps
    node_deps = deps["package.json"]
    
    # Check main dependencies
    main_deps = node_deps["dependencies"]
    assert len(main_deps) == 2
    main_names = {d["name"] for d in main_deps}
    assert main_names == {"express", "lodash"}
    
    # Check dev dependencies
    dev_deps = node_deps["devDependencies"]
    assert len(dev_deps) == 2
    dev_names = {d["name"] for d in dev_deps}
    assert dev_names == {"jest", "typescript"} 