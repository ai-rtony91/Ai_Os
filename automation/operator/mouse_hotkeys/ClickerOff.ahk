; ============================================================
;  ClickerOff.ahk
;  AHK v2.0+
;  PURPOSE : Remotely DISABLE ActiveClicker without closing it
;  HOW     : Double-click this file to send the OFF signal
;  REQUIRES: ActiveClicker.ahk must already be running
;
;  NOTE    : This PAUSES the clicker (MButton stops sending Enter)
;            It does NOT exit ActiveClicker.ahk
;            To fully exit: right-click the tray icon -> Exit Clicker
; ============================================================

#Requires AutoHotkey v2.0
#SingleInstance Force

DetectHiddenWindows(true)

if WinExist("ActiveClicker.ahk ahk_class AutoHotkey")
{
    PostMessage(0x5555, 0, 0)
    ToolTip("[Clicker] Turned OFF.")
    Sleep(1500)
}
else
{
    MsgBox("ActiveClicker.ahk is not running.`nNothing to disable.", "Clicker Not Running", "Icon!")
}

ToolTip()
ExitApp()
