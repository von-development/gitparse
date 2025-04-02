"""Default size and other limits for GitParse."""

FILE_SIZE_LIMITS = {
    # General Limits
    'max_file_size': 10 * 1024 * 1024,  # 10MB max file size
    'max_total_size': 100 * 1024 * 1024,  # 100MB max total repository size
    'max_files': 10000,  # Maximum number of files to process

    # Size Limits by File Type
    'text_file_size': 1 * 1024 * 1024,  # 1MB for text files
    'code_file_size': 500 * 1024,  # 500KB for code files
    'config_file_size': 100 * 1024,  # 100KB for config files

    # Directory Limits
    'max_depth': 20,  # Maximum directory depth
    'max_files_per_dir': 1000,  # Maximum files per directory

    # Content Limits
    'max_line_length': 1000,  # Maximum characters per line
    'max_lines': 50000,  # Maximum lines per file

    # Memory Limits
    'max_memory_usage': 1024 * 1024 * 1024,  # 1GB max memory usage
    'chunk_size': 8192,  # 8KB chunks for file reading

    # Time Limits
    'clone_timeout': 300,  # 5 minutes for cloning
    'file_read_timeout': 30,  # 30 seconds per file
    'total_timeout': 1800,  # 30 minutes total
}
