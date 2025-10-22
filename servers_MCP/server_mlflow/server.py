"""
MLflow MCP Server - wraps tools_MLflower for agent interaction
Focused on core operations: save_experiment, update_run, download artifacts
Enhanced with comprehensive logging and debugging
Includes get_last_run_id for convenient workflow
"""

from mcp.server.fastmcp import FastMCP
import tools_MLflower
import config as config_module
from typing import Optional, List, Dict, Any
import json
from pathlib import Path
import logging
import traceback
import sys
import io

# Force UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mlflow_server.log')
        # NOTE: DO NOT log to stdout or stderr - it breaks MCP protocol!
    ]
)
logger = logging.getLogger(__name__)

logger.info("=" * 80)
logger.info("Starting MLflow MCP Server")
logger.info("=" * 80)

# Initialize MCP server
mcp = FastMCP("MLflow Server")

# Load configuration
try:
    cfg = config_module.cnfg_experiment()
    logger.info(f"Configuration loaded: host={cfg.host_mlflow}, port={cfg.port_mlflow}")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}", exc_info=True)
    exit(1)

# Initialize MLflow wrapper
try:
    mlflow_client = tools_MLflower.MLFlower(
        host=cfg.host_mlflow,
        port=cfg.port_mlflow,
        username_mlflow=getattr(cfg, 'username_mlflow', None),
        password_mlflow=getattr(cfg, 'password_mlflow', None),
        remote_storage_folder=getattr(cfg, 'remote_storage_folder', None),
        username_ssh=getattr(cfg, 'username_ssh', None),
        ppk_key_path=getattr(cfg, 'ppk_key_path', None),
        password_ssh=getattr(cfg, 'password_ssh', None),
    )
    logger.info(f"MLflow client initialized: is_available={mlflow_client.is_available}")
except Exception as e:
    logger.error(f"Failed to initialize MLflow client: {e}", exc_info=True)
    exit(1)

# Check if client is available
if not mlflow_client.is_available:
    logger.error("ERROR: MLflow client not available")
    exit(1)

logger.info("MLflow client is available and ready")


# ============================================================================
# CORE: SAVE EXPERIMENT (Main operation)
# ============================================================================

