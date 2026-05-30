#Requires AutoHotkey v2.0
#SingleInstance Force

isPaused := false
blockedGameProcesses := ["GTA5.exe", "PlayGTAV.exe", "bf6.exe"]
SetTimer CheckBlockedGameProcesses, 2000

CheckBlockedGameProcesses() {
    global blockedGameProcesses
    for processName in blockedGameProcesses {
        if ProcessExist(processName) {
            ExitApp
        }
    }
}

MButton::{
    global isPaused
    if isPaused {
        return
    }
    Send "{Enter}"
}

; Manual pause/resume: Ctrl + Alt + P toggles MButton Enter behavior.
^!p::{
    global isPaused
    isPaused := !isPaused
}

; Emergency stop: Ctrl + Alt + M exits the helper.
^!m::ExitApp
