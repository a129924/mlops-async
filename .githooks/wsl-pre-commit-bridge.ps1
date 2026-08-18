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

    $utf8 = [System.Text.UTF8Encoding]::new($false, $true)
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = 'git'
    $startInfo.Arguments = (($Arguments | ForEach-Object {
        ConvertTo-WindowsCommandLineArgument -Argument $_
    }) -join ' ')
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.StandardOutputEncoding = $utf8
    $startInfo.StandardErrorEncoding = $utf8

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    if (-not $process.Start()) {
        throw 'Could not start Windows Git.'
    }

    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $process.WaitForExit()
    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()

    if ($process.ExitCode -ne 0) {
        $output = @(
            $stdout -split "`r?`n"
            $stderr -split "`r?`n"
        ) | Where-Object { $_.Length -gt 0 }
        throw "$Description failed (exit $($process.ExitCode)): $($output -join [Environment]::NewLine)"
    }

    $values = @($stdout -split "`r?`n" | Where-Object { $_.Length -gt 0 })
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

    $utf8 = [System.Text.UTF8Encoding]::new($false, $true)
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = 'git'
    $startInfo.Arguments = ((@('config', '--worktree', '--null', '--get-all', $Key) | ForEach-Object {
        ConvertTo-WindowsCommandLineArgument -Argument $_
    }) -join ' ')
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.StandardOutputEncoding = $utf8
    $startInfo.StandardErrorEncoding = $utf8

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    if (-not $process.Start()) {
        throw 'Could not start Windows Git.'
    }

    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $process.WaitForExit()
    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult().Trim()

    if ($process.ExitCode -eq 1 -and $stdout.Length -eq 0) {
        return $null
    }
    if ($process.ExitCode -ne 0) {
        $suffix = if ($stderr.Length -gt 0) { ": $stderr" } else { '' }
        throw "Could not read $Key from the current worktree configuration (exit $($process.ExitCode))$suffix"
    }

    $values = [System.Collections.Generic.List[string]]::new()
    $start = 0
    for ($index = 0; $index -lt $stdout.Length; $index++) {
        if ($stdout[$index] -eq [char]0) {
            $values.Add($stdout.Substring($start, $index - $start))
            $start = $index + 1
        }
    }
    if ($start -ne $stdout.Length) {
        throw "Could not strictly parse $Key from the current worktree configuration."
    }
    if ($values.Count -ne 1 -or [string]::IsNullOrWhiteSpace($values[0])) {
        throw "$Key requires exactly one non-empty current-worktree value."
    }

    return $values[0]
}

function ConvertTo-WindowsCommandLineArgument {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$Argument
    )

    if ($Argument.Length -eq 0) {
        return '""'
    }
    if ($Argument -notmatch '[\s"]') {
        return $Argument
    }

    $quotedArgument = [System.Text.StringBuilder]::new()
    [void]$quotedArgument.Append([char]34)
    $backslashCount = 0
    foreach ($character in $Argument.ToCharArray()) {
        if ($character -eq [char]92) {
            $backslashCount++
            continue
        }

        if ($character -eq [char]34) {
            [void]$quotedArgument.Append([string]::new([char]92, ($backslashCount * 2) + 1))
            [void]$quotedArgument.Append([char]34)
        }
        else {
            [void]$quotedArgument.Append([string]::new([char]92, $backslashCount))
            [void]$quotedArgument.Append($character)
        }
        $backslashCount = 0
    }
    [void]$quotedArgument.Append([string]::new([char]92, $backslashCount * 2))
    [void]$quotedArgument.Append([char]34)
    return $quotedArgument.ToString()
}

