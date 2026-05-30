; ============================================================
;  AIOSRevive.ahk
;  AHK v2.0+
;
;  PURPOSE : Launched by ActiveClicker when gaming is detected.
;            Watches silently until ALL gaming / anti-cheat
;            processes are gone, then relaunches ActiveClicker
;            and exits itself.
;
;  You never need to launch this manually.
; ============================================================

#Requires AutoHotkey v2.0
#SingleInstance Force

A_IconTip := "AIOSRevive â€” Waiting for gaming to end..."

SetTimer(CheckGamingCleared, 2000)

CheckGamingCleared() {
    static procs := [
        "EasyAntiCheat.exe",
        "EasyAntiCheat_EOS.exe",
        "EAAntiCheat.GameService.exe",
        "r5apex.exe",
        "bf2042.exe",
        "bf6.exe",
        "FIFA23.exe",
        "FIFA24.exe",
        "FIFA25.exe",
        "NHL24.exe",
        "NHL25.exe",
        "Battlefield.exe",
        "bf1.exe",
        "bfv.exe",
        "GTA5.exe",
        "PlayGTAV.exe"
    ]

    detected := false
    for p in procs {
        if ProcessExist(p) {
            detected := true
            break
        }
    }

    if !detected {
        try {
            fw := WinGetProcessName("A")
            if RegExMatch(fw, "i)(EasyAntiCheat|r5apex|bf2042|bf6|apex|valorant|fortnite|fifa|nhl|battlefield|overwatch|warzone|tarkov|rainbow|siege|destiny|halo|gta)")
                detected := true
        }
    }

    if !detected {
        ; All gaming cleared â€” relaunch clicker in revive mode and exit
        ToolTip("[AIOSRevive] Gaming cleared â€” relaunching ActiveClicker...")
        Sleep(1000)
        Run(A_AhkPath ' "C:\Users\mylab\AHK\ActiveClicker.ahk" revive')
        Sleep(500)
        ExitApp()
    }
}

