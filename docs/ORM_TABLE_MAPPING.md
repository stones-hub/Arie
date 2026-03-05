# ORM 表映射写法说明（以 User 为例）

下面这段是「一个 Python 类 ↔ 一张数据库表」的写法，用的是 **SQLAlchemy 2.0 声明式映射**。  
**不是固定死的**：类名、表名、字段名、类型、约束都可以按你的表来改；**固定的是「这种写法所代表的含义」**。

---

## 逐行含义

### 1. 类定义与表名

```python
class User(OrmBase):
    """用户表。"""

    __tablename__ = "user"
```

| 写法 | 含义 | 是否固定 |
|------|------|----------|
| `class User(OrmBase)` | 声明这是一个 ORM 模型，且继承我们项目的基类 `Base`（别名为 OrmBase）。必须继承 Base，否则不会参与建表。 | 类名可改（如 `Account`）；**必须继承 OrmBase/Base**。 |
| `__tablename__ = "user"` | 对应数据库里的**表名**。SQLAlchemy 按这个名字建表、查表。 | **可改**，改成你库里实际表名（如 `"users"`、`"t_user"`）。 |

---

### 2. 主键 id

```python
id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
```

| 部分 | 含义 |
|------|------|
| `id` | 属性名，在 Python 里用 `user.id` 访问；**一般**也作为数据库列名（列名默认=属性名）。 |
| `Mapped[int]` | 类型注解：这一列在 Python 里是 `int` 类型。SQLAlchemy 2.0 推荐写上，便于类型检查。 |
| `mapped_column(...)` | 声明这是表里的**一列**，括号里是列在数据库中的行为。 |
| `primary_key=True` | 主键。 |
| `autoincrement=True` | 自增：插入时不写 id，数据库自动生成。 |

列名、是否主键、是否自增都可以按表设计改；**主键列通常都要有**。

---

### 3. 普通列：email、name

```python
email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
name: Mapped[str] = mapped_column(String(100), nullable=False)
```

| 部分 | 含义 |
|------|------|
| `String(255)` / `String(100)` | 数据库类型：变长字符串，最大长度 255 / 100。可改成 `Text`、`Integer` 等。 |
| `unique=True` | 唯一约束：表中不能出现重复的 email。 |
| `index=True` | 给该列建索引，按 email 查询更快。 |
| `nullable=False` | 非空：插入/更新时不能为 NULL。 |

类型、长度、是否唯一、是否建索引、是否可空都可以按业务改。

---

### 4. 可空外键：department_id

```python
department_id: Mapped[int | None] = mapped_column(nullable=True)
```

| 部分 | 含义 |
|------|------|
| `Mapped[int | None]` | Python 类型：可能是 `int` 或 `None`（可空）。 |
| `nullable=True` | 数据库允许该列为 NULL。 |
| 无 `ForeignKey` | 部门在另一库，这里只存 id，不做数据库级外键。 |

若表在同一库且要做外键，可加 `ForeignKey("department.id")`；当前项目是跨库，所以只存 id。

---

### 5. 时间戳：created_at、updated_at

```python
created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
```

| 部分 | 含义 |
|------|------|
| `DateTime` | 数据库类型：日期时间。 |
| `server_default=func.now()` | **默认值在数据库侧**：插入时若未提供，用数据库的“当前时间”（如 MySQL 的 `CURRENT_TIMESTAMP`）。 |
| `onupdate=func.now()` | 仅 **updated_at**：该行被更新时，数据库自动把这一列设为当前时间。 |

可改成 `Date`、或不用默认值，按需求来。

---

### 6. `__repr__`（可选）

```python
def __repr__(self) -> str:
    return f"<User id={self.id} email={self.email}>"
```

| 含义 | 说明 |
|------|------|
| 调试用 | 在控制台、日志里打印 `user` 时显示的内容。 |
| 非必须 | 不写也可以，表结构不受影响；写了方便排查问题。 |

---

## 小结：哪些是「约定」、哪些可改

| 项目 | 说明 |
|------|------|
| **必须** | 继承 `OrmBase`（Base）、用 `__tablename__` 指定表名、用 `mapped_column` 定义列。 |
| **可改** | 类名、表名、每个列的名字/类型/长度、unique/index/nullable、是否自增、是否默认值等，都按你的表设计来。 |
| **固定的是「语义」** | 例如 `primary_key=True` 就表示主键，`nullable=False` 就表示非空；**具体用在哪一列、叫什么名字，都是你自己定的。** |

所以：**这不是写死的一串代码，而是「按表结构填空」的模板**；每个表一个类，每个字段一行 `Mapped[类型] = mapped_column(类型, 约束...)`，类型和约束按数据库和业务来设即可。
