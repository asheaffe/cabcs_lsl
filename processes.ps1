# script.ps1

Write-Host "Starting all processes..."

$processes = @()
$processes += Start-Process python -ArgumentList "lsl_app/lsl_app.py" -WindowStyle Hidden -PassThru
$processes += Start-Process python -ArgumentList "lsl_app/device_layers/etg_layer.py" -WindowStyle Hidden -PassThru
$processes += Start-Process python -ArgumentList "nback_2025/nback_layer.py" -WindowStyle Hidden -PassThru
$processes += Start-Process python -ArgumentList "lsl_app/device_layers/watch_layer.py" -WindowStyle Hidden -PassThru
$processes += Start-Process python -ArgumentList "lsl_app/device_layers/drt_layer.py" -WindowStyle Hidden -PassThru