$domains = @('eidot.ai', 'eidot.dev', 'eidot.io', 'eidot.co.il', 'eidot.run')
foreach ($d in $domains) {
    try {
        $r = Invoke-WebRequest -Uri "https://$d" -UseBasicParsing -Method HEAD -TimeoutSec 6 -ErrorAction Stop
        Write-Host "$d : ALIVE ($($r.StatusCode)) - probably taken"
    } catch {
        Write-Host "$d : NO RESPONSE - likely available"
    }
}
