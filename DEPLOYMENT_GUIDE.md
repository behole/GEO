# GEO Optimization System - Deployment Guide

## 🚀 **Deployment Options**

You have **3 main deployment approaches** for the GEO optimization system:

---

### **Option 1: Umbrella Command (RECOMMENDED)**

**Single command to rule them all!** Use the new `run_geo_system.py` umbrella script:

#### **Quick Commands:**
```bash
cd "/Users/jjoosshhmbpm1/GEO OPT"

# Run complete system (all 4 agents in sequence)
python run_geo_system.py --mode full

# Run individual agents
python run_geo_system.py --mode discovery     # Agent 1 only
python run_geo_system.py --mode content       # Agent 2 only
python run_geo_system.py --mode competitive   # Agent 3 only
python run_geo_system.py --mode monitoring    # Agent 4 only

# Continuous monitoring (production mode)
python run_geo_system.py --continuous --interval 6

# System management
python run_geo_system.py --status             # Check status
python run_geo_system.py --stop               # Stop monitoring
python run_geo_system.py --help               # Full help
```

---

### **Option 2: Agent 4 as Orchestrator (PRODUCTION)**

Let Agent 4 manage everything automatically:

```bash
cd "/Users/jjoosshhmbpm1/GEO OPT"

# Start continuous monitoring (runs all agents on schedule)
python -c "
import asyncio
from monitoring_alerting_agent.monitoring_alerting_agent import start_continuous_monitoring
status = asyncio.run(start_continuous_monitoring(interval_hours=6))
print('✅ All agents now running automatically every 6 hours')
"

# Check status anytime
python -c "
from monitoring_alerting_agent.monitoring_alerting_agent import get_monitoring_status
status = get_monitoring_status()
print(f'Monitoring Active: {status[\"monitoring_active\"]}')
print(f'System Health: {status[\"system_health\"]}')
"
```

---

### **Option 3: Individual Agent Execution**

Run each agent separately (for development/testing):

```bash
cd "/Users/jjoosshhmbpm1/GEO OPT"

# Agent 1 - Discovery Baseline
python -c "
import asyncio
from discovery_baseline_agent.discovery_baseline_agent import run_discovery_baseline_analysis
result = asyncio.run(run_discovery_baseline_analysis())
"

# Agent 2 - Content Analysis
python -c "
import asyncio
from content_analysis_agent.content_analysis_agent import run_content_analysis
result = asyncio.run(run_content_analysis())
"

# Agent 3 - Competitive Intelligence
python -c "
import asyncio
from competitive_intelligence_agent.competitive_intelligence_agent import run_competitive_intelligence_analysis
result = asyncio.run(run_competitive_intelligence_analysis())
"

# Agent 4 - Monitoring & Alerting
python -c "
import asyncio
from monitoring_alerting_agent.monitoring_alerting_agent import run_monitoring_agent
result = asyncio.run(run_monitoring_agent('full'))
"
```

---

## 📋 **Recommended Deployment Workflow**

### **For Development/Testing:**
1. **Individual Testing:** Run each agent separately to test functionality
2. **Full System Test:** Use `python run_geo_system.py --mode full`
3. **Status Checks:** Use `python run_geo_system.py --status`

### **For Production:**
1. **Configure Environment:** Set up `.env` file with real API keys and settings
2. **Start Continuous Monitoring:** Use `python run_geo_system.py --continuous --interval 6`
3. **Monitor Health:** Regular status checks with `python run_geo_system.py --status`

---

## ⚙️ **Configuration Requirements**

### **Environment Variables (.env file):**
```bash
# Brand Configuration
BRAND_NAME="Brush on Block"
BRAND_WEBSITE="https://brushonblock.com"

# Monitoring Settings
MONITORING_ENABLED=true
REAL_TIME_MONITORING=true
MONITORING_INTERVAL_HOURS=6
ALERT_SENSITIVITY=medium

# Data Retention
DATA_RETENTION_DAYS=365
HISTORICAL_ANALYSIS_DAYS=90

# Output Settings
OUTPUT_DIR="./monitoring_results"
DASHBOARD_ENABLED=true

# Agent Integration Paths (update these for production)
AGENT1_RESULTS_PATH="../discovery_baseline_agent/results/latest/"
AGENT2_RESULTS_PATH="../content_analysis_agent/results/latest/"
AGENT3_RESULTS_PATH="../competitive_intelligence_agent/results/latest/"

# Notification Channels (configure for production)
SLACK_WEBHOOK_URL=""
EMAIL_ALERTS=""
SMS_ALERTS=""
```

### **Agent Result Paths:**
Update these paths in your `.env` file to point to where each agent saves its results:
- Agent 1 results: Discovery baseline analysis
- Agent 2 results: Content gap analysis and optimization opportunities
- Agent 3 results: Competitive intelligence and strategic insights

