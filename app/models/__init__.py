# 数据模型与 Schema（Pydantic 请求/响应体、ORM 模型）
from app.models.department import DepartmentResponse
from app.models.user import UserWithDepartmentResponse

# 解析 UserWithDepartmentResponse 中对 DepartmentResponse 的前向引用
UserWithDepartmentResponse.model_rebuild()
