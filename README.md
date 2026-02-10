# GenX_FX Trading System

## 📓 Knowledge Base
- **NotebookLM**: [Access here](https://notebooklm.google.com/notebook/e8f4c29d-9aec-4d5f-8f51-2ca168687616)
- **Note**: This notebook is available for reading and writing. AI agents must read it before starting work.


🚀 **Production-Ready Forex Trading System** with MetaTrader 5 integration, Python automation, and Node.js backend infrastructure.

## 🌐 Live Deployment

**Production URL:** `https://lengkundee01.org`

For detailed domain deployment instructions, see [DOMAIN_DEPLOYMENT_GUIDE.md](DOMAIN_DEPLOYMENT_GUIDE.md)

## 📋 Project Overview

GenX_FX is a comprehensive trading system combining:
- **MetaTrader 5 Integration** - Automated Expert Advisors for forex trading
- **Production Application** - Node.js/Express backend with MongoDB
- **Python Automation** - System monitoring, health checks, and deployment tools
- **Documentation** - Extensive guides for setup and operations

## ✨ Key Features

- 🤖 **8 Expert Advisors** for automated forex trading
- 🔐 **Secure Authentication** with JWT and account lockout protection
- 🗄️ **MongoDB Database** with robust data management
- 📊 **Real-time Monitoring** with health checks and metrics
- 🐳 **Docker Support** for containerized deployment
- 🛡️ **Security First** with Helmet, CORS, and rate limiting
- ⚡ **CI/CD Pipeline** with automated testing and deployment
- 🌐 **Domain Ready** with nginx reverse proxy configuration

## 🚀 Quick Start

### For Trading System Users:

```bash
# Clone the repository
git clone https://github.com/Mouy-leng/GenX_FX-c62abe22.git
cd GenX_FX-c62abe22

# Run the launcher (Unix/Linux/Mac)
./launch_cloned_branch.sh

# Or on Windows
launch_cloned_branch.bat
```

### For Production Deployment:

```bash
# Navigate to ProductionApp
cd ProductionApp

# Copy environment file
cp .env.example .env

# Install dependencies
npm install

# Start with Docker Compose
docker-compose up -d
```

For detailed deployment instructions, see [ProductionApp/README.md](ProductionApp/README.md)

## 📚 Documentation

### Essential Guides

| Document | Purpose |
|----------|---------|
| [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) | Complete documentation index |
| [REPOSITORY_LAUNCH_GUIDE.md](REPOSITORY_LAUNCH_GUIDE.md) | Trading system launch guide |
| [MT5_EXPERT_ADVISORS_QUICK_REFERENCE.md](MT5_EXPERT_ADVISORS_QUICK_REFERENCE.md) | MT5 Expert Advisors reference |
| [ProductionApp/README.md](ProductionApp/README.md) | Production app documentation |

### Domain & Deployment Guides

| Document | Purpose |
|----------|---------|
| [QUICK_START_DOMAIN_DEPLOYMENT.md](QUICK_START_DOMAIN_DEPLOYMENT.md) | ⚡ Quick 30-minute deployment guide |
| [DOMAIN_DEPLOYMENT_GUIDE.md](DOMAIN_DEPLOYMENT_GUIDE.md) | Complete domain deployment instructions |
| [DNS_CONFIGURATION_GUIDE.md](DNS_CONFIGURATION_GUIDE.md) | Namecheap DNS setup guide |
| [MONITORING_GUIDE.md](MONITORING_GUIDE.md) | Application monitoring & health checks |
| [GITHUB_SECRETS_GUIDE.md](GITHUB_SECRETS_GUIDE.md) | GitHub Actions secrets configuration |

### System Configuration

| Document | Purpose |
|----------|---------|
| [VPS_CONFIGURATION.md](VPS_CONFIGURATION.md) | VPS server configuration |
| [CREDENTIAL_ORGANIZATION_GUIDE.md](CREDENTIAL_ORGANIZATION_GUIDE.md) | Secure credential management |
| [LAUNCH_WORKFLOW_DIAGRAM.md](LAUNCH_WORKFLOW_DIAGRAM.md) | Visual workflow diagram |

## 🏗️ Project Structure

```
GenX_FX/
├── ProductionApp/          # Node.js production application
│   ├── src/               # Application source code
│   ├── config/            # Configuration files
│   ├── tests/             # Test suite
│   └── docker-compose.yml # Docker deployment
├── A6-9V/                 # Trading system components
│   └── Trading/GenX_FX/   # Core trading application
├── scripts/               # Automation scripts
├── docs/                  # Additional documentation
├── launch_cloned_branch.sh # Unix launcher
├── launch_cloned_branch.bat # Windows launcher
└── README.md              # This file
```

## 🤖 MetaTrader 5 Trading System

### Demo Account Configuration
- **Account Type:** Demo (Hedging)
- **Login:** 279260115
- **Server:** Exness-MT5Trail8
- **Balance:** 39,499.31 USD

### Expert Advisors (8 Total)
1. ExpertMAPSAR_Enhanced
2. ExpertMAPSAR Enhanced
3. ExpertMAPSARSizeOptimized
4. ExpertMAPSAR
5. ExpertMACD
6. ExpertMAMA
7. bridges3rd
8. Advisors_backup_20251226_235613

### Trading Pairs
**Forex:** EURUSD, USDJPY, GBPUSD, GBPJPY, USDCAD, USDCHF, USDARS  
**Precious Metals:** XAUUSD  
**Crypto:** BTCUSD, ETHUSD, BTCCNH, BTCXAU, BTCZAR

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
cd ProductionApp
docker-compose up -d
```

This will start:
- Application server (Node.js/Express)
- MongoDB database
- Redis cache
- Nginx reverse proxy

### Access Services

- **Application:** http://localhost:3000
- **Health Check:** http://localhost:3000/health
- **MongoDB:** localhost:27017
- **Redis:** localhost:6379
- **Nginx:** http://localhost:80

## 🔐 Security

### Security Features
- JWT-based authentication
- Account lockout after failed attempts
- Rate limiting on API endpoints
- Helmet.js security headers
- CORS configuration
- Input validation and sanitization
- Password hashing with bcrypt
- SSL/TLS support for production

### Important Notes
⚠️ **Demo Account:** This repository includes demo account credentials for testing
⚠️ **Never commit** real trading credentials to version control
⚠️ **Always use** environment variables for sensitive data
⚠️ **Configure SSL** certificates for production domains

## 🌐 Domain Configuration

### Namecheap Domain Setup

1. **Configure DNS records** in your Namecheap dashboard:
   ```
   A Record:    @        -> 203.147.134.218
   A Record:    www      -> 203.147.134.218
   CNAME:       api      -> lengkundee01.org
   ```

2. **Update environment variables** in `.env`:
   ```bash
   DOMAIN=lengkundee01.org
   CORS_ORIGIN=https://lengkundee01.org
   ```

3. **Configure SSL** certificates (see [DOMAIN_DEPLOYMENT_GUIDE.md](DOMAIN_DEPLOYMENT_GUIDE.md))

4. **Deploy with nginx** reverse proxy (configuration included)

For complete domain deployment instructions, see [DOMAIN_DEPLOYMENT_GUIDE.md](DOMAIN_DEPLOYMENT_GUIDE.md)

## 🧪 Testing

```bash
cd ProductionApp

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

## 📊 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | ❌ |
| POST | `/api/auth/login` | User login | ❌ |
| GET | `/api/auth/me` | Get current user | ✅ |
| POST | `/api/auth/logout` | User logout | ✅ |

### Health Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Basic health check |
| GET | `/health/detailed` | Detailed system info |

For complete API documentation, see [ProductionApp/README.md](ProductionApp/README.md)

## 🚀 CI/CD Pipeline

The repository includes GitHub Actions workflows for:
- ✅ Automated testing on push
- 🔐 Security audits
- 🐳 Docker image builds
- 📊 Code coverage reports
- 🚀 Deployment automation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md) for details.

## 📜 License

Private workspace. See [OWNERSHIP.md](OWNERSHIP.md) for repository ownership and governance.

## 🆘 Support

- **Issues:** https://github.com/Mouy-leng/GenX_FX-c62abe22/issues
- **Documentation:** [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- **Trading Guide:** [REPOSITORY_LAUNCH_GUIDE.md](REPOSITORY_LAUNCH_GUIDE.md)

## 📞 Contact

**Organization:** A6-9V  
**Repository:** https://github.com/Mouy-leng/GenX_FX-c62abe22  
**Domain:** https://lengkundee01.org  
**Last Updated:** January 2026

---

**Built with ❤️ using Node.js, Python, MetaTrader 5, and Docker**

*Remember: Always test on demo before going live with real funds!*
