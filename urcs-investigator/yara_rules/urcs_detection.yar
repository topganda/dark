/*
URCS Detection Rules
Detects unauthorized resource-consuming software patterns
*/

rule urcs_detection {
    meta:
        description = "Detects unauthorized resource-consuming software"
        author = "URCS Investigator Team"
        date = "2024"
        reference = "MITRE ATT&CK T1055.012, T1543.003"
        severity = "high"
    
    strings:
        // Pool and wallet indicators
        $pool_string = "gulf.moneroocean.stream:10032"
        $wallet_prefix = "49d3f" nocase
        $stratum_protocol = "stratum+tcp://"
        
        // Process and service names
        $mutex_pattern = /gupdatem_[0-9]{4}/
        $service_name = "Google Update Service"
        
        // Registry paths
        $registry_path = "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run\\ctfmon"
        
        // File paths
        $system_path = "\\System32\\spool\\drivers\\color\\"
        
        // Mining-related strings
        $xmrig_string = "xmrig" nocase
        $mining_string = "mining" nocase
        $crypto_string = "cryptocurrency" nocase
        
        // Evasion techniques
        $task_manager = "taskmgr.exe" nocase
        $process_hollow = "process hollow" nocase
        $injection = "injection" nocase
    
    condition:
        uint16(0) == 0x5A4D and 
        (all of ($pool_string, $wallet_prefix) or 
         $mutex_pattern or 
         $registry_path or
         $system_path or
         all of ($xmrig_string, $mining_string) or
         all of ($task_manager, $injection))
}

rule urcs_persistence {
    meta:
        description = "Detects URCS persistence mechanisms"
        author = "URCS Investigator Team"
        date = "2024"
        reference = "MITRE ATT&CK T1543.003, T1053.005"
        severity = "medium"
    
    strings:
        // Registry persistence
        $run_key = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
        $ctfmon = "ctfmon" nocase
        $gupdatem = "gupdatem" nocase
        
        // Service persistence
        $service_create = "CreateService" nocase
        $service_start = "StartService" nocase
        
        // Scheduled task persistence
        $task_create = "CreateTask" nocase
        $schtasks = "schtasks" nocase
        $ddriver = "Ddriver" nocase
    
    condition:
        uint16(0) == 0x5A4D and 
        (all of ($run_key, $ctfmon) or
         all of ($service_create, $gupdatem) or
         all of ($task_create, $ddriver))
}

rule urcs_evasion {
    meta:
        description = "Detects URCS evasion techniques"
        author = "URCS Investigator Team"
        date = "2024"
        reference = "MITRE ATT&CK T1562.001"
        severity = "medium"
    
    strings:
        // Task Manager detection
        $taskmgr = "taskmgr.exe" nocase
        $process_list = "EnumProcesses" nocase
        
        // CPU throttling
        $thread_affinity = "SetThreadAffinityMask" nocase
        $cpu_usage = "GetSystemPowerStatus" nocase
        
        // Self-deletion
        $delete_file = "DeleteFile" nocase
        $remove_item = "Remove-Item" nocase
        
        // Process injection
        $virtual_alloc = "VirtualAllocEx" nocase
        $write_process = "WriteProcessMemory" nocase
        $create_remote = "CreateRemoteThread" nocase
    
    condition:
        uint16(0) == 0x5A4D and 
        (all of ($taskmgr, $thread_affinity) or
         all of ($virtual_alloc, $write_process, $create_remote) or
         all of ($delete_file, $remove_item))
}

rule urcs_network {
    meta:
        description = "Detects URCS network communication"
        author = "URCS Investigator Team"
        date = "2024"
        reference = "MITRE ATT&CK T1071.001"
        severity = "high"
    
    strings:
        // DNS queries
        $api_ipify = "api.ipify.org" nocase
        $dns_query = "DnsQuery" nocase
        
        // Stratum protocol
        $stratum = "stratum" nocase
        $pool_connection = "pool" nocase
        $mining_pool = "mining pool" nocase
        
        // Network functions
        $connect = "connect" nocase
        $send = "send" nocase
        $recv = "recv" nocase
        
        // Port numbers
        $port_10032 = ":10032"
        $port_3333 = ":3333"
        $port_7777 = ":7777"
    
    condition:
        uint16(0) == 0x5A4D and 
        (all of ($api_ipify, $dns_query) or
         all of ($stratum, $pool_connection) or
         any of ($port_10032, $port_3333, $port_7777))
}