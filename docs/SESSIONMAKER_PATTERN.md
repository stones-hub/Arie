# `SessionUserLocal = sessionmaker(...)` 是什么写法？是 Python 语法吗？

## 一、就是普通的「赋值」

```python
SessionUserLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_user)
```

这一行没有用到任何特殊语法，就是最常见的：

**变量名 = 表达式的结果**

- 右边：**`sessionmaker(...)`** 是一个**函数调用**，会返回一个对象。
- 左边：**`SessionUserLocal`** 是一个变量名，用来保存这个返回值。

所以：**`SessionUserLocal` 里存的是 `sessionmaker()` 返回的那个对象**，没有新语法。

---

## 二、`sessionmaker()` 返回的是什么？

`sessionmaker()` 是 SQLAlchemy 提供的函数，它返回的是一个**可调用对象**（callable）。

在 Python 里，「可调用」的意思是：可以像函数一样在后面加括号来调用，例如：

```python
result = SessionUserLocal()   # 用括号「调用」SessionUserLocal
```

- 你写的是 `SessionUserLocal()`，相当于「调用 SessionUserLocal 这个对象」。
- 这个对象内部实现了 `__call__`，所以加括号就会执行一段逻辑：**创建一个新的 Session 并返回**。

所以：**`SessionUserLocal` 不是用 `def` 定义的函数，而是一个「可以像函数一样被调用」的对象**，一般叫它「工厂」：调用一次，就「生产」出一个新 Session。

---

## 三、和普通函数对比

| 写法 | 含义 |
|------|------|
| `def foo(): return 1` | `foo` 是函数，`foo()` 得到 1。 |
| `bar = sessionmaker(...)` | `bar` 是 sessionmaker 返回的对象；`bar()` 会新建一个 Session。 |

从「使用方式」上看，`SessionUserLocal()` 和 `foo()` 一样：都是「名字 + 括号」表示调用。  
区别只是：**函数是用 `def` 定义的，而 `SessionUserLocal` 是别人（sessionmaker）返回给你的一个可调用对象**。这都属于 Python 的常规用法，不是额外语法。

---

## 四、整条链路串起来

```text
1. sessionmaker(...) 被调用
   → 返回一个「Session 工厂」对象

2. SessionUserLocal = 这个对象
   → 变量 SessionUserLocal 指向该工厂

3. 在 deps.py 里写：db = SessionUserLocal()
   → 调用该工厂的 __call__
   → 工厂根据当初的 bind=engine_user 创建一个新 Session
   → 这个 Session 使用用户库的连接池

4. 请求结束，deps 里执行 db.close()
   → 连接还回连接池
```

---

## 五、小结

- **是普通 Python**：`名字 = 某个返回值`，没有任何特殊语法。
- **`SessionUserLocal`**：是「Session 工厂」这个对象的名字，不是 `def` 定义的函数。
- **`SessionUserLocal()`**：表示「调用这个工厂」，得到一个新的、绑定用户库的 Session。

所以：**这是标准的「赋值 + 可调用对象」用法，只是 SQLAlchemy 用这种模式来做 Session 的创建和配置。**

---

## 六、关于 `[Session]` 这种写法（类型提示里才会出现）

**我们项目里的代码没有写 `[Session]`。** 你如果在 IDE 里把鼠标悬停在 `SessionUserLocal` 或 `SessionUserLocal()` 上，可能会看到类似：

- `SessionUserLocal` 的类型是「调用后返回 Session 的 callable」
- 或写成 `Callable[[], Session]`、`sessionmaker[Session]` 等

这里的 **`[Session]` 是类型注解（type hint）里的写法**，用来告诉类型检查器 / IDE：「调用这个东西会得到 `Session` 类型的值」。它**只影响提示和静态检查**，运行时不会执行，也不是「函数调用的特殊语法」。

类比：

- `list[int]` 表示「元素是 int 的列表」
- `Callable[[], Session]` 表示「无参、返回 Session 的可调用对象」

所以：**真正执行时你只会看到 `SessionUserLocal()` 这种普通调用；`[Session]` 只出现在类型系统里，不是我们手写的调用方式。**
