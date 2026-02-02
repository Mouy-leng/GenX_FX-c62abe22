# Plane Project Management Integration

## Overview

[Plane](https://github.com/makeplane/plane) is an open-source project management tool that can help organize and track work on the GenX_FX trading system. This guide explains how to use Plane for managing development, testing, and deployment tasks.

## What is Plane?

Plane is a modern, open-source project management platform that offers:

- **Issue Tracking**: Create, assign, and track tasks and bugs
- **Project Views**: Kanban boards, lists, calendars, and Gantt charts
- **Cycles & Sprints**: Organize work into time-boxed iterations
- **Modules**: Group related issues into feature sets
- **Pages**: Built-in documentation and wiki
- **GitHub Integration**: Sync with GitHub issues and pull requests

## Why Use Plane for GenX_FX?

The GenX_FX trading system has multiple components:
- Trading algorithms and strategies
- MetaTrader integration
- Python automation scripts
- Windows service management
- Credential and security management

Plane helps coordinate these moving parts by providing:
1. **Unified Dashboard**: See all active work across components
2. **Priority Management**: Focus on critical trading system fixes
3. **Deployment Planning**: Track production releases and testing
4. **Team Collaboration**: Coordinate between developers and traders
5. **Documentation Hub**: Keep system docs alongside tasks

## Getting Started with Plane

### Option 1: Plane Cloud (Recommended for Quick Start)

1. Visit [plane.so](https://plane.so)
2. Sign up with your GitHub account
3. Create a new workspace for "GenX_FX"
4. Create projects:
   - `Trading Core` - Main trading algorithms
   - `Infrastructure` - Services, monitoring, deployment
   - `Integration` - MetaTrader, brokers, data feeds
   - `Documentation` - Guides, runbooks, policies

### Option 2: Self-Hosted Plane

For enhanced security and control over trading system data:

```bash
# Clone Plane repository
git clone https://github.com/makeplane/plane.git
cd plane

# Use Docker Compose for deployment
./setup.sh

# Follow the setup wizard
# Access at http://localhost
```

**Benefits of Self-Hosting**:
- Complete data control for sensitive trading information
- Custom authentication (important for financial systems)
- Integration with internal networks
- No external data exposure

## Project Structure in Plane

### Recommended Project Setup

#### 1. Trading Core
**Purpose**: Algorithm development, strategy testing, backtesting

**Labels**:
- `algorithm` - Trading strategy code
- `backtest` - Historical testing
- `optimization` - Performance tuning
- `risk-management` - Position sizing, stops

**Cycles**: Weekly sprints for strategy iterations

#### 2. Infrastructure
**Purpose**: Services, monitoring, deployment, system health

**Labels**:
- `monitoring` - Dashboard and alerts
- `deployment` - Production releases
- `service` - Windows service management
- `security` - Credentials, encryption

**Modules**:
- MetaTrader Integration
- Python Service Management
- Health Monitoring System

#### 3. Integration
**Purpose**: External system connections

**Labels**:
- `broker-api` - Broker connectivity
- `data-feed` - Market data providers
- `mt-bridge` - MetaTrader communication

#### 4. Documentation
**Purpose**: System documentation, runbooks, procedures

Use Plane Pages for:
- Setup guides
- Troubleshooting procedures
- API documentation
- Trading playbooks

## GitHub Integration

### Connect Plane to This Repository

1. In Plane, go to **Project Settings** → **Integrations**
2. Select **GitHub**
3. Authorize Plane to access `Mouy-leng/GenX_FX-c62abe22`
4. Enable sync options:
   - ✓ Import existing issues
   - ✓ Two-way sync
   - ✓ Auto-link PRs to issues

### Workflow Integration

**Using Issue References**:
```
# In commit messages and PRs
fix: Resolve MT login timeout issue [PLANE-123]

# Plane automatically links the commit to issue PLANE-123
```

**PR Automation**:
- PRs automatically appear in linked issues
- Issue status updates when PR is merged
- Deploy tracking from GitHub Actions

## Recommended Workflows

### 1. Bug Tracking Workflow

```
New Bug → Triage → Priority Assessment → Assign → In Progress → Testing → Closed
```

**Labels**: `bug`, `critical`, `urgent`, `minor`

### 2. Feature Development Workflow

```
Idea → Spec → Design Review → Development → Code Review → Testing → Deploy → Done
```

**Labels**: `feature`, `enhancement`, `research`

### 3. Trading Strategy Workflow

```
Concept → Backtest → Paper Trade → Review Results → Live Test (Small) → Full Deploy
```

**Labels**: `strategy`, `backtest-pass`, `paper-trade`, `live-approved`

### 4. Security & Credentials Workflow

```
Security Issue → Assessment → Implementation → Audit → Verification → Closed
```

**Labels**: `security`, `credentials`, `audit-required`

## Best Practices

### Issue Creation

**Good Issue Title**: 
```
[MT] Login timeout after 30 seconds on A6-9V EA
```

**Include**:
- Component prefix: `[MT]`, `[Python]`, `[Service]`
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- System details (Windows version, MT version)

### Using Cycles

Create weekly or bi-weekly cycles:
- `Current Week` - Bug fixes and monitoring
- `Sprint 12: Strategy Optimization`
- `December Deployment Cycle`

Add issues to cycles for focused work periods.

### Priority Levels

- **Urgent**: Trading system down, data loss risk
- **High**: Critical feature, security issue
- **Medium**: Important improvement, non-critical bug
- **Low**: Enhancement, documentation, refactoring

### Using Modules

Group related features:
- **Module**: "MetaTrader Auto-Login System"
  - Issue: Implement credential encryption
  - Issue: Add retry logic
  - Issue: Create monitoring dashboard
  - Issue: Write setup documentation

## Integration with Existing Tools

### MetaTrader Expert Advisors
- Track EA development in `Trading Core` project
- Use labels: `ea-development`, `mql4`, `mql5`
- Link backtesting results in issue comments

### Python Services
- Track service issues in `Infrastructure` project
- Link to Python scripts in repository
- Document service dependencies

### Windows Services
- Use `windows-service` label
- Track installation and configuration issues
- Document auto-start and monitoring setup

## Reporting and Metrics

### Key Metrics to Track

1. **Velocity**: Issues completed per cycle
2. **Bug Resolution Time**: Time from report to fix
3. **Deployment Frequency**: Releases per month
4. **Strategy Development**: Time from concept to live

### Custom Views

Create filtered views:
- "Critical Bugs" - All urgent/high bugs
- "This Week" - Current cycle issues
- "My Tasks" - Assigned to you
- "Deployment Queue" - Ready for production

## Security Considerations

### Sensitive Information

**DO NOT** include in Plane issues:
- Trading account credentials
- API keys or tokens
- Broker account numbers
- Actual trading positions or P&L

**DO** include:
- System architecture details
- Error logs (sanitized)
- Configuration approaches
- Deployment procedures

### Access Control

Set up Plane workspace roles:
- **Admin**: Full system access
- **Developer**: Code and infrastructure issues
- **Trader**: Strategy and trading-related issues
- **Viewer**: Read-only access

## Migration from Current System

If currently tracking work elsewhere:

1. **Export existing issues**:
   - GitHub Issues: Use Plane's import
   - Spreadsheets: Bulk import via CSV
   - Other tools: Manual migration for active items

2. **Set up initial projects** (1-2 hours)
   - Create project structure
   - Add labels and states
   - Configure GitHub sync

3. **Train team** (1 week)
   - Weekly standups in Plane
   - Create and assign issues
   - Track progress

4. **Iterate** (Ongoing)
   - Adjust workflows based on usage
   - Add custom views
   - Refine automation

## Support and Resources

### Plane Documentation
- Official Docs: [docs.plane.so](https://docs.plane.so)
- GitHub: [github.com/makeplane/plane](https://github.com/makeplane/plane)
- Community: [GitHub Discussions](https://github.com/makeplane/plane/discussions)

### Internal Resources
- Project Management Lead: GenX_FX Project Management Team
- Plane Admin: GenX_FX DevOps & Tooling Team
- Support Channel: `#genx-fx-plane-support` (Slack/Teams)

## Quick Reference

### Common Commands

**Create Issue**: `Ctrl/Cmd + I`
**Quick Search**: `Ctrl/Cmd + K`
**Create Cycle**: Project → Cycles → New Cycle
**Bulk Edit**: Select issues → Bulk Operations

### Keyboard Shortcuts

- `C` - Create new issue
- `Q` - Quick actions
- `1,2,3,4` - Switch between views
- `Ctrl + Enter` - Submit/Save

## Maintenance

### Weekly Tasks
- Review and prioritize new issues
- Update cycle progress
- Close completed items

### Monthly Tasks
- Archive completed cycles
- Review metrics and velocity
- Update project documentation
- Clean up stale issues

## Getting Help

For questions about:
- **Plane setup**: See [Plane docs](https://docs.plane.so)
- **This integration**: Check `docs/` folder or create issue
- **Trading system**: See `A6-9V_Master_System_README.md`

---

**Last Updated**: 2025-12-26
**Maintained By**: GenX_FX Development Team
