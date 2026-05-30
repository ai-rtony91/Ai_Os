# Logi Options+ Wake Restore
# Triggered on resume from sleep — restarts Logi agent so it reloads saved button profiles
Start-Sleep -Seconds 8
Stop-Process -Name 'logioptionsplus_agent' -ErrorAction SilentlyContinue
Stop-Process -Name 'logioptionsplus_appbroker' -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
Start-Process 'C:\Program Files\LogiOptionsPlus\logioptionsplus_agent.exe'
