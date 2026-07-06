$domains = @(
    'aiintegrity.com', 'ai-integrity.com', 'aiintegrity.io', 'aiintegrity.dev',
    'agentledger.io', 'chainagents.io', 'prooftrail.dev', 'agentproof.io',
    'aicomply.io', 'auditagent.dev', 'agent-evidence.io'
)
foreach ($d in $domains) {
    try {
        $r = Invoke-WebRequest -Uri "https://$d" -UseBasicParsing -Method HEAD -TimeoutSec 6 -ErrorAction Stop
        Write-Host "$d : ALIVE ($($r.StatusCode))"
    } catch {
        Write-Host "$d : FREE-or-redirected"
    }
}
