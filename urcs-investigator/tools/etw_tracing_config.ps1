# ETW Tracing Configuration for URCS Detection
# Run as Administrator

# Create ETW session for URCS monitoring
logman create trace "URCS_Tracing" -ow -o "C:\ETW_Logs\urcs_trace.etl" -f bincirc -max 2048 -mode Circular

# Add providers
logman add counter "URCS_Tracing" -si 5 -v mmddhhmm -f csv -o "C:\ETW_Logs\urcs_perf.csv" "\Processor(_Total)\% Processor Time"
logman add counter "URCS_Tracing" -si 5 -v mmddhhmm -f csv -o "C:\ETW_Logs\urcs_perf.csv" "\Memory\Available MBytes"

# Add Windows Kernel Process provider
logman add etw "URCS_Tracing" Microsoft-Windows-Kernel-Process

# Add Windows Kernel Registry provider
logman add etw "URCS_Tracing" Microsoft-Windows-Kernel-Registry

# Add Windows Kernel File provider
logman add etw "URCS_Tracing" Microsoft-Windows-Kernel-File

# Start tracing
logman start "URCS_Tracing"

Write-Host "ETW tracing enabled successfully"
