; ============================================================
;  ClickerOn.ahk
;  AHK v2.0+
;  PURPOSE : Remotely ENABLE ActiveClicker without opening it
;  HOW     : Double-click this file to send the ON signal
;  REQUIRES: ActiveClicker.ahk must already be running
; ============================================================

#Requires AutoHotkey v2.0
#SingleInstance Force

DetectHiddenWindows(true)

if WinExist("ActiveClicker.ahk ahk_class AutoHotkey")
{
    PostMessage(0x5554, 0, 0)
    ToolTip("[Clicker] Turned ON.")
    Sleep(1500)
}
else
{
    MsgBox("ActiveClicker.ahk is not running.`nLaunch it first from C:\Users\mylab\AHK\", "Clicker Not Running", "Icon!")
}

ToolTip()
ExitApp()
