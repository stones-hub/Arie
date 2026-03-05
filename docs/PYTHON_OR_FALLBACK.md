# Python 的 `or` 与“默认值/兜底”用法

## 一、`or` 在这里是什么意思

```python
_url_user = settings.database_url_user or settings.database_url
_url_dept = settings.database_url_dept or settings.database_url
```

**含义**：`A or B` 表示「若 `A` 为真值就用 `A`，否则用 `B`」。

- Python 的 **真值（truthy）**：非零数字、非空字符串、非空容器、`True` 等。
- **假值（falsy）**：`None`、`0`、`""`（空字符串）、`False`、空列表/字典等。

所以：

- `database_url_user` 有配置（非空字符串）→ 为真 → 取 `settings.database_url_user`。
- `database_url_user` 为 `None` 或 `""` → 为假 → 取 `settings.database_url`，相当于「没配就用默认连接串」。

这就是用 `or` 做 **兜底（fallback）**：前面为空就用后面的值。

---

## 二、规则一句话

**`A or B` 的结果 = 从左到右第一个为真的那个；若都为假，则取最后一个（即 `B`）。**

| A 的值   | B 的值   | `A or B` 结果 |
|----------|----------|----------------|
| `"mysql://..."` | `"sqlite://..."` | `"mysql://..."`（取 A） |
| `None`   | `"sqlite://..."` | `"sqlite://..."`（取 B） |
| `""`     | `"sqlite://..."` | `"sqlite://..."`（取 B） |
| `None`   | `None`   | `None`（都假，取 B） |

---

## 三、在本项目中的用法（app/db/session.py）

```python
_url_user = settings.database_url_user or settings.database_url
_url_dept = settings.database_url_dept or settings.database_url
```

- **单库**：不配 `DATABASE_URL_USER` / `DATABASE_URL_DEPT` 时，二者为 `None`，`_url_user` 和 `_url_dept` 都等于 `database_url`，用户表和部门表用同一个库。
- **多库**：在 .env 里配了 `DATABASE_URL_USER`、`DATABASE_URL_DEPT` 时，取配置的字符串，两个库分开。

等价于「若单独配置了用户库/部门库就用它，否则用默认的 `database_url`」。

---

## 四、和三元表达式、`get` 的对比

| 写法 | 含义 |
|------|------|
| `x or default` | 若 `x` 为假值就用 `default`；写法最简，适合「有值用值、没值用默认」。 |
| `x if x is not None else default` | 只有 `x is None` 时才用 `default`；`x` 为 `""` 时仍取 `""`，不会兜底。 |
| `dict.get("key", default)` | 键不存在时用 `default`；和 `or` 的「假值兜底」不是同一回事。 |

在「配置可为 `None` 或空串，希望统一兜底到默认连接串」的场景，用 `settings.xxx or settings.database_url` 是常见、合适的写法。
