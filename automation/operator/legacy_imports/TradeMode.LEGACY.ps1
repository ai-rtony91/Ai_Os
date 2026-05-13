# TradeMode - Z Fold Network + VPN Mandatory
Write-Host "TradeMode: Switching to Z Fold Hotspot..." -ForegroundColor Green
netsh wlan disconnect
Start-Sleep -Seconds 2
netsh interface set interface name="Ethernet 2" admin=enabled
Start-Sleep -Seconds 3
Write-Host "Connected to Z Fold. VPN MANDATORY - Kill-Switch ACTIVE" -ForegroundColor Yellow