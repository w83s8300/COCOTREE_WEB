# 批次移動 Vue 檔案腳本
$viewsPath = "c:\Docker_dance-studio-main\dance-studio-website\src\views"

# 移動管理檔案到 management/
$managementFiles = @("Teachers.vue", "Courses.vue", "Rooms.vue", "Styles.vue", "Schedules.vue", "EnrollmentAdmin.vue")
foreach ($file in $managementFiles) {
    $source = Join-Path $viewsPath $file
    $dest = Join-Path "$viewsPath\management" $file
    if (Test-Path $source) {
        Get-Content $source | Set-Content $dest -Encoding UTF8
        Write-Host "移動 $file 到 management/"
    }
}

# 移動表單檔案到 forms/
$formFiles = @("AddTeacher.vue", "AddCourse.vue", "AddRoom.vue", "AddStyle.vue", "AddSchedule.vue")
foreach ($file in $formFiles) {
    $source = Join-Path $viewsPath $file
    $dest = Join-Path "$viewsPath\forms" $file
    if (Test-Path $source) {
        Get-Content $source | Set-Content $dest -Encoding UTF8
        Write-Host "移動 $file 到 forms/"
    }
}

# 移動公開頁面到 public/
$publicFiles = @("Home.vue", "About.vue", "Contact.vue", "Gallery.vue", "History.vue", "Faq.vue", "Pricing.vue", "Venue.vue", "Instructors.vue")
foreach ($file in $publicFiles) {
    $source = Join-Path $viewsPath $file
    $dest = Join-Path "$viewsPath\public" $file
    if (Test-Path $source) {
        Get-Content $source | Set-Content $dest -Encoding UTF8
        Write-Host "移動 $file 到 public/"
    }
}

# 移動學生功能到 student/
$studentFiles = @("Schedule.vue")
foreach ($file in $studentFiles) {
    $source = Join-Path $viewsPath $file
    $dest = Join-Path "$viewsPath\student" $file
    if (Test-Path $source) {
        Get-Content $source | Set-Content $dest -Encoding UTF8
        Write-Host "移動 $file 到 student/"
    }
}

Write-Host "檔案移動完成！"
