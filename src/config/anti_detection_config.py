#!/usr/bin/env python3
"""
Anti-detection configuration settings for the RequestManager
Allows easy adjustment of anti-detection parameters without code changes.
"""

import os
from typing import Dict, Any, List

# Default anti-detection configuration
DEFAULT_ANTI_DETECTION_CONFIG = {
    # Rate limiting settings
    'rate_limiting': {
        'base_delay_min': 5.0,  # Minimum base delay in seconds
        'base_delay_max': 8.0,  # Maximum base delay in seconds
        'jitter_range': 3.0,    # Jitter range in seconds
        'max_delay': 15.0,      # Maximum delay in seconds
        'backoff_cap': 6,       # Maximum backoff multiplier
    },
    
    # Session rotation settings
    'session_rotation': {
        'requests_before_rotation': 15,  # Rotate every N requests
        'max_session_duration': 300,     # Rotate every N seconds
        'max_consecutive_failures': 2,   # Rotate after N failures
    },
    
    # User agent rotation settings
    'user_agent_rotation': {
        'rotation_frequency': 10,  # Rotate user agent every N requests
        'retry_rotation': True,    # Always rotate on retry
    },
    
    # Behavioral simulation settings
    'behavioral_simulation': {
        'reading_delay_chance': 0.4,      # 40% chance of reading delay
        'reading_delay_min': 1.0,         # Minimum reading delay
        'reading_delay_max': 3.0,         # Maximum reading delay
        'mouse_movement_chance': 0.2,     # 20% chance of mouse movement
        'mouse_movement_min': 0.2,        # Minimum mouse movement delay
        'mouse_movement_max': 0.8,        # Maximum mouse movement delay
        'thinking_delay_chance': 0.15,    # 15% chance of thinking delay
        'thinking_delay_min': 2.0,        # Minimum thinking delay
        'thinking_delay_max': 5.0,        # Maximum thinking delay
        'page_load_chance': 0.1,          # 10% chance of page load delay
        'page_load_min': 0.5,             # Minimum page load delay
        'page_load_max': 1.5,             # Maximum page load delay
        'mistake_chance': 0.05,           # 5% chance of user mistake
        'mistake_delay_min': 0.1,         # Minimum mistake delay
        'mistake_delay_max': 0.3,         # Maximum mistake delay
        'network_latency_chance': 0.3,    # 30% chance of network latency
        'network_latency_min': 0.1,       # Minimum network latency
        'network_latency_max': 0.5,       # Maximum network latency
    },
    
    # Soft block detection settings
    'soft_block_detection': {
        'enabled': True,                  # Enable soft block detection
        'min_response_length': 1000,      # Minimum expected response length
        'indicators': [                   # Soft block indicators
            'captcha',
            'verify you are human',
            'please wait',
            'access denied',
            'blocked',
            'suspicious activity',
            'too many requests',
            'rate limit',
            'security check',
            'cloudflare',
            'ddos protection',
            'please complete the security check',
        ],
    },
    
    # Request modification settings
    'request_modification': {
        'add_cache_buster_chance': 0.05,  # 5% chance to add cache buster
        'cache_buster_param': '_',        # Cache buster parameter name
    },
    
    # Session health monitoring
    'session_health': {
        'max_healthy_failures': 2,        # Max failures for healthy session
        'max_healthy_requests': 20,       # Max requests for healthy session
        'max_healthy_duration': 600,      # Max duration for healthy session (10 min)
    },
    
    # Retry settings
    'retry_settings': {
        'max_retries': 3,                 # Maximum retry attempts
        'retry_delay_base': 2,            # Base delay for retries
        'rate_limit_wait_multiplier': 60, # Wait time multiplier for rate limits
        'forbidden_wait_multiplier': 30,  # Wait time multiplier for 403 errors
        'soft_block_wait_multiplier': 30, # Wait time multiplier for soft blocks
    },
    
    # Browser fingerprinting settings
    'browser_fingerprinting': {
        'screen_resolutions': [           # Common screen resolutions
            (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
            (1280, 720), (1600, 900), (1024, 768), (2560, 1440)
        ],
        'viewport_sizes': [               # Common viewport sizes
            (1920, 937), (1366, 625), (1536, 722), (1440, 789),
            (1280, 617), (1600, 789), (1024, 768), (2560, 1313)
        ],
        'color_depths': [24, 32],         # Color depths
        'timezone_offsets': [             # Timezone offsets (minutes)
            -300, -240, -180, -120, -60, 0, 60, 120, 180, 240, 300, 360, 420, 480
        ],
        'languages': [                    # Language preferences
            'en-US,en;q=0.9',
            'en-US,en;q=0.9,es;q=0.8',
            'en-US,en;q=0.9,fr;q=0.8',
            'en-US,en;q=0.9,de;q=0.8',
            'en-US,en;q=0.9,it;q=0.8'
        ],
    },
    
    # Logging and monitoring
    'logging': {
        'log_session_rotation': True,     # Log session rotations
        'log_soft_blocks': True,          # Log soft block detections
        'log_behavioral_patterns': False, # Log behavioral patterns (verbose)
        'log_rate_limiting': True,        # Log rate limiting delays
    },
}


def get_anti_detection_config() -> Dict[str, Any]:
    """
    Get anti-detection configuration, allowing environment variable overrides.
    
    Returns:
        Dictionary containing anti-detection configuration settings.
    """
    config = DEFAULT_ANTI_DETECTION_CONFIG.copy()
    
    # Allow environment variable overrides
    env_overrides = {
        'ANTI_DETECTION_BASE_DELAY_MIN': ('rate_limiting', 'base_delay_min', float),
        'ANTI_DETECTION_BASE_DELAY_MAX': ('rate_limiting', 'base_delay_max', float),
        'ANTI_DETECTION_JITTER_RANGE': ('rate_limiting', 'jitter_range', float),
        'ANTI_DETECTION_MAX_DELAY': ('rate_limiting', 'max_delay', float),
        'ANTI_DETECTION_REQUESTS_BEFORE_ROTATION': ('session_rotation', 'requests_before_rotation', int),
        'ANTI_DETECTION_MAX_SESSION_DURATION': ('session_rotation', 'max_session_duration', int),
        'ANTI_DETECTION_MAX_CONSECUTIVE_FAILURES': ('session_rotation', 'max_consecutive_failures', int),
        'ANTI_DETECTION_USER_AGENT_ROTATION_FREQUENCY': ('user_agent_rotation', 'rotation_frequency', int),
        'ANTI_DETECTION_SOFT_BLOCK_DETECTION': ('soft_block_detection', 'enabled', lambda x: x.lower() == 'true'),
        'ANTI_DETECTION_MIN_RESPONSE_LENGTH': ('soft_block_detection', 'min_response_length', int),
    }
    
    for env_var, (section, key, converter) in env_overrides.items():
        value = os.getenv(env_var)
        if value is not None:
            try:
                config[section][key] = converter(value)
            except (ValueError, TypeError) as e:
                print(f"Warning: Invalid value for {env_var}: {value}. Using default.")
    
    return config


def get_rate_limiting_config() -> Dict[str, Any]:
    """Get rate limiting configuration."""
    return get_anti_detection_config()['rate_limiting']


def get_session_rotation_config() -> Dict[str, Any]:
    """Get session rotation configuration."""
    return get_anti_detection_config()['session_rotation']


def get_behavioral_simulation_config() -> Dict[str, Any]:
    """Get behavioral simulation configuration."""
    return get_anti_detection_config()['behavioral_simulation']


def get_soft_block_detection_config() -> Dict[str, Any]:
    """Get soft block detection configuration."""
    return get_anti_detection_config()['soft_block_detection']


def get_session_health_config() -> Dict[str, Any]:
    """Get session health monitoring configuration."""
    return get_anti_detection_config()['session_health']


def get_retry_config() -> Dict[str, Any]:
    """Get retry configuration."""
    return get_anti_detection_config()['retry_settings']


def get_browser_fingerprinting_config() -> Dict[str, Any]:
    """Get browser fingerprinting configuration."""
    return get_anti_detection_config()['browser_fingerprinting']


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration."""
    return get_anti_detection_config()['logging']


# Export configuration for easy access
ANTI_DETECTION_CONFIG = get_anti_detection_config() 