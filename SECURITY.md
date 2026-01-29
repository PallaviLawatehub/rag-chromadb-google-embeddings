# 🔐 Security Guidelines for RAG Application

## Critical Security Rules

### 1. **Never Commit API Keys**

- `.env` file is in `.gitignore` - it will NOT be committed
- Always use `.env.example` as a template for developers
- Use `git status` to verify `.env` is not staged before committing

### 2. **API Key Management**

#### Google Gemini API Key

- Get from: https://aistudio.google.com/apikey
- Store ONLY in `.env` file
- Rotate if exposed (generate new key, delete old one)
- Enable billing alerts in Google Cloud Console

#### ChromaDB Cloud API Key

- Store ONLY in `.env` file
- Treat like a password

### 3. **What NOT to Do**

❌ Hardcode API keys in Python files
❌ Commit `.env` file to Git
❌ Share API keys in chat/email/Slack
❌ Use API keys on client-side (browser/mobile)
❌ Log API keys to console

### 4. **What TO Do**

✅ Store keys in `.env` file (git-ignored)
✅ Use `os.getenv("KEY_NAME")` to load them
✅ Rotate keys periodically
✅ Use different keys for dev/prod
✅ Enable IP restrictions if available
✅ Monitor usage for unusual activity

### 5. **Setup for New Developers**

1. Copy `.env.example` to `.env`
2. Add actual API keys to `.env`
3. Never commit `.env` file
4. Verify with `git status` before pushing

## Current Security Status

✅ All API keys are stored in `.env` (git-ignored)
✅ All code uses `os.getenv()` to load keys
✅ `.gitignore` properly configured
✅ `.env.example` provided as template

## If API Key is Compromised

1. **Immediately delete the old key** from Google Cloud Console
2. **Generate a new API key**
3. **Update `.env` file** with new key
4. **Force push** if old key was accidentally committed:
   ```bash
   git filter-branch --tree-filter 'rm -f .env' HEAD
   git push --force
   ```

## Additional Resources

- Google Gemini API Security: https://ai.google.dev/docs
- ChromaDB Security: https://docs.trychroma.com/
- Git Security: https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work
