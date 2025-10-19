#!/usr/bin/env python3
import sys
sys.path.append('.')

from app import deepseek_manager, claude_manager
import time

def check_api_status():
    print('=== API KEY STATUS DIAGNOSIS ===')
    current_time = time.time()
    
    print('\n🔍 DeepSeek Keys Status:')
    deepseek_stats = deepseek_manager.get_stats()
    deepseek_available_count = 0
    
    for i, stats in deepseek_stats.items():
        rate_limited = stats['rate_limited_until'] > current_time
        time_until_available = max(0, stats['rate_limited_until'] - current_time)
        requests = stats['requests']
        failures = stats['failures']
        
        if not rate_limited:
            deepseek_available_count += 1
            status = "✅ AVAILABLE"
        else:
            status = f"❌ RATE LIMITED ({time_until_available:.1f}s)"
        
        print(f'  Key {i+1}: {status} | Requests: {requests} | Failures: {failures}')
    
    print(f'\n📊 DeepSeek Summary: {deepseek_available_count}/{len(deepseek_stats)} keys available')
    
    print('\n🧠 Claude Keys Status:')
    claude_stats = claude_manager.get_stats()
    claude_available_count = 0
    
    for i, stats in claude_stats.items():
        rate_limited = stats['rate_limited_until'] > current_time
        time_until_available = max(0, stats['rate_limited_until'] - current_time)
        consecutive_errors = stats['consecutive_errors']
        requests = stats['requests']
        failures = stats['failures']
        concurrent = stats['concurrent_connections']
        
        # Check if key is actually available
        key_available = claude_manager.is_key_available(i)
        
        if key_available:
            claude_available_count += 1
            status = "✅ AVAILABLE"
        elif rate_limited:
            status = f"❌ RATE LIMITED ({time_until_available:.1f}s)"
        elif consecutive_errors >= 3:
            status = f"🚫 ERROR COOLDOWN ({consecutive_errors} errors)"
        else:
            status = "⚠️ UNAVAILABLE"
        
        print(f'  Key {i+1}: {status} | Requests: {requests} | Failures: {failures} | Errors: {consecutive_errors} | Concurrent: {concurrent}')
    
    print(f'\n📊 Claude Summary: {claude_available_count}/{len(claude_stats)} keys available')
    
    # Overall recommendation
    print('\n🔧 PERFORMANCE ANALYSIS:')
    if deepseek_available_count == 0 and claude_available_count == 0:
        print('❌ CRITICAL: All API keys are unavailable! This is why processing is slow.')
        print('   Solution: Wait for rate limits to reset or check API key validity.')
    elif deepseek_available_count > 0:
        print(f'✅ DeepSeek keys available: {deepseek_available_count}')
        print('   Processing should use DeepSeek (faster, concurrent processing)')
    elif claude_available_count > 0:
        print(f'⚠️ Only Claude keys available: {claude_available_count}')
        print('   Processing will be SLOWER (sequential processing to avoid concurrent connection limits)')
    
    # Check for excessive rate limiting
    total_failures = sum(stats['failures'] for stats in deepseek_stats.values()) + sum(stats['failures'] for stats in claude_stats.values())
    if total_failures > 20:
        print(f'\n⚠️ WARNING: High failure count ({total_failures} total failures)')
        print('   This suggests API keys might be invalid or heavily rate limited.')

if __name__ == '__main__':
    check_api_status()
