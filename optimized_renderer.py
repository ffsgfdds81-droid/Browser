# -*- coding: utf-8 -*-
"""
Optimized Rendering Engine
Combines WebGL/WebGPU acceleration with advanced rendering techniques
"""

import math
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import threading
from collections import deque

from webgpu_support import get_webgpu_support, GPUBackend, ShaderType
from memory_manager import get_memory_manager, memory_pooled

class RenderMode(Enum):
    IMMEDIATE = "immediate"
    BATCHED = "batched"
    DEFERRED = "deferred"
    GPU_ACCELERATED = "gpu_accelerated"

class BlendMode(Enum):
    NORMAL = "normal"
    ADDITIVE = "additive"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"

@dataclass
class RenderCommand:
    """Single render command"""
    command_type: str
    vertices: Optional[np.ndarray] = None
    texture_id: Optional[str] = None
    shader_id: Optional[str] = None
    transform_matrix: Optional[np.ndarray] = None
    blend_mode: BlendMode = BlendMode.NORMAL
    depth: float = 0.0
    viewport: Optional[Tuple[int, int, int, int]] = None

@dataclass
class RenderBatch:
    """Batch of render commands"""
    commands: List[RenderCommand]
    texture_id: str
    shader_id: str
    blend_mode: BlendMode
    vertex_count: int

