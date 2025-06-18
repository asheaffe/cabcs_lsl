# script.ps1
Write-Host "Starting all processes..."

# Initialize array to store process objects
$processes = @()

# Function to cleanup all processes
function Stop-AllProcesses {
    Write-Host "`nStopping all processes..."
    foreach ($process in $processes) {
        if ($process -and !$process.HasExited) {
            try {
                Write-Host "Stopping process ID: $($process.Id)"
                $process.Kill()
                $process.WaitForExit(5000)  # Wait up to 5 seconds
            }
            catch {
                Write-Host "Failed to stop process ID: $($process.Id) - $($_.Exception.Message)"
            }
        }
    }
    Write-Host "All processes stopped."
}

# Register event handler for Ctrl+C
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action {
    Stop-AllProcesses
}

# Set up Ctrl+C handler
$null = Register-ObjectEvent -InputObject ([Console]) -EventName CancelKeyPress -Action {
    Stop-AllProcesses
    [Environment]::Exit(0)
}

try {
    # Start all processes and store them in the array
    Write-Host "Starting Python processes..."
    $processes += Start-Process python3.11 -ArgumentList "lsl_app/lsl_app.py" -PassThru
    $processes += Start-Process python3.11 -ArgumentList "lsl_app/device_layers/etg_layer.py" -PassThru
    #$processes += Start-Process python3.11 -ArgumentList "nback_2025/nback_layer.py" -PassThru
    $processes += Start-Process python3.11 -ArgumentList "lsl_app/device_layers/watch_layer.py" -PassThru
    
    Write-Host "Starting ngrok..."
    $processes += Start-Process powershell -ArgumentList "-Command", "ngrok.exe http --url=raccoon-steady-infinitely.ngrok-free.app 8080" -PassThru

    Write-Host "All processes started. Press Ctrl+C to stop all processes."
    Write-Host "Process IDs: $($processes.Id -join ', ')"

    # Keep the script running and monitor processes
    while ($true) {
        Start-Sleep -Seconds 2
        
        # Check if any process has exited unexpectedly
        $runningProcesses = $processes | Where-Object { $_ -and !$_.HasExited }
        if ($runningProcesses.Count -lt $processes.Count) {
            Write-Host "Some processes have exited. Running processes: $($runningProcesses.Count)/$($processes.Count)"
        }
        
        # If all processes have exited, break the loop
        if ($runningProcesses.Count -eq 0) {
            Write-Host "All processes have exited."
            break
        }
    }
}
catch {
    Write-Host "Error occurred: $($_.Exception.Message)"
}
finally {
    # Ensure cleanup happens even if something goes wrong
    Stop-AllProcesses
}