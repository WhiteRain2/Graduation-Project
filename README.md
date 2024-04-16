## API Document

#### **API 1: 获取学生信息**

- **HTTP 方法**: GET

- **URL**: `http://113.45.166.63:8000/getinfo/<user_id>/`

- 参数：

  - `user_id`: 学生ID (URL路径参数)

- **方法简介**: 该接口用于获取一个学生的已完成课程、愿望课程以及已加入的共同体信息。

- **返回格式**: JSON

- **示例返回**:

```json
  {
      "id": 1234,
      "name": "张三",
      "completed_courses": [
          { "id": 1, "name": "数学", "score": 90 }
      ],
      "wish_courses": [
          { "id": 2, "name": "英语" }
      ],
      "communities": [
          { "id": 3, "name": "英语爱好者", "description": "解锁英语学习的秘密。" }
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

- API 1 使用GET方法，用户ID作为URL的一部分传递。
- API 2 和 API 3 使用POST方法，需要在请求体中传递JSON格式的参数。
- 当发生错误时，API会返回包含 `error` 键的JSON对象，并且可能包含不同的HTTP状态代码，根据错误类型而异。

## Log

#### 2024-4-16

已完成前后端分离，API接口设计，`共同体管理`, `学生行为`模块。

#### 2024-4-17

分离云端数据库，部署项目到线上，并提供云API接口（服务待完善）。
