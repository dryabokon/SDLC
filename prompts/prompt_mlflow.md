# MLflow - Get Last Run ID Quick Reference

## Prerequisites
- MLflow MCP server must be running
- Experiment must exist with at least one completed run

## Get Last Run ID

### Command
```
mlflow:get_last_run_id(experiment_name="<experiment_name>")
```

### Example
```
mlflow:get_last_run_id(experiment_name="titanic")
```

### Response
```json
{
  "status": "success",
  "run_id": "4f6237ecab80420a9c6fc88e92a10493",
  "experiment_name": "titanic"
}
```

## Using the Run ID

Once you have the `run_id`, you can:

### Get Run Parameters
```
mlflow:get_run_params(run_id="4f6237ecab80420a9c6fc88e92a10493")
```

### Get Run Metrics
```
mlflow:get_run_metrics(run_id="4f6237ecab80420a9c6fc88e92a10493")
```

### Download Artifacts
```
mlflow:download_artifacts(
  run_id="4f6237ecab80420a9c6fc88e92a10493",
  local_dir="./results"
)
```

### Update Run with New Metrics
```
mlflow:update_run(
  run_id="4f6237ecab80420a9c6fc88e92a10493",
  metrics={"new_metric": 0.95}
)
```

## Common Workflow

```
1. Get last run ID:      mlflow:get_last_run_id(experiment_name="titanic")
2. Extract run_id from response
3. Get metrics:          mlflow:get_run_metrics(run_id="...")
4. Download artifacts:   mlflow:download_artifacts(run_id="...", local_dir="./results")
```

## Troubleshooting

**Error: "MLFlower object has no attribute get_last_run_id"**
- Solution: Restart the MLflow MCP server to load updated code

**Error: "Experiment not found"**
- Check experiment name spelling
- Verify experiment exists with `get_experiment_id(experiment_name="...")`

**Error: "No runs found"**
- Experiment exists but has no completed runs
- Run `save_experiment()` first to create a run