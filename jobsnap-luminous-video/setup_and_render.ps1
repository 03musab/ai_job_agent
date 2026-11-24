# One-click Audio Mix + HyperFrames 1080p MP4 Render + Fast Mux for JobSnap Luminous Glass (32.0s)
# Usage:
#   Auto-detect files in work\ and full render:
#     powershell -ExecutionPolicy Bypass -File jobsnap-luminous-video\setup_and_render.ps1
#   Pass exact audio file paths (and fast 2-second mux onto already-rendered MP4 with -MuxOnly):
#     powershell -ExecutionPolicy Bypass -File jobsnap-luminous-video\setup_and_render.ps1 -Voice "path\to\voice.mp3" -Music "path\to\music.mp3" -MuxOnly

param(
    [string]$Voice = "",
    [string]$Music = "",
    [switch]$MuxOnly
)

$ErrorActionPreference = "Stop"
$Root  = "c:\Users\musab\Desktop\ai_job_agent\jobsnap-luminous-video"
$AeSrc = "c:\Users\musab\Desktop\ai_job_agent\.agents\skills\claude-motion\vendor\ae-motion\ae-motion.js"

New-Item -ItemType Directory -Force -Path "$Root\assets\audio" | Out-Null
New-Item -ItemType Directory -Force -Path "$Root\renders" | Out-Null
if (Test-Path $AeSrc) { Copy-Item $AeSrc "$Root\assets\ae-motion.js" -Force }

Push-Location $Root

# List all audio files currently inside work\ so nothing is silently missed
$WorkAudio = Get-ChildItem -Path "work" -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension -match '^\.(mp3|wav|m4a|aac|ogg|flac)$' }
Write-Host "Audio files found in jobsnap-luminous-video\work\:" -ForegroundColor DarkCyan
if ($WorkAudio) { $WorkAudio | ForEach-Object { Write-Host "  - $($_.Name)" } } else { Write-Host "  (none)" -ForegroundColor Yellow }

# 1. Resolve Voiceover file
$VoSrc = $null
if ($Voice -and (Test-Path $Voice)) {
    $VoSrc = (Resolve-Path $Voice).Path
} else {
    $VoMatch = $WorkAudio | Where-Object { $_.Name -ne "My_voice.mp3" -and $_.Name -match '(vo|voice|narrat|eleven|speech|script|record)' } | Select-Object -First 1
    if ($VoMatch) { $VoSrc = $VoMatch.FullName }
}

if ($VoSrc) {
    Write-Host "1/5 Mastering voiceover ($VoSrc -> assets\audio\vo.wav at -15 LUFS)..." -ForegroundColor Cyan
    ffmpeg -v error -y -i "$VoSrc" -af "highpass=f=75,acompressor=threshold=-20dB:ratio=2.2:attack=8:release=120:makeup=2,loudnorm=I=-15:TP=-1.5:LRA=9" -ar 48000 -ac 2 -c:a pcm_s24le assets\audio\vo.wav
} else {
    Write-Host "1/5 WARNING: No voiceover file matched! Pass -Voice ""path\to\file.mp3"" or name it work\vo_final.mp3" -ForegroundColor Red
}

# 2. Resolve Background Music file
$BgSrc = $null
if ($Music -and (Test-Path $Music)) {
    $BgSrc = (Resolve-Path $Music).Path
} else {
    $BgMatch = $WorkAudio | Where-Object { $_.FullName -ne $VoSrc -and $_.Name -ne "My_voice.mp3" -and $_.Name -match '(bg|music|song|track|beat|bgm|instrumental|pixabay|uppbeat|suno)' } | Select-Object -First 1
    if (-not $BgMatch) {
        $BgMatch = $WorkAudio | Where-Object { $_.FullName -ne $VoSrc -and $_.Name -ne "My_voice.mp3" } | Select-Object -First 1
    }
    if ($BgMatch) { $BgSrc = $BgMatch.FullName }
}

