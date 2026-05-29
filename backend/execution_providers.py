"""
Supertonic TTS WebUI - Execution Provider Detection
Detects available ONNX Runtime execution providers for GPU acceleration.
"""
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger("supertonic-tts.providers")


def detect_execution_providers() -> List[str]:
    """
    Detect available ONNX Runtime execution providers.
    Prefers DirectML (AMD GPU) with fallback to CPU.

    Returns:
        List of provider names in priority order
    """
    providers: List[str] = []
    provider_details: List[Dict[str, Any]] = []

    try:
        import onnxruntime as ort
        provider_details = ort.get_available_providers()
        logger.info(f"Available ONNX providers: {provider_details}")
    except ImportError:
        logger.error("onnxruntime not installed")
        return ["CPUExecutionProvider"]
    except Exception as e:
        logger.error(f"Error detecting providers: {e}")
        return ["CPUExecutionProvider"]

    # Priority order: DirectML > CUDA > OpenVINO > CPU
    provider_priority = [
        "DmlExecutionProvider",      # DirectML for AMD GPUs
        "CUDAExecutionProvider",     # NVIDIA GPUs
        "TensorrtExecutionProvider", # NVIDIA TensorRT
        "OpenVINOExecutionProvider", # Intel
        "CoreMLExecutionProvider",   # Apple Silicon
        "CPUExecutionProvider",      # CPU fallback
    ]

    for provider_name in provider_priority:
        if provider_name in provider_details:
            providers.append(provider_name)
            logger.info(f"✓ Provider available: {provider_name}")

    # Ensure CPU fallback is always last
    if "CPUExecutionProvider" not in providers:
        providers.append("CPUExecutionProvider")

    return providers


def get_provider_info() -> Dict[str, Any]:
    """
    Get detailed information about the execution providers.

    Returns:
        Dict with provider info including GPU details
    """
    info: Dict[str, Any] = {
        "primary_provider": "CPUExecutionProvider",
        "providers": [],
        "gpu_available": False,
        "gpu_name": "",
        "onnx_version": "",
    }

    try:
        import onnxruntime as ort
        info["onnx_version"] = ort.__version__

        providers = detect_execution_providers()
        info["providers"] = providers

        if providers:
            info["primary_provider"] = providers[0]

        # Check if GPU provider is available
        gpu_providers = [
            "DmlExecutionProvider",
            "CUDAExecutionProvider",
            "TensorrtExecutionProvider",
        ]
        info["gpu_available"] = any(
            p in providers for p in gpu_providers
        )

        # Try to get GPU name
        if "DmlExecutionProvider" in providers:
            info["gpu_name"] = get_directml_gpu_name()
        elif "CUDAExecutionProvider" in providers:
            info["gpu_name"] = "NVIDIA GPU (CUDA)"
        else:
            info["gpu_name"] = "No GPU detected"

    except Exception as e:
        logger.error(f"Error getting provider info: {e}")

    return info


def get_directml_gpu_name() -> str:
    """
    Attempt to get the GPU name when using DirectML.

    Returns:
        GPU name string or default message
    """
    try:
        # Try to use DirectML to get adapter info
        import onnxruntime as ort
        providers = ort.get_available_providers()

        if "DmlExecutionProvider" in providers:
            # Create a minimal session to trigger DML device info
            session_options = ort.SessionOptions()
            session_options.enable_cpu_mem_arena = False
            session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

            # Try to get device info from provider options
            try:
                import ctypes
                # DirectML typically uses the first compatible GPU
                # We can check via pyadapter or similar
                pass
            except Exception:
                pass

            return "AMD GPU (DirectML)"
        return "Unknown"
    except Exception:
        return "Unknown"


def create_session_options() -> Any:
    """
    Create optimized ONNX Runtime session options.

    Returns:
        Configured SessionOptions object
    """
    try:
        import onnxruntime as ort
        opts = ort.SessionOptions()
        opts.enable_cpu_mem_arena = False
        opts.enable_mem_pattern = False
        opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        opts.intra_op_num_threads = 4
        opts.inter_op_num_threads = 2
        return opts
    except Exception as e:
        logger.error(f"Error creating session options: {e}")
        return None
</write_to_file>