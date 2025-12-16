# Django 技术实践：对标 Java 后端实现

本文档记录 Django 项目在实现业务过程中的技术点应用，并对比 Java 项目的解决方案。

---

## 1. 事务管理

### 业务场景
新增/更新员工时，需要同时操作员工表和工作经历表，要求原子性（要么全部成功，要么全部回滚）。

### Django 实现
```python
from django.db import transaction

@staticmethod
@transaction.atomic  # 装饰器声明事务边界
def save(data: dict) -> Emp:
    emp = Emp.objects.create(...)
    EmpExpr.objects.bulk_create([...])
    return emp
```

### Java 对标
```java
@Transactional(rollbackFor = Exception.class)
public void save(Emp emp) {
    empMapper.insert(emp);
    empExprMapper.insertBatch(emp.getExprList());
}
```

### 技术对比
| 维度 | Django | Java Spring |
|------|--------|-------------|
| 声明方式 | `@transaction.atomic` 装饰器 | `@Transactional` 注解 |
| 默认行为 | 任何异常回滚 | 仅 RuntimeException 回滚 |
| 嵌套事务 | `transaction.atomic()` 上下文管理器 | `propagation` 属性配置 |

---

## 2. 全局异常处理

### 业务场景
1. 员工手机号重复时，捕获数据库唯一键冲突，返回友好提示
2. 删除部门时，若部门下有员工，返回业务错误

### Django 实现

**自定义业务异常：**
```python
# common/exceptions.py
class BusinessException(Exception):
    """业务异常 - 对标 Java BusinessException"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
```

**全局异常处理器：**
```python
def custom_exception_handler(exc, context):
    # 1. 处理 IntegrityError（唯一键冲突）
    if isinstance(exc, IntegrityError):
        match = re.search(r"Duplicate entry '(.+?)' for key", str(exc))
        if match:
            return Response(Result.error_data(f"数据已存在：{match.group(1)}"))
    
    # 2. 处理 BusinessException
    if isinstance(exc, BusinessException):
        return Response(Result.error_data(exc.message))
    
    # 3. 其他异常
    return Response(Result.error_data("程序出错啦，请联系管理员~"), status=500)
```

**注册到 settings.py：**
```python
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
}
```

### Java 对标
```java
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler
    public Result handleDuplicateKeyException(DuplicateKeyException e) {
        String message = e.getMessage();
        int i = message.indexOf("Duplicate entry");
        String[] arr = message.substring(i).split(" ");
        return Result.error("数据已存在：" + arr[2]);
    }
    
    @ExceptionHandler
    public Result handleBusinessException(BusinessException e) {
        return Result.error(e.getMessage());
    }
}
```

### 技术对比
| 维度 | Django DRF | Java Spring |
|------|------------|-------------|
| 全局捕获 | `EXCEPTION_HANDLER` 配置 | `@RestControllerAdvice` |
| 异常匹配 | `isinstance()` 类型判断 | `@ExceptionHandler` 方法重载 |
| 数据库异常 | `IntegrityError` | `DuplicateKeyException` |

---

## 3. 分页条件查询

### 业务场景
员工列表支持按姓名、性别、入职日期范围筛选，并分页返回。

### Django 实现
```python
@staticmethod
def page(params: dict) -> dict:
    name = params.get('name')
    gender = params.get('gender')
    begin = params.get('begin')
    end = params.get('end')
    page = int(params.get('page', 1))
    pageSize = int(params.get('pageSize', 10))
    
    # 动态构建查询条件
    queryset = Emp.objects.all()
    if name:
        queryset = queryset.filter(name__icontains=name)
    if gender:
        queryset = queryset.filter(gender=int(gender))
    if begin and end:
        queryset = queryset.filter(entry_date__range=[begin, end])
    
    # 分页
    total = queryset.count()
    start = (page - 1) * pageSize
    empList = queryset[start:start + pageSize]
    
    return {'total': total, 'rows': empList}
```

### Java 对标
```java
// Service 层
public PageResult<Emp> page(EmpQueryParam param) {
    PageHelper.startPage(param.getPage(), param.getPageSize());
    List<Emp> list = empMapper.list(param);  // MyBatis 动态 SQL
    Page<Emp> page = (Page<Emp>) list;
    return new PageResult<>(page.getTotal(), page.getResult());
}
```
```xml
<!-- MyBatis Mapper XML -->
<select id="list" resultType="Emp">
    select * from emp
    <where>
        <if test="name != null and name != ''">
            and name like concat('%', #{name}, '%')
        </if>
        <if test="gender != null">
            and gender = #{gender}
        </if>
        <if test="begin != null and end != null">
            and entry_date between #{begin} and #{end}
        </if>
    </where>
    order by update_time desc
</select>
```

