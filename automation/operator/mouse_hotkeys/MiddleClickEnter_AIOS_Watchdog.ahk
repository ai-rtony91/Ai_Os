#NoEnv
#SingleInstance Force
#Persistent
SetTitleMatchMode, 2
DetectHiddenWindows, On

; ------------------------------------------------------------
; AI_OS MiddleClickEnter Watchdog
;
; Purpose:
; - Start MiddleClickEnter.ahk only when AI_OS is open
; - Stop MiddleClickEnter.ahk when AI_OS is closed
; - Stop it during gaming so it does not interfere
; ------------------------------------------------------------

targetScript := "C:\Users\mylab\OneDrive\Desktop\Ai_Os shortcut tools\MiddleClickEnter.ahk"
targetPid := ""

SetTimer, WatchAIOS, 1000
return

WatchAIOS:
    aiosOpen := false
    gamingOpen := false

    ; Detect AI_OS-related windows.
    ; Add/remove names here if needed.
    if WinExist("AI_OS MAIN CONTROL")
        aiosOpen := true

    if WinExist("Ai_Os")
        aiosOpen := true

    if WinExist("AI_OS")
        aiosOpen := true

    if WinExist("CODEX")
        aiosOpen := true

    ; Detect GTA / gaming.
    if WinExist("ahk_exe GTA5.exe")
        gamingOpen := true

    if WinExist("ahk_exe PlayGTAV.exe")
        gamingOpen := true

    ; If gaming is open, force MiddleClickEnter off.
    if (gamingOpen) {
        Gosub, StopTarget
        return
    }

    ; If AI_OS is open, start MiddleClickEnter.
    if (aiosOpen) {
        if (targetPid = "") {
            Run, "%targetScript%", , , newPid
            targetPid := newPid
        }
    } else {
        Gosub, StopTarget
    }

return

StopTarget:
    if (targetPid != "") {
        Process, Close, %targetPid%
        targetPid := ""
    }
return

; Manual emergency stop:
; Ctrl + Alt + M exits the watchdog and stops MiddleClickEnter.
^!m::
    Gosub, StopTarget
    ExitApp
return