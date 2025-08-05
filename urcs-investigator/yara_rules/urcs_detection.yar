/*
URCS Detection Rules
Detects unauthorized resource-consuming software patterns
Comprehensive detection for all documented URCS behaviors
*/

rule urcs_detection {
    meta:
        description = "Detects unauthorized resource-consuming software"
        author = "URCS Investigator Team"
        date = "2024"
        reference = "MITRE ATT&CK T1055.012, T1543.003"
        severity = "high"
    
    strings:
        // 1. Fake-update dropper indicators
        $chrome_update = "Chrome_update.exe" nocase
        $fake_installer = "fake" nocase
        $dropper = "dropper" nocase
        
        // 2. Registry persistence - ctfmon
        $ctfmon = "ctfmon" nocase
        $registry_run = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
        
        // 3. Windows service masquerading
        $google_update = "Google Update Service" nocase
        $gupdatem = "gupdatem" nocase
        $service_masquerade = "masquerading" nocase
        
        // 4. Scheduled task resurrection
        $ddriver = "Ddriver" nocase
        $scheduled_task = "scheduled task" nocase
        $resurrection = "resurrection" nocase
        
        // 5. Process hollowing
        $explorer_exe = "explorer.exe" nocase
        $process_hollow = "process hollow" nocase
        $hollowing = "hollowing" nocase
        
        // 6. Self-deletion
        $delete_file = "DeleteFile" nocase
        $delete_file_w = "DeleteFileW" nocase
        $remove_item = "Remove-Item" nocase
        $self_delete = "self-delete" nocase
        
        // 7. Watchdog thread and CPU throttling
        $task_manager = "taskmgr.exe" nocase
        $watchdog = "watchdog" nocase
        $cpu_throttle = "throttle" nocase
        $thread_affinity = "SetThreadAffinityMask" nocase
        
        // 8. Battery-aware throttling
        $battery_status = "GetSystemPowerStatus" nocase
        $ac_power = "AC power" nocase
        $battery_power = "battery" nocase
        $idle_time = "idle" nocase
        
        // 9. Obfuscated Monero wallet & pool
        $monero_wallet = "49d3f" nocase
        $pool_string = "gulf.moneroocean.stream:10032"
        $stratum_protocol = "stratum+tcp://"
        $obfuscated = "obfuscated" nocase
        
        // 10. Random 8-letter filename
        $system32_color = "System32\\spool\\drivers\\color\\"
        $random_filename = /[a-z]{8}\\.exe/
        
        // 11. DNS beacon
        $api_ipify = "api.ipify.org" nocase
        $dns_beacon = "dns beacon" nocase
        $dns_query = "DnsQuery" nocase
        
        // Mining-related strings
        $xmrig = "xmrig" nocase
        $mining = "mining" nocase
        $cryptocurrency = "cryptocurrency" nocase
        $monero = "monero" nocase
        
        // Evasion techniques
        $injection = "injection" nocase
        $evasion = "evasion" nocase
        $stealth = "stealth" nocase
    
    condition:
        uint16(0) == 0x5A4D and 
        (
            // Fake-update dropper
            all of ($chrome_update, $fake_installer) or
            all of ($dropper, $chrome_update) or
            
            // Registry persistence
            all of ($ctfmon, $registry_run) or
            
            // Service masquerading
            all of ($google_update, $gupdatem) or
            
            // Scheduled task
            all of ($ddriver, $scheduled_task) or
            
            // Process hollowing
            all of ($explorer_exe, $process_hollow) or
            
            // Self-deletion
            all of ($delete_file, $self_delete) or
            all of ($delete_file_w, $self_delete) or
            
            // Watchdog and throttling
            all of ($task_manager, $watchdog, $cpu_throttle) or
            
            // Battery awareness
            all of ($battery_status, $ac_power, $battery_power) or
            
            // Obfuscated mining
            all of ($monero_wallet, $pool_string, $obfuscated) or
            
            // Random filename in system directory
            all of ($system32_color, $random_filename) or
            
            // DNS beacon
            all of ($api_ipify, $dns_beacon) or
            
            // General mining indicators
            all of ($xmrig, $mining, $monero) or
            
            // Evasion techniques
            all of ($injection, $evasion, $stealth)
        )
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
        $google_update_service = "Google Update Service (gupdatem)" nocase
        
        // Scheduled task persistence
        $task_create = "CreateTask" nocase
        $schtasks = "schtasks" nocase
        $ddriver = "Ddriver" nocase
        $every_30_min = "every 30 min" nocase
        
        // File system persistence
        $system32_color = "System32\\spool\\drivers\\color\\"
        $random_8_letter = /[a-z]{8}\.exe/
    
    condition:
        uint16(0) == 0x5A4D and 
        (
            // Registry persistence with ctfmon
            all of ($run_key, $ctfmon) or
            
            // Service masquerading as Google Update
            all of ($service_create, $google_update_service) or
            all of ($gupdatem, $service_start) or
            
            // Scheduled task resurrection
            all of ($task_create, $ddriver, $every_30_min) or
            all of ($schtasks, $ddriver) or
            
            // File system persistence
            all of ($system32_color, $random_8_letter)
        )
}

