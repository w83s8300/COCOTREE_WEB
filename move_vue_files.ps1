# 移動 Vue 檔案到對應資料夾的 PowerShell 腳本

$viewsPath = "c:\Docker_dance-studio-main\dance-studio-website\src\views"

# 管理功能檔案
$managementFiles = @(
    "EnrollmentAdmin.vue",
    "Students.vue", 
    "Teachers.vue",
    "Courses.vue",
    "Rooms.vue",
    "Styles.vue",
    "Schedules.vue"
)

# 表單檔案
$formFiles = @(
    "AddStudent.vue",
    "AddTeacher.vue", 
    "AddCourse.vue",
    "AddRoom.vue",
    "AddStyle.vue",
    "AddSchedule.vue"
)

# 公開頁面檔案
$publicFiles = @(
    "Home.vue",
    "About.vue",
    "Contact.vue", 
    "Gallery.vue",
    "History.vue",
    "Faq.vue",
    "Pricing.vue",
    "Venue.vue",
    "Instructors.vue"
)

# 學生功能檔案
$studentFiles = @(
    "Schedule.vue"
)

# 移動管理功能檔案
foreach ($file in $managementFiles) {
    $sourcePath = Join-Path $viewsPath $file
    $destPath = Join-Path "$viewsPath\management" $file
    if (Test-Path $sourcePath) {
        Move-Item $sourcePath $destPath -Force
        Write-Host "移動 $file 到 management/"
    }
}

# 移動表單檔案
foreach ($file in $formFiles) {
    $sourcePath = Join-Path $viewsPath $file
    $destPath = Join-Path "$viewsPath\forms" $file
    if (Test-Path $sourcePath) {
        Move-Item $sourcePath $destPath -Force
        Write-Host "移動 $file 到 forms/"
    }
}

# 移動公開頁面檔案
foreach ($file in $publicFiles) {
    $sourcePath = Join-Path $viewsPath $file
    $destPath = Join-Path "$viewsPath\public" $file
    if (Test-Path $sourcePath) {
        Move-Item $sourcePath $destPath -Force
        Write-Host "移動 $file 到 public/"
    }
}

# 移動學生功能檔案
foreach ($file in $studentFiles) {
    $sourcePath = Join-Path $viewsPath $file
    $destPath = Join-Path "$viewsPath\student" $file
    if (Test-Path $sourcePath) {
        Move-Item $sourcePath $destPath -Force
        Write-Host "移動 $file 到 student/"
    }
}

Write-Host "檔案移動完成！"
