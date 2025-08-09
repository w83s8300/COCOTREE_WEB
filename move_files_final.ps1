# 檔案移動映射
$fileMapping = @{
    # 管理功能
    "Students.vue" = "management"
    "Teachers.vue" = "management" 
    "Courses.vue" = "management"
    "Rooms.vue" = "management"
    "Styles.vue" = "management"
    "Schedules.vue" = "management"
    "EnrollmentAdmin.vue" = "management"
    
    # 表單
    "AddStudent.vue" = "forms"
    "AddTeacher.vue" = "forms"
    "AddCourse.vue" = "forms"
    "AddRoom.vue" = "forms"
    "AddStyle.vue" = "forms"
    "AddSchedule.vue" = "forms"
    
    # 公開頁面
    "Home.vue" = "public"
    "About.vue" = "public"
    "Contact.vue" = "public"
    "Gallery.vue" = "public"
    "History.vue" = "public"
    "Faq.vue" = "public"
    "Pricing.vue" = "public"
    "Venue.vue" = "public"
    "Instructors.vue" = "public"
    
    # 學生功能
    "Schedule.vue" = "student"
}

$sourceDir = "c:\Docker_dance-studio-main\dance-studio-website\src\views"

foreach ($file in $fileMapping.Keys) {
    $targetDir = $fileMapping[$file]
    $sourcePath = Join-Path $sourceDir $file
    $targetPath = Join-Path $sourceDir "$targetDir\$file"
    
    if (Test-Path $sourcePath) {
        Write-Host "移動 $file 到 $targetDir/"
        Copy-Item $sourcePath $targetPath -Force
        Remove-Item $sourcePath -Force
    } else {
        Write-Host "檔案不存在: $file"
    }
}

Write-Host "移動完成！"