function Invoke-WslProcess {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [AllowEmptyString()]
        [string[]]$Arguments
    )

    $utf8 = [System.Text.UTF8Encoding]::new($false, $true)
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = 'wsl.exe'
    $startInfo.Arguments = (($Arguments | ForEach-Object {
        ConvertTo-WindowsCommandLineArgument -Argument $_
    }) -join ' ')
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.StandardOutputEncoding = $utf8
    $startInfo.StandardErrorEncoding = $utf8

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    if (-not $process.Start()) {
        throw 'Could not start wsl.exe.'
    }

    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $process.WaitForExit()

    return [PSCustomObject]@{
        ExitCode = $process.ExitCode
        Stdout = $stdoutTask.GetAwaiter().GetResult()
        Stderr = $stderrTask.GetAwaiter().GetResult()
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

    $result = Invoke-WslProcess -Arguments (@('-d', $Distro, '--') + $Arguments)
    $exitCode = $result.ExitCode
    $stdout = $result.Stdout
    $stderr = $result.Stderr.Trim()

    if ($exitCode -ne 0) {
        $diagnostic = if ($stderr.Length -gt 0) { $stderr } else { '<no stderr output>' }
        throw "$Description failed for WSL distro '$Distro' (exit $exitCode); stderr: $diagnostic"
    }

    $values = @($stdout -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($values.Count -ne 1) {
        throw "$Description must produce exactly one non-empty value from stdout for WSL distro '$Distro'."
    }

    return [string]$values[0]
}

function ConvertTo-LinuxSingleObjectPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Distro,
        [Parameter(Mandatory = $true)]
        [string]$VariableName,
        [Parameter(Mandatory = $true)]
        [string]$WindowsPath
    )

    if ([string]::IsNullOrWhiteSpace($WindowsPath)) {
        throw "$VariableName is set but is empty; refusing to run the WSL pre-commit bridge."
    }
    if ($WindowsPath.Contains(';')) {
        throw "$VariableName contains a Windows multi-path separator; refusing to run the WSL pre-commit bridge because alternate-object path-list quoting cannot be translated unambiguously."
    }

    $isDriveQualifiedPath = $WindowsPath -match '^[A-Za-z]:[\\/]'
    $firstColonIndex = $WindowsPath.IndexOf(':')
    if ($firstColonIndex -ge 0 -and
        ((-not $isDriveQualifiedPath) -or $WindowsPath.IndexOf(':', $firstColonIndex + 1) -ge 0)) {
        throw "$VariableName contains a colon-separated multi-path value; refusing to run the WSL pre-commit bridge because alternate-object path-list quoting cannot be translated unambiguously."
    }
    if ($WindowsPath -notmatch '^(?:[A-Za-z]:[\\/]|\\\\[^\\/]+[\\/][^\\/]+)') {
        throw "$VariableName is set but is not one absolute Windows path; refusing to run the WSL pre-commit bridge."
    }

    $linuxPath = Invoke-WslValue -Distro $Distro -Arguments @('wslpath', '-a', '--', $WindowsPath) -Description "Converting $VariableName with wslpath"
    if ($linuxPath.Contains(';') -or $linuxPath.Contains(':')) {
        throw "Converting $VariableName with wslpath produced a multi-path value; refusing to run the WSL pre-commit bridge."
    }
    if (-not $linuxPath.StartsWith('/')) {
        throw "Converting $VariableName with wslpath did not produce an absolute Linux path; refusing to run the WSL pre-commit bridge."
    }

    return $linuxPath
}

