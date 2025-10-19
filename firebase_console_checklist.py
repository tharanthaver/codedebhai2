#!/usr/bin/env python3
"""
Firebase Console Configuration Checklist
Interactive script to guide through Firebase Console settings
"""

import webbrowser
import sys
from datetime import datetime

def print_header():
    """Print script header"""
    print("🔥 Firebase Console Configuration Checklist")
    print("=" * 50)
    print(f"Project: codedebhai-454b5")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

def open_firebase_console():
    """Open Firebase Console in browser"""
    console_url = "https://console.firebase.google.com/project/codedebhai-454b5"
    print(f"\n🌐 Opening Firebase Console: {console_url}")
    
    try:
        webbrowser.open(console_url)
        print("✅ Firebase Console opened in browser")
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print(f"   Please manually open: {console_url}")

def check_authorized_domains():
    """Guide through authorized domains configuration"""
    print("\n" + "="*50)
    print("1️⃣  AUTHORIZED DOMAINS CONFIGURATION")
    print("="*50)
    
    print("\n📍 Navigation Path:")
    print("   Firebase Console → Authentication → Settings → Authorized domains")
    
    print("\n✅ Required domains to add:")
    domains = [
        "localhost",
        "127.0.0.1",
        "localhost:5000",
        "127.0.0.1:5000"
    ]
    
    for domain in domains:
        print(f"   • {domain}")
    
    print("\n📝 Steps:")
    print("   1. Click 'Add domain' button")
    print("   2. Enter each domain listed above")
    print("   3. Click 'Add' for each domain")
    print("   4. Verify all domains are listed")
    
    response = input("\n❓ Have you added all required domains? (y/n): ").lower().strip()
    return response == 'y'

def check_phone_authentication():
    """Guide through phone authentication setup"""
    print("\n" + "="*50)
    print("2️⃣  PHONE AUTHENTICATION SETUP")
    print("="*50)
    
    print("\n📍 Navigation Path:")
    print("   Firebase Console → Authentication → Sign-in method")
    
    print("\n📝 Steps:")
    print("   1. Find 'Phone' in the sign-in providers list")
    print("   2. Click on 'Phone' to configure")
    print("   3. Toggle 'Enable' switch to ON")
    print("   4. Click 'Save'")
    
    print("\n🔧 Optional: Test Phone Numbers")
    print("   • You can add test phone numbers for development")
    print("   • Format: +91XXXXXXXXXX (with your test number)")
    print("   • Add a 6-digit verification code (e.g., 123456)")
    
    response = input("\n❓ Is Phone authentication enabled? (y/n): ").lower().strip()
    return response == 'y'

def check_recaptcha_settings():
    """Guide through reCAPTCHA configuration"""
    print("\n" + "="*50)
    print("3️⃣  reCAPTCHA CONFIGURATION")
    print("="*50)
    
    print("\n📍 Navigation Path:")
    print("   Firebase Console → Authentication → Settings → Advanced")
    
    print("\n📝 Steps:")
    print("   1. Scroll down to 'Advanced settings'")
    print("   2. Find 'Enable reCAPTCHA Verification'")
    print("   3. Ensure it's ENABLED (this is usually enabled by default)")
    print("   4. Note: reCAPTCHA domains should automatically include your authorized domains")
    
    print("\n⚠️  Important Notes:")
    print("   • reCAPTCHA is required for phone authentication")
    print("   • It should work automatically with your authorized domains")
    print("   • If issues persist, check Google Cloud Console for reCAPTCHA settings")
    
    response = input("\n❓ Is reCAPTCHA verification enabled? (y/n): ").lower().strip()
    return response == 'y'

