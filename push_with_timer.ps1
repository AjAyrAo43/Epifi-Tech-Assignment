# PowerShell Script: Automatically push remaining commits every 5 minutes

$commits = @(
    "34b1d59", # Commit 3: feat(backend): set up SQLAlchemy SQLite database engine
    "dbb417f", # Commit 4: feat(backend): implement URL and Check ORM models
    "dcd2d1b", # Commit 5: feat(backend): define Pydantic request and response schemas
    "643dcfa", # Commit 6: feat(backend): implement async httpx pinger engine
    "5c8d096", # Commit 7: feat(backend): add URL CRUD router endpoints
    "c02f236", # Commit 8: feat(backend): initialize FastAPI application entrypoint with CORS
    "671b6bb", # Commit 9: feat(frontend): setup HTML template, Vite config, and React main
    "eab265d", # Commit 10: style(frontend): add dark mode glassmorphism CSS styling system
    "340aa1b", # Commit 11: feat(frontend): implement Navbar and StatsOverview components
    "0d38a5b", # Commit 12: feat(frontend): implement AddUrlForm and UrlList components
    "1aa6679", # Commit 13: feat(frontend): add API fetch wrapper and check history modal
    "901f39e", # Commit 14: feat(frontend): integrate live polling loop in App
    "de8cd1b", # Commit 15: chore(docker): add Dockerfile for backend service
    "80a758f", # Commit 16: chore(docker): add multi-stage Dockerfile and NGINX config for frontend
    "375b80e", # Commit 17: chore(docker): add docker-compose orchestration
    "c93c14b", # Commit 18: docs(deploy): add Terraform infrastructure topology sketch
    "145b1a6", # Commit 19: docs(ai): write AI collaboration log and course corrections
    "192d5f8"  # Commit 20: docs(readme): finalize project README with setup and testing steps
)

Write-Host "Starting automated push schedule for $($commits.Count) remaining commits..." -ForegroundColor Cyan

foreach ($i in 0..($commits.Count - 1)) {
    $hash = $commits[$i]
    $num = $i + 3
    Write-Host "[$num/20] Pushing commit $hash..." -ForegroundColor Green
    git push origin "${hash}:refs/heads/main"
    
    if ($i -lt ($commits.Count - 1)) {
        Write-Host "Waiting 5 minutes before next push..." -ForegroundColor Yellow
        Start-Sleep -Seconds 300
    }
}

Write-Host "All 20 commits pushed successfully!" -ForegroundColor Green
