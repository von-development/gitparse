"""Default variables and configurations for GitParse."""

from gitparse.vars.exclude_patterns import DEFAULT_EXCLUDE_PATTERNS
from gitparse.vars.file_types import MIME_TO_LANGUAGE, COMMON_EXTENSIONS
from gitparse.vars.limits import FILE_SIZE_LIMITS
from gitparse.vars.git_hosts import GIT_HOSTS

__all__ = [
    'DEFAULT_EXCLUDE_PATTERNS',
    'MIME_TO_LANGUAGE',
    'COMMON_EXTENSIONS',
    'FILE_SIZE_LIMITS',
    'GIT_HOSTS'
] 