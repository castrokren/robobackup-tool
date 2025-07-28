# Contributing to Windows Backup Tool

Thank you for your interest in contributing to the Windows Backup Tool! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature/fix
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

## Development Setup

1. Install Python 3.7+ on Windows
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and small
- Use type hints where appropriate

## Testing

- Test both GUI and service modes
- Test with local and network paths
- Verify logging functionality
- Test error handling scenarios
- Test on different Windows versions if possible

## Pull Request Guidelines

1. **Title**: Use a clear, descriptive title
2. **Description**: Explain what the change does and why
3. **Testing**: Describe how you tested the changes
4. **Screenshots**: Include screenshots for UI changes
5. **Logs**: Include relevant log output for debugging

## Issue Reporting

When reporting issues, please include:

1. **Environment**: Windows version, Python version
2. **Steps**: How to reproduce the issue
3. **Expected vs Actual**: What you expected vs what happened
4. **Logs**: Relevant log files from the `logs/` directory
5. **Screenshots**: If applicable

## Feature Requests

When requesting features:

1. **Use Case**: Explain the problem you're trying to solve
2. **Proposed Solution**: Describe your suggested approach
3. **Alternatives**: Consider if there are existing workarounds
4. **Priority**: Indicate if this is a nice-to-have or critical

## Security

- Never commit sensitive information (passwords, API keys)
- Report security issues privately
- Follow secure coding practices
- Test with appropriate permissions

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create a release tag
4. Build and test the executable
5. Upload release assets

## Questions?

If you have questions about contributing, please:

1. Check the existing issues and discussions
2. Create a new issue with the "question" label
3. Join our community discussions

Thank you for contributing to Windows Backup Tool! 