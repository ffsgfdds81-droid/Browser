#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Develer Browser - Advanced Launch Script
Handles proper initialization of advanced optimization systems
"""

import sys
import os
import traceback

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def initialize_advanced_systems():
    """Initialize all advanced optimization systems"""
    try:
        print("Initializing advanced optimization systems...")
        
        # Initialize systems in order
        print("  [1/6] Memory Manager...")
        from memory_manager import get_memory_manager
        memory_manager = get_memory_manager()
        memory_stats = memory_manager.get_memory_stats()
        print(f"        Memory: {memory_stats['current_memory_mb']:.1f}MB")
        
        print("  [2/6] WebGPU Support...")
        from webgpu_support import get_webgpu_support
        gpu_support = get_webgpu_support()
        gpu_stats = gpu_support.get_performance_stats()
        print(f"        Backend: {gpu_stats['backend']}")
        
        print("  [3/6] Optimized Renderer...")
        from optimized_renderer import get_renderer
        renderer = get_renderer()
        render_stats = renderer.get_performance_stats()
        print(f"        Mode: {render_stats['render_mode']}")
        
        print("  [4/6] Browser Pool...")
        from browser_memory_pool import get_browser_pool
        browser_pool = get_browser_pool()
        pool_stats = browser_pool.get_pool_stats()
        print(f"        Components: {len(pool_stats['pool_sizes'])} types")
        
        print("  [5/6] Performance Monitor...")
        from performance_monitor import get_performance_monitor
        performance_monitor = get_performance_monitor()
        monitor_stats = performance_monitor.get_performance_stats()
        print(f"        Monitoring: Active")
        
        print("  [6/6] Shader Effects...")
        from shader_effect_system import get_shader_effect_manager
        shader_manager = get_shader_effect_manager()
        shader_effects = shader_manager.get_available_effects()
        print(f"        Effects: {len(shader_effects)} available")
        
        print("All advanced systems initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Advanced system initialization failed: {e}")
        traceback.print_exc()
        return False

def launch_browser():
    """Launch the browser"""
    try:
        print("Launching Develer Browser...")
        
        # Import browser
        from browser import BrowserApplication
        
        # Create application
        app = BrowserApplication(sys.argv)
        print("Browser application created")
        
        # Run application
        print("Starting browser...")
        return app.exec_()
        
    except Exception as e:
        print(f"Browser launch failed: {e}")
        traceback.print_exc()
        return 1

def main():
    """Main launch function"""
    print("=" * 60)
    print("Develer Browser - Advanced Optimized Version")
    print("=" * 60)
    print()
    
    # Initialize advanced systems
    if not initialize_advanced_systems():
        print("Failed to initialize advanced systems")
        return 1
    
    print()
    
    # Launch browser
    return launch_browser()

if __name__ == "__main__":
    sys.exit(main())