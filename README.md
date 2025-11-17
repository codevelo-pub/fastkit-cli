<div align="center">
  <h1>⚙️ FastKit CLI</h1>
  
  <p><strong>Command-Line Tools for FastKit</strong></p>
  
  <p>Scaffold projects and generate code like Laravel Artisan</p>
  
  [![PyPI version](https://badge.fury.io/py/fastkit-cli.svg)](https://pypi.org/project/fastkit-cli/)
  [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  
</div>

---

## 🚀 What is FastKit CLI?

FastKit CLI is a powerful command-line tool that brings Laravel Artisan-style developer experience to FastKit projects. Scaffold complete projects in seconds and generate boilerplate code with simple commands.

**Stop copying and pasting boilerplate code.**

---

## 📦 Installation
```bash
pip install fastkit-cli
```

Verify installation:
```bash
fastkit --version
```

---

## 🎯 Quick Start

### Create a New Project
```bash
fastkit new my-awesome-api
```

This creates a complete FastKit project with:
- ✅ FastAPI application setup
- ✅ Database configuration (PostgreSQL by default)
- ✅ Authentication (JWT) built-in
- ✅ Docker & Docker Compose
- ✅ Alembic migrations setup
- ✅ Testing framework configured
- ✅ Example models, repositories, services
- ✅ CI/CD workflow (GitHub Actions)

### Start Development
```bash
cd my-awesome-api
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
fastkit migrate

# Start development server
fastkit serve
```

Visit `http://localhost:8000/docs` - your API is ready! 🎉

---

## 📋 Available Commands

### Project Management

#### `fastkit new`

Create a new FastKit project with interactive prompts.
```bash
fastkit new my-project

# Options:
fastkit new my-project \
  --auth          # Include authentication (default: yes)
  --admin         # Include admin panel (default: yes)
  --db postgresql # Database: postgresql|mysql|sqlite
  --docker        # Include Docker setup (default: yes)
```

**What gets created:**
```
my-project/
├── app/
│   ├── models/        # User, Role models (if --auth)
│   ├── repositories/  # Data access layer
│   ├── services/      # Business logic
│   ├── controllers/   # API endpoints
│   └── main.py        # FastAPI application
├── alembic/           # Database migrations
├── tests/             # Test suite
├── docker-compose.yml # Docker setup
├── .env.example       # Environment template
└── README.md          # Project documentation
```

---

### Code Generation

#### `fastkit make:model`

Generate a SQLAlchemy model.
```bash
fastkit make:model Product

# With migration:
fastkit make:model Product -m
fastkit make:model Product --migration
```

**Generated:** `app/models/product.py`
```python
from fastkit_core.database import Base
from sqlalchemy import Column, String, Float

class Product(Base):
    __tablename__ = "products"
    
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
```

#### `fastkit make:repository`

Generate a repository for data access.
```bash
fastkit make:repository ProductRepository

# Specify model:
fastkit make:repository ProductRepository --model Product
```

**Generated:** `app/repositories/product_repository.py`
```python
from fastkit_core.database import BaseRepository
from app.models.product import Product

class ProductRepository(BaseRepository[Product]):
    def find_by_name(self, name: str):
        return self.first_where(name=name)
```

#### `fastkit make:service`

Generate a service for business logic.
```bash
fastkit make:service ProductService
```

**Generated:** `app/services/product_service.py`
```python
from fastkit_core.services import BaseService
from app.repositories.product_repository import ProductRepository

class ProductService(BaseService):
    def __init__(self, repository: ProductRepository):
        super().__init__(repository)
```

#### `fastkit make:controller`

Generate a controller with routes.
```bash
# Basic controller
fastkit make:controller ProductController

# Resource controller (full CRUD)
fastkit make:controller ProductController --resource
```

**Generated:** `app/controllers/product_controller.py`

With `--resource`:
```python
from fastapi import APIRouter, Depends
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/")
def list_products(service: ProductService = Depends()):
    return service.get_all()

@router.post("/")
def create_product(name: str, price: float, service: ProductService = Depends()):
    return service.create({"name": name, "price": price})

@router.get("/{product_id}")
def get_product(product_id: int, service: ProductService = Depends()):
    return service.get_by_id(product_id)

@router.put("/{product_id}")
def update_product(product_id: int, data: dict, service: ProductService = Depends()):
    return service.update(product_id, data)

@router.delete("/{product_id}")
def delete_product(product_id: int, service: ProductService = Depends()):
    service.delete(product_id)
    return {"message": "Product deleted"}
```

#### `fastkit make:migration`

Generate a database migration.
```bash
fastkit make:migration create_products_table

# Auto-generate from models:
fastkit make:migration --auto
```

---

### Database Commands

#### `fastkit migrate`

Run pending migrations.
```bash
# Run all pending migrations
fastkit migrate

# Migrate to specific revision
fastkit migrate --revision abc123

# Show SQL without executing
fastkit migrate --sql
```

#### `fastkit migrate:rollback`

Rollback the last migration.
```bash
# Rollback last migration
fastkit migrate:rollback

# Rollback multiple steps
fastkit migrate:rollback --steps 3
```

#### `fastkit migrate:status`

Show migration status.
```bash
fastkit migrate:status
```

Output:
```
┌────────────────┬──────────────────────────────┬───────────┐
│ Revision       │ Description                  │ Status    │
├────────────────┼──────────────────────────────┼───────────┤
│ abc123         │ create_users_table           │ ✓ Applied │
│ def456         │ create_products_table        │ ✓ Applied │
│ ghi789         │ add_products_category        │ Pending   │
└────────────────┴──────────────────────────────┴───────────┘
```

#### `fastkit db:seed`

Seed the database with sample data.
```bash
# Run all seeders
fastkit db:seed

# Run specific seeder
fastkit db:seed --class UserSeeder
```

---

### Server Commands

#### `fastkit serve`

Start the development server.
```bash
# Default (localhost:8000)
fastkit serve

# Custom host and port
fastkit serve --host 0.0.0.0 --port 3000

# Without auto-reload
fastkit serve --no-reload

# With workers (production)
fastkit serve --workers 4
```

#### `fastkit shell`

Open an interactive Python shell with app context.
```bash
fastkit shell
```
```python
>>> from app.models.user import User
>>> users = User.query.all()
>>> print(len(users))
5
```

---

### Testing Commands

#### `fastkit test`

Run the test suite.
```bash
# Run all tests
fastkit test

# Run specific file
fastkit test tests/test_users.py

# Run with coverage
fastkit test --cov

# Run and open coverage report
fastkit test --cov --cov-report html
open htmlcov/index.html
```

---

### Utility Commands

#### `fastkit routes`

List all registered routes.
```bash
fastkit routes
```

Output:
```
┌────────┬─────────────────────────────┬──────────────────┐
│ Method │ Path                        │ Name             │
├────────┼─────────────────────────────┼──────────────────┤
│ GET    │ /                           │ root             │
│ GET    │ /docs                       │ swagger_ui       │
│ POST   │ /auth/register              │ register         │
│ POST   │ /auth/login                 │ login            │
│ GET    │ /users                      │ list_users       │
│ POST   │ /users                      │ create_user      │
│ GET    │ /users/{user_id}            │ get_user         │
│ PUT    │ /users/{user_id}            │ update_user      │
│ DELETE │ /users/{user_id}            │ delete_user      │
└────────┴─────────────────────────────┴──────────────────┘
```

#### `fastkit config`

Show current configuration.
```bash
fastkit config

# Show specific config
fastkit config database
```

---

## 🎨 Customization

### Custom Templates

Create your own code generation templates:
```bash
# Create templates directory
mkdir -p templates/

# Create custom model template
# templates/model.py.stub
```
```python
from fastkit_core.database import Base
from sqlalchemy import Column, String

class {{class_name}}(Base):
    __tablename__ = "{{table_name}}"
    
    # Your custom fields here
    name = Column(String(100))
```

### Use Custom Template
```bash
fastkit make:model Product --template templates/model.py.stub
```

---

## 📚 Documentation

- [**Commands Reference**](https://docs.fastkit.dev/cli/commands) - All commands detailed
- [**Scaffolding Guide**](https://docs.fastkit.dev/cli/scaffolding) - Project setup
- [**Code Generation**](https://docs.fastkit.dev/cli/generators) - Custom generators
- [**Configuration**](https://docs.fastkit.dev/cli/configuration) - CLI config options

---

## 🎓 Examples

### Complete Workflow Example
```bash
# 1. Create new project
fastkit new blog-api --auth

cd blog-api

# 2. Generate blog post functionality
fastkit make:model Post -m
fastkit make:repository PostRepository --model Post
fastkit make:service PostService
fastkit make:controller PostController --resource

# 3. Run migration
fastkit migrate

# 4. Seed database
fastkit db:seed

# 5. Start server
fastkit serve

# 6. Run tests
fastkit test --cov
```

### Creating a Complete Feature
```bash
# Generate complete CRUD for "Product" feature
fastkit make:model Product -m
fastkit make:repository ProductRepository
fastkit make:service ProductService  
fastkit make:controller ProductController --resource

# Register routes in app/main.py:
# app.include_router(product_controller.router)

fastkit migrate
fastkit serve
```

---

## 🔧 Configuration

### Global Config

`~/.fastkit/config.yaml`:
```yaml
defaults:
  database: postgresql
  auth: true
  docker: true

templates:
  path: ~/.fastkit/templates

editor: code  # VS Code
```

### Project Config

`.fastkit.yaml` in project root:
```yaml
paths:
  models: app/models
  repositories: app/repositories
  services: app/services
  controllers: app/controllers
  migrations: alembic/versions

database:
  driver: postgresql
  host: localhost
  port: 5432
```

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

### Development Setup
```bash
git clone https://github.com/fastkit/fastkit-cli.git
cd fastkit-cli
pip install -e ".[dev]"

# Run tests
pytest

# Test CLI locally
fastkit --help
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🔗 Links

- [**FastKit Core**](https://github.com/fastkit/fastkit-core) - Core framework
- [**FastKit Auth**](https://github.com/fastkit/fastkit-auth) - Authentication
- [**Documentation**](https://docs.fastkit.dev/cli) - Full CLI docs
- [**PyPI**](https://pypi.org/project/fastkit-cli/) - Package repository

---

<div align="center">
  
**Built with ❤️ by the FastKit team**

[⭐ Star us on GitHub](https://github.com/fastkit/fastkit-cli)

</div>
