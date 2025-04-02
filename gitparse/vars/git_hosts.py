"""Configuration for known Git hosting services."""

GIT_HOSTS = {
    # Major Hosting Services
    'github': {
        'domain': 'github.com',
        'api_url': 'https://api.github.com',
        'raw_url': 'https://raw.githubusercontent.com',
        'clone_url': 'https://github.com/{user}/{repo}.git',
        'web_url': 'https://github.com/{user}/{repo}',
        'api_version': 'v3',
    },
    'gitlab': {
        'domain': 'gitlab.com',
        'api_url': 'https://gitlab.com/api/v4',
        'raw_url': 'https://gitlab.com/{user}/{repo}/raw',
        'clone_url': 'https://gitlab.com/{user}/{repo}.git',
        'web_url': 'https://gitlab.com/{user}/{repo}',
        'api_version': 'v4',
    },
    'bitbucket': {
        'domain': 'bitbucket.org',
        'api_url': 'https://api.bitbucket.org/2.0',
        'raw_url': 'https://bitbucket.org/{user}/{repo}/raw',
        'clone_url': 'https://bitbucket.org/{user}/{repo}.git',
        'web_url': 'https://bitbucket.org/{user}/{repo}',
        'api_version': '2.0',
    },

    # Self-hosted Options
    'gitea': {
        'domain': None,  # Set by user
        'api_url': '{host}/api/v1',
        'raw_url': '{host}/{user}/{repo}/raw',
        'clone_url': '{host}/{user}/{repo}.git',
        'web_url': '{host}/{user}/{repo}',
        'api_version': 'v1',
    },
    'gogs': {
        'domain': None,  # Set by user
        'api_url': '{host}/api/v1',
        'raw_url': '{host}/{user}/{repo}/raw',
        'clone_url': '{host}/{user}/{repo}.git',
        'web_url': '{host}/{user}/{repo}',
        'api_version': 'v1',
    },

    # Default SSH Settings
    'ssh': {
        'port': 22,
        'known_hosts': '~/.ssh/known_hosts',
        'identity_file': '~/.ssh/id_rsa',
        'timeout': 30,
    },

    # Rate Limits (requests per hour)
    'rate_limits': {
        'github': 5000,
        'gitlab': 2000,
        'bitbucket': 1000,
        'gitea': None,  # Set by server
        'gogs': None,  # Set by server
    },
}
