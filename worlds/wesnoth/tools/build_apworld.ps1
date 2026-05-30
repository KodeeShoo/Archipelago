param(
    [string]$OutputPath = "../../../dist/wesnoth.apworld"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent (Split-Path -Parent $root)
$dist = Split-Path -Parent (Join-Path $PSScriptRoot $OutputPath)
$target = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot $OutputPath) -ErrorAction SilentlyContinue
$source = $root
$staging = Join-Path $repoRoot "build\wesnoth_apworld_staging"

if (-not (Test-Path -LiteralPath $source)) {
    throw "Could not find world source at $source"
}

if (Test-Path -LiteralPath $staging) {
    Remove-Item -LiteralPath $staging -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $staging | Out-Null
New-Item -ItemType Directory -Force -Path $dist | Out-Null
Copy-Item -LiteralPath $source -Destination (Join-Path $staging "wesnoth") -Recurse

$resolvedOutput = Join-Path $PSScriptRoot $OutputPath
if (Test-Path -LiteralPath $resolvedOutput) {
    Remove-Item -LiteralPath $resolvedOutput -Force
}

$zipOutput = [System.IO.Path]::ChangeExtension($resolvedOutput, ".zip")
if (Test-Path -LiteralPath $zipOutput) {
    Remove-Item -LiteralPath $zipOutput -Force
}

Compress-Archive -Path (Join-Path $staging "wesnoth") -DestinationPath $zipOutput -Force
Move-Item -LiteralPath $zipOutput -Destination $resolvedOutput
Write-Host "Built $resolvedOutput"
