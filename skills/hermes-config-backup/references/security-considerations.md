# Security Considerations for Configuration Backups

When backing up Hermes Agent configuration, particularly the `.env` file containing sensitive credentials, follow these security guidelines:

## Risk Assessment
The `.env` file contains:
- API keys for LLM providers (OpenRouter, Google Gemini, DeepSeek, etc.)
- Tool API keys (Exa, Parallel, Firecrawl, FAL.ai, etc.)
- Platform credentials (Telegram bot token, Slack tokens, etc.)
- Service account credentials and other secrets

If compromised, these credentials could lead to:
- Unauthorized API usage and associated costs
- Access to connected services and accounts
- Potential data breaches or service abuse

## Backup Security Best Practices

### 1. Treat Backups as Sensitive Data
- Consider backup files as sensitive as the originals
- Apply the same protection level to backups as to live credentials
- Never store backups in publicly accessible locations

### 2. Encryption Options
For additional protection, consider encrypting the backup:

**Using GPG (recommended):**
```bash
# Encrypt after zip creation
gpg --symmetric --cipher-algo AES256 ~/ENV/temp/hermes.zip
# Creates hermes.zip.gpg - remove the plain zip after encryption
rm ~/ENV/temp/hermes.zip

# To decrypt later:
gpg --decrypt ~/ENV/temp/hermes.zip.gpg > /tmp/hermes.zip
unzip /tmp/hermes.zip -d /tmp/restore
# Clean up decrypted copy
rm /tmp/hermes.zip
```

**Using OpenSSL:**
```bash
openssl enc -aes-256-cbc -salt -in ~/ENV/temp/hermes.zip -out ~/ENV/temp/hermes.zip.enc
# Remove plain version after encryption
rm ~/ENV/temp/hermes.zip
```

### 3. Secure Storage Locations
- Encrypted external drives
- Password managers with file attachment capabilities (1Password, Bitwarden, etc.)
- Encrypted cloud storage (with client-side encryption)
- Secure offline storage (USB drives in safe)

### 4. Access Control
- Set restrictive file permissions: `chmod 600` on backup files
- Limit who can access backup locations
- Monitor access to backup storage

### 5. Backup Lifecycle Management
- Regularly rotate backups (keep multiple versions)
- Test restore procedures periodically
- Securely delete old backups when no longer needed
- Consider expiration dates for backup retention

### 6. During the Backup Process
- Use secure temporary directories (avoid world-writable /tmp if possible)
- Clean up temporary files immediately after backup
- Verify backup integrity before deleting source
- Never email backup files or transfer over unencrypted channels

## Specific to Telegram Bot Token
The Telegram bot token in particular grants full control over your bot:
- Anyone with the token can send messages as your bot
- They can read all messages users send to the bot
- They can modify bot settings and configurations
- Treat it with the same care as a password

## Restore Procedures
When restoring from backup:
1. Verify the backup source is trusted
2. Restore to a secure location first (not directly to ~/.hermes)
3. Verify file contents before copying to production
4. Set appropriate permissions: `chmod 600 ~/.hermes/.env`
5. Consider rotating credentials after restore if breach is suspected

## Automated Backup Security
If using automated backup scripts:
- Ensure scripts themselves are secured (proper permissions)
- Avoid logging sensitive information
- Use secure methods for any encryption passphrases
- Limit script execution permissions to trusted users

## Emergency Response
If you suspect a backup has been compromised:
1. Immediately revoke/rotate all credentials in the backup
2. Start with critical services: Telegram bot token, API keys with billing
3. Audit recent activity for unauthorized access
4. Review backup storage access logs if available