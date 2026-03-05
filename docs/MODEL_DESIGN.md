# 为什么一个“表”文件里会有多个 class（ORM 与 Schema 区分）

## 一、结论先说

- **和数据库表一一对应的，每个表只有一个 class**：`User` 对应表 `user`，`Department` 对应表 `department`。
- 同一个文件里的**其他 class** 不是表，而是 **API 用的数据结构（Schema）**：用来描述请求体、响应体长什么样，做校验和序列化，**不参与建表、不落库**。

所以：**model 文件 = 一个 ORM 表类 + 多个 Pydantic Schema 类**，不是“一个表多个 class”。

---

## 二、两类 class 分别是什么

| 类型 | 继承谁 | 作用 | 是否对应表 |
|------|--------|------|------------|
| **ORM 模型** | `Base`（SQLAlchemy） | 和数据库表映射，用于查询、写入 | ✅ 一个类对应一张表 |
| **Pydantic Schema** | `BaseModel`（Pydantic） | 定义 API 入参/出参结构，校验、序列化 | ❌ 不对应表 |

---

## 三、以 user 为例

| 类名 | 类型 | 含义 |
|------|------|------|
| **User** | ORM | 表 `user` 的映射，`db.get(User, id)`、`db.add(user)` 用这个。 |
| UserBase | Schema | 公共字段（email, name, department_id），给 Create/Response 复用。 |
| UserCreate | Schema | 创建用户的**请求体**：客户端 POST 的 JSON 长这样。 |
| UserUpdate | Schema | 更新用户的**请求体**：只含要改的字段（可选）。 |
| UserResponse | Schema | 单用户**响应体**：返回给前端的结构（含 id、时间等）。 |
| UserWithDepartmentResponse | Schema | 带部门信息的**响应体**：UserResponse + 嵌套的部门对象。 |

所以：**只有 `User` 对应表**；UserCreate、UserResponse 等只是“接口约定”，不建表。

---

## 四、以 department 为例

| 类名 | 类型 | 含义 |
|------|------|------|
| **Department** | ORM | 表 `department` 的映射。 |
| DepartmentResponse | Schema | 部门在 API 里的**响应体**结构（如嵌套在用户详情里）。 |

同样：**只有 `Department` 对应表**；DepartmentResponse 只用于出参形状。

---

## 五、为什么要拆成多个 Schema 而不是只用一个类？

- **请求和响应结构往往不同**：创建时不需要传 `id`、`created_at`，响应里要带；更新时只传部分字段。
- **安全与清晰**：请求体只暴露“允许客户端写的字段”；响应体只暴露“允许返回的字段”，避免把内部字段误返回。
- **校验与文档**：Pydantic 按 Schema 做校验、生成 OpenAPI 文档，不同接口用不同 Schema 更清晰。

---

## 六、对应关系小结

```
数据库表          ORM 类（一个表一个类）    Pydantic Schema（多个，不对应表）
─────────────────────────────────────────────────────────────────────────
user       →     User                     UserCreate, UserUpdate, UserResponse, ...
department →     Department               DepartmentResponse
```

所以：**model 对应数据库的是“每个表一个 ORM 类”；同一个文件里多出来的 class 都是 API 用的 Schema，不对应表。**