if ($BgSrc) {
    Write-Host "2/5 Mixing and auto-ducking background music ($BgSrc -> assets\audio\music.wav)..." -ForegroundColor Cyan
    $DstBg = Join-Path "$Root\work" ("bg_music" + [System.IO.Path]::GetExtension($BgSrc))
    if ($BgSrc -ine $DstBg) { Copy-Item "$BgSrc" "$DstBg" -Force }
    python src\music.py
} else {
    Write-Host "2/5 WARNING: No background music matched! Pass -Music ""path\to\track.mp3"" or name it work\bg_music.mp3" -ForegroundColor Red
}

# 3. Mix licensed SFX if configured
Write-Host "3/5 Checking SFX bus..." -ForegroundColor Cyan
python src\mix_sfx.py

# Guard: stop before rendering if NO audio tracks exist at all
$HasVo  = Test-Path "assets\audio\vo.wav"
$HasBg  = Test-Path "assets\audio\music.wav"
$HasSfx = Test-Path "assets\audio\sfx.wav"
if (-not ($HasVo -or $HasBg -or $HasSfx)) {
    Write-Host "`nSTOPPED: Neither vo.wav nor music.wav was created. Put your files in work\ or pass -Voice and -Music paths, then re-run." -ForegroundColor Red
    Pop-Location
    exit 1
}

# Fast 2-second mux onto already-rendered MP4 if -MuxOnly is passed
if ($MuxOnly -and (Test-Path "renders\jobsnap-luminous-16x9.mp4")) {
    Write-Host "Fast-muxing audio onto existing renders\jobsnap-luminous-16x9.mp4..." -ForegroundColor Cyan
    $Inputs = @("-i", "renders\jobsnap-luminous-16x9.mp4")
    $AudIdx = @()
    $n = 1
    if ($HasVo)  { $Inputs += @("-i", "assets\audio\vo.wav");    $AudIdx += "[$($n):a]"; $n++ }
    if ($HasBg)  { $Inputs += @("-i", "assets\audio\music.wav"); $AudIdx += "[$($n):a]"; $n++ }
    if ($HasSfx) { $Inputs += @("-i", "assets\audio\sfx.wav");   $AudIdx += "[$($n):a]"; $n++ }
    $Filter = ($AudIdx -join "") + "amix=inputs=$($AudIdx.Count):duration=first:normalize=0,alimiter=limit=0.92[aout]"
    ffmpeg -v error -y @Inputs -filter_complex $Filter -map "0:v:0" -map "[aout]" -c:v copy -c:a aac -b:a 192k -shortest renders\jobsnap-luminous-16x9-with-audio.mp4
    ffmpeg -v error -y -i renders\jobsnap-luminous-16x9-with-audio.mp4 -c:v libx264 -b:v 4500k -maxrate 6000k -bufsize 12000k -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart renders\jobsnap-luminous-16x9-social.mp4
    Write-Host "`nDONE (2s fast mux)! Videos with audio ready:" -ForegroundColor Green
    Write-Host "  Master 1080p:  $Root\renders\jobsnap-luminous-16x9-with-audio.mp4"
    Write-Host "  Social / Web:  $Root\renders\jobsnap-luminous-16x9-social.mp4"
    Pop-Location
    exit 0
}

# 4. Assemble HyperFrames composition with audio tracks mounted
Write-Host "4/5 Building 32.0s 1080p HyperFrames composition (audio mounted)..." -ForegroundColor Cyan
python src\build.py

# 5. Render High-Quality 1080p Master MP4 + Social Copy
Write-Host "5/5 Rendering 1080p MP4 with HyperFrames..." -ForegroundColor Cyan
npx --yes hyperframes render -q high -o renders\jobsnap-luminous-16x9.mp4

if (Test-Path "renders\jobsnap-luminous-16x9.mp4") {
    Write-Host "Creating social/phone-ready MP4 copy..." -ForegroundColor Cyan
    ffmpeg -v error -y -i renders\jobsnap-luminous-16x9.mp4 -c:v libx264 -b:v 4500k -maxrate 6000k -bufsize 12000k -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart renders\jobsnap-luminous-16x9-social.mp4
    Write-Host ""
    Write-Host "DONE! Your finished videos with audio are ready:" -ForegroundColor Green
    Write-Host "  Master 1080p:  $Root\renders\jobsnap-luminous-16x9.mp4"
    Write-Host "  Social / Web:  $Root\renders\jobsnap-luminous-16x9-social.mp4"
}

Pop-Location
