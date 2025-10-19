# Firebase SMS OTP Authentication Fix Guide

## Error: "Failed to send SMS OTP. Firebase: Hostname match not found (auth/captcha-check-failed)"

This error occurs when Firebase authentication is not properly configured for your domain/hostname. Here's a comprehensive fix:

## 1. Firebase Console Configuration

### Step 1: Add Authorized Domains
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `codedebhai-454b5`
3. Navigate to **Authentication** → **Settings** → **Authorized domains**
4. Add these domains:
   - `localhost` (for local development)
   - `127.0.0.1` (alternative localhost)
   - Your production domain (if any)

### Step 2: Configure Phone Authentication
1. In Firebase Console, go to **Authentication** → **Sign-in method**
2. Enable **Phone** authentication
3. Add your phone numbers to the **Phone numbers for testing** section if needed

### Step 3: reCAPTCHA Configuration
1. Go to **Authentication** → **Settings** → **Advanced**
2. Check **Enable reCAPTCHA verification**
3. Configure reCAPTCHA domains to include:
   - `localhost:5000`
   - `127.0.0.1:5000`
   - Your production domain

## 2. Code Fixes Applied

### Enhanced Error Handling
- Added specific error handling for `auth/captcha-check-failed`
- Better reCAPTCHA initialization and reset logic
- Improved user feedback for different error scenarios

### reCAPTCHA Improvements
- Proper reCAPTCHA lifecycle management
- Automatic re-initialization on errors
- Better validation before sending OTP

### Firebase Configuration
- Set authentication language to English
- Enhanced phone number validation
- Better session management

## 3. Testing the Fix

Run the test script to verify Firebase configuration:

```powershell
python test_firebase_config.py
```

## 4. Common Solutions

### Solution 1: Clear Browser Data
- Clear browser cache and cookies
- Disable browser extensions that might interfere
- Try in incognito/private mode

### Solution 2: Check Network
- Ensure stable internet connection
- Try different network if using corporate/restricted network
- Check if Firebase services are blocked

### Solution 3: Verify Project Configuration
- Double-check Firebase project ID matches in code
- Verify API keys are correct and active
- Ensure Firebase project has billing enabled (required for SMS)

### Solution 4: Domain Verification
- For production, verify domain ownership in Firebase Console
- Add domain to OAuth redirect domains
- Update CORS settings if needed

## 5. Environment-Specific Fixes

### Local Development
- Use `localhost:5000` in authorized domains
- Enable testing phone numbers
- Use visible reCAPTCHA for easier debugging

### Production
- Add production domain to authorized domains
- Configure proper SSL certificates
- Use invisible reCAPTCHA for better UX

## 6. Troubleshooting Steps

1. **Check Browser Console**: Look for specific Firebase error codes
2. **Verify Network**: Test from different devices/networks
3. **Firebase Status**: Check Firebase status page for outages
4. **API Limits**: Verify SMS quotas and billing status
5. **Project Settings**: Confirm all configuration matches

## 7. Alternative Solutions

If Firebase continues to fail, the system can fallback to:
- MSG91 SMS service (already configured)
- Twilio SMS service
- Other OTP providers

## 8. Monitoring and Logging

- Enhanced error logging added to track issues
- Browser console logs for debugging
- Server-side Firebase admin SDK logs

## Files Modified

1. `templates/firebase_auth.html` - Enhanced error handling and reCAPTCHA management
2. `firebase_otp.py` - Backend Firebase integration (already configured)
3. `app.py` - Routes for OTP verification (already configured)

## Next Steps

1. Apply the Firebase Console configurations above
2. Test with the provided test script
3. Monitor error logs for any remaining issues
4. Consider implementing fallback SMS providers if needed