@mcp.tool()
async def save_experiment(
        experiment_name: str,
        params: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, float]] = None,
        artifacts: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Save an experiment run to MLflow (core operation)

    Args:
        experiment_name: Name of the experiment
        params: Dictionary of parameters (config, hyperparams, etc)
        metrics: Optional dictionary of metrics (loss, accuracy, etc)
        artifacts: Optional list of local file paths to log

    Returns:
        run_id and status

    Example:
        save_experiment(
            experiment_name="yolo-training",
            params={"model": "yolov8n", "epochs": 100, "lr": 0.001},
            metrics={"mAP50": 0.85, "mAP75": 0.72},
            artifacts=["model.onnx", "results.json"]
        )
    """
    params = params or {}
    metrics = metrics or {}
    artifacts = artifacts or []

    # Debug info to return
    debug_info = {
        "experiment_name": experiment_name,
        "params_received": params,
        "metrics_received": metrics,
        "artifacts_received": artifacts,
        "param_types": {k: type(v).__name__ for k, v in params.items()},
        "metric_types": {k: type(v).__name__ for k, v in metrics.items()}
    }

    logger.info("=" * 80)
    logger.info("save_experiment called")
    logger.info(f"  experiment_name: {experiment_name}")
    logger.info(f"  params: {params}")
    logger.info(f"  metrics: {metrics}")
    logger.info(f"  artifacts: {artifacts}")
    logger.debug(f"  debug_info: {debug_info}")

    try:
        logger.info("Calling mlflow_client.save_experiment...")
        run_id = mlflow_client.save_experiment(
            experiment_name=experiment_name,
            params=params,
            metrics=metrics,
            artifacts=artifacts
        )

        logger.info(f"✓ save_experiment succeeded with run_id: {run_id}")

        return {
            "status": "success",
            "run_id": run_id,
            "experiment_name": experiment_name,
            "params_logged": len(params),
            "metrics_logged": len(metrics),
            "artifacts_logged": len(artifacts),
            "message": f"Experiment '{experiment_name}' saved with run_id: {run_id}",
            "debug": debug_info
        }

    except Exception as e:
        logger.error(f"✗ save_experiment failed: {str(e)}", exc_info=True)
        error_msg = {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "experiment_name": experiment_name,
            "traceback": traceback.format_exc(),
            "debug": debug_info
        }
        logger.error(f"Error response: {json.dumps(error_msg, indent=2)}")
        return error_msg


# ============================================================================
# READ: GET EXPERIMENT METADATA
# ============================================================================

@mcp.tool()
async def get_experiment_id(
        experiment_name: str,
        create: bool = True
) -> Dict[str, Any]:
    """
    Get or create an experiment ID

    Args:
        experiment_name: Name of the experiment
        create: Whether to create if doesn't exist

    Returns:
        experiment_id or error
    """
    logger.info(f"get_experiment_id called: experiment_name={experiment_name}, create={create}")

    try:
        exp_id = mlflow_client.get_experiment_id(
            experiment_name=experiment_name,
            create=create
        )

        if exp_id is None:
            logger.warning(f"Experiment '{experiment_name}' not found and create=False")
            return {
                "status": "not_found",
                "experiment_name": experiment_name,
                "message": f"Experiment '{experiment_name}' not found and create=False"
            }

        logger.info(f"✓ Got experiment_id: {exp_id}")
        return {
            "status": "success",
            "experiment_id": exp_id,
            "experiment_name": experiment_name
        }

    except Exception as e:
        logger.error(f"✗ get_experiment_id failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


@mcp.tool()
async def get_last_run_id(experiment_name: str) -> Dict[str, Any]:
    """
    Get the last (most recent) run ID from an experiment

    Args:
        experiment_name: Name of the experiment

    Returns:
        run_id of the most recent run or error

    Example:
        get_last_run_id(experiment_name="yolo-training")
        # Returns: {"status": "success", "run_id": "abc123def456", ...}
    """
    logger.info(f"get_last_run_id called: experiment_name={experiment_name}")

    try:
        run_id = mlflow_client.get_last_run_id(experiment_name)

        if run_id is None:
            logger.warning(f"No runs found for experiment '{experiment_name}'")
            return {
                "status": "not_found",
                "experiment_name": experiment_name,
                "message": f"No runs found for experiment '{experiment_name}'"
            }

        logger.info(f"✓ Retrieved last run_id: {run_id}")
        return {
            "status": "success",
            "run_id": run_id,
            "experiment_name": experiment_name
        }

    except Exception as e:
        logger.error(f"✗ get_last_run_id failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "experiment_name": experiment_name,
            "traceback": traceback.format_exc()
        }


# ============================================================================
# READ: GET RUN DETAILS
# ============================================================================

@mcp.tool()
async def get_run_params(run_id: str) -> Dict[str, Any]:
    """
    Get parameters from a specific run

    Args:
        run_id: The run ID

    Returns:
        Dictionary of parameters
    """
    logger.info(f"get_run_params called: run_id={run_id}")

    try:
        params = mlflow_client.get_run_params(run_id)
        logger.info(f"✓ Retrieved {len(params)} parameters")
        return {
            "status": "success",
            "run_id": run_id,
            "params": params,
            "count": len(params)
        }
    except Exception as e:
        logger.error(f"✗ get_run_params failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "run_id": run_id,
            "traceback": traceback.format_exc()
        }


@mcp.tool()
async def get_run_metrics(run_id: str) -> Dict[str, Any]:
    """
    Get metrics from a specific run

    Args:
        run_id: The run ID

    Returns:
        Dictionary of metrics
    """
    logger.info(f"get_run_metrics called: run_id={run_id}")

    try:
        metrics = mlflow_client.get_run_metrics(run_id)
        logger.info(f"✓ Retrieved {len(metrics)} metrics")
        return {
            "status": "success",
            "run_id": run_id,
            "metrics": metrics,
            "count": len(metrics)
        }
    except Exception as e:
        logger.error(f"✗ get_run_metrics failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "run_id": run_id,
            "traceback": traceback.format_exc()
        }


@mcp.tool()
async def get_run_artifact_filenames(run_id: str) -> Dict[str, Any]:
    """
    Get list of artifact filenames for a run

    Args:
        run_id: The run ID

    Returns:
        List of artifact URIs
    """
    logger.info(f"get_run_artifact_filenames called: run_id={run_id}")

    try:
        filenames = mlflow_client.get_run_artifact_filenames(run_id)
        logger.info(f"✓ Retrieved {len(filenames)} artifact filenames")
        return {
            "status": "success",
            "run_id": run_id,
            "artifacts": filenames,
            "count": len(filenames)
        }
    except Exception as e:
        logger.error(f"✗ get_run_artifact_filenames failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "run_id": run_id,
            "traceback": traceback.format_exc()
        }


# ============================================================================
# WRITE: UPDATE EXISTING RUN
# ============================================================================

@mcp.tool()
async def update_run(
        run_id: str,
        metrics: Optional[Dict[str, float]] = None,
        artifacts: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Update an existing run with additional metrics and artifacts

    Args:
        run_id: The run ID to update
        metrics: Dictionary of metrics to add
        artifacts: List of local file paths to add

    Returns:
        Status of update

    Example:
        update_run(
            run_id="abc123",
            metrics={"accuracy": 0.95, "loss": 0.05},
            artifacts=["final_model.pth"]
        )
    """
    metrics = metrics or {}
    artifacts = artifacts or []

    logger.info(f"update_run called: run_id={run_id}, metrics={metrics}, artifacts={artifacts}")

    try:
        mlflow_client.update_run(
            run_id=run_id,
            metrics=metrics,
            artifacts=artifacts
        )

        logger.info(f"✓ update_run succeeded for run_id: {run_id}")
        return {
            "status": "success",
            "run_id": run_id,
            "metrics_updated": len(metrics),
            "artifacts_added": len(artifacts),
            "message": f"Run {run_id} updated successfully"
        }

    except Exception as e:
        logger.error(f"✗ update_run failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "run_id": run_id,
            "traceback": traceback.format_exc()
        }


