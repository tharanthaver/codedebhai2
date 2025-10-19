#!/usr/bin/env python3
"""
Simple Screenshot Generator for Fast Word Document Generation
Creates minimal black background with white text screenshots for maximum speed.
No terminal paths, no complex styling - just clean, readable output.
"""

import os
import io
import logging
from PIL import Image, ImageDraw, ImageFont


def create_simple_screenshot(output_text, width=900, height=None):
    """
    Create a super-fast simple screenshot with black background and white text.
    """
    try:
        # Clean and prepare output text
        output_text = output_text.strip() or "Program executed successfully. No explicit print statements found."
        
        # Simple color scheme for maximum speed
        COLORS = {
            'bg': '#000000',        # Pure black background
            'text': '#ffffff',      # Pure white text
        }
        
        # Fast font loading - try to use system monospace fonts
        font_paths = [
            # Windows fonts
            "C:\\Windows\\Fonts\\consola.ttf",     # Consolas
            "C:\\Windows\\Fonts\\cour.ttf",       # Courier New
            "C:\\Windows\\Fonts\\lucon.ttf",      # Lucida Console
            # Linux fonts
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            # macOS fonts
            "/System/Library/Fonts/Courier.ttc",
            "/Library/Fonts/Courier New.ttf"
        ]
        
        font = None
        font_size = 18  # Monospace terminal-like size
        
        # Try to load a monospace font quickly
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, font_size)
                    break
            except Exception:
                continue
        
        # Fallback to default font if no monospace font found
        if not font:
            try:
                font = ImageFont.load_default()
            except Exception:
                font = None
        
        # Prepare text lines
        lines = output_text.splitlines() or ["No output."]
        if not lines:
            lines = ["No output."]
        
        # Calculate dimensions for minimal processing
        line_height = 20  # Terminal-like line spacing
        padding = 16
        max_chars = max(len(line) for line in lines)
        actual_width = min(width, max(600, max_chars * 11 + padding * 2))
        content_height = len(lines) * line_height + padding * 2
        # Auto-fit height to avoid clipping; use provided height only if larger
        actual_height = content_height if not height or height < content_height else height
        # Create image with black background
        image = Image.new('RGB', (actual_width, actual_height), color=COLORS['bg'])
        draw = ImageDraw.Draw(image)
        # Draw all text lines (auto-fit avoids overflow)
        y_offset = padding
        for line in lines:
            draw.text((padding, y_offset), line, fill=COLORS['text'], font=font)
            y_offset += line_height
        
        # Convert to bytes for return
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)
        return buffer.read()
        
    except Exception as e:
        logging.error(f"Error creating simple screenshot: {e}")
        # Return minimal fallback image
        try:
            # Create a basic error image
            fallback_image = Image.new('RGB', (800, 200), color='#000000')
            fallback_draw = ImageDraw.Draw(fallback_image)
            fallback_draw.text((20, 20), "Screenshot generation failed", fill='#ffffff')
            fallback_draw.text((20, 50), str(output_text)[:100], fill='#ffffff')
            
            fallback_buffer = io.BytesIO()
            fallback_image.save(fallback_buffer, format="PNG")
            fallback_buffer.seek(0)
            return fallback_buffer.read()
        except Exception:
            return b""


def create_ultra_fast_screenshot(output_text):
    """
    Ultra-fast screenshot with minimal processing for maximum speed.
    Fixed dimensions, no font loading, basic text rendering.
    
    Args:
        output_text (str): The code output to display
    
    Returns:
        bytes: PNG image data as bytes
    """
    try:
        # Fixed dimensions for speed
        width, height = 900, 101
        
        # Clean text
        output_text = output_text.strip() or "Program executed successfully. No explicit print statements found."
        lines = output_text.splitlines()[:15]  # Limit to 15 lines for speed
        
        # Create image
        image = Image.new('RGB', (width, height), color='#000000')
        draw = ImageDraw.Draw(image)
        
        # Use default font for maximum speed (no file loading)
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
        
        # Draw text quickly
        y_pos = 20
        for line in lines:
            if y_pos > height - 30:
                break
            # Truncate long lines for speed
            if len(line) > 120:
                line = line[:117] + "..."
            draw.text((20, y_pos), line, fill='#ffffff', font=font)
            y_pos += 22
        
        # Quick PNG export
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.read()
        
    except Exception as e:
        logging.error(f"Ultra-fast screenshot error: {e}")
        return b""