function Get-DefaultWslDistro {
    $result = Invoke-WslProcess -Arguments @('--', 'sh', '-lc', 'printf %s "$WSL_DISTRO_NAME"')
    $exitCode = $result.ExitCode
    $stdout = $result.Stdout
    $stderr = $result.Stderr.Trim()

    if ($exitCode -ne 0) {
        $diagnostic = if ($stderr.Length -gt 0) { $stderr } else { '<no stderr output>' }
        throw "Could not determine the WSL default distro (exit $exitCode); stderr: $diagnostic"
    }

    $values = @($stdout -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($values.Count -ne 1) {
        throw 'Could not determine exactly one non-empty WSL default distro from stdout.'
    }

    return [string]$values[0]
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

$availabilityResult = Invoke-WslProcess -Arguments @('-d', $distro, '--', 'sh', '-lc', 'exit 0')
$availabilityExitCode = $availabilityResult.ExitCode
if ($availabilityExitCode -ne 0) {
    $availabilityOutput = @($availabilityResult.Stdout, $availabilityResult.Stderr) | Where-Object { $_.Length -gt 0 }
    throw "Checking WSL distro availability failed for WSL distro '$distro' (exit $availabilityExitCode): $($availabilityOutput -join [Environment]::NewLine)"
}

$base64Result = Invoke-WslProcess -Arguments @('-d', $distro, '--', 'sh', '-lc', 'command -v base64')
$base64ExitCode = $base64Result.ExitCode
if ($base64ExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($base64Result.Stdout.Trim())) {
    $base64Output = @($base64Result.Stdout, $base64Result.Stderr) | Where-Object { $_.Length -gt 0 }
    throw "WSL pre-commit bridge requires base64 on PATH inside WSL distro '$distro' (exit $base64ExitCode); no Windows Python fallback is available: $($base64Output -join [Environment]::NewLine)"
}

$linuxWorkTree = Invoke-WslValue -Distro $distro -Arguments @('wslpath', '-a', '--', $windowsWorkTree) -Description 'Converting the Windows Git worktree root with wslpath'
$linuxGitDir = Invoke-WslValue -Distro $distro -Arguments @('wslpath', '-a', '--', $windowsGitDir) -Description 'Converting the Windows Git directory with wslpath'
$linuxGitIndexFile = ''
$linuxGitObjectDirectory = ''
$linuxGitAlternateObjectDirectories = ''
$windowsSkip = [Environment]::GetEnvironmentVariable('SKIP', 'Process')
$skipForWsl = if ([string]::IsNullOrEmpty($windowsSkip)) {
    'unset'
}
else {
    'value:' + [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($windowsSkip))
}
if (Test-Path -LiteralPath 'Env:GIT_INDEX_FILE') {
    $windowsGitIndexFile = [Environment]::GetEnvironmentVariable('GIT_INDEX_FILE', 'Process')
    if ([string]::IsNullOrWhiteSpace($windowsGitIndexFile)) {
        throw 'GIT_INDEX_FILE is set but is empty; refusing to run the WSL pre-commit bridge.'
    }

    if ($windowsGitIndexFile -notmatch '^(?:[A-Za-z]:[\\/]|\\\\[^\\/]+[\\/][^\\/]+)') {
        if ($windowsGitIndexFile -match '^(?:[A-Za-z]:|[\\/])') {
            throw 'GIT_INDEX_FILE is set but is not an absolute Windows path or a valid relative path; refusing to run the WSL pre-commit bridge.'
        }

        try {
            $windowsGitIndexFile = [System.IO.Path]::GetFullPath(
                [System.IO.Path]::Combine($windowsWorkTree, $windowsGitIndexFile)
            )
        }
        catch {
            throw "GIT_INDEX_FILE could not be resolved from the Windows Git worktree root; refusing to run the WSL pre-commit bridge: $($_.Exception.Message)"
        }
    }

    if ($windowsGitIndexFile -notmatch '^(?:[A-Za-z]:[\\/]|\\\\[^\\/]+[\\/][^\\/]+)') {
        throw 'GIT_INDEX_FILE did not resolve to an absolute Windows path; refusing to run the WSL pre-commit bridge.'
    }

    $linuxGitIndexFile = Invoke-WslValue -Distro $distro -Arguments @('wslpath', '-a', '--', $windowsGitIndexFile) -Description 'Converting GIT_INDEX_FILE with wslpath'
    if (-not $linuxGitIndexFile.StartsWith('/')) {
        throw 'Converting GIT_INDEX_FILE with wslpath did not produce an absolute Linux path; refusing to run the WSL pre-commit bridge.'
    }
}

if (Test-Path -LiteralPath 'Env:GIT_OBJECT_DIRECTORY') {
    $windowsGitObjectDirectory = [Environment]::GetEnvironmentVariable('GIT_OBJECT_DIRECTORY', 'Process')
    $linuxGitObjectDirectory = ConvertTo-LinuxSingleObjectPath -Distro $distro -VariableName 'GIT_OBJECT_DIRECTORY' -WindowsPath $windowsGitObjectDirectory
}

if (Test-Path -LiteralPath 'Env:GIT_ALTERNATE_OBJECT_DIRECTORIES') {
    $windowsGitAlternateObjectDirectories = [Environment]::GetEnvironmentVariable('GIT_ALTERNATE_OBJECT_DIRECTORIES', 'Process')
    $linuxGitAlternateObjectDirectories = ConvertTo-LinuxSingleObjectPath -Distro $distro -VariableName 'GIT_ALTERNATE_OBJECT_DIRECTORIES' -WindowsPath $windowsGitAlternateObjectDirectories
}

$bashScript = @'
set -eu
if [ "$#" -lt 6 ]; then
    echo "WSL pre-commit bridge requires six metadata arguments" >&2
    exit 1
fi
worktree=$1
gitdir=$2
gitindex=$3
gitobjectdir=$4
gitalternateobjectdirs=$5
skip_payload=$6
shift 6

if [ ! -x "$worktree/.venv/bin/python" ]; then
    echo "WSL pre-commit bridge requires executable Linux virtualenv Python: $worktree/.venv/bin/python" >&2
    exit 1
fi

cd "$worktree"
export GIT_DIR="$gitdir"
export GIT_WORK_TREE="$worktree"
if [ -n "$gitindex" ]; then
    export GIT_INDEX_FILE="$gitindex"
else
    unset GIT_INDEX_FILE
fi
if [ -n "$gitobjectdir" ]; then
    export GIT_OBJECT_DIRECTORY="$gitobjectdir"
else
    unset GIT_OBJECT_DIRECTORY
fi
if [ -n "$gitalternateobjectdirs" ]; then
    export GIT_ALTERNATE_OBJECT_DIRECTORIES="$gitalternateobjectdirs"
else
    unset GIT_ALTERNATE_OBJECT_DIRECTORIES
fi
case "$skip_payload" in
    unset)
        unset SKIP
        ;;
    value:*)
        skip=$(printf %s "${skip_payload#value:}" | base64 -d)
        export SKIP="$skip"
        ;;
    *)
        echo "WSL pre-commit bridge received an invalid SKIP payload" >&2
        exit 1
        ;;
esac
exec uv run --frozen --no-sync python -m pre_commit hook-impl --config=.pre-commit-config.yaml --hook-type=pre-commit -- "$@"
'@

$encodedBashScript = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($bashScript))
$bashWrapper = 'set -o pipefail; printf %s "$1" | base64 -d | bash -s -- "${@:2}"'
$wslArguments = @(
    '-d', $distro, '--exec', 'bash', '-lc', $bashWrapper,
    'wsl-pre-commit-bridge', $encodedBashScript, $linuxWorkTree, $linuxGitDir, $linuxGitIndexFile,
    $linuxGitObjectDirectory, $linuxGitAlternateObjectDirectories, $skipForWsl
)
if ($null -ne $HookArguments) {
    $wslArguments += $HookArguments
}

$hookResult = Invoke-WslProcess -Arguments $wslArguments
if ($hookResult.Stdout.Length -gt 0) {
    [Console]::Out.Write($hookResult.Stdout)
}
if ($hookResult.Stderr.Length -gt 0) {
    [Console]::Error.Write($hookResult.Stderr)
}
exit $hookResult.ExitCode
