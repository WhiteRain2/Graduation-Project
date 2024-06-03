# 毕业设计项目：虚拟学习社区中异质学习共同体构建算法及应用

## 项目简介
本项目是一个虚拟学习社区推荐系统，前端使用Vue3，后端使用Django（ASGI启动），数据库为MySQL。项目的目标是为学生推荐最适合的学习共同体，从而提高学生在虚拟学习社区的参与度与满意度。

- GitHub仓库地址: [https://github.com/WhiteRain2/Graduation-Project](https://github.com/WhiteRain2/Graduation-Project)
- 项目演示地址: [http://120.26.228.25/](http://120.26.228.25/)
- 示例账号: `Jack`
- 示例密码: `admin123456`

## 系统安装与部署

### 前端部分

#### 安装

1. 克隆仓库
    ```sh
    git clone https://github.com/WhiteRain2/Graduation-Project.git
    cd Graduation-Project/web
    ```

2. 安装依赖
    ```sh
    npm install
    ```

#### 启动

3. 运行项目
    ```sh
    npm run serve
    ```

### 后端部分

#### 安装

1. 克隆仓库（如果还没有克隆）
    ```sh
    git clone https://github.com/WhiteRain2/Graduation-Project.git
    cd Graduation-Project/backend
    ```

2. 创建并激活虚拟环境
    ```sh
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    .\venv\Scripts\activate   # Windows
    ```

3. 安装依赖
    ```sh
    pip install -r requirements.txt
    ```

#### 配置

4. 修改数据库配置
    在 `backend/settings.py` 中配置数据库连接信息：
    
    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'your_db_name',
            'USER': 'your_db_user',
            'PASSWORD': 'your_db_password',
            'HOST': 'your_db_host',
            'PORT': 'your_db_port',
        }
    }
    ```

#### 启动

5. 运行数据库迁移
    ```sh
    python manage.py migrate
    ```

6. 创建超级用户
    ```sh
    python manage.py createsuperuser
    ```

7. 启动服务器（ASGI）
    ```sh
    daphne -b 0.0.0.0 -p 8000 backend.asgi:application
    ```

## 系统使用

1. 打开浏览器，访问前端地址（默认`http://localhost:8080`），登录页面将自动出现。
2. 使用示例账号登录：
   - 用户名: `Jack`
   - 密码: `admin123456`
3. 成功登录后，用户可以浏览推荐的学习共同体，查看详细信息并决定是否加入。

## 项目演示

可以访问部署的项目演示地址来体验系统：[http://120.26.228.25/](http://120.26.228.25/)

如有任何问题，请在GitHub仓库提交issue。感谢您的使用与支持！

# API Document

  #### **API 1: 获取特定对象的信息**

  - **HTTP 方法**: POST
  - **URL**: `http://120.26.228.25:8000/getinfo/`
  - **请求体参数**：
    - `type`: 对象类型 (可选值: `community` 或 `student`)
    - `id`: 对象的ID
  - **方法简介**: 该接口根据请求体参数`type`来确定获取学生信息还是获取社区信息。
  - **返回格式**: JSON
  - **示例返回 (学生信息)**:

  ```json
    {
        "id": 1234,
        "name": "张三",
        "gender": "男",
        "learning_style": "发散型",
        "activity_level": 3,
        "self_description": "我是一名热爱学习的学生",
        "completed_courses": [
            { "id": 1, "name": "数学", "score": 90 }
        ],
        "wish_courses": [
            { "id": 2, "name": "英语" }
        ],
        "communities_count": 1,
        "communities": [
            { "id": 3, "name": "英语爱好者", "description": "解锁英语学习的秘密。" }
        ]
    }
  ```

  - **示例返回 (社区信息)**:

  ```json
    {
        "id": 4,
        "name": "计算机科学交流群",
        "description": "一起深入学习计算机科学领域。",
        "gender_ratio": 0.7,
        "learning_style": "聚敛型",
        "activity_level": 4,
        "members_count": 20,
        "members": [
            {
                "id": 1235,
                "name": "李四",
                "gender": "女",
                "learning_style": "同化型",
                "self_description": "我是一名计算机科学专业的学生"
            }
        ],
        "completed_courses": [
            { "id": 1, "name": "计算机网络", "member_ratio": 0.8 }
        ],
        "wish_courses": [
            { "id": 2, "name": "数据结构与算法", "member_ratio": 0.6 }
        ]
    }
  ```

------

#### **API 2: 推荐学习共同体**

  - **HTTP 方法**: POST
  - **URL**: `http://120.26.228.25:8000/getrecommend/`
  - 请求体参数：
    - `student_id`: 学生ID (JSON字段)
    - `course_id`: 课程ID (JSON字段)
  - **方法简介**: 接收POST请求，包含学生ID和课程ID，为学生更新愿望课程并提供相应的学习共同体推荐。
  - **返回格式**: JSON
  - **示例返回**:

  ```json
    [
        {
            "id": 4,
            "name": "计算机科学交流群",
            "description": "一起深入学习计算机科学领域。",
            "similarity": 0.95
        }
    ]
  ```

------

#### **API 3: 学生加入/离开共同体操作**

  - **HTTP 方法**: POST
  - **URL**: `http://120.26.228.25:8000/operation/`
  - 请求体参数：
    - `operation`: 操作类型（"join" 或 "leave"）(JSON字段)
    - `student_id`: 学生ID (JSON字段)
    - `community_id`: 共同体ID (JSON字段)
  - **方法简介**: 该接口用于处理学生的加入或离开共同体的请求操作。
  - **返回格式**: JSON
  - **示例返回**:

  ```json
    {
        "message": "Operation completed successfully."
    }
  ```

------

  注意事项：

  - API 1 使用 POST 方法，需要在请求体中传递JSON格式的参数。
  - API 1 现在支持获取 `community` 和 `student` 类型的信息。
  - API 2 和 API 3 使用 POST 方法，需要在请求体中传递JSON格式的参数。
  - 当发生错误时，API会返回包含 `error` 键的JSON对象，并且可能包含不同的 HTTP 状态代码，根据错误类型而异。

