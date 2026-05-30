#Requires AutoHotkey v2.0
#SingleInstance Force

; ============================================================
;  ButtonID.ahk — MX Master 3S Button Identifier
;  Press any mouse button to see its AHK name.
;  Press Escape or close the window to exit.
; ============================================================

MyGui := Gui("+AlwaysOnTop", "MX Master 3S — Button Identifier")
MyGui.SetFont("s14 bold", "Consolas")
MyGui.Add("Text", "w420 Center", "Press any mouse button...")
MyGui.SetFont("s22 bold", "Consolas")
global ResultText := MyGui.Add("Text", "w420 h60 Center cBlue", "---")
MyGui.SetFont("s10 norm", "Segoe UI")
MyGui.Add("Text", "w420 Center cGray", "ESC to exit  |  Leave this window open while testing")
MyGui.Show("w440 h160")

ShowButton(name) {
    global ResultText
    ResultText.Value := name
    ToolTip(name)
    SetTimer(() => ToolTip(), -1500)
}

; ---- All catchable mouse buttons ----
MButton::  ShowButton("MButton  (scroll wheel click)")
XButton1:: ShowButton("XButton1  (back/side button)")
XButton2:: ShowButton("XButton2  (forward/side button)")
WheelLeft::  ShowButton("WheelLeft  (horizontal scroll ←)")
WheelRight:: ShowButton("WheelRight  (horizontal scroll →)")

Escape:: ExitApp
