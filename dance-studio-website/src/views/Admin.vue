<template>
  <div class="admin-layout">
    <div class="sidebar">
      <h2>管理選單</h2>
      <nav>
        <ul>
          <li><router-link to="/admin/students">學生列表</router-link></li>
          <li><router-link to="/admin/teachers">老師列表</router-link></li>
          <li><router-link to="/admin/courses">課程列表</router-link></li>
          <li><router-link to="/admin/schedules">課程時間表</router-link></li>
          <li><router-link to="/admin/rooms">教室列表</router-link></li>
          <li><router-link to="/admin/styles">風格</router-link></li>
        </ul>
      </nav>
    </div>
    <div class="main-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Admin'
};
</script>

<style scoped>
.admin-layout {
  display: flex;
}

.sidebar {
  width: 250px;
  background-color: #f4f4f4;
  padding: 20px;
  height: 100vh;
}

.sidebar h2 {
  text-align: center;
  margin-bottom: 20px;
}

.sidebar nav ul {
  list-style: none;
  padding: 0;
}

.sidebar nav ul li {
  margin-bottom: 10px;
}

.sidebar nav ul li a {
  text-decoration: none;
  color: #333;
  display: block;
  padding: 10px;
  border-radius: 4px;
}

.sidebar nav ul li a:hover,
.sidebar nav ul li a.router-link-exact-active {
  background-color: #ddd;
}

.main-content {
  flex-grow: 1;
  padding: 20px;
}
</style>