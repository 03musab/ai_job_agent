# Clean all old silent videos & unused video folders, then export ONE final 1080p MP4
# with Voiceover + Ducked BG Music + ALL 36 Synced Stereo Sound Effects baked in!
#
# Run from workspace root:
#   powershell -ExecutionPolicy Bypass -File jobsnap-luminous-video\export_final_video.ps1
# Or pass explicit paths to your voice & BG music files:
#   powershell -ExecutionPolicy Bypass -File jobsnap-luminous-video\export_final_video.ps1 -Voice "path\to\voice.mp3" -Music "path\to\music.mp3"

param(
    [string]$Voice = "",
    [string]$Music = "",
    [switch]$RemuxSfx
)

$ErrorActionPreference = "Stop"
$WS    = "c:\Users\musab\Desktop\ai_job_agent"
$Root  = "$WS\jobsnap-luminous-video"
$AeSrc = "$WS\.agents\skills\claude-motion\vendor\ae-motion\ae-motion.js"

# Fast 2-second SFX re-mix onto existing rendered JobSnap_Launch_FINAL_1080p.mp4
if ($RemuxSfx -and (Test-Path "$Root\renders\JobSnap_Launch_FINAL_1080p.mp4")) {
    Push-Location $Root
    Write-Host "1/2 Rebuilding punchy stereo SFX track (assets\audio\sfx.wav)..." -ForegroundColor Cyan
    python src\mix_sfx.py
    Write-Host "2/2 Fast-mixing Voice + BG Music + Punchy SFX into FINAL MP4s (2 seconds)..." -ForegroundColor Cyan
    Copy-Item "renders\JobSnap_Launch_FINAL_1080p.mp4" "renders\_video_src.mp4" -Force
    $Inputs = @("-i", "renders\_video_src.mp4")
    $AudIdx = @()
    $Stems  = @()
    $n = 1
    if (Test-Path "assets\audio\vo.wav")    { $Inputs += @("-i", "assets\audio\vo.wav");    $AudIdx += "[$($n):a]volume=1.0[a$n];";  $Stems += "[a$n]"; $n++ }
    if (Test-Path "assets\audio\music.wav") { $Inputs += @("-i", "assets\audio\music.wav"); $AudIdx += "[$($n):a]volume=0.72[a$n];"; $Stems += "[a$n]"; $n++ }
    if (Test-Path "assets\audio\sfx.wav")   { $Inputs += @("-i", "assets\audio\sfx.wav");   $AudIdx += "[$($n):a]volume=1.15[a$n];"; $Stems += "[a$n]"; $n++ }
    if ($Stems.Count -eq 1) {
        $Filter = ($AudIdx -join "") + "$($Stems[0])alimiter=limit=0.94[aout]"
    } else {
        $Filter = ($AudIdx -join "") + ($Stems -join "") + "amix=inputs=$($Stems.Count):duration=longest:normalize=0,alimiter=limit=0.94[aout]"
    }
    ffmpeg -v error -y @Inputs -filter_complex $Filter -map "0:v:0" -map "[aout]" -c:v copy -c:a aac -b:a 256k -t 32.0 -movflags +faststart renders\JobSnap_Launch_FINAL_1080p.mp4
    ffmpeg -v error -y -i renders\JobSnap_Launch_FINAL_1080p.mp4 -c:v libx264 -b:v 4500k -maxrate 6000k -bufsize 12000k -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart renders\JobSnap_Launch_FINAL_Social.mp4
    Remove-Item -Force renders\_video_src.mp4 -ErrorAction SilentlyContinue
    Write-Host "`nDONE (2s fast remux)! Play JobSnap_Launch_FINAL_1080p.mp4 to hear all clicks, whooshes, ticks & chimes!" -ForegroundColor Green
    Pop-Location
    exit 0
}

# 1. Delete old unused video projects & old silent MP4 renders (keeps work\ voice & music safe!)
Write-Host "1/6 Cleaning up old video folders and old silent MP4 renders..." -ForegroundColor Cyan
foreach ($oldDir in @("$WS\jobsnap-launch-video", "$WS\jobsnap-launch-video-9x16")) {
    if (Test-Path $oldDir) {
        Remove-Item -Recurse -Force $oldDir
        Write-Host "  Deleted old folder: $oldDir" -ForegroundColor DarkGray
    }
}
if (Test-Path "$Root\renders") {
    Get-ChildItem -Path "$Root\renders" -Filter "*.mp4" -ErrorAction SilentlyContinue | Remove-Item -Force
}

New-Item -ItemType Directory -Force -Path "$Root\assets\audio" | Out-Null
New-Item -ItemType Directory -Force -Path "$Root\renders" | Out-Null
if (Test-Path $AeSrc) { Copy-Item $AeSrc "$Root\assets\ae-motion.js" -Force }

Push-Location $Root

# 2. Render all 36 synced stereo Sound Effects -> assets\audio\sfx.wav
Write-Host "2/6 Generating all 36 voice-synced stereo sound effects (assets\audio\sfx.wav)..." -ForegroundColor Cyan
python src\mix_sfx.py

