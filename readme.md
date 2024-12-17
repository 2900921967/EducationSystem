# 教务管理系统

## 项目概述
本项目是一个基于 **Flask** 和 **MySQL** 的教务管理系统，提供用户管理、课程分配、成绩管理等功能。系统支持三种用户角色：**管理员**、**教师** 和 **学生**，不同角色登录后可访问不同的功能。

---

## 功能说明（Demo版本）

### 1. 用户角色
- **管理员**：
    - 添加、删除用户。
    - 添加、删除课程。
    - 分配课程给教师。
- **教师**：
    - 查看所分配的课程。
    - 给学生打分。
    - 查看和删除已打分的成绩。
- **学生**：
    - 查看选修的课程。
    - 查看自己的成绩。

### 2. 用户操作界面
- 登录界面。
- 注册界面。
- 不同用户类型的功能界面。

---

## 技术栈

### 后端
- **Python** - 主要编程语言。
- **Flask** - 轻量级 Web 框架。
- **MySQL** - 数据库存储用户、课程和成绩数据。

### 前端
- **HTML/CSS** - 页面布局和样式。
- **Bootstrap** - 前端 UI 框架，提供美观的页面设计。
- **SweetAlert2** - 交互式弹窗库。

### 依赖
- **pymysql** - Python 操作 MySQL 数据库。
- **hashlib** - 密码加密处理。

---

## 安装与运行

### 1. 克隆项目代码
```bash
git clone https://github.com/2900921967/EducationSystem.git
cd EducationSystem
```

### 2. 安装依赖
```bash
pip install flask pymysql
```

### 3. 配置数据库
- 使用 MySQL 工具执行 `database.sql` 脚本，创建数据库和必要的表结构。
- 确保 MySQL 运行，并在 `app.py` 中配置数据库连接参数：

```python
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'EducationSystem',
}
```

### 4. 运行项目
```bash
python app.py
```

### 5. 访问应用
打开浏览器，访问：
```
http://127.0.0.1:5000
```

---
