# Contributing to GitWrapped

Thanks for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/gitwrapped.git`
3. Create a branch: `git checkout -b feature/my-feature`
4. Install in dev mode: `pip install -e ".[dev]"`

## Development

```bash
# Install with dev dependencies
pip install -e .

# Run the CLI
python -m gitwrapped.cli --help
```

## Code Style

- Use type hints
- Write docstrings for public functions
- Follow existing patterns in the codebase
- Keep the CLI output user-friendly

## Making Changes

1. Make your changes
2. Test locally: `gitwrapped --since "1 month ago"`
3. Commit with a clear message
4. Push your branch
5. Open a pull request

## Pull Requests

- Describe what you changed and why
- Keep PRs focused on a single change
- Ensure the CLI still works without an API key

Thank you for contributing!
