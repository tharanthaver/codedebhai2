# Firebase Domain Configuration Fix

## Issue: Cannot add `127.0.0.1:5000` to Firebase Authorized Domains

Firebase authorized domains don't accept IP addresses with ports. Here's how to fix this:

## ✅ Correct Firebase Authorized Domains

Add only these domains in Firebase Console:
1. **`localhost`** (for local development)
2. Your production domain (when you deploy)

### Steps:
1. Go to Firebase Console → Authentication → Settings → Authorized domains
2. Add only: `localhost`
3. Do NOT add IP addresses or ports

## 🔧 Code Modifications for Local Development

Since Firebase only accepts `localhost`, we need to ensure your Flask app runs on `localhost:5000` instead of `127.0.0.1:5000`.

### Option 1: Modify Flask App Configuration (Recommended)

Update your Flask app to explicitly bind to localhost:

```python
if __name__ == '__main__':
    app.run(
        host='localhost',  # Changed from '127.0.0.1' or '0.0.0.0'
        port=5000,
        debug=True
    )
```

### Option 2: Use URL Redirect Solution

If you must use `127.0.0.1`, you can set up a local redirect.

## 🔄 Alternative Solutions

### Solution 1: Update Flask Host Binding
Modify your app.py to run on localhost:

```python
# At the bottom of app.py, change the run configuration
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
```

### Solution 2: Use MSG91 or Other SMS Provider as Primary
Since you already have MSG91 configured, you can use it as the primary SMS provider and Firebase as backup.

### Solution 3: Browser Host File (Advanced)
Add this line to your hosts file:
- Windows: `C:\Windows\System32\drivers\etc\hosts`
- Add: `127.0.0.1 localhost`

## 🚀 Quick Fix Steps

1. **Update Flask Configuration:**
   ```python
   # In app.py, find the run configuration and change it to:
   if __name__ == '__main__':
       socketio.run(app, host='localhost', port=5000, debug=True)
   ```

2. **Firebase Console:**
   - Add only `localhost` to authorized domains
   - Remove any IP addresses

3. **Access Your App:**
   - Use `http://localhost:5000` instead of `http://127.0.0.1:5000`

4. **Test Firebase Auth:**
   - Go to `http://localhost:5000/firebase_auth`
   - Try phone authentication

## 🔍 Testing the Fix

After making these changes:
1. Stop your Flask app if running
2. Start it again with the new configuration
3. Open `http://localhost:5000/firebase_auth`
4. Try phone authentication
5. Check browser console for any remaining errors

## 📋 Troubleshooting

If you still get domain errors:
1. Clear browser cache and cookies
2. Try incognito/private mode
3. Check that you're accessing via `localhost` not `127.0.0.1`
4. Verify only `localhost` is in Firebase authorized domains
5. Wait a few minutes for Firebase changes to propagate

## ⚡ Immediate Action Required

Run this command to update your Flask app configuration:
```bash
# This will be done in the next step
```
