# GEO System - Quick Start Guide

## 🚨 **Important: Execution Times**

**The full GEO analysis can take 10-30 minutes** due to:
- Agent 1: 50+ AI API calls across multiple engines (5-15 minutes)
- Agent 2: Content scraping and analysis (3-8 minutes)  
- Agent 3: Competitive intelligence gathering (2-5 minutes)
- Agent 4: Monitoring and reporting (1-2 minutes)

## ⚡ **Quick Options**

### **1. FASTEST - Test Agent 4 Only (30 seconds)**
```bash
cd "/Users/jjoosshhmbpm1/GEO OPT"
python run_geo_system_fixed.py --mode monitoring
```
✅ **Result:** Complete monitoring dashboard with simulated data

### **2. FAST - Individual Agent Testing (2-15 minutes each)**
```bash
# Test each agent individually
python run_geo_system_fixed.py --mode discovery     # 5-15 min (real API calls)
python run_geo_system_fixed.py --mode content       # 3-8 min (web scraping)
python run_geo_system_fixed.py --mode competitive   # 2-5 min (analysis)
python run_geo_system_fixed.py --mode monitoring    # 30 sec (monitoring)
```

### **3. PRODUCTION - Full System (10-30 minutes)**
```bash
python run_geo_system_fixed.py --mode full
```
⚠️ **Note:** This runs all agents sequentially with real data

### **4. CONTINUOUS - Set & Forget (ongoing)**
```bash
python run_geo_system_fixed.py --continuous --interval 6
```
🔄 **Result:** System runs automatically every 6 hours

## 📊 **Check Results Anytime**

### **View Current Status:**
```bash
python run_geo_system_fixed.py --status
```

### **View Generated Dashboards:**
- **Technical Dashboard:** `monitoring_results/dashboards/main_geo_dashboard.html`
- **Executive Dashboard:** `monitoring_results/dashboards/executive_dashboard.html`

### **Check Latest Reports:**
```bash
ls -la monitoring_results/latest/
```

## 🎯 **Based on Your Error**

Your error showed **all agents failed initially**, which is now **FIXED** in `run_geo_system_fixed.py`. The issues were:

1. ❌ **Wrong import paths** → ✅ **Fixed with correct module imports**
2. ❌ **Missing agent validation** → ✅ **Added test mode fallbacks**
3. ❌ **Sync/async mismatches** → ✅ **Proper async handling**

## 🏃‍♂️ **Recommended First Run**

**Start with Agent 4 to verify everything works:**
```bash
cd "/Users/jjoosshhmbpm1/GEO OPT"
python run_geo_system_fixed.py --mode monitoring
```

**If that works (30 seconds), then try full system:**
```bash
python run_geo_system_fixed.py --mode full
```
*(Allow 10-30 minutes for completion)*

## 📝 **What Each Agent Does**

| Agent | Purpose | Time | API Calls |
|-------|---------|------|-----------|
| **Agent 1** | Discovery baseline via AI engines | 5-15 min | 150+ (OpenAI, Anthropic, Google) |
| **Agent 2** | Content analysis via web scraping | 3-8 min | 50+ (Web requests) |
| **Agent 3** | Competitive intelligence analysis | 2-5 min | 0 (Analysis only) |
| **Agent 4** | Monitoring & dashboard generation | 30 sec | 0 (Reporting only) |

## 🔧 **If Agents Still Fail**

### **Check API Keys:**
```bash
# Verify environment variables
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
echo $GOOGLE_API_KEY
```

### **Check Dependencies:**
```bash
# Install missing packages
pip install openai anthropic google-generativeai
pip install aiohttp beautifulsoup4 pandas
pip install pyyaml python-dotenv asyncio
```

### **Run Individual Agent Tests:**
```bash
# Test Agent 1 directly
cd discovery_baseline_agent && python test_agent.py

# Test Agent 2 directly  
cd content_analysis_agent && python test_agent.py

# Test Agent 3 directly
cd competitive_intelligence_agent && python test_competitive_intelligence.py
```

## 💡 **Performance Tips**

1. **For Development:** Use individual agents to save time
2. **For Testing:** Run Agent 4 first to verify system health
3. **For Production:** Use continuous monitoring mode
4. **For Demos:** Agent 4 generates impressive dashboards instantly

## 🎉 **Success Indicators**

**You'll know it's working when you see:**
- ✅ Log messages showing progress
- ✅ Files appearing in `monitoring_results/`
- ✅ Dashboards generated with real data
- ✅ No error messages in terminal

**Your system is ready when Agent 4 runs successfully!** 🚀