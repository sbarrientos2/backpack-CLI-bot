# Security Best Practices

## API Key Security

### Critical Security Rules

1. **NEVER commit your `.env` file to git**
   - The `.env` file contains your actual API keys
   - Always check git status before committing
   - Verify `.env` is in `.gitignore`

2. **Protect your API keys like passwords**
   - Never share them via email, chat, or screenshots
   - Don't paste them in bug reports or support tickets
   - Don't store them in cloud documents or notes apps

3. **Rotate your API keys regularly**
   - Change keys at least monthly
   - Immediately rotate if you suspect compromise
   - Rotate after team member changes

4. **Use API key restrictions**
   - Set IP whitelist restrictions on Backpack Exchange
   - Use read-only keys for monitoring/analytics features
   - Use trading keys only when necessary

### How to Check if Your Keys Are Compromised

Run these commands to check if `.env` was ever committed to git:

```bash
# Check if .env is in git history
git log --all --full-history -- .env

# Check if .env is tracked by git
git ls-files .env

# Search for API keys in all commits
git log -p --all -S 'BACKPACK_API_KEY'
```

If any of these return results, **your keys are compromised** and must be rotated immediately.

### What to Do if Keys Are Compromised

1. **Immediately revoke compromised keys** on Backpack Exchange
2. **Generate new API keys** with proper restrictions
3. **Update your `.env` file** with new keys
4. **Check account activity** for unauthorized trades
5. **Enable 2FA** if not already enabled
6. **If keys were in public repo**: Assume they're compromised even after deletion

### Setting Up API Keys Securely

**IMPORTANT: Sub-Account vs Main Account**

Backpack Exchange uses sub-accounts to isolate funds and positions:
- **Main Account**: Your primary account with full balance and perpetual positions
- **Sub-Accounts**: Isolated accounts (like "CLI Bot", "Market Maker", etc.)

**API keys are account-specific!** If you create API keys while viewing a sub-account, those keys can only access that sub-account's data.

**To see perpetual positions in the bot:**
1. Switch to your **Main account** in Backpack Exchange (look for the "M" icon)
2. Go to Settings → API **while on the Main account**
3. Create new API keys
4. Update your `.env` file with these keys

**Current limitation:** If you see "Positions unavailable - Use Main account API keys", your current API keys are from a sub-account without perpetual trading access.

**Steps to set up:**

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual keys:
   ```bash
   nano .env  # or use your preferred editor
   ```

3. Verify `.env` is in `.gitignore`:
   ```bash
   cat .gitignore | grep ".env"
   ```

4. Check git won't commit it:
   ```bash
   git status  # .env should NOT appear here
   ```

## Runtime Security

### File Permissions

Set restrictive permissions on your `.env` file:

```bash
chmod 600 .env  # Only you can read/write
```

### Environment Isolation

- Use Python virtual environments (`venv`)
- Don't run the bot with root/admin privileges
- Run in isolated containers if possible

### Network Security

- Use HTTPS/WSS connections only (already configured)
- Run on trusted networks
- Consider VPN for additional protection
- Monitor for unusual API activity

## Code Security

### Error Handling

- Error messages are sanitized to prevent key leakage
- Authentication errors don't expose response details
- Errors are truncated to 200 characters

### Dependencies

- Regularly update dependencies: `pip install --upgrade -r requirements.txt`
- Check for security vulnerabilities: `pip-audit`
- Only install packages from trusted sources

## Operational Security

### Backup Security

- Exclude `.env` from backups when possible
- Encrypt backups containing sensitive data
- Use secure backup storage

### Shared Systems

- Don't run on shared hosting
- Use dedicated servers or local machines
- Clear terminal history after viewing keys:
  ```bash
  history -c  # Clear bash history
  ```

### Screen Sharing

- Close the application before screen sharing
- Don't share terminal windows with API activity
- Be aware of recording software

## Monitoring

### Watch for Suspicious Activity

- Unexpected trades or orders
- Login from unusual locations
- API calls you didn't make
- Balance changes you didn't authorize

### Audit Regularly

- Review API key permissions monthly
- Check active API sessions
- Monitor account activity logs
- Review order history

## Quick Security Checklist

- [ ] `.env` file is NOT committed to git
- [ ] `.env` has restrictive file permissions (600)
- [ ] API keys have IP restrictions enabled
- [ ] API keys are rotated monthly
- [ ] Dependencies are up to date
- [ ] 2FA is enabled on exchange account
- [ ] Monitoring is set up for unusual activity
- [ ] Backups are encrypted and secured

## Emergency Contacts

If you believe your account is compromised:

1. **Backpack Exchange Support**: support@backpack.exchange
2. **Revoke API Keys**: https://backpack.exchange/settings/api
3. **Change Password**: https://backpack.exchange/settings/security

## Additional Resources

- [Backpack API Documentation](https://docs.backpack.exchange/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Secure Coding Best Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
