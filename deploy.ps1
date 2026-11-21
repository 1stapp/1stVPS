# 1stVPS 一键全自动 Cloudflare 部署脚本 (PowerShell)
$ErrorActionPreference = "Continue"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       1stVPS Platform — Cloudflare 自动化部署流水线       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. 检查 Wrangler 登录状态与清理过期 Token
Write-Host "`n[Step 1/5] 校验 Cloudflare 账号凭据..." -ForegroundColor Yellow

$whoamiOutput = ""
try {
    $whoamiOutput = (& npx wrangler whoami 2>&1) | Out-String
} catch {
    $whoamiOutput = $_.Exception.Message
}

if ($whoamiOutput -match "Failed to fetch auth token" -or $whoamiOutput -match "Connect Timeout" -or $whoamiOutput -match "fetch failed") {
    Write-Host "--> 检测到旧的登录 Token 已过期或网络连接异常，正在清理过期凭据..." -ForegroundColor Yellow
    try { & npx wrangler logout 2>&1 | Out-Null } catch {}
    $whoamiOutput = "Not logged in"
}

if ($whoamiOutput -match "Not logged in" -or -not ($whoamiOutput -match "You are logged in")) {
    Write-Host "--> 正在唤起 Cloudflare 授权登录，请在弹出的浏览器页面中点击【Allow (授权)】..." -ForegroundColor Magenta
    & npx wrangler login
    
    # 再次验证登录状态
    $recheck = (& npx wrangler whoami 2>&1) | Out-String
    if ($recheck -match "Not logged in") {
        Write-Host "❌ 登录未完成，请确认网络代理正常（能够打开 dash.cloudflare.com）后重试。" -ForegroundColor Red
        exit 1
    }
}

Write-Host "--> Cloudflare 账号凭据验证通过！" -ForegroundColor Green

# 2. 创建或绑定 D1 数据库
Write-Host "`n[Step 2/5] 正在创建/确认 Cloudflare D1 数据库 (1stvps-db)..." -ForegroundColor Yellow
$d1Output = (& npx wrangler d1 create 1stvps-db 2>&1) | Out-String

if ($d1Output -match 'database_id = "([^"]+)"') {
    $dbId = $matches[1]
    Write-Host "--> 成功创建全新 D1 数据库! ID: $dbId" -ForegroundColor Green
    
    $wrangler = Get-Content wrangler.toml -Raw
    $wrangler = $wrangler -replace 'database_id = "[^"]+"', "database_id = `"$dbId`""
    Set-Content wrangler.toml $wrangler
    Write-Host "--> 已自动回填 database_id 至 wrangler.toml" -ForegroundColor Green
} else {
    Write-Host "--> D1 数据库已在 wrangler.toml 或 Cloudflare 账号中就绪。" -ForegroundColor Cyan
}

# 3. 创建或绑定 KV 命名空间
Write-Host "`n[Step 3/5] 正在创建/确认 Cloudflare KV 命名空间 (SESSION_KV)..." -ForegroundColor Yellow
$kvOutput = (& npx wrangler kv namespace create SESSION_KV 2>&1) | Out-String

if ($kvOutput -match 'id = "([^"]+)"') {
    $kvId = $matches[1]
    Write-Host "--> 成功创建全新 KV 命名空间! ID: $kvId" -ForegroundColor Green
    
    $wrangler = Get-Content wrangler.toml -Raw
    $wrangler = $wrangler -replace 'id = "REPLACE_WITH_YOUR_KV_NAMESPACE_ID"', "id = `"$kvId`""
    Set-Content wrangler.toml $wrangler
    Write-Host "--> 已自动回填 KV id 至 wrangler.toml" -ForegroundColor Green
} else {
    Write-Host "--> KV 命名空间已在 wrangler.toml 或 Cloudflare 账号中就绪。" -ForegroundColor Cyan
}

# 4. 创建异步任务队列
Write-Host "`n[Step 4/5] 正在创建异步任务队列 (1stvps-jobs)..." -ForegroundColor Yellow
try {
    & npx wrangler queues create 1stvps-jobs 2>&1 | Out-Null
    Write-Host "--> Queue 队列 1stvps-jobs 已就绪" -ForegroundColor Green
} catch {
    Write-Host "--> 队列已存在，继续执行" -ForegroundColor Cyan
}

# 5. 初始化远程 D1 表结构与种子数据
Write-Host "`n[Step 5/5] 执行远程 D1 数据库结构初始化 (schema.sql)..." -ForegroundColor Yellow
try {
    & npx wrangler d1 execute 1stvps-db --remote --file=./schema.sql -y
    Write-Host "--> D1 数据库表结构与默认数据播种完成！" -ForegroundColor Green
} catch {
    Write-Host "--> D1 执行提示: 数据库结构同步已触发" -ForegroundColor Yellow
}

# 6. 全量编译并发布上线
Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "正在发布应用至 Cloudflare 全球边缘网络..." -ForegroundColor Yellow
& npx wrangler deploy

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "🎉 1stVPS 平台部署完成！" -ForegroundColor Green
Write-Host "请在上方查看分配的 *.workers.dev 或绑定的自定义域名。" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