# ============================================================================
# ARTIFACTS: DOWNLOAD AND MANAGE
# ============================================================================

@mcp.tool()
async def download_artifacts(
        run_id: str,
        local_dir: str
) -> Dict[str, Any]:
    """
    Download all artifacts from a run to local directory

    Args:
        run_id: The run ID
        local_dir: Local directory to download to

    Returns:
        Status and downloaded files
    """
    logger.info(f"download_artifacts called: run_id={run_id}, local_dir={local_dir}")

    try:
        # Create directory if doesn't exist
        Path(local_dir).mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created directory: {local_dir}")

        mlflow_client.download_artifacts(local_dir, run_id)

        # List downloaded files
        downloaded = list(Path(local_dir).rglob("*"))
        downloaded_files = [str(f.relative_to(local_dir)) for f in downloaded if f.is_file()]

        logger.info(f"✓ Downloaded {len(downloaded_files)} artifacts")
        return {
            "status": "success",
            "run_id": run_id,
            "local_dir": str(local_dir),
            "files_downloaded": downloaded_files,
            "count": len(downloaded_files)
        }

    except Exception as e:
        logger.error(f"✗ download_artifacts failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "run_id": run_id,
            "local_dir": local_dir,
            "traceback": traceback.format_exc()
        }


# ============================================================================
# DELETE: REMOVE RUN
# ============================================================================

