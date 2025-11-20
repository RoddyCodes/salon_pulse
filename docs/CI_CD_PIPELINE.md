# CI/CD Pipeline Documentation

## Overview

This project uses **GitHub Actions** for continuous integration and deployment, following industry best practices for Python web applications.

## Pipeline Stages

```
┌─────────────────┐
│  Code Quality   │  ← Black, isort, Flake8, Pylint
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Security      │  ← Bandit, Safety
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Tests       │  ← Pytest, Coverage
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Build       │  ← Package, Validate
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Deploy       │  ← Production (main branch only)
└─────────────────┘
```

## Workflow Triggers

- **Push to `main` or `develop`**: Full CI/CD pipeline runs
- **Pull Requests**: Full validation without deployment
- **Manual Trigger**: Can be run anytime via GitHub Actions UI

## Stage Details

### 1. Code Quality (Job: `code-quality`)

**Purpose**: Ensure code follows Python best practices and style guidelines

**Tools**:

- **Black**: Code formatter (PEP 8 compliant)
- **isort**: Import statement organizer
- **Flake8**: Style guide enforcement
- **Pylint**: Static code analysis

**Pass Criteria**:

- ✅ Code formatted with Black
- ✅ Imports sorted correctly
- ✅ No Flake8 violations
- ⚠️ Pylint warnings won't fail build

**Local Testing**:

```bash
# Format code
black backend/ scripts/ run.py

# Sort imports
isort backend/ scripts/ run.py

# Check style
flake8 backend/ scripts/ run.py

# Run static analysis
pylint backend/ scripts/ run.py
```

### 2. Security Scanning (Job: `security`)

**Purpose**: Identify security vulnerabilities in code and dependencies

**Tools**:

- **Bandit**: Scans Python code for security issues
- **Safety**: Checks dependencies for known vulnerabilities

**Checks**:

- SQL injection vulnerabilities
- Hardcoded passwords/secrets
- Insecure random number generation
- Known CVEs in dependencies

**Artifacts**: Security reports uploaded for review

**Local Testing**:

```bash
# Scan code for security issues
bandit -r backend/ scripts/ run.py

# Check dependency vulnerabilities
safety check
```

### 3. Testing (Job: `test`)

**Purpose**: Validate functionality across multiple Python versions

**Test Matrix**:

- Python 3.11
- Python 3.12
- Python 3.13 (primary)

**Coverage Requirements**:

- Unit tests for all backend modules
- Integration tests for Flask routes
- Minimum 70% code coverage (recommended)

**Test Types**:

- **Unit Tests**: `test_models.py`, `test_analytics.py`
- **Integration Tests**: `test_routes.py`
- **Fixtures**: Reusable test data in `conftest.py`

**Local Testing**:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html

# Run specific test
pytest tests/test_models.py::TestTechnicianModel::test_create_technician

# Run by marker
pytest -m unit
pytest -m integration
```

**Coverage Report**: HTML report uploaded as artifact

### 4. Build & Validate (Job: `build`)

**Purpose**: Ensure application can be built and started successfully

**Steps**:

1. Install dependencies
2. Initialize database schema
3. Test application startup (10s timeout)
4. Generate test data
5. Validate CLI tools run successfully
6. Create deployment artifact

**Artifact**: `salon-pulse-build.tar.gz` (retained for 30 days)

**Local Testing**:

```bash
# Test full build process
python -m backend.models
python run.py  # Should start successfully
python scripts/seed_data.py
python scripts/analyze.py
```

### 5. Deployment (Job: `deploy`)

**Trigger**: Only runs on `main` branch pushes

**Current Status**: Placeholder for deployment logic

**Supported Platforms**:

- Heroku
- AWS (EC2, ECS, Lambda)
- DigitalOcean
- Google Cloud Run
- Azure App Service

## Environment Variables & Secrets

### Required Secrets (for deployment)

Add these in GitHub Settings → Secrets and variables → Actions:

```yaml
HEROKU_API_KEY: <your-heroku-api-key>
HEROKU_APP_NAME: salon-pulse
HEROKU_EMAIL: <your-email>

# Or for AWS
AWS_ACCESS_KEY_ID: <your-aws-key>
AWS_SECRET_ACCESS_KEY: <your-aws-secret>
```

### Environment Variables

Set in workflow file or repository settings:

- `PYTHON_VERSION`: Python version (currently 3.13)
- `FLASK_ENV`: production|development
- `DATABASE_URL`: Production database connection string

## Running Locally

### Setup Development Environment

```bash
# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -r requirements-test.txt

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### Run Quality Checks

```bash
# Full quality check
black backend/ scripts/ run.py
isort backend/ scripts/ run.py
flake8 backend/ scripts/ run.py
pylint backend/ scripts/ run.py
```

### Run Tests

```bash
# All tests with coverage
pytest tests/ -v --cov=backend --cov-report=term-missing

# Watch mode (requires pytest-watch)
ptw tests/ -- --cov=backend
```

## Continuous Deployment

### Deploying to Heroku

1. **Create Heroku app**:

```bash
heroku create salon-pulse
```

2. **Add PostgreSQL** (recommended for production):

```bash
heroku addons:create heroku-postgresql:mini
```

3. **Set environment variables**:

```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=<your-secret-key>
```

4. **Create Procfile**:

```
web: gunicorn run:app
```

5. **Add to requirements.txt**:

```
gunicorn==21.2.0
psycopg2-binary==2.9.9  # For PostgreSQL
```

6. **Deploy**:

```bash
git push heroku main
```

### Deploying to AWS EC2

1. **Launch EC2 instance** (Ubuntu 22.04 LTS)
2. **SSH into instance**
3. **Install dependencies**:

```bash
sudo apt update
sudo apt install python3-pip nginx
```

4. **Clone repository**:

```bash
git clone <your-repo-url>
cd salon_pulse
```

5. **Setup application**:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

6. **Configure Nginx** as reverse proxy
7. **Setup systemd service** for auto-restart

## Monitoring & Observability

### Recommended Tools

- **Sentry**: Error tracking and monitoring
- **Datadog**: Application performance monitoring
- **New Relic**: Full-stack observability
- **Codecov**: Code coverage tracking

### Adding Sentry

```python
# In backend/models.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="<your-sentry-dsn>",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

## Troubleshooting

### Pipeline Failures

**Black formatting fails**:

```bash
# Auto-fix locally
black backend/ scripts/ run.py
git add .
git commit -m "Format code with Black"
```

**Tests fail**:

```bash
# Run locally to debug
pytest tests/ -v --tb=short
```

**Import errors in tests**:

```bash
# Ensure you're in project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

### Local Development Issues

**Pre-commit hook failures**:

```bash
# Run hooks manually
pre-commit run --all-files

# Skip hooks (not recommended)
git commit --no-verify
```

## Best Practices

### Before Committing

1. ✅ Run `black` and `isort`
2. ✅ Run `flake8` to check style
3. ✅ Run `pytest` to ensure tests pass
4. ✅ Check `bandit` for security issues
5. ✅ Update tests for new features

### Pull Request Checklist

- [ ] All CI checks passing
- [ ] Code coverage maintained or improved
- [ ] No new security vulnerabilities
- [ ] Documentation updated
- [ ] Tests added for new features

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Code Style](https://black.readthedocs.io/)
- [Flake8 Rules](https://www.flake8rules.com/)
- [Bandit Security Checks](https://bandit.readthedocs.io/)