def check_billing_status():
    """Guide through billing verification"""
    print("\n" + "="*50)
    print("4️⃣  BILLING VERIFICATION")
    print("="*50)
    
    print("\n⚠️  CRITICAL: SMS authentication requires billing to be enabled!")
    
    print("\n📍 Navigation Path:")
    print("   Firebase Console → Project Settings (gear icon) → Usage and billing")
    
    print("\n📝 Steps:")
    print("   1. Click on project settings (gear icon)")
    print("   2. Go to 'Usage and billing' tab")
    print("   3. Check if you're on 'Blaze (Pay as you go)' plan")
    print("   4. If not, click 'Modify plan' and upgrade to Blaze plan")
    
    print("\n💰 Cost Information:")
    print("   • SMS verification costs approximately $0.05 per SMS")
    print("   • First 10,000 verifications per month are free")
    print("   • You can set spending limits to control costs")
    
    response = input("\n❓ Is billing enabled (Blaze plan)? (y/n): ").lower().strip()
    return response == 'y'

def check_project_settings():
    """Verify project settings"""
    print("\n" + "="*50)
    print("5️⃣  PROJECT SETTINGS VERIFICATION")
    print("="*50)
    
    print("\n📍 Navigation Path:")
    print("   Firebase Console → Project Settings (gear icon) → General")
    
    print("\n✅ Verify these settings:")
    print("   • Project ID: codedebhai-454b5")
    print("   • Web API Key should be present")
    print("   • Default GCP resource location should be set")
    
    print("\n📝 If you need to add a web app:")
    print("   1. Scroll to 'Your apps' section")
    print("   2. Click 'Add app' → Web app")
    print("   3. Give it a name (e.g., 'CodeDeBhai Web')")
    print("   4. Copy the config object (this should match your HTML template)")
    
    response = input("\n❓ Are project settings correct? (y/n): ").lower().strip()
    return response == 'y'

def run_final_test():
    """Suggest running the final test"""
    print("\n" + "="*50)
    print("6️⃣  FINAL TESTING")
    print("="*50)
    
    print("\n🧪 After completing all configurations:")
    print("   1. Run your Flask app: python app.py")
    print("   2. Navigate to: http://localhost:5000/firebase_auth")
    print("   3. Test phone authentication with your number")
    print("   4. Check browser console for any errors")
    
    print("\n🔍 Troubleshooting:")
    print("   • Clear browser cache if issues persist")
    print("   • Try incognito/private mode")
    print("   • Check browser console for detailed error messages")
    print("   • Verify network connection")

def main():
    """Main checklist function"""
    print_header()
    
    # Open Firebase Console
    open_console = input("\n❓ Open Firebase Console in browser? (y/n): ").lower().strip()
    if open_console == 'y':
        open_firebase_console()
    
    print("\n🚀 Let's go through the configuration checklist...")
    
    # Run through all checks
    checks = [
        ("Authorized Domains", check_authorized_domains),
        ("Phone Authentication", check_phone_authentication),
        ("reCAPTCHA Configuration", check_recaptcha_settings),
        ("Billing Status", check_billing_status),
        ("Project Settings", check_project_settings)
    ]
    
    results = []
    
    for check_name, check_function in checks:
        try:
            result = check_function()
            results.append((check_name, result))
        except KeyboardInterrupt:
            print("\n\n⏹️  Configuration interrupted by user")
            return 1
        except Exception as e:
            print(f"\n❌ Error during {check_name} check: {e}")
            results.append((check_name, False))
    
    # Print summary
    print("\n" + "="*50)
    print("📋 CONFIGURATION SUMMARY")
    print("="*50)
    
    all_passed = True
    for check_name, result in results:
        status = "✅ COMPLETE" if result else "❌ INCOMPLETE"
        print(f"   {check_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\n🎯 Overall Status: {'✅ ALL CONFIGURED' if all_passed else '⚠️  NEEDS ATTENTION'}")
    
    if all_passed:
        print("\n🎉 Great! All Firebase configurations appear to be complete.")
        print("   You should now be able to use Firebase SMS authentication.")
        run_final_test()
    else:
        print("\n⚠️  Please complete the incomplete configurations above.")
        print("   Then run this script again to verify.")
    
    print("\n📚 Additional Resources:")
    print("   • Firebase Auth Documentation: https://firebase.google.com/docs/auth")
    print("   • Phone Auth Guide: https://firebase.google.com/docs/auth/web/phone-auth")
    print("   • Troubleshooting Guide: ./FIREBASE_SMS_OTP_FIX.md")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Script interrupted by user")
        sys.exit(1)
