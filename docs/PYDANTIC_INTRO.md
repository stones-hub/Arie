# Pydantic 是什么、用来做什么、怎么用

## 一、这个库是干什么的

**Pydantic** 是 Python 里做「**数据校验 + 类型转换**」的库：你用**类型注解**描述「数据长什么样」，它负责在运行时检查数据是否符合、并自动转成对应类型（如把 `"123"` 转成 `123`）。

常见用途：

- **API 请求/响应**：定义请求体、响应体的结构和校验规则。
- **配置**：从环境变量、`.env` 读配置并保证类型正确（如 `Settings`）。
- **任何“外来数据”**：字典、JSON、表单等，需要按固定结构校验和转换时。

---

## 二、安装

本项目已在 `requirements.txt` 中通过 FastAPI、pydantic-settings 间接依赖 Pydantic。若单独使用：

```bash
pip install pydantic          # 核心：BaseModel 等
pip install pydantic-settings # 配置：BaseSettings、从 .env 读
```

---

## 三、基础用法示例

### 1. 用 BaseModel 定义“一块数据的形状”

```python
from pydantic import BaseModel


class Person(BaseModel):
    name: str
    age: int
    email: str | None = None  # 可选，默认 None


# 用字典创建，自动校验并转换类型
p = Person(name="张三", age="25", email="zhang@example.com")
print(p.name, p.age)  # 张三 25（age 若传 "25" 会自动转成 int）

# 缺少必填字段会报错
# Person(name="李四")  # ValidationError: age field required

# 类型不对会报错
# Person(name="王五", age="不是数字")  # ValidationError
```

### 2. 从 JSON 字符串 / 字典解析

```python
from pydantic import BaseModel


class Item(BaseModel):
    id: int
    title: str
    price: float


# 从字典
data = {"id": 1, "title": "商品A", "price": 9.99}
item = Item(**data)

# 从 JSON 字符串
import json
json_str = '{"id": 2, "title": "商品B", "price": 19.5}'
item2 = Item.model_validate_json(json_str)

# 再转回字典 / JSON（序列化）
print(item.model_dump())           # {'id': 1, 'title': '商品A', 'price': 9.99}
print(item.model_dump_json())      # 出 JSON 字符串
```

### 3. 默认值、可选字段

```python
from pydantic import BaseModel
from typing import Optional


class CreateUserRequest(BaseModel):
    name: str
    age: int = 18              # 有默认值，可不传
    nickname: Optional[str] = None  # 可选，不传则为 None
```

### 4. 在 FastAPI 里当请求体 / 响应体（本项目用法）

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class UserCreate(BaseModel):
    name: str
    age: int = 18


class UserResponse(BaseModel):
    id: int
    name: str
    age: int


@app.post("/users", response_model=UserResponse)
def create_user(payload: UserCreate):
    # payload 已是校验过的 UserCreate 实例
    user_id = 1  # 模拟入库
    return UserResponse(id=user_id, name=payload.name, age=payload.age)
```

客户端传的 JSON 会被 FastAPI 自动转成 `UserCreate`，不符合就自动 422；返回的 `UserResponse` 会被自动序列化成 JSON。

---

## 四、配置：用 BaseSettings 从 .env / 环境变量读

适合「配置项从环境变量或 .env 文件来」的场景（即本项目的 `Settings`）。

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "My App"
    debug: bool = False
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 第一次使用时，会从 .env、环境变量里按“字段名大写”读
# 例如 APP_NAME、DEBUG、PORT
settings = Settings()
print(settings.app_name, settings.debug, settings.port)
```

`.env` 示例：

```env
APP_NAME=Web API
DEBUG=true
PORT=9000
```

---

## 五、常用类型与校验

```python
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum


# 多继承：Status 同时继承 str 和 Enum（两者都是类）
# 这样枚举值既是枚举成员，又像字符串，序列化成 JSON 时直接是 "pending"/"done"
class Status(str, Enum):
    PENDING = "pending"
    DONE = "done"


class Example(BaseModel):
    name: str
    count: int
    tags: List[str] = []           # 字符串列表
    email: EmailStr                 # 需装 email-validator，校验邮箱格式
    status: Status = Status.PENDING # 枚举，只接受枚举值
```

---

## 如何定义枚举类型

Python 用标准库 **`enum`** 定义枚举，常见三种写法如下。

### 1. 最基础：继承 `Enum`

```python
from enum import Enum


class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


# 使用
print(Color.RED)        # Color.RED
print(Color.RED.name)   # RED
print(Color.RED.value) # 1

# 用值取回枚举成员
c = Color(2)
print(c)  # Color.GREEN
```

成员名（如 `RED`）和值（如 `1`）都可以自己定；不写值则自动从 1 递增。

### 2. 值和名字一致：用 `auto()`

```python
from enum import Enum, auto


class Status(Enum):
    PENDING = auto()   # 1
    RUNNING = auto()   # 2
    DONE = auto()      # 3
```

适合只关心「有哪几种状态」、不关心具体数字时用。

### 3. 继承 `str` 和 `Enum`（适合 API/JSON）

希望枚举在转 JSON、和字符串比较时**直接当字符串用**，可以多继承 `str` 和 `Enum`，并把值写成字符串：

```python
from enum import Enum


class Status(str, Enum):
    PENDING = "pending"
    DONE = "done"


# 序列化成 JSON 时是 "pending"/"done"，不是复杂对象
import json
print(json.dumps(Status.PENDING))  # "pending"

# 和字符串比较
if Status.PENDING == "pending":
    print("相等")
```

在 Pydantic / FastAPI 里用这种枚举，请求、响应里的值就是普通字符串，最省事。

### 小结

| 写法 | 适用场景 |
|------|----------|
| `class X(Enum): A = 1` | 需要数字或自定义值 |
| `class X(Enum): A = auto()` | 只要几个互不相同的成员名 |
| `class X(str, Enum): A = "a"` | API/JSON 里希望直接是字符串 |

---

## 六、和本项目的对应关系

| 文件 / 用法 | Pydantic 作用 |
|-------------|----------------|
| `app/config/settings.py` | `Settings(BaseSettings)`：从 .env/环境变量读配置并校验类型。 |
| `app/models/user.py` | `UserCreate`、`UserUpdate`、`UserResponse` 等：API 请求体、响应体结构 + 校验。 |
| `app/models/department.py` | `DepartmentResponse`：部门接口响应结构。 |
| FastAPI 路由参数 | `payload: UserCreate`、`response_model=UserResponse`：自动校验请求、序列化响应。 |

---

## 七、一句话总结

- **Pydantic**：用类型注解定义数据结构，自动做**校验 + 类型转换**。
- **BaseModel**：定义普通数据结构（请求/响应、配置以外的数据）。
- **BaseSettings**：定义配置，从环境变量、`.env` 读取并校验。
- 本项目里：**配置**和 **API 入参/出参** 都依赖 Pydantic。
