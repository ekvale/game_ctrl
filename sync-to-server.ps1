# Create a PowerShell sync script
while ($true) {
    robocopy D:\game_ctrl /MIR do-deploy:/opt/game_ctrl/
    Start-Sleep -Seconds 5
} 