def benchmark_screenshot_methods(sample_output):
    """
    Benchmark different screenshot methods to compare performance.
    
    Args:
        sample_output (str): Sample code output for testing
    
    Returns:
        dict: Performance metrics for each method
    """
    import time
    
    results = {}
    
    # Test simple screenshot
    start_time = time.time()
    try:
        simple_result = create_simple_screenshot(sample_output)
        simple_time = time.time() - start_time
        simple_size = len(simple_result)
        results['simple'] = {
            'time': simple_time,
            'size_bytes': simple_size,
            'success': True
        }
    except Exception as e:
        results['simple'] = {
            'time': time.time() - start_time,
            'error': str(e),
            'success': False
        }
    
    # Test ultra-fast screenshot
    start_time = time.time()
    try:
        ultra_result = create_ultra_fast_screenshot(sample_output)
        ultra_time = time.time() - start_time
        ultra_size = len(ultra_result)
        results['ultra_fast'] = {
            'time': ultra_time,
            'size_bytes': ultra_size,
            'success': True
        }
    except Exception as e:
        results['ultra_fast'] = {
            'time': time.time() - start_time,
            'error': str(e),
            'success': False
        }
    
    return results


# Example usage and testing
if __name__ == "__main__":
    # Sample code output for testing
    sample_code_output = """Hello, World!
The sum is: 15
Processing complete.
Result: [1, 2, 3, 4, 5]
Total items: 5
Average: 3.0
Maximum value: 5
Minimum value: 1
Execution completed successfully."""
    
    print("Testing Simple Screenshot Generator...")
    
    # Benchmark performance
    print("\nRunning performance benchmarks...")
    benchmark_results = benchmark_screenshot_methods(sample_code_output)
    
    for method, metrics in benchmark_results.items():
        print(f"\n{method.upper()} METHOD:")
        if metrics['success']:
            print(f"  Time: {metrics['time']:.4f} seconds")
            print(f"  Size: {metrics['size_bytes']:,} bytes")
            print(f"  Speed: {'✓ FAST' if metrics['time'] < 0.1 else '⚠ SLOW'}")
        else:
            print(f"  Failed: {metrics.get('error', 'Unknown error')}")
    
    # Test individual methods
    print("\nTesting simple screenshot...")
    simple_screenshot = create_simple_screenshot(sample_code_output)
    if simple_screenshot:
        print(f"✓ Simple screenshot generated successfully ({len(simple_screenshot):,} bytes)")
    else:
        print("✗ Simple screenshot failed")
    
    print("\nTesting ultra-fast screenshot...")
    ultra_screenshot = create_ultra_fast_screenshot(sample_code_output)
    if ultra_screenshot:
        print(f"✓ Ultra-fast screenshot generated successfully ({len(ultra_screenshot):,} bytes)")
    else:
        print("✗ Ultra-fast screenshot failed")
    
    print("\n" + "="*50)
    print("RECOMMENDATION:")
    if benchmark_results.get('ultra_fast', {}).get('success'):
        ultra_time = benchmark_results['ultra_fast']['time']
        print(f"Use ULTRA-FAST method for maximum speed ({ultra_time:.4f}s per screenshot)")
    elif benchmark_results.get('simple', {}).get('success'):
        simple_time = benchmark_results['simple']['time']
        print(f"Use SIMPLE method for reliable speed ({simple_time:.4f}s per screenshot)")
    else:
        print("Both methods failed - check system configuration")
    print("="*50)