class OptimizedRenderer:
    """
    High-performance rendering engine with GPU acceleration
    """
    
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        self.render_mode = RenderMode.BATCHED
        
        # GPU support
        self.gpu_support = get_webgpu_support()
        self.memory_manager = get_memory_manager()
        
        # Rendering state
        self.current_pipeline = None
        self.current_texture = None
        self.current_blend_mode = BlendMode.NORMAL
        self.transform_stack = []
        
        # Batching system
        self.command_queue = deque()
        self.active_batches = {}
        self.max_batch_size = 1000
        
        # Performance monitoring
        self.frame_stats = {
            'frames_per_second': 0,
            'render_time_ms': 0,
            'batch_count': 0,
            'draw_calls': 0,
            'vertices_rendered': 0
        }
        
        # Frame timing
        self.frame_times = deque(maxlen=60)
        self.last_frame_time = time.time()
        
        # Shaders
        self.shaders = {}
        self._initialize_shaders()
        
        # Vertex buffers
        self.vertex_buffers = {}
        self._create_geometry_buffers()
        
        # Rendering context (would be actual canvas/WebGL context)
        self.context = None
        self._initialize_context()
        
        # Threading for async rendering
        self.render_thread = None
        self.async_rendering = False
    
    def _initialize_context(self):
        """Initialize rendering context"""
        # This would initialize the actual WebGL/WebGL2/WebGPU context
        # For now, we'll use the GPU support's context
        self.context = self.gpu_support.context
    
    def _initialize_shaders(self):
        """Initialize basic shaders"""
        shader_lib = self.gpu_support.get_shader_library()
        
        # Basic texture shader
        basic_pipeline = self.gpu_support.create_render_pipeline(
            shader_lib['vertex_quad'],
            shader_lib['fragment_basic']
        )
        self.shaders['basic'] = basic_pipeline
        
        # Blur shader
        blur_pipeline = self.gpu_support.create_render_pipeline(
            shader_lib['vertex_quad'],
            shader_lib['fragment_blur']
        )
        self.shaders['blur'] = blur_pipeline
        
        # Edge detection shader
        edge_pipeline = self.gpu_support.create_render_pipeline(
            shader_lib['vertex_quad'],
            shader_lib['fragment_edge_detection']
        )
        self.shaders['edge'] = edge_pipeline
    
    def _create_geometry_buffers(self):
        """Create common geometry buffers"""
        # Quad vertices (position + texcoords)
        quad_vertices = np.array([
            # Position (x, y)    Texcoord (u, v)
            -1.0, -1.0,          0.0, 1.0,   # Bottom left
             1.0, -1.0,          1.0, 1.0,   # Bottom right
            -1.0,  1.0,          0.0, 0.0,   # Top left
             1.0, -1.0,          1.0, 1.0,   # Bottom right
             1.0,  1.0,          1.0, 0.0,   # Top right
            -1.0,  1.0,          0.0, 0.0    # Top left
        ], dtype=np.float32)
        
        quad_buffer = self.gpu_support.create_buffer(quad_vertices)
        self.vertex_buffers['quad'] = quad_buffer
        
        # Other common geometries could be added here
        # (triangles, circles, etc.)
    
    def set_render_mode(self, mode: RenderMode):
        """Set rendering mode"""
        self.render_mode = mode
        if mode == RenderMode.GPU_ACCELERATED:
            self._optimize_for_gpu()
    
    def _optimize_for_gpu(self):
        """Optimize settings for GPU rendering"""
        if self.gpu_support.backend == GPUBackend.WEBGPU:
            # WebGPU-specific optimizations
            self.max_batch_size = 10000
        elif self.gpu_support.backend == GPUBackend.WEBGL:
            # WebGL-specific optimizations
            self.max_batch_size = 5000
        else:
            # Fallback optimizations
            self.max_batch_size = 1000
    
    def push_transform(self, matrix: np.ndarray):
        """Push transform matrix to stack"""
        if self.transform_stack:
            combined = np.dot(matrix, self.transform_stack[-1])
        else:
            combined = matrix.copy()
        self.transform_stack.append(combined)
    
    def pop_transform(self):
        """Pop transform matrix from stack"""
        if self.transform_stack:
            self.transform_stack.pop()
    
    def get_current_transform(self) -> np.ndarray:
        """Get current transform matrix"""
        if self.transform_stack:
            return self.transform_stack[-1].copy()
        return np.eye(3, dtype=np.float32)
    
    def draw_quad(self, x: float, y: float, width: float, height: float,
                  texture_id: Optional[str] = None, shader_id: Optional[str] = None,
                  blend_mode: BlendMode = BlendMode.NORMAL):
        """Draw a textured quad"""
        # Create transform matrix
        transform = np.array([
            [width, 0, x],
            [0, height, y],
            [0, 0, 1]
        ], dtype=np.float32)
        
        command = RenderCommand(
            command_type='draw_quad',
            vertices=self.vertex_buffers.get('quad'),
            texture_id=texture_id or self.current_texture,
            shader_id=shader_id or self.shaders.get('basic'),
            transform_matrix=transform,
            blend_mode=blend_mode
        )
        
        self._queue_command(command)
    
    def draw_textured_rect(self, x: float, y: float, width: float, height: float,
                          texture_id: str, source_rect: Optional[Tuple[float, float, float, float]] = None):
        """Draw textured rectangle with optional source rect"""
        # Create custom vertices for source rect if specified
        if source_rect:
            u1, v1, u2, v2 = source_rect
            vertices = np.array([
                # Position (x, y)    Texcoord (u, v)
                -1.0, -1.0,          u1, v2,   # Bottom left
                 1.0, -1.0,          u2, v2,   # Bottom right
                -1.0,  1.0,          u1, v1,   # Top left
                 1.0, -1.0,          u2, v2,   # Bottom right
                 1.0,  1.0,          u2, v1,   # Top right
                -1.0,  1.0,          u1, v1    # Top left
            ], dtype=np.float32)
            
            temp_buffer = self.gpu_support.create_buffer(vertices)
            command = RenderCommand(
                command_type='draw_quad',
                vertices=temp_buffer,
                texture_id=texture_id,
                shader_id=self.shaders.get('basic')
            )
        else:
            command = RenderCommand(
                command_type='draw_quad',
                vertices=self.vertex_buffers.get('quad'),
                texture_id=texture_id,
                shader_id=self.shaders.get('basic')
            )
        
        self._queue_command(command)
    
    def apply_post_processing(self, effect: str, source_texture: str, target_texture: str):
        """Apply post-processing effect"""
        if effect == 'blur':
            shader_id = self.shaders.get('blur')
        elif effect == 'edge':
            shader_id = self.shaders.get('edge')
        else:
            shader_id = self.shaders.get('basic')
        
        command = RenderCommand(
            command_type='post_process',
            vertices=self.vertex_buffers.get('quad'),
            texture_id=source_texture,
            shader_id=shader_id
        )
        
        self._queue_command(command)
    
    def _queue_command(self, command: RenderCommand):
        """Queue a render command"""
        if self.render_mode == RenderMode.IMMEDIATE:
            self._execute_command(command)
        else:
            self.command_queue.append(command)
            self._try_batch_command(command)
    
    def _try_batch_command(self, command: RenderCommand):
        """Try to batch command with existing ones"""
        batch_key = (command.texture_id, command.shader_id, command.blend_mode)
        
        if batch_key not in self.active_batches:
            self.active_batches[batch_key] = RenderBatch(
                commands=[],
                texture_id=command.texture_id or '',
                shader_id=command.shader_id or '',
                blend_mode=command.blend_mode,
                vertex_count=0
            )
        
        batch = self.active_batches[batch_key]
        batch.commands.append(command)
        batch.vertex_count += 6  # Quad has 6 vertices
        
        # Flush batch if it gets too large
        if batch.vertex_count >= self.max_batch_size:
            self._flush_batch(batch_key)
    
    def _flush_batch(self, batch_key: Tuple[str, str, BlendMode]):
        """Flush a batch to GPU"""
        if batch_key not in self.active_batches:
            return
        
        batch = self.active_batches[batch_key]
        if not batch.commands:
            return
        
        # Execute all commands in batch
        for command in batch.commands:
            self._execute_command(command)
        
        # Clear batch
        batch.commands.clear()
        batch.vertex_count = 0
    
    def _execute_command(self, command: RenderCommand):
        """Execute a single render command"""
        if command.command_type == 'draw_quad':
            self._render_quad(command)
        elif command.command_type == 'post_process':
            self._render_post_process(command)
    
    def _render_quad(self, command: RenderCommand):
        """Render a quad"""
        pipeline_id = command.shader_id
        vertex_buffer = command.vertices
        texture_bindings = {'u_texture': command.texture_id} if command.texture_id else None
        
        success = self.gpu_support.render_frame(
            pipeline_id=pipeline_id,
            vertex_buffer=vertex_buffer,
            texture_bindings=texture_bindings
        )
        
        if success:
            self.frame_stats['draw_calls'] += 1
            self.frame_stats['vertices_rendered'] += 6
    
    def _render_post_process(self, command: RenderCommand):
        """Render post-processing effect"""
        # Similar to quad render but with different shader setup
        pipeline_id = command.shader_id
        vertex_buffer = command.vertices
        texture_bindings = {'u_texture': command.texture_id} if command.texture_id else None
        
        self.gpu_support.render_frame(
            pipeline_id=pipeline_id,
            vertex_buffer=vertex_buffer,
            texture_bindings=texture_bindings
        )
    
    def flush_all_batches(self):
        """Flush all active batches"""
        for batch_key in list(self.active_batches.keys()):
            self._flush_batch(batch_key)
    
    def begin_frame(self):
        """Begin a new frame"""
        self.command_queue.clear()
        self.frame_stats['batch_count'] = 0
        self.frame_stats['draw_calls'] = 0
        self.frame_stats['vertices_rendered'] = 0
    
    def end_frame(self):
        """End current frame and render"""
        if self.render_mode != RenderMode.IMMEDIATE:
            self.flush_all_batches()
        
        # Update frame timing
        current_time = time.time()
        frame_time = (current_time - self.last_frame_time) * 1000  # Convert to ms
        self.frame_times.append(frame_time)
        self.last_frame_time = current_time
        
        # Calculate FPS
        if len(self.frame_times) > 1:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            self.frame_stats['frames_per_second'] = 1000.0 / avg_frame_time
            self.frame_stats['render_time_ms'] = avg_frame_time
    
    def render_to_texture(self, width: int, height: int, render_func: Callable) -> str:
        """Render to off-screen texture"""
        # Create render target texture
        target_texture = self.gpu_support.create_texture(width, height)
        
        # This would set up framebuffer object and render to texture
        # For now, we'll simulate it
        render_func()
        
        return target_texture
    
    def create_render_texture(self, width: int, height: int) -> str:
        """Create render target texture"""
        return self.gpu_support.create_texture(width, height)
    
    def clear(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0):
        """Clear screen"""
        if self.context:
            if hasattr(self.context, 'clearColor'):
                self.context.clearColor(r, g, b, a)
                self.context.clear(self.context.COLOR_BUFFER_BIT)
    
    def set_viewport(self, x: int, y: int, width: int, height: int):
        """Set viewport"""
        if self.context:
            if hasattr(self.context, 'viewport'):
                self.context.viewport(x, y, width, height)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            'frame_stats': self.frame_stats.copy(),
            'gpu_stats': self.gpu_support.get_performance_stats(),
            'memory_stats': self.memory_manager.get_memory_stats(),
            'render_mode': self.render_mode.value,
            'batch_count': len(self.active_batches),
            'queued_commands': len(self.command_queue)
        }
    
    def enable_async_rendering(self):
        """Enable asynchronous rendering"""
        if not self.async_rendering:
            self.async_rendering = True
            self.render_thread = threading.Thread(target=self._render_loop, daemon=True)
            self.render_thread.start()
    
    def disable_async_rendering(self):
        """Disable asynchronous rendering"""
        self.async_rendering = False
        if self.render_thread:
            self.render_thread.join(timeout=1.0)
    
    def _render_loop(self):
        """Async rendering loop"""
        while self.async_rendering:
            # Process command queue
            while self.command_queue:
                command = self.command_queue.popleft()
                self._execute_command(command)
            
            # Small sleep to prevent busy-waiting
            time.sleep(0.001)
    
    def cleanup(self):
        """Cleanup renderer resources"""
        self.disable_async_rendering()
        self.command_queue.clear()
        self.active_batches.clear()
        self.gpu_support.cleanup()

# Global renderer instance
_global_renderer = None

def get_renderer(width: int = 1920, height: int = 1080) -> OptimizedRenderer:
    """Get global renderer instance"""
    global _global_renderer
    if _global_renderer is None:
        _global_renderer = OptimizedRenderer(width, height)
    return _global_renderer

def cleanup_renderer():
    """Cleanup global renderer"""
    global _global_renderer
    if _global_renderer:
        _global_renderer.cleanup()
        _global_renderer = None