@mcp.tool()
async def delete_run(run_id: str) -> Dict[str, Any]:
    """
    Delete a run from MLflow

    Args:
        run_id: The run ID to delete

    Returns:
        Status of deletion
    """
    logger.info(f"delete_run called: run_id={run_id}")

    try:
        mlflow_client.delete_run(run_id)
        logger.info(f"✓ Deleted run: {run_id}")
        return {
            "status": "success",
            "run_id": run_id,
            "message": f"Run {run_id} deleted"
        }
    except Exception as e:
        logger.error(f"✗ delete_run failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "run_id": run_id,
            "traceback": traceback.format_exc()
        }


# ============================================================================
# TRACKING: CONFIGURE URI
# ============================================================================

@mcp.tool()
async def set_tracking_local(folder_out: str) -> Dict[str, Any]:
    """
    Set tracking to local folder

    Args:
        folder_out: Local folder path for MLflow tracking

    Returns:
        Status
    """
    logger.info(f"set_tracking_local called: folder_out={folder_out}")

    try:
        mlflow_client.set_tracking_local(folder_out)
        logger.info(f"✓ Tracking set to local folder: {folder_out}")
        return {
            "status": "success",
            "tracking_uri": folder_out,
            "type": "local",
            "message": f"Tracking set to local folder: {folder_out}"
        }
    except Exception as e:
        logger.error(f"✗ set_tracking_local failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


@mcp.tool()
async def set_tracking_remote(connection_string: str) -> Dict[str, Any]:
    """
    Set tracking to remote database

    Args:
        connection_string: Database connection string
                          Format: <dialect>+<driver>://<user>:<pass>@<host>:<port>/<db>

    Returns:
        Status
    """
    logger.info(f"set_tracking_remote called: connection_string={connection_string}")

    try:
        mlflow_client.set_tracking_remote(connection_string)
        logger.info(f"✓ Tracking set to remote database")
        return {
            "status": "success",
            "tracking_uri": connection_string,
            "type": "remote",
            "message": "Tracking set to remote database"
        }
    except Exception as e:
        logger.error(f"✗ set_tracking_remote failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


# ============================================================================
# INFO: GET CURRENT STATE
# ============================================================================

@mcp.tool()
async def get_uris() -> Dict[str, Any]:
    """
    Get current MLflow URIs and configuration

    Returns:
        Current tracking and artifact URIs
    """
    logger.info("get_uris called")

    try:
        artifact_uri = mlflow_client.get_uris()
        logger.info(f"✓ Retrieved URIs")
        return {
            "status": "success",
            "artifact_uri": artifact_uri,
            "mlflow_host": cfg.host_mlflow,
            "mlflow_port": cfg.port_mlflow,
            "message": "Current MLflow configuration"
        }
    except Exception as e:
        logger.error(f"✗ get_uris failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """
    Check if MLflow server is available

    Returns:
        Server status
    """
    logger.info("health_check called")

    try:
        is_available = mlflow_client.is_available
        status = "healthy" if is_available else "unhealthy"
        logger.info(f"✓ health_check: {status}")
        return {
            "status": status,
            "mlflow_available": is_available,
            "host": cfg.host_mlflow,
            "port": cfg.port_mlflow
        }
    except Exception as e:
        logger.error(f"✗ health_check failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }


# ============================================================================
# MAIN ENTRY POINTS
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Starting MLflow MCP Server")
    logger.info(f"  Host: {cfg.host_mlflow}")
    logger.info(f"  Port: {cfg.port_mlflow}")
    logger.info(f"  Status: {'Available' if mlflow_client.is_available else 'Unavailable'}")
    logger.info(f"  Log file: mlflow_server.log")
    mcp.run()


def main():
    """Entry point for console script"""
    logger.info(f"Starting MLflow MCP Server (main)")
    logger.info(f"  Host: {cfg.host_mlflow}")
    logger.info(f"  Port: {cfg.port_mlflow}")
    logger.info(f"  Status: {'Available' if mlflow_client.is_available else 'Unavailable'}")
    logger.info(f"  Log file: mlflow_server.log")
    mcp.run()