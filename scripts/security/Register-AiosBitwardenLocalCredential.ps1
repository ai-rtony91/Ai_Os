[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$credentialDirectory = Join-Path -Path $env:LOCALAPPDATA -ChildPath "AIOS\Security"
$credentialPath = Join-Path -Path $credentialDirectory -ChildPath "bitwarden-master-password.dpapi"

$registered = $false
$pathPresent = $false

try {
    $masterPassword = Read-Host -Prompt "Enter Bitwarden master password" -AsSecureString

    if (-not (Test-Path -LiteralPath $credentialDirectory)) {
        New-Item -Path $credentialDirectory -ItemType Directory -Force | Out-Null
    }

    $encryptedCredential = ConvertFrom-SecureString -SecureString $masterPassword
    [System.IO.File]::WriteAllText($credentialPath, $encryptedCredential, [System.Text.Encoding]::ASCII)
    $registered = $true

    try {
        $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
        $acl = Get-Acl -LiteralPath $credentialPath
        $acl.SetAccessRuleProtection($true, $false)
        $acl.Access | ForEach-Object { $null = $acl.RemoveAccessRule($_) }
        if ($identity) {
            $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
                $identity,
                [System.Security.AccessControl.FileSystemRights]::FullControl,
                [System.Security.AccessControl.InheritanceFlags]::None,
                [System.Security.AccessControl.PropagationFlags]::None,
                [System.Security.AccessControl.AccessControlType]::Allow
            )
            $null = $acl.AddAccessRule($accessRule)
            Set-Acl -LiteralPath $credentialPath -AclObject $acl | Out-Null
        }
    } catch {
        # Optional hardening only; safe to continue if ACL changes are blocked.
    }

    $pathPresent = Test-Path -LiteralPath $credentialPath
} catch {
    $registered = $false
    $pathPresent = Test-Path -LiteralPath $credentialPath
}

Write-Output ("AIOS_BITWARDEN_LOCAL_CREDENTIAL_REGISTERED={0}" -f $registered.ToString().ToLower())
Write-Output ("AIOS_BITWARDEN_LOCAL_CREDENTIAL_PATH_PRESENT={0}" -f $pathPresent.ToString().ToLower())