rule urcs_evasion {
    meta:
        description = "Detects URCS evasion techniques"
        author = "URCS Investigator Team"
        date = "2024"
        reference = "MITRE ATT&CK T1562.001"
        severity = "medium"
    
    strings:
        // Task Manager detection and CPU throttling
        $taskmgr = "taskmgr.exe" nocase

        $watchdog_thread = "watchdog thread" nocase
        $cpu_throttle = "CPU throttle" nocase
        
        // Thread affinity manipulation
        $thread_affinity = "SetThreadAffinityMask" nocase
        $cpu_usage = "GetSystemPowerStatus" nocase
        
        // Battery-aware throttling
        $battery_status = "GetSystemPowerStatus" nocase
        $ac_power = "AC power" nocase
        $battery_power = "battery" nocase
        $idle_time = "idle time" nocase
        $idle_5_min = "5 min" nocase
        
        // Self-deletion after injection
        $delete_file = "DeleteFile" nocase
        $delete_file_w = "DeleteFileW" nocase
        $remove_item = "Remove-Item" nocase
        $self_delete = "self-delete" nocase
        $after_injection = "after injection" nocase
        
        // Process injection
        $virtual_alloc = "VirtualAllocEx" nocase
        $write_process = "WriteProcessMemory" nocase
        $create_remote = "CreateRemoteThread" nocase
        $process_hollow = "process hollow" nocase
        
        // Explorer.exe targeting
        $explorer_exe = "explorer.exe" nocase
        $hollow_explorer = "hollow explorer" nocase
    
    condition:
        uint16(0) == 0x5A4D and 
        (
            // Watchdog thread with Task Manager detection
            all of ($taskmgr, $watchdog_thread, $cpu_throttle) or
            
            // Battery-aware throttling
            all of ($battery_status, $ac_power, $battery_power, $idle_5_min) or
            
            // Self-deletion after injection
            all of ($delete_file, $self_delete, $after_injection) or
            all of ($delete_file_w, $self_delete, $after_injection) or
            
            // Process hollowing into explorer.exe
            all of ($explorer_exe, $process_hollow, $virtual_alloc, $write_process) or
            
            // Thread affinity manipulation
            all of ($thread_affinity, $cpu_usage, $taskmgr)
        )
}

rule urcs_network {
    meta:
        description = "Detects URCS network communication"
        author = "URCS Investigator Team"
        date = "2024"
        reference = "MITRE ATT&CK T1071.001"
        severity = "high"
    
    strings:
        // DNS beacon to api.ipify.org
        $api_ipify = "api.ipify.org" nocase
        $dns_query = "DnsQuery" nocase
        $dns_beacon = "dns beacon" nocase
        
        // Stratum protocol and mining pools
        $stratum = "stratum" nocase
        $pool_connection = "pool" nocase
        $mining_pool = "mining pool" nocase
        $gulf_moneroocean = "gulf.moneroocean.stream:10032"
        
        // Network functions
        $connect = "connect" nocase
        $send = "send" nocase
        $recv = "recv" nocase
        
        // Port numbers for mining
        $port_10032 = ":10032"
        $port_3333 = ":3333"
        $port_7777 = ":7777"
        
        // Mining traffic patterns
        $mining_traffic = "mining traffic" nocase
        $before_mining = "before mining" nocase
    
    condition:
        uint16(0) == 0x5A4D and 
        (
            // DNS beacon to api.ipify.org before mining
            all of ($api_ipify, $dns_query, $before_mining) or
            all of ($api_ipify, $dns_beacon) or
            
            // Stratum protocol connections
            all of ($stratum, $pool_connection, $gulf_moneroocean) or
            all of ($stratum, $mining_pool) or
            
            // Mining port connections
            any of ($port_10032, $port_3333, $port_7777) or
            
            // Mining traffic patterns
            all of ($mining_traffic, $connect, $send, $recv)
        )
}

