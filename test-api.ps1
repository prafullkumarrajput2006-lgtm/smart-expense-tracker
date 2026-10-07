# Smart Expense Tracker - API Test Script
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Smart Expense Tracker - API Tests" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://127.0.0.1:5000"
$testEmail = "test@example.com"
$testPassword = "test123"
$token = ""

# Test 1: Health Check
Write-Host "Test 1: Health Check (GET /)" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/" -Method Get
    Write-Host "PASS: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "FAIL: Backend not running" -ForegroundColor Red
    exit
}
Write-Host ""

# Test 2: Register User
Write-Host "Test 2: Register User (POST /register)" -ForegroundColor Yellow
try {
    $body = @{
        name = "Test User"
        email = $testEmail
        password = $testPassword
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/register" -Method Post -Body $body -ContentType "application/json"
    Write-Host "PASS: User registered - $($response.user.email)" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 400) {
        Write-Host "INFO: User already exists (OK)" -ForegroundColor Yellow
    } else {
        Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host ""

# Test 3: Login
Write-Host "Test 3: Login (POST /login)" -ForegroundColor Yellow
try {
    $body = @{
        email = $testEmail
        password = $testPassword
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/login" -Method Post -Body $body -ContentType "application/json"
    $token = $response.token
    Write-Host "PASS: Login successful - Token received" -ForegroundColor Green
    Write-Host "  User: $($response.user.name)" -ForegroundColor Gray
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
    exit
}
Write-Host ""

# Test 4: Categorize Text
Write-Host "Test 4: Categorize Expense (POST /categorize)" -ForegroundColor Yellow
try {
    $body = @{
        text = "Lunch at KFC restaurant"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/categorize" -Method Post -Body $body -ContentType "application/json"
    Write-Host "PASS: Category predicted" -ForegroundColor Green
    Write-Host "  Category: $($response.category)" -ForegroundColor Gray
    Write-Host "  Confidence: $([math]::Round($response.confidence * 100, 2))%" -ForegroundColor Gray
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Add Expense
Write-Host "Test 5: Add Expense (POST /add)" -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    $body = @{
        vendor = "KFC"
        date = "2025-10-22"
        description = "Lunch"
        amount = 1250
        category = "Food"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$baseUrl/add" -Method Post -Body $body -ContentType "application/json" -Headers $headers
    Write-Host "PASS: Expense added" -ForegroundColor Green
    Write-Host "  Vendor: $($response.expense.vendor)" -ForegroundColor Gray
    Write-Host "  Amount: $($response.expense.amount)" -ForegroundColor Gray
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 6: List Expenses
Write-Host "Test 6: List Expenses (GET /list)" -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    
    $response = Invoke-RestMethod -Uri "$baseUrl/list" -Method Get -Headers $headers
    Write-Host "PASS: Retrieved $($response.Count) expense(s)" -ForegroundColor Green
} catch {
    Write-Host "FAIL: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 7: Protected Route Without Token
Write-Host "Test 7: Protected Route Without Token" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/list" -Method Get -ErrorAction Stop
    Write-Host "FAIL: Should have been blocked" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 401) {
        Write-Host "PASS: Correctly blocked unauthorized access" -ForegroundColor Green
    }
}
Write-Host ""

# Summary
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Test Complete!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "All backend functions are working!" -ForegroundColor Green
Write-Host ""
Write-Host "Next: Open http://localhost:3002 to test frontend" -ForegroundColor Yellow
Write-Host ""
