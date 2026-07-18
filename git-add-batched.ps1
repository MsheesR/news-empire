$files = Get-ChildItem -Path "news-empire" -Filter "*.html" | Select-Object -ExpandProperty FullName
$batchSize = 100
$totalFiles = $files.Count
$addedCount = 0

Write-Host "Total HTML files to add: $totalFiles"

for ($i = 0; $i -lt $totalFiles; $i += $batchSize) {
    $batch = $files[$i..($i + $batchSize - 1)]
    
    # Run git add for the batch
    $gitArgs = @("add") + $batch
    & git $gitArgs 2>&1 | Out-Null
    
    $addedCount += $batch.Count
    Write-Host "Added $addedCount / $totalFiles files..."
    
    # Wait for 1 second to let antivirus/indexer release file locks on .git/objects
    Start-Sleep -Seconds 1
}

# Add any remaining files
& git add news-empire/ 2>&1 | Out-Null

Write-Host "Done adding files."
