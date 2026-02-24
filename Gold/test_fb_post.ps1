# Quick Facebook Post Test
# Run this to post directly to Facebook

$MCP_URL = "http://localhost:8083"

Write-Host "`n=== Facebook Real Post Test ===`n" -ForegroundColor Cyan

# Facebook Post
$body = @{
    page_id = "106665648626271"
    message = "Hello from my AI Employee System! Test post."
    dry_run = $false
} | ConvertTo-Json

Write-Host "Posting to Facebook..."
$result = Invoke-RestMethod -Uri "$MCP_URL/tools/post_to_facebook" -Method POST -ContentType "application/json" -Body $body

Write-Host "`nResult:" -ForegroundColor Yellow
$result | ConvertTo-Json

if ($result.success) {
    Write-Host "`n[OK] POSTED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "Post ID: $($result.post_id)"
    Write-Host "Check: https://www.facebook.com/106665648626271"
} else {
    Write-Host "`n[FAILED] Error: $($result.error)" -ForegroundColor Red
    Write-Host "`nFix: Check your Facebook Access Token in .env file"
    Write-Host "Get new token from: https://developers.facebook.com/tools/explorer/"
}