### 技术对比
| 维度 | Django ORM | Java MyBatis |
|------|------------|--------------|
| 动态条件 | QuerySet 链式调用 | XML `<if>` 标签 |
| 分页 | 切片 `[start:end]` | PageHelper 插件 |
| 模糊查询 | `__icontains` | `concat('%', #{}, '%')` |
| 范围查询 | `__range` | `between #{} and #{}` |

---

## 4. 业务校验与条件删除

### 业务场景
删除部门前，检查该部门下是否有员工。若有员工，禁止删除并返回提示。

### Django 实现
```python
@staticmethod
def deleteById(id: int) -> None:
    from common.exceptions import BusinessException
    from ..models import Emp
    
    # 1. 判断部门下是否有员工
    count = Emp.objects.filter(dept_id=id).count()
    if count > 0:
        raise BusinessException("部门下有员工，不能删除")
    
    # 2. 删除部门
    Dept.objects.filter(pk=id).delete()
```

### Java 对标
```java
@Override
public void deleteById(Integer id) {
    // 1. 判断部门下是否有员工
    Integer count = empMapper.countByDeptId(id);
    if (count > 0) {
        throw new BusinessException("部门下有员工，不能删除");
    }
    // 2. 删除部门
    deptMapper.deleteById(id);
}
```

### 技术对比
| 维度 | Django | Java |
|------|--------|------|
| 条件计数 | `Model.objects.filter().count()` | `Mapper.countByXxx()` |
| 业务异常 | `raise BusinessException()` | `throw new BusinessException()` |
| 删除操作 | `Model.objects.filter().delete()` | `Mapper.deleteById()` |

---

## 5. 批量操作

### 业务场景
- 批量删除员工及其工作经历
- 批量插入工作经历

### Django 实现
```python
# 批量删除
Emp.objects.filter(pk__in=ids).delete()
EmpExpr.objects.filter(emp_id__in=ids).delete()

# 批量插入
EmpExpr.objects.bulk_create([
    EmpExpr(emp_id=emp.id, begin=expr.get('begin'), ...)
    for expr in exprList
])
```

### Java 对标
```java
// 批量删除
empMapper.deleteByIds(ids);
empExprMapper.deleteByEmpIds(ids);

// 批量插入（MyBatis foreach）
empExprMapper.insertBatch(exprList);
```
```xml
<insert id="insertBatch">
    insert into emp_expr (emp_id, begin, end, company, job) values
    <foreach collection="list" item="item" separator=",">
        (#{item.empId}, #{item.begin}, #{item.end}, #{item.company}, #{item.job})
    </foreach>
</insert>
```

### 技术对比
| 维度 | Django ORM | Java MyBatis |
|------|------------|--------------|
| 批量删除 | `filter(pk__in=ids).delete()` | `WHERE id IN (...)` |
| 批量插入 | `bulk_create([...])` | `<foreach>` 拼接 VALUES |
| SQL 效率 | 单条 SQL | 单条 SQL |

---

## 6. 关联查询与嵌套序列化

### 业务场景
查询员工详情时，同时返回工作经历列表。

### Django 实现
```python
# Service 层
@staticmethod
def getInfo(id: int) -> dict:
    emp = Emp.objects.get(pk=id)
    exprList = EmpExpr.objects.filter(emp_id=id)
    return {'emp': emp, 'exprList': exprList}

# Serializer 层 - 嵌套序列化
class EmpDetailSerializer(serializers.ModelSerializer):
    exprList = serializers.SerializerMethodField()
    
    def get_exprList(self, obj):
        expr_list = self.context.get('expr_list', [])
        return EmpExprSerializer(expr_list, many=True).data
```

### Java 对标
```java
// Service 层
public Emp getInfo(Integer id) {
    Emp emp = empMapper.getById(id);
    List<EmpExpr> exprList = empExprMapper.getByEmpId(id);
    emp.setExprList(exprList);
    return emp;
}
```

### 技术对比
| 维度 | Django | Java |
|------|--------|------|
| 关联查询 | 两次独立查询 | 两次独立查询 |
| 嵌套组装 | `SerializerMethodField` | Entity 内嵌 List |
| 返回格式 | Serializer 定义 | Jackson 自动序列化 |

---

## 总结

Django 以 **ORM 链式调用** 和 **装饰器** 为核心，实现了与 Java Spring + MyBatis 相似的企业级功能：

| 功能 | Django | Java |
|------|--------|------|
| 事务管理 | `@transaction.atomic` | `@Transactional` |
| 全局异常 | `EXCEPTION_HANDLER` | `@RestControllerAdvice` |
| 动态查询 | QuerySet 链式调用 | MyBatis 动态 SQL |
| 分页 | 切片 | PageHelper |
| 批量操作 | `bulk_create()` | `<foreach>` |

两者设计理念一致，只是语法和工具不同。
