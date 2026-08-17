[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$HookArguments
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-GitSingleValue {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,
        [Parameter(Mandatory = $true)]
        [string]$Description
    )

    $output = @(& git @Arguments 2>&1)
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "$Description failed (exit $exitCode): $($output -join [Environment]::NewLine)"
    }

    $values = @($output | Where-Object { $_ -is [string] -and $_.Length -gt 0 })
    if ($values.Count -ne 1) {
        throw "$Description must produce exactly one non-empty value."
    }

    return [string]$values[0]
}

function Get-WorktreeConfigValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Key
    )

    $stdoutPath = [System.IO.Path]::GetTempFileName()
    $stderrPath = [System.IO.Path]::GetTempFileName()
    try {
        $process = Start-Process -FilePath 'git' `
            -ArgumentList @('config', '--worktree', '--null', '--get-all', $Key) `
            -NoNewWindow -PassThru -Wait `
            -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
        $stdout = [System.IO.File]::ReadAllBytes($stdoutPath)
        $stderr = [System.IO.File]::ReadAllText($stderrPath).Trim()

        if ($process.ExitCode -eq 1 -and $stdout.Length -eq 0) {
            return $null
        }
        if ($process.ExitCode -ne 0) {
            $suffix = if ($stderr.Length -gt 0) { ": $stderr" } else { '' }
            throw "Could not read $Key from the current worktree configuration (exit $($process.ExitCode))$suffix"
        }

        $text = [System.Text.Encoding]::UTF8.GetString($stdout)
        $values = [System.Collections.Generic.List[string]]::new()
        $start = 0
        for ($index = 0; $index -lt $text.Length; $index++) {
            if ($text[$index] -eq [char]0) {
                $values.Add($text.Substring($start, $index - $start))
                $start = $index + 1
            }
        }
        if ($start -ne $text.Length) {
            throw "Could not strictly parse $Key from the current worktree configuration."
        }
        if ($values.Count -ne 1 -or [string]::IsNullOrWhiteSpace($values[0])) {
            throw "$Key requires exactly one non-empty current-worktree value."
        }

        return $values[0]
    }
    finally {
        Remove-Item -LiteralPath $stdoutPath, $stderrPath -Force -ErrorAction SilentlyContinue
    }
}

function Invoke-WslValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Distro,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,
        [Parameter(Mandatory = $true)]
        [string]$Description
    )

    $output = @(& wsl.exe -d $Distro -- @Arguments 2>&1)
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "$Description failed for WSL distro '$Distro' (exit $exitCode): $($output -join [Environment]::NewLine)"
    }

    $values = @($output | Where-Object { $_ -is [string] -and $_.Length -gt 0 })
    if ($values.Count -ne 1) {
        throw "$Description must produce exactly one non-empty value for WSL distro '$Distro'."
    }

    return [string]$values[0]
}

function Get-DefaultWslDistro {
    $output = @(& wsl.exe -- sh -lc 'printf %s "$WSL_DISTRO_NAME"' 2>&1)
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "Could not determine the WSL default distro (exit $exitCode): $($output -join [Environment]::NewLine)"
    }

    $distro = ($output -join '').Trim()
    if ([string]::IsNullOrWhiteSpace($distro)) {
        throw 'Could not determine a non-empty WSL default distro.'
    }

    return $distro
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Windows Git is required for the WSL pre-commit bridge.'
}
if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    throw 'wsl.exe is required for the WSL pre-commit bridge; no Windows Python fallback is available.'
}

$windowsWorkTree = Get-GitSingleValue -Arguments @('rev-parse', '--show-toplevel') -Description 'Resolving the Windows Git worktree root'
$windowsGitDir = Get-GitSingleValue -Arguments @('rev-parse', '--absolute-git-dir') -Description 'Resolving the Windows Git directory'

$configuredDistro = Get-WorktreeConfigValue -Key 'hooks.wslDistro'
if ($null -ne $configuredDistro) {
    $distro = $configuredDistro
}
elseif (-not [string]::IsNullOrWhiteSpace($env:CODEX_WSL_DISTRO)) {
    $distro = $env:CODEX_WSL_DISTRO
}
else {
    $distro = Get-DefaultWslDistro
}

$availabilityOutput = @(& wsl.exe -d $distro -- sh -lc 'exit 0' 2>&1)
$availabilityExitCode = $LASTEXITCODE
if ($availabilityExitCode -ne 0) {
    throw "Checking WSL distro availability failed for WSL distro '$distro' (exit $availabilityExitCode): $($availabilityOutput -join [Environment]::NewLine)"
}

$base64Output = @(& wsl.exe -d $distro -- sh -lc 'command -v base64' 2>&1)
$base64ExitCode = $LASTEXITCODE
if ($base64ExitCode -ne 0 -or [string]::IsNullOrWhiteSpace(($base64Output -join '').Trim())) {
    throw "WSL pre-commit bridge requires base64 on PATH inside WSL distro '$distro' (exit $base64ExitCode); no Windows Python fallback is available: $($base64Output -join [Environment]::NewLine)"
}

$linuxWorkTree = Invoke-WslValue -Distro $distro -Arguments @('wslpath', '-a', '--', $windowsWorkTree) -Description 'Converting the Windows Git worktree root with wslpath'
$linuxGitDir = Invoke-WslValue -Distro $distro -Arguments @('wslpath', '-a', '--', $windowsGitDir) -Description 'Converting the Windows Git directory with wslpath'

$bashScript = @'
set -eu
worktree=$1
gitdir=$2
shift 2

if [ ! -x "$worktree/.venv/bin/python" ]; then
    echo "WSL pre-commit bridge requires executable Linux virtualenv Python: $worktree/.venv/bin/python" >&2
    exit 1
fi

cd "$worktree"
export GIT_DIR="$gitdir"
export GIT_WORK_TREE="$worktree"
exec uv run --frozen --no-sync python -m pre_commit hook-impl --config=.pre-commit-config.yaml --hook-type=pre-commit -- "$@"
'@

$encodedBashScript = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($bashScript))
$bashWrapper = 'printf %s "$1" | base64 -d | bash -s -- "${@:2}"'
$wslArguments = @(
    '-d', $distro, '--exec', 'bash', '-lc', $bashWrapper,
    'wsl-pre-commit-bridge', $encodedBashScript, $linuxWorkTree, $linuxGitDir
) + $HookArguments

& wsl.exe @wslArguments
exit $LASTEXITCODE
