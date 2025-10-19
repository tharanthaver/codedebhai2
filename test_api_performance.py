#!/usr/bin/env python3
import sys
sys.path.append('.')

from app import solve_coding_problem, try_deepseek_api, try_claude_api, claude_manager
import time

def test_api_performance():
    print('=== API PERFORMANCE TEST ===')
    
    # Test question
    test_question = "Write a Python program to find the factorial of a number using recursion."
    
    print('\n🧪 Testing DeepSeek API directly...')
    start_time = time.time()
    try:
        result = try_deepseek_api(f"Write only the Python code to solve: {test_question}")
        deepseek_time = time.time() - start_time
        print(f'✅ DeepSeek Response Time: {deepseek_time:.2f} seconds')
        print(f'📝 DeepSeek Result: {result[:100]}...' if len(result) > 100 else f'📝 DeepSeek Result: {result}')
    except Exception as e:
        deepseek_time = time.time() - start_time
        print(f'❌ DeepSeek Failed in {deepseek_time:.2f} seconds: {e}')
    
    print('\n🧠 Testing Claude API directly...')
    start_time = time.time()
    try:
        key_index, claude_key = claude_manager.get_best_available_key()
        if claude_key:
            result = try_claude_api(f"Write only the Python code to solve: {test_question}", claude_key, key_index)
            claude_time = time.time() - start_time
            print(f'✅ Claude Response Time: {claude_time:.2f} seconds')
            print(f'📝 Claude Result: {result[:100]}...' if len(result) > 100 else f'📝 Claude Result: {result}')
        else:
            print('❌ No Claude keys available')
    except Exception as e:
        claude_time = time.time() - start_time
        print(f'❌ Claude Failed in {claude_time:.2f} seconds: {e}')
    
    print('\n🔄 Testing solve_coding_problem() function...')
    start_time = time.time()
    try:
        result = solve_coding_problem(test_question, "python")
        solve_time = time.time() - start_time
        print(f'✅ solve_coding_problem() Time: {solve_time:.2f} seconds')
        print(f'📝 Result: {result[:100]}...' if len(result) > 100 else f'📝 Result: {result}')
    except Exception as e:
        solve_time = time.time() - start_time
        print(f'❌ solve_coding_problem() Failed in {solve_time:.2f} seconds: {e}')
    
    print('\n📊 PERFORMANCE SUMMARY:')
    if 'deepseek_time' in locals():
        print(f'DeepSeek: {deepseek_time:.2f}s')
    if 'claude_time' in locals():
        print(f'Claude: {claude_time:.2f}s')
    if 'solve_time' in locals():
        print(f'solve_coding_problem(): {solve_time:.2f}s')
    
    # Diagnosis
    print('\n🔧 DIAGNOSIS:')
    if 'solve_time' in locals() and solve_time > 30:
        print('❌ SLOW: solve_coding_problem() is taking too long')
        print('   Possible causes:')
        print('   - Network connectivity issues')
        print('   - API endpoint problems')
        print('   - Complex retry logic causing delays')
    elif 'solve_time' in locals() and solve_time < 15:
        print('✅ API performance is normal')
        print('   The slowdown might be elsewhere in the PDF processing pipeline')

if __name__ == '__main__':
    test_api_performance()
