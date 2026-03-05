# Python 常用语法糖速查

> 语法糖 = 用“更短的写法”表达一段常见的代码逻辑，本质上都是编译器/解释器帮你自动展开。

下面列的是在日常写脚本、服务端代码时最常见、最有用的一些语法糖，每条都给出“语法糖写法 + 展开后的长写法”，方便理解。

---

## 1. 推导式（Comprehension）

### 1.1 列表推导式 list comprehension

```python
nums = [1, 2, 3, 4, 5]

# 语法糖写法：
squares = [x * x for x in nums if x % 2 == 0]

# 等价长写法：
squares = []
for x in nums:
    if x % 2 == 0:
        squares.append(x * x)
```

总结：

- `[表达式 for 变量 in 可迭代对象 if 条件]`
- 结果是 list；常用于对一组数据做**映射 + 过滤**。

### 1.2 字典推导式 dict comprehension

```python
# 语法糖：
name_to_length = {name: len(name) for name in ["alice", "bob", "carol"]}

# 等价长写法：
name_to_length = {}
for name in ["alice", "bob", "carol"]:
    name_to_length[name] = len(name)
```

结构：

- `{key_expr: value_expr for 变量 in 可迭代对象}`

在你的线程池示例里：

```python
future_to_path = {
    executor.submit(process_file, path): path
    for path in paths
}
```

等价于：

```python
future_to_path = {}
for path in paths:
    future = executor.submit(process_file, path)
    future_to_path[future] = path
```

### 1.3 集合推导式 set comprehension

```python
lengths = {len(name) for name in ["a", "bb", "ccc", "bb"]}
# 结果是 set，元素自动去重
```

### 1.4 生成器表达式 generator expression

```python
gen = (x * x for x in range(10))

for value in gen:
    print(value)
```

- 用圆括号 `()`，返回的是惰性生成器，需要迭代才能取值。

---

## 2. `with` 上下文管理器

核心思想：**进入 with 块前做一些准备，离开（无论是否异常）时一定做清理**。

### 2.1 模式

```python
with expr as var:
    # 使用 var 做事
    ...
```

大致等价于：

```python
mgr = expr
var = mgr.__enter__()
try:
    ...
finally:
    mgr.__exit__(exc_type, exc_val, exc_tb)
```

### 2.2 线程池中的例子

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    ...
```

等价于：

```python
executor = ThreadPoolExecutor(max_workers=5)
try:
    ...
finally:
    executor.shutdown(wait=True)  # 确保线程池里的线程都优雅退出
```

常见场景：文件、锁、线程池、数据库连接等**需要释放资源**的对象，都建议用 `with`。

### 2.3 文件操作

```python
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()
# 出 with 后文件自动关闭
```

---

## 3. 条件表达式（三元运算符）

```python
# 语法糖：
msg = "ok" if success else "failed"

# 等价长写法：
if success:
    msg = "ok"
else:
    msg = "failed"
```

结构：

- `表达式_if_true if 条件 else 表达式_if_false`
- 适合简单赋值、返回值场景；复杂逻辑还是用普通 if/else 更清晰。

---

## 4. 多重比较 & 链式比较

```python
if 0 < x < 10:
    ...
```

等价于：

```python
if x > 0 and x < 10:
    ...
```

Python 允许这样写多重比较，既简洁又贴近数学符号。

---

## 5. 解包（unpacking）与星号表达式

### 5.1 序列解包

```python
pair = ("alice", 18)
name, age = pair  # 左右一一对应
```

### 5.2 星号收集多余元素

```python
head, *middle, tail = [1, 2, 3, 4, 5]
# head = 1, middle = [2, 3, 4], tail = 5
```

常见用法：只关心第一个/最后一个，其余用 `*_` 丢掉。

### 5.3 函数参数解包

```python
def add(a, b):
    return a + b

args = (1, 2)
result = add(*args)  # 等价于 add(1, 2)

kwargs = {"a": 1, "b": 2}
result = add(**kwargs)  # 等价于 add(a=1, b=2)
```

---

## 6. `enumerate` 和 `zip`

### 6.1 enumerate：同时拿索引和值

```python
names = ["alice", "bob", "carol"]
for idx, name in enumerate(names, start=1):
    print(idx, name)
```

等价于手动维护下标：

```python
for i in range(len(names)):
    print(i + 1, names[i])
```

### 6.2 zip：同时遍历多个序列

```python
names = ["alice", "bob"]
ages = [18, 20]
for name, age in zip(names, ages):
    print(name, age)
```

等价于：

```python
for i in range(min(len(names), len(ages))):
    print(names[i], ages[i])
```

---

## 7. f-string（格式化字符串）

```python
name = "alice"
age = 18
msg = f"name={name} age={age}"
print(msg)
```

等价于：

```python
msg = "name=" + name + " age=" + str(age)
```

特点：

- 读写都很舒服；
- 可在大括号里直接写表达式：`f"{x * 2=}"`。

---

## 8. for-else / while-else

很多人容易忽略的一个语法糖，用于表达“循环正常结束”与“被 break 打断”的区别。

```python
for x in data:
    if 条件满足:
        print("找到目标")
        break
else:
    # 只有当 for 循环「没有通过 break 提前退出」时才会执行这里
    print("循环结束也没找到")
```

常见用法：搜索/校验时区分“找到”与“完全没找到”的情况，而不用额外布尔变量。

---

## 9. 装饰器 @decorator

```python
def log_calls(func):
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def hello(name: str) -> None:
    print(f"Hello, {name}")
```

等价于：

```python
def hello(name: str) -> None:
    print(f"Hello, {name}")

hello = log_calls(hello)  # 用装饰器包一层
```

作用：在不改原函数代码的前提下，为函数统一加前后逻辑（日志、鉴权、缓存等）。

---

## 10. 赋值表达式（海象运算符 `:=`，Python 3.8+）

```python
while (line := f.readline()) != "":
    print(line)
```

等价于：

```python
while True:
    line = f.readline()
    if line == "":
        break
    print(line)
```

特点：

- 可以在表达式里“顺便赋值”，减少重复代码；
- 适合 while/if 这种“先算，再用”的地方。

---

## 小结

上面这些语法糖中，**你已经在项目里实际用到的有**：

- 推导式（特别是字典推导式）：`{executor.submit(...): path for path in paths}`
- `with` 上下文管理器：`with ThreadPoolExecutor(...) as executor:`
- 解包、`Tuple[...]`、`Dict[...]` 类型标注
- f-string：`f"user_id={user_id} action={action}"`

建议的学习方式：

1. 遇到看不懂的推导式或 with 用法时，**先把它展开成 for 循环 + try/finally 的长写法**；
2. 理解后再改回语法糖写法，体会“代码短了多少、逻辑有没有更清晰”；
3. 对复杂逻辑宁可不用语法糖，先保证可读性，再考虑简化。

