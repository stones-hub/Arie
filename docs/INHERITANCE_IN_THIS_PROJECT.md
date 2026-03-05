# Python 继承说明 & 本项目中的继承关系

## 一、Python 继承是什么

继承就是：**子类「是」父类的一种，自动拥有父类的属性和方法**；子类可以只写自己多出来的部分，也可以覆盖父类的方法。

```text
class 子类(父类):
    ...
```

- 子类实例可以调用父类里定义的方法和属性。
- 子类可以定义新方法、新属性。
- 子类可以重写父类的方法（同名方法，用子类的实现）。
- 一个类可以有多个父类：`class C(A, B):`（多继承）。

---

## 二、面向对象三要素：继承、重写、多态（示例）

下面用同一套例子把**继承**、**重写**、**多态**串起来，可直接复制到 Python 里运行。

### 1. 继承（Inheritance）

子类写在括号里，就自动拥有父类的属性和方法。

```python
class Animal:
    """父类：动物。"""
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        return "..."

    def info(self) -> str:
        return f"我是{self.name}，叫起来：{self.speak()}"


class Dog(Animal):
    """子类：狗。只写多出来的部分。"""
    def speak(self) -> str:   # 下一节讲：这是重写
        return "汪汪"


# 继承的效果：Dog 自动有 name、info()，因为 Animal 有
dog = Dog("阿黄")
print(dog.name)      # 阿黄（来自父类 __init__ 里的 self.name）
print(dog.info())   # 我是阿黄，叫起来：汪汪（info 来自父类，但里面调用的 speak 已是子类的）
```

---

### 2. 重写（Override）

子类里写**同名方法**，就覆盖父类的实现；需要时可用 `super()` 先调父类再扩展。

```python
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        return "..."

    def describe(self) -> str:
        return f"{self.name}（动物）"


class Cat(Animal):
    def speak(self) -> str:
        # 重写：完全替换父类的 speak
        return "喵喵"

    def describe(self) -> str:
        # 重写 + 复用父类：先调父类再追加
        return super().describe() + "，会喵喵叫"


cat = Cat("小花")
print(cat.speak())     # 喵喵（用的是 Cat 的 speak，不是 Animal 的）
print(cat.describe())  # 小花（动物），会喵喵叫（父类 describe + 子类追加）
```

要点：

- **完全重写**：子类定义同名方法即可，调用时用子类的实现。
- **扩展父类**：在子类方法里写 `super().方法名(...)`，先执行父类逻辑，再写自己的逻辑。

---

### 3. 多态（Polymorphism）

**同一接口、不同实现**：多个子类都有同名方法，但行为不同；写代码时只依赖「父类类型 / 共同接口」，运行时实际是哪个子类，就执行哪个子类的实现。

```python
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        return "..."

    def info(self) -> str:
        return f"{self.name}: {self.speak()}"


class Dog(Animal):
    def speak(self) -> str:
        return "汪汪"


class Cat(Animal):
    def speak(self) -> str:
        return "喵喵"


class Bird(Animal):
    def speak(self) -> str:
        return "叽叽"


# 多态：同一函数只依赖「会 speak 的动物」，不关心具体是狗还是猫还是鸟
def let_them_speak(animals: list[Animal]) -> None:
    for a in animals:
        print(a.info())   # 每个子类自己的 speak() 会被调用


let_them_speak([
    Dog("阿黄"),
    Cat("小花"),
    Bird("小绿"),
])
# 输出：
# 阿黄: 汪汪
# 小花: 喵喵
# 小绿: 叽叽
```

要点：

- **接口一致**：都叫 `speak()`，返回值都是「叫声」。
- **实现不同**：Dog / Cat / Bird 各自重写 `speak()`，行为不同。
- **按父类写逻辑**：`let_them_speak` 只认「Animal 有 `info()`」，而 `info()` 内部会调用各自的 `speak()`，所以同一段代码能应对多种子类，这就是多态。

