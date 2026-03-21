---
name: security-patterns
version: "1.0.0"
description: Security vulnerability patterns, OWASP Top 10, and remediation strategies. Use when analyzing code for security issues or providing security recommendations.
allowed-tools: Read, Grep, Glob, WebSearch
---

# Security Patterns

Security analysis and vulnerability detection patterns.

## Skill Usage

| Aspect | Details |
|--------|---------|
| **Consumer** | `subagent-security-analyst` |
| **Purpose** | Security vulnerability detection and remediation |
| **Invocation** | Security subagent reads this skill; NOT directly invocable by users |
| **Related Skills** | `shared-patterns` |

---

## Quick Security Checklist

### Critical Security Issues (FAIL)

- [ ] SQL/NoSQL injection vulnerabilities
- [ ] XSS (Cross-Site Scripting) vulnerabilities
- [ ] Authentication bypass
- [ ] Hardcoded secrets in code
- [ ] Missing authorization checks
- [ ] Command injection vulnerabilities

### High Priority (CONCERNS)

- [ ] Weak password policies
- [ ] Missing rate limiting
- [ ] Insecure session management
- [ ] Missing security headers
- [ ] Outdated dependencies with CVEs
- [ ] Verbose error messages

### Medium Priority

- [ ] Missing input validation
- [ ] Insufficient logging
- [ ] Missing CSRF protection
- [ ] Insecure file uploads

---

## Quick Vulnerability Detection

### SQL/NoSQL Injection

```typescript
// ❌ VULNERABLE
const query = `SELECT * FROM users WHERE id = '${userId}'`
const user = await db.find({ username: req.body.username })

// ✅ SECURE
const query = 'SELECT * FROM users WHERE id = ?'
const user = await db.find({ username: { $eq: req.body.username } })
```

### XSS Prevention

```typescript
// ❌ VULNERABLE
element.innerHTML = userInput
<div dangerouslySetInnerHTML={{__html: userInput}} />

// ✅ SECURE
element.textContent = userInput
<div>{userInput}</div>
```

### Authentication

```typescript
// ❌ VULNERABLE
if (user.password === req.body.password) { /* login */ }

// ✅ SECURE
import bcrypt from 'bcrypt'
if (await bcrypt.compare(req.body.password, user.passwordHash)) { /* login */ }
```

---

## Detailed Security Guides

For comprehensive security patterns, see:

- **[owasp-top-10.md](owasp-top-10.md)** - OWASP Top 10 vulnerabilities
  - A01:2021 - Broken Access Control
  - A02:2021 - Cryptographic Failures
  - A03:2021 - Injection
  - A04:2021 - Insecure Design
  - A05:2021 - Security Misconfiguration
  - And more...

- **[vulnerability-detection.md](vulnerability-detection.md)** - Detection patterns
  - Code smell patterns
  - Regex patterns for finding vulnerabilities
  - Common anti-patterns
  - Static analysis techniques

- **[remediation-patterns.md](remediation-patterns.md)** - Fix strategies
  - Authentication fixes
  - Authorization patterns
  - Input validation
  - Error handling

- **[security-headers.md](security-headers.md)** - HTTP security headers
  - Content-Security-Policy
  - X-Frame-Options
  - Strict-Transport-Security

---

## Severity Levels

| Severity | Description | Action |
|----------|-------------|--------|
| **Critical** | Remote code execution, auth bypass, data breach | IMMEDIATE FIX |
| **High** | Privilege escalation, XSS, CSRF | FIX BEFORE DEPLOY |
| **Medium** | Info disclosure, weak crypto | FIX IN SPRINT |
| **Low** | Missing headers, verbose errors | BACKLOG |
| **Info** | Best practice violations | DOCUMENT |

---

## Security Report Format

```markdown
## [CRITICAL/HIGH/MEDIUM/LOW] Vulnerability Name

- **Location**: `path/to/file.ts:line`
- **Category**: OWASP A0X - Category Name
- **Description**: What the vulnerability is
- **Impact**: What could happen if exploited
- **Proof of Concept**: How it could be exploited
- **Remediation**: Specific fix with code example
- **References**: CVE numbers, documentation links
```

---

## When to Consult This Skill

- Analyzing code for security vulnerabilities
- Reviewing authentication/authorization flows
- Auditing dependencies for CVEs
- Implementing security best practices
- Responding to security incidents
