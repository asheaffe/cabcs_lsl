# run_app.ps1
# UnauthorizedAccess fix run on powershell command line:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
python3 main.py 2>&1 | Where-Object { 
    $_ -notmatch "Exception ignored in.*BaseSubprocessTransport" -and
    $_ -notmatch "RuntimeError: Event loop is closed" -and
    $_ -notmatch "File.*asyncio.*base_subprocess.py" -and
    $_ -notmatch "File.*asyncio.*proactor_events.py" -and
    $_ -notmatch "File.*asyncio.*base_events.py"
}