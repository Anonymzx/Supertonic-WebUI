"""
Supertonic TTS WebUI - Execution Provider Detection
Detects available ONNX Runtime execution providers for GPU acceleration.
"""
import logging
from typing import List, Dict, Any

logger = logging.getLogger("supertonic-tts.providers")


def detect_execution_providers() -> List[str]:
    """
    Detect available ONNX Runtime execution providers.
    Returns list of provider names in priority order.

    Priority: DmlExecutionProvider (AMD GPU) > CUDAExecutionProvider > CPUExecutionProvider
    """
    try:
        import onnxruntime as ort
        available = ort.get_available_providers()
        logger.info(f"Available ONNX providers: {available}")

        providers = []
        # DirectML for AMD GPUs (priority)
        if "DmlExecutionProvider" in available:
            providers.append("DmlExecutionProvider")
            logger.info("[OK] DirectML provider available (AMD GPU)")
        # CUDA for NVIDIA GPUs
        if "CUDAExecutionProvider" in available:
            providers.append("CUDAExecutionProvider")
            logger.info("[OK] CUDA provider available (NVIDIA GPU)")
        # CPU fallback (always last)
        providers.append("CPUExecutionProvider")
        logger.info("[OK] CPU provider available")

        return providers

    except ImportError:
        logger.error("[FAIL] onnxruntime not installed")
        return ["CPUExecutionProvider"]
    except Exception as e:
        logger.error(f"[FAIL] Error detecting providers: {e}")
        return ["CPUExecutionProvider"]


def get_provider_info() -> Dict[str, Any]:
    """Get detailed information about execution providers and GPU."""
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

        # Check if GPU is available
        info["gpu_available"] = any(
            p in providers
            for p in ["DmlExecutionProvider", "CUDAExecutionProvider", "TensorrtExecutionProvider"]
        )

        if "DmlExecutionProvider" in providers:
            info["gpu_name"] = "AMD GPU (DirectML)"
        elif "CUDAExecutionProvider" in providers:
            info["gpu_name"] = "NVIDIA GPU (CUDA)"
        else:
            info["gpu_name"] = "CPU (no GPU detected)"

    except Exception as e:
        logger.error(f"[FAIL] Error getting provider info: {e}")

    return info


def create_session_options():
    """Create optimized ONNX Runtime session options."""
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
        logger.error(f"[FAIL] Error creating session options: {e}")
        return None