rule urcs_fake_installer {
    meta:
        description = "Detects fake installer dropper behavior"
        author = "URCS Investigator Team"
        date = "2024"
        reference = "MITRE ATT&CK T1204.002"
        severity = "high"
    
    strings:
        // Fake installer indicators
        $chrome_update = "Chrome_update.exe" nocase
        $fake_installer = "fake installer" nocase
        $side_by_side = "side-by-side" nocase
        $legitimate_installer = "legitimate installer" nocase
        
        // Dropper behavior
        $dropper = "dropper" nocase
        $extract = "extract" nocase
        $payload = "payload" nocase
        
        // Installation simulation
        $install = "install" nocase

        $chrome_install = "chrome install" nocase
    
    condition:
        uint16(0) == 0x5A4D and 
        (
            // Fake Chrome update installer
            all of ($chrome_update, $fake_installer) or
            
            // Side-by-side with legitimate installer
            all of ($side_by_side, $legitimate_installer, $chrome_update) or
            
            // Dropper behavior
            all of ($dropper, $extract, $payload) or
            
            // Installation simulation
            all of ($install, $chrome_install, $fake_installer)
        )
}

rule urcs_self_deletion {
    meta:
        description = "Detects self-deletion behavior after injection"
        author = "URCS Investigator Team"
        date = "2024"
        reference = "MITRE ATT&CK T1070.004"
        severity = "medium"
    
    strings:
        // Self-deletion functions
        $delete_file = "DeleteFile" nocase
        $delete_file_w = "DeleteFileW" nocase
        $remove_item = "Remove-Item" nocase
        
        // Self-deletion indicators
        $self_delete = "self-delete" nocase
        $self_removal = "self-removal" nocase
        
        // After injection context
        $after_injection = "after injection" nocase
        $post_injection = "post injection" nocase
        $injection_complete = "injection complete" nocase
        
        // File path manipulation
        $own_path = "own path" nocase
        $current_file = "current file" nocase
        $executable_path = "executable path" nocase
    
    condition:
        uint16(0) == 0x5A4D and 
        (
            // Self-deletion after injection
            all of ($delete_file, $self_delete, $after_injection) or
            all of ($delete_file_w, $self_delete, $after_injection) or
            
            // Self-removal patterns
            all of ($remove_item, $self_removal, $post_injection) or
            
            // Delete own executable
            all of ($delete_file, $own_path, $executable_path) or
            
            // Self-deletion with context
            all of ($self_delete, $injection_complete, $current_file)
        )
}

rule urcs_battery_aware {
    meta:
        description = "Detects battery-aware throttling behavior"
        author = "URCS Investigator Team"
        date = "2024"
        reference = "MITRE ATT&CK T1562.001"
        severity = "medium"
    
    strings:
        // Battery status functions
        $battery_status = "GetSystemPowerStatus" nocase
        $power_status = "power status" nocase
        $battery_info = "battery info" nocase
        
        // Power states
        $ac_power = "AC power" nocase
        $battery_power = "battery power" nocase
        $charging = "charging" nocase
        $discharging = "discharging" nocase
        
        // Idle time detection
        $idle_time = "idle time" nocase
        $idle_5_min = "5 min" nocase
        $idle_10_min = "10 min" nocase
        $user_activity = "user activity" nocase
        
        // Throttling behavior
        $throttle = "throttle" nocase
        $cpu_usage = "CPU usage" nocase
        
        // Usage percentages
        $usage_90 = "90%" nocase
        $usage_100 = "100%" nocase
        $usage_60 = "60%" nocase
        $usage_70 = "70%" nocase
    
    condition:
        uint16(0) == 0x5A4D and 
        (
            // Battery-aware throttling
            all of ($battery_status, $ac_power, $usage_90) or
            all of ($battery_status, $battery_power, $usage_60) or
            
            // Idle time detection
            all of ($idle_time, $idle_5_min, $usage_100) or
            all of ($idle_time, $idle_10_min, $usage_90) or
            
            // User activity detection
            all of ($user_activity, $usage_60, $usage_70) or
            
            // Power state monitoring
            all of ($power_status, $charging, $throttle) or
            all of ($battery_info, $discharging, $cpu_usage)
        )
}