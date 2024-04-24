- # API Document

  #### **API 1: 获取特定对象的信息**

  - **HTTP 方法**: POST
  - **URL**: `http://113.45.166.63:8000/getinfo/`
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

  **API 2: 推荐学习共同体**

  - **HTTP 方法**: POST
  - **URL**: `http://113.45.166.63:8000/getrecommend/`
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

  **API 3: 学生加入/离开共同体操作**

  - **HTTP 方法**: POST
  - **URL**: `http://113.45.166.63:8000/operation/`
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

# Log

#### 2024-4-16

已完成前后端分离，API接口设计，`共同体管理`, `学生行为`模块。

#### 2024-4-17

分离云端数据库，部署项目到线上，并提供云API接口（服务待完善）。

#### 2024-4-24

重构数据库模型，增加更多学生个性化信息，更新接口。
