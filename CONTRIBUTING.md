# Contributing to Redis Cluster on Kubernetes

Thank you for your interest in contributing to this project! This guide will help you get started.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/sre.rediscluster.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes thoroughly
6. Commit with clear messages: `git commit -m "Add: description of changes"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Guidelines

### Code Style

- **YAML files**: Use 2-space indentation
- **Python files**: Follow PEP 8 guidelines
- **Shell scripts**: Follow Google Shell Style Guide
- **Comments**: Add clear comments explaining complex logic

### Testing Your Changes

Before submitting a PR, test your changes:

```bash
# Validate YAML syntax
kubectl apply --dry-run=client -f redis-cluster.yaml

# Test Python scripts
python3 -m py_compile local-redis-client.py k8-redis-client.py

# If possible, test in a real Kubernetes cluster
kubectl create -f redis-cluster.yaml
# ... verify functionality ...
kubectl delete -f redis-cluster.yaml
```

### Documentation

- Update README.md if you change functionality
- Update DEMO.md if you change deployment steps
- Add inline comments for complex configurations
- Include examples for new features

## What to Contribute

We welcome contributions including:

### Bug Fixes
- Fix issues in YAML configurations
- Correct documentation errors
- Fix Python client bugs

### Features
- Add monitoring/alerting configurations
- Implement backup/restore scripts
- Add Helm chart support
- Improve security configurations (TLS, AUTH)

### Documentation
- Improve installation instructions
- Add troubleshooting guides
- Create video tutorials or blog posts
- Translate documentation

### Testing
- Add test scripts
- Create CI/CD pipelines
- Add performance benchmarks

## Pull Request Guidelines

### PR Title Format
```
<Type>: <Short description>

Types: Fix, Add, Update, Remove, Refactor, Docs
Examples:
- Fix: Correct typo in README
- Add: Helm chart for Redis cluster
- Update: Upgrade Redis to 7.0
- Docs: Add troubleshooting section
```

### PR Description
Include:
1. What changes were made
2. Why the changes were needed
3. How to test the changes
4. Any breaking changes or migration notes

### Example PR Description
```markdown
## Changes
- Updated Redis version from 6.2.6 to 7.0.0
- Added resource limits to pod spec
- Updated documentation

## Rationale
Redis 7.0 includes important security fixes and performance improvements

## Testing
1. Deploy with: `kubectl apply -f redis-cluster.yaml`
2. Verify version: `kubectl exec redis-cluster-0 -- redis-cli INFO server`
3. Test cluster operations as described in DEMO.md

## Breaking Changes
None - upgrade is backward compatible
```

## File Organization

```
sre.rediscluster/
├── README.md              # Main documentation
├── DEMO.md                # Step-by-step demo guide
├── CONTRIBUTING.md        # This file
├── LICENSE                # MIT License
├── .gitignore             # Ignore patterns
├── redis-cluster.yaml     # Main deployment file
├── redis-expose.yaml      # External service example
├── redis-service-example.yaml  # Alternative config
├── values.yaml            # Configuration values
├── k8-redis-client.py     # Kubernetes Python client
├── local-redis-client.py  # Local Python client
└── etc/
    └── bootstrap-pod.sh   # Pod initialization script
```

### Files Not to Include

The following files should NOT be committed (they're in .gitignore):
- `*.zip` - Archive files (download separately if needed)
- `*.log` - Log files
- `__pycache__/` - Python cache
- `.idea/`, `.vscode/` - IDE settings
- `*.kubeconfig` - Kubernetes config files

## Code Review Process

1. All PRs require at least one review
2. CI checks must pass (once implemented)
3. Documentation must be updated
4. No breaking changes without discussion

## Questions?

- Open an issue for questions about contributing
- Tag issues with `question` label
- Be respectful and follow the Code of Conduct

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Report inappropriate behavior

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🚀