---

### 4. 小结对照

| 概念 | 含义 | 代码上的体现 |
|------|------|----------------|
| **继承** | 子类拥有父类的属性和方法 | `class Dog(Animal):`，Dog 可直接用 `name`、`info()` |
| **重写** | 子类用同名方法替换/扩展父类逻辑 | 在 Dog 里定义 `speak()`，或 `super().describe()` |
| **多态** | 同一接口多种实现，按「父类/接口」写代码 | `let_them_speak(animals)` 只依赖 `Animal`，实际跑的是各子类的 `speak()` |

---

## 三、本项目里哪里在继承

下面只列 **app 目录下** 的继承，并说明「子类从父类得到了什么」。

---

### 1. 数据库 / ORM 基类（app/db/session.py）

| 代码 | 含义 |
|------|------|
| `class Base(DeclarativeBase):` | 我们的 ORM 基类继承 SQLAlchemy 的 `DeclarativeBase`。这样 `Base` 具备「声明式映射」能力（metadata、表注册等），我们又在 `Base` 上加了 `__repr__`、`to_dict()`，所以所有继承 `Base` 的模型都自动有这两个方法。 |

---

### 2. 模型层：表模型（app/models/user.py、department.py）

| 代码 | 含义 |
|------|------|
| `class User(OrmBase):` | `User` 继承我们自己的 `Base`（这里别名叫 `OrmBase`）。所以 `User` 是一张「表」、在 `Base.metadata` 里，并且有 `user.to_dict()`、`repr(user)` 等基类方法。 |
| `class Department(OrmBase):` | 同上，部门表继承 `Base`，具备表结构 + 基类方法。 |

---

### 3. 模型层：Pydantic Schema（app/models/user.py）

| 代码 | 含义 |
|------|------|
| `class UserBase(BaseModel):` | 继承 Pydantic 的 `BaseModel`，得到校验、序列化等能力；我们只定义字段 `email, name, department_id`。 |
| `class UserCreate(UserBase):` | 继承 `UserBase`，所以自动拥有 `email, name, department_id`，当前没有额外字段。 |
| `class UserUpdate(BaseModel):` | 继承 `BaseModel`，请求体里只放要更新的字段（可选）。 |
| `class UserResponse(UserBase):` | 继承 `UserBase`，所以有 `email, name, department_id`，再额外加 `id, created_at, updated_at`。 |
| `class UserWithDepartmentResponse(UserResponse):` | 继承 `UserResponse`，在用户信息基础上再多一个 `department` 字段（嵌套部门信息）。 |

---

### 4. 模型层：部门 Schema（app/models/department.py）

| 代码 | 含义 |
|------|------|
| `class DepartmentResponse(BaseModel):` | 继承 Pydantic 的 `BaseModel`，用于 API 返回部门信息（如 `id, name`）。 |

---

### 5. 配置（app/config/settings.py）

| 代码 | 含义 |
|------|------|
| `class Settings(BaseSettings):` | 继承 Pydantic 的 `BaseSettings`，自动从环境变量 / `.env` 读配置，我们只定义 `app_name`、`debug`、`database_url` 等字段。 |

---

## 四、继承链一览（本项目）

```text
# ORM 表（同一套 metadata + 基类方法）
DeclarativeBase  →  Base  →  User
                         →  Department

# 用户相关 Schema（请求/响应）
BaseModel  →  UserBase  →  UserCreate
                        →  UserResponse  →  UserWithDepartmentResponse
BaseModel  →  UserUpdate

# 部门 Schema
BaseModel  →  DepartmentResponse

# 配置
BaseSettings  →  Settings
```

总结：**「继承」在项目里用于三类：ORM 表共用一个 Base、请求/响应共用一个 BaseModel/UserBase、配置共用一个 BaseSettings。** 子类没有写的逻辑，就用父类的；子类写了同名方法或字段，就覆盖或扩展父类。