---

## 📊 **Monitoring Outputs**

All agents generate structured outputs in the `monitoring_results/` directory:

### **Generated Files:**
```
monitoring_results/
├── dashboards/
│   ├── main_geo_dashboard.html         # Technical dashboard
│   └── executive_dashboard.html        # Executive summary
├── agent_feedback/
│   ├── discovery_baseline_agent_latest_feedback.json
│   ├── content_analysis_agent_latest_feedback.json
│   └── competitive_intelligence_agent_latest_feedback.json
├── monitoring_run_YYYYMMDD_HHMMSS/
│   ├── MONITORING_EXECUTIVE_SUMMARY.md # Executive report
│   ├── alerts_summary.csv              # Alert details
│   └── monitoring_complete.json        # Full technical data
├── business_impact.db                  # ROI and business metrics
├── monitoring_data.db                  # Performance history
└── latest/                             # Symlink to latest results
```

### **Dashboard Access:**
- **Technical Dashboard:** Open `monitoring_results/dashboards/main_geo_dashboard.html`
- **Executive Dashboard:** Open `monitoring_results/dashboards/executive_dashboard.html`

---

## 🔄 **Automation Schedules**

### **Recommended Monitoring Intervals:**

| Use Case | Interval | Command |
|----------|----------|---------|
| **Development** | Manual | `python run_geo_system.py --mode full` |
| **Testing** | Daily | `python run_geo_system.py --continuous --interval 24` |
| **Production** | 6 hours | `python run_geo_system.py --continuous --interval 6` |
| **High-frequency** | 1 hour | `python run_geo_system.py --continuous --interval 1` |

### **Automated Reports:**
- **Daily:** Executive summary generated at 6 AM and 6 PM
- **Weekly:** Strategic report generated every Sunday at noon
- **Real-time:** Alerts generated immediately for critical issues

---

## 🚨 **Alert Management**

### **Alert Severity Levels:**
- **🔴 Critical:** Immediate response required (ROI decline >20%)
- **🟠 High:** Action needed within 24 hours (competitive threats)
- **🟡 Medium:** Review within 1 week (optimization opportunities)
- **🟢 Low:** FYI notifications (milestone achievements)

### **Notification Channels:**
- **Slack:** Real-time alerts with color-coded severity
- **Email:** Daily summaries and critical alerts
- **SMS:** Critical alerts only (configured per stakeholder)

---

## 📈 **Business Impact Tracking**

### **Key Metrics Monitored:**
- **ROI Performance:** Monthly investment vs. generated value
- **GEO Scores:** Discovery (target: 60), Context (target: 75), Competitive (target: 45)
- **Market Position:** Competitive ranking and market share
- **Conversion Funnel:** AI citations → website visits → purchases
- **Brand Value:** Qualified mention tracking and sentiment

### **Executive Reporting:**
- **Daily:** Performance snapshot with key metrics
- **Weekly:** Strategic trends and competitive analysis
- **Monthly:** Comprehensive ROI analysis and recommendations

---

## 🔧 **Troubleshooting**

### **Common Issues:**

**1. "No agent results available"**
```bash
# Solution: Run agents individually first to generate baseline data
python run_geo_system.py --mode discovery
python run_geo_system.py --mode content
python run_geo_system.py --mode competitive
python run_geo_system.py --mode monitoring
```

**2. "Monitoring not starting"**
```bash
# Check status
python run_geo_system.py --status

# Stop and restart
python run_geo_system.py --stop
python run_geo_system.py --continuous --interval 6
```

**3. "Agent integration failed"**
- Check that agent result paths in `.env` point to actual result files
- Ensure all agents have been run at least once
- Verify file permissions for result directories

---

## 🎯 **Success Metrics**

### **System Health Indicators:**
- ✅ **Data Quality Score:** >80/100
- ✅ **Alert Accuracy:** High
- ✅ **System Health:** Excellent
- ✅ **Agent Integration:** 3/3 healthy
- ✅ **ROI Performance:** Positive trending

### **Business KPIs:**
- 📈 **Discovery Score Improvement:** Target +10 points/month
- 📈 **Context Score Growth:** Target +15 points/month  
- 📈 **Competitive Position:** Maintain top 3 ranking
- 💰 **ROI Growth:** Target >200% return on investment
- 🎯 **Conversion Rate:** Track AI citations → purchases

---

## 🚀 **Ready to Deploy!**

**Choose your deployment approach:**

### **🥇 Recommended for Most Users:**
```bash
python run_geo_system.py --continuous --interval 6
```

### **🧪 For Testing:**
```bash
python run_geo_system.py --mode full
```

### **📊 Check Status Anytime:**
```bash
python run_geo_system.py --status
```

Your comprehensive GEO optimization system is ready for production deployment! 🎉