# 3. Auto-detect or use provided Voiceover + Background Music
$WorkAudio = Get-ChildItem -Path "work" -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension -match '^\.(mp3|wav|m4a|aac|ogg|flac)$' }
Write-Host "Audio files found in work\:" -ForegroundColor DarkCyan
if ($WorkAudio) { $WorkAudio | ForEach-Object { Write-Host "  - $($_.Name)" } } else { Write-Host "  (none)" -ForegroundColor Yellow }

$VoSrc = $null
if ($Voice -and (Test-Path $Voice)) {
    $VoSrc = (Resolve-Path $Voice).Path
} else {
    $VoMatch = $WorkAudio | Where-Object { $_.Name -ne "My_voice.mp3" -and $_.Name -match '(vo|voice|narrat|eleven|speech|script|record)' } | Select-Object -First 1
    if ($VoMatch) { $VoSrc = $VoMatch.FullName }
}
if ($VoSrc) {
    Write-Host "3/6 Mastering voiceover ($VoSrc -> assets\audio\vo.wav at -15 LUFS)..." -ForegroundColor Cyan
    ffmpeg -v error -y -i "$VoSrc" -af "highpass=f=75,acompressor=threshold=-20dB:ratio=2.2:attack=8:release=120:makeup=2,loudnorm=I=-15:TP=-1.5:LRA=9" -ar 48000 -ac 2 -c:a pcm_s24le assets\audio\vo.wav
} else {
    Write-Host "3/6 Note: No voiceover file matched in work\ (you can pass -Voice ""path\to\voice.mp3"")." -ForegroundColor Yellow
}

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
    Write-Host "4/6 Mixing and auto-ducking BG music ($BgSrc -> assets\audio\music.wav)..." -ForegroundColor Cyan
    $DstBg = Join-Path "$Root\work" ("bg_music" + [System.IO.Path]::GetExtension($BgSrc))
    if ($BgSrc -ine $DstBg) { Copy-Item "$BgSrc" "$DstBg" -Force }
    python src\music.py
} else {
    Write-Host "4/6 Note: No BG music file matched in work\ (you can pass -Music ""path\to\music.mp3"")." -ForegroundColor Yellow
}

# 4. Build HyperFrames composition and render fresh 1080p video
Write-Host "5/6 Building and rendering 32.0s 1080p video via HyperFrames..." -ForegroundColor Cyan
python src\build.py
npx --yes hyperframes render -q high -o renders\_raw_video.mp4

# 5. Studio-grade FFmpeg 3-stem audio master (guarantees Voice + BG Music + All 36 SFX are baked into the MP4!)
Write-Host "6/6 Mastering final 3-stem audio (Voice + BG Music + 36 SFX) into final MP4s..." -ForegroundColor Cyan
$Inputs = @("-i", "renders\_raw_video.mp4")
$AudIdx = @()
$Stems  = @()
$n = 1
if (Test-Path "assets\audio\vo.wav")    { $Inputs += @("-i", "assets\audio\vo.wav");    $AudIdx += "[$($n):a]volume=1.0[a$n];";  $Stems += "[a$n]"; $n++ }
if (Test-Path "assets\audio\music.wav") { $Inputs += @("-i", "assets\audio\music.wav"); $AudIdx += "[$($n):a]volume=0.72[a$n];"; $Stems += "[a$n]"; $n++ }
if (Test-Path "assets\audio\sfx.wav")   { $Inputs += @("-i", "assets\audio\sfx.wav");   $AudIdx += "[$($n):a]volume=1.15[a$n];"; $Stems += "[a$n]"; $n++ }

if ($Stems.Count -eq 1) {
    $Filter = ($AudIdx -join "") + "$($Stems[0])alimiter=limit=0.92[aout]"
} else {
    $Filter = ($AudIdx -join "") + ($Stems -join "") + "amix=inputs=$($Stems.Count):duration=longest:normalize=0,alimiter=limit=0.92[aout]"
}
ffmpeg -v error -y @Inputs -filter_complex $Filter -map "0:v:0" -map "[aout]" -c:v copy -c:a aac -b:a 256k -t 32.0 -movflags +faststart renders\JobSnap_Launch_FINAL_1080p.mp4

# Create social-ready (<20 MB) version too
ffmpeg -v error -y -i renders\JobSnap_Launch_FINAL_1080p.mp4 -c:v libx264 -b:v 4500k -maxrate 6000k -bufsize 12000k -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart renders\JobSnap_Launch_FINAL_Social.mp4

# Clean up temp raw video
Remove-Item -Force renders\_raw_video.mp4 -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "DONE! Old videos deleted. New FINAL video with ALL SFX ready:" -ForegroundColor Green
Write-Host "  Master 1080p: $Root\renders\JobSnap_Launch_FINAL_1080p.mp4"
Write-Host "  Social / Web: $Root\renders\JobSnap_Launch_FINAL_Social.mp4"
Write-Host "Audio stems baked in: $($Stems.Count) (SFX + any matched Voice/Music)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Green

Pop-Location
