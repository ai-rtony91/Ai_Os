; ============================================================
;  ActiveClicker.ahk
;  AHK v2.0+
;
;  AUTO-LAUNCH : Starts when terminal opens (via PS profile)
;  GAMING      : Fully exits + hands off to AIOSRevive.ahk
;  AUTO-REVIVE : AIOSRevive.ahk relaunches this after gaming ends
;  TERMINAL    : Exits cleanly when terminal closes (normal mode)
;  REVIVE MODE : Launched with "revive" arg â€” skips terminal watch
;
;  TOGGLE : F8 = manual ON / OFF
;  REMOTE : ClickerOn.ahk  -> PostMessage 0x5554
;           ClickerOff.ahk -> PostMessage 0x5555
; ============================================================

#Requires AutoHotkey v2.0
#SingleInstance Force

; ---- Mode: were we launched by AIOSRevive after gaming? ----
global ReviveMode := (A_Args.Length > 0 && A_Args[1] = "revive")

; ---- Global state ----
global Enabled   := true
global GABlocked := false

; ---- Remote message listeners ----
OnMessage(0x5554, MsgEnable)
OnMessage(0x5555, MsgDisable)

; ---- Watchers ----
SetTimer(WatchGaming, 2000)

; ---- Logi Options+ wake restore ----
; WM_WTSSESSION_CHANGE (0x02B1) fires on session unlock (screen wake / Modern Standby resume)
; WTS_SESSION_UNLOCK = 8
OnMessage(0x02B1, OnSessionChange)

OnSessionChange(wParam, lParam, msg, hwnd) {
    if (wParam = 8) {  ; session unlocked = screen woke up
        SetTimer(RestartLogiAgent, -12000)  ; 12s delay — let USB re-enumerate first
    }
}

RestartLogiAgent() {
    Run('powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "C:\Users\mylab\AHK\LogiWakeRestore.ps1"', , "Hide")
    ToolTip("[Clicker] Logi restored after wake")
    SetTimer(() => ToolTip(), -3000)
}

; ---- Screenshot long press flag ----
global SSLongPress := false

; ---- CapsLock-safe key sender ----
; Releases all modifier keys first so combos like Win+Shift+S fire clean.
CapsSafe(keys) {
    local c := GetKeyState("CapsLock", "T")
    SetCapsLockState(c ? "AlwaysOn" : "AlwaysOff")
    Send("{Ctrl up}{Alt up}{Shift up}{LWin up}{RWin up}" keys)
    SetCapsLockState(c ? "On" : "Off")
}

; ---- Tray ----
UpdateTray()

; ==============================================================
;  HOTKEYS
; ==============================================================

F8:: {
    global Enabled
    Enabled := !Enabled
    UpdateTray()
    ToolTip("[Clicker] " (Enabled ? "ON" : "OFF"))
    SetTimer(() => ToolTip(), -2000)
}

MButton:: {
    global Enabled, GABlocked
    if Enabled && !GABlocked
        CapsSafe("{Enter}")
}


; ==============================================================
;  SCREENSHOT â€” XButton1 (forward thumb)
;
;  SHORT PRESS  = Win+Shift+S  â†’ snip mode selector (pick type)
;  LONG PRESS   = PrintScreen  â†’ full screen capture instantly
;
;  Hold threshold: 500ms
; ==============================================================

^!+2:: {
    global SSLongPress
    SSLongPress := false
    SetTimer(FireFullScreen, -500)
}

^!+2 up:: {
    global SSLongPress
    SetTimer(FireFullScreen, 0)
    if !SSLongPress
        CapsSafe("#+s")             ; short press â€” snip selector
}

FireFullScreen() {
    global SSLongPress
    SSLongPress := true
    CapsSafe("{PrintScreen}")       ; long press â€” full screen
}

; ==============================================================
;  CLAUDE ALLOW ONCE â€” XButton1 (back thumb) = Ctrl+NumpadEnter
; ==============================================================

XButton1:: CapsSafe("^{NumpadEnter}")

; ==============================================================
;  VOICE TYPING â€” Square button (gesture button next to scroll)
;
;  SETUP REQUIRED (one time):
;  Open Logi Options+ â†’ MX Master 3S â†’ Gesture Button
;  Set to "Keystroke" â†’ press Ctrl+Alt+Shift+F1 to capture it.
;  AHK catches that combo here and fires Win+H (voice typing).
; ==============================================================

^!+1:: {
    global Enabled, GABlocked
    if Enabled && !GABlocked
        CapsSafe("#{h}")            ; Win+H = Windows voice typing anywhere
}

; ==============================================================
;  GAMING / TERMINAL WATCHER
; ==============================================================

WatchGaming() {
    global GABlocked, ReviveMode
    static TerminalSeen := false

    ; ---- Terminal close detection (normal mode only) ----
    if !ReviveMode {
        termNow := ProcessExist("WindowsTerminal.exe") ? true : false
        if TerminalSeen && !termNow {
            ; Terminal was open and is now gone â€” exit cleanly, no revive
            ExitApp()
        }
        if termNow
            TerminalSeen := true
    }

    ; ---- Gaming process list ----
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

    ; Also check active window name
    if !detected {
        try {
            fw := WinGetProcessName("A")
            if RegExMatch(fw, "i)(EasyAntiCheat|r5apex|bf2042|bf6|apex|valorant|fortnite|fifa|nhl|battlefield|overwatch|warzone|tarkov|rainbow|siege|destiny|halo|gta)")
                detected := true
        }
    }

    ; ---- Gaming detected â€” hand off to AIOSRevive and exit ----
    if detected && !GABlocked {
        GABlocked := true
        ToolTip("[Clicker] Gaming detected â€” Exiting. AIOSRevive watching...")
        Sleep(800)
        Run(A_AhkPath ' "C:\Users\mylab\AHK\AIOSRevive.ahk"')
        Sleep(400)
        ExitApp()
    }
}

; ==============================================================
;  TRAY
; ==============================================================

ToggleItem(name, pos, menu) {
    global Enabled
    Enabled := !Enabled
    UpdateTray()
}

UpdateTray() {
    global Enabled, GABlocked, ReviveMode

    A_TrayMenu.Delete()
    A_TrayMenu.Add("Toggle  (F8)", ToggleItem)
    A_TrayMenu.Add()
    A_TrayMenu.Add("Exit Clicker", (*) => ExitApp())

    suffix := ReviveMode ? "  [revive]" : ""

    if GABlocked
        A_IconTip := "ActiveClicker â€” BLOCKED  (gaming active)" . suffix
    else if Enabled
        A_IconTip := "ActiveClicker â€” ON   (MButton = Enter)" . suffix
    else
        A_IconTip := "ActiveClicker â€” OFF  (paused)" . suffix
}

; ==============================================================
;  REMOTE CONTROL
; ==============================================================

MsgEnable(wParam, lParam, msg, hwnd) {
    global Enabled
    Enabled := true
    UpdateTray()
    ToolTip("[Clicker] Enabled remotely")
    SetTimer(() => ToolTip(), -2000)
}

MsgDisable(wParam, lParam, msg, hwnd) {
    global Enabled
    Enabled := false
    UpdateTray()
    ToolTip("[Clicker] Disabled remotely")
    SetTimer(() => ToolTip(), -2000)
}

