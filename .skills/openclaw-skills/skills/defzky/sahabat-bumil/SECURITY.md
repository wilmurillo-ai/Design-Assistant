# Security Information

## 🔒 Security Overview

**Sahabat Bumil** is designed with user privacy and security in mind. This document explains the security considerations for this skill.

---

## ✅ Security Checklist

| Aspect | Status | Details |
|--------|--------|---------|
| **No External API Calls** | ✅ | Code does NOT make any HTTP requests |
| **No Credentials Required** | ✅ | No API keys, tokens, or secrets needed |
| **Local Data Storage** | ✅ | All data stored in `~/.openclaw/` |
| **No Elevated Privileges** | ✅ | Runs with normal user permissions |
| **No Persistence** | ✅ | Does not modify system files |
| **Open Source** | ✅ | Full code available on GitHub |

---

## 📦 Dependencies

### **requests (requests>=2.28.0)**

**Why Included:**
- Currently **NOT USED** in the code
- Included for **potential future features**:
  - Fetching hospital data from APIs
  - Nutrition database updates
  - Online prenatal class finder

**Current Usage:**
```python
# No actual HTTP calls in current version
# requests library is available but not used
```

**Security Impact:**
- ✅ Low risk - library is well-maintained
- ✅ No network calls in current version
- ✅ Can be verified by auditing code

---

## 🗄️ Data Storage

### **Local Files Created:**

| File | Location | Purpose |
|------|----------|---------|
| `pregnancy_contractions.json` | `~/.openclaw/` | Contraction timing data |
| `pregnancy_kicks.json` | `~/.openclaw/` | Baby movement tracking |

**Data Never Leaves Your Device:**
- ❌ No data sent to external servers
- ❌ No telemetry or analytics
- ❌ No cloud synchronization
- ✅ All data stays local

---

## 🔍 Code Audit

### **Network Calls:**

```bash
# Search for network-related code
grep -r "requests\." src/
grep -r "http" src/
grep -r "socket" src/
```

**Result:** ✅ No network calls found in current version

### **File Access:**

**Files Accessed:**
- ✅ `~/.openclaw/pregnancy_*.json` (own data files)
- ✅ Standard Python libraries only

**Files NOT Accessed:**
- ❌ System files
- ❌ Other application data
- ❌ User documents
- ❌ Browser data
- ❌ Credentials/secrets

---

## 🏥 Medical Disclaimer

**IMPORTANT:** This skill provides **informational guidance only**.

**NOT a Substitute For:**
- ❌ Professional medical advice
- ❌ Doctor consultations
- ❌ Emergency services

**Always Consult:**
- ✅ Your doctor/midwife
- ✅ Healthcare professionals
- ✅ Emergency services (118/119 in Indonesia)

**Code References:**
- `SKILL.md` - Contains explicit medical disclaimers
- `indonesian_nutrition.py` - States "consult your doctor"
- `contraction_timer.py` - Emergency contact guidance

---

## 🔐 Installation Safety

### **Recommended Installation:**

```bash
# 1. Install in isolated environment (recommended)
python3 -m venv venv
source venv/bin/activate

# 2. Install skill
git clone https://github.com/defzky/openclaw-sahabat-bumil.git
cd sahabat-bumil
pip install -r requirements.txt
```

### **Audit Before Installing:**

```bash
# 1. Check for network calls
grep -r "requests.post\|requests.get" src/

# 2. Check for system commands
grep -r "subprocess\|os.system" src/

# 3. Check for file access
grep -r "open(" src/ | grep -v ".json"

# 4. Review SKILL.md for hidden characters
cat -A SKILL.md | grep -v "^\$"
```

---

## 📊 VirusTotal Scan

**Status:** Pending

**Expected Results:**
- ✅ No malware detected
- ✅ No suspicious patterns
- ⚠️ `requests` library flagged (normal - it's a common library)
- ℹ️ Control characters (CLEANED in v1.1.0)

---

## 🐛 Known Issues

**None** - No security vulnerabilities known.

---

## 📞 Reporting Security Issues

**Found a security issue?**

1. **DO NOT** create public GitHub issue
2. **Email:** dev.fajrizky@gmail.com
3. **Include:** Description, steps to reproduce, potential impact

**Response Time:** Within 48 hours

---

## ✅ Security Best Practices for Users

1. **Review Code** - Audit before installing
2. **Use Virtual Environment** - Isolate installation
3. **Check Permissions** - Don't run with elevated privileges
4. **Monitor Network** - Use firewall to monitor outbound connections
5. **Backup Data** - Regular backups of `~/.openclaw/`
6. **Keep Updated** - Update when security patches released

---

## 📝 Version History

| Version | Date | Security Changes |
|---------|------|------------------|
| **1.1.0** | 2026-04-07 | Removed control characters, added SECURITY.md |
| **1.0.0** | 2026-04-07 | Initial release |

---

## 🔗 Resources

- **GitHub:** https://github.com/defzky/openclaw-sahabat-bumil
- **ClawHub:** https://clawhub.ai/defzky/sahabat-bumil
- **Report Issue:** dev.fajrizky@gmail.com

---

**Last Updated:** 2026-04-07  
**Author:** Bowo (Fajrizky)
