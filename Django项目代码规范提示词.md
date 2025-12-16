# Django 项目代码规范

你是我的 Django/DRF 代码代理。请严格遵守以下项目约定生成/重构代码，目标是达到 Java 三层架构的严谨性、规范性、可维护性

## 1）分层结构与职责边界

**views（Controller）层：极薄**
- 只负责：解析 HTTP 输入 → 调用 Service → 返回统一 Result
- 禁止：直接 ORM 操作、复杂业务 if/else、事务逻辑、字段拼装

**services（Service）层：业务唯一入口**
- 负责：业务规则、校验、ORM 访问、异常转换、事务边界（如需要）
- 禁止：接收 request 对象；禁止返回 Result；禁止做序列化

**serializers 层：仅用于"输出结构定义"**
- 不再拆分大量请求 DTO（除非必要）
- 主要作用：将 Model 输出为前端所需 JSON（字段筛选）
- 全局驼峰渲染器自动转换字段名，无需手动 source= 映射

## 2）输入参数策略（对标 Java "实体直用"）

- 约定：前端传参结构可靠，不强制为每个接口创建输入 Serializer/DTO
- 绝大多数接口：View 将 request.data / request.query_params 直接传给 Service
- 输入校验：统一放到 Service
- 仅当参数结构复杂且嵌套深时，才允许引入输入 Serializer

## 3）输出序列化策略（全局配置）

- 每个资源只保留一个输出 Serializer（例如 DeptSerializer）
- **全局驼峰渲染器**：`djangorestframework-camel-case` 自动转换 snake_case → camelCase
- **全局时间格式**：`DATETIME_FORMAT: '%Y-%m-%d %H:%M:%S'`（去掉 T）
- View 直接调用 Serializer，不需要 Presenter 层

## 4）统一响应封装

- 所有接口统一返回：`Result.success(data)` / `Result.error(message)`
- Result 类位于 `common/result.py`

## 5）全局异常处理（对标 Java GlobalExceptionHandler）

- 异常处理器位于 `common/exceptions.py`
- 在 `settings.py` 中通过 `REST_FRAMEWORK.EXCEPTION_HANDLER` 注册
- 处理以下异常类型：
  - `IntegrityError`：解析 "Duplicate entry" 信息，返回友好提示（如：数据已存在：xxx）
  - `BusinessException`：自定义业务异常，直接返回异常消息
  - 其他异常：记录日志，返回通用错误提示

**业务异常使用示例：**
```python
from common.exceptions import BusinessException

# Service 层抛出业务异常
if count > 0:
    raise BusinessException("部门下有员工，不能删除")
```

## 6）接口路由约定

**严格按照 `api接口文档.md` 进行开发**

部门管理接口示例：
- `GET /depts` - 查询列表
- `POST /depts` - 新增（name 在 body）
- `PUT /depts` - 修改（id 和 name 在 body）
- `DELETE /depts?id=x` - 删除（id 在 query 参数）
- `GET /depts/{id}` - 根据 ID 查询（路径参数）

员工管理接口示例：
- `GET /emps` - 分页条件查询（支持 name、gender、begin、end、page、pageSize）
- `POST /emps` - 新增员工（包含工作经历 exprList）
- `PUT /emps` - 修改员工
- `DELETE /emps?ids=1,2,3` - 批量删除

## 7）变量和方法命名规范（对标 Java）

**方法命名对标 Java：**
| Java | Django |
|------|--------|
| `findAll()` | `findAll()` |
| `getById(id)` | `getById(id)` |
| `getInfo(id)` | `getInfo(id)` |
| `add(dept)` | `add(data)` |
| `save(emp)` | `save(data)` |
| `update(dept)` | `update(data)` |
| `deleteById(id)` | `deleteById(id)` |
| `delete(ids)` | `delete(ids)` |
| `page(params)` | `page(params)` |

**变量命名对标 Java：**
| Java | Django |
|------|--------|
| `deptList` | `deptList` |
| `empList` | `empList` |
| `exprList` | `exprList` |
| `pageResult` | `pageResult` |
| `id` | `id`（不用 pk） |

**命名风格：**
- Service 方法使用驼峰命名：`findAll`、`getById`、`deleteById`、`getInfo`
- 变量使用驼峰命名：`deptList`、`empList`、`pageResult`
- 路由参数使用 `id` 而非 `pk`

## 8）事务管理（对标 Java @Transactional）

- 使用 `@transaction.atomic` 装饰器
- 放置在 Service 方法上，确保业务操作的原子性
- 对标 Java `@Transactional(rollbackFor = Exception.class)`

```python
from django.db import transaction

@staticmethod
@transaction.atomic
def save(data: dict) -> Emp:
    # 多表操作自动回滚
    emp = Emp.objects.create(...)
    EmpExpr.objects.bulk_create([...])
    return emp
```

## 9）代码示例

**View 层示例：**
```python
def get(self, request):
    logger.info("查询所有部门")
    deptList = DeptService.findAll()
    return Result.success(DeptSerializer(deptList, many=True).data)

def delete(self, request):
    id = request.query_params.get('id')
    logger.info(f"删除部门：{id}")
    DeptService.deleteById(int(id))
    return Result.success()
```

**Service 层示例（带业务校验）：**
```python
@staticmethod
def deleteById(id: int) -> None:
    """删除部门 - 对标 Java DeptServiceImpl.deleteById()"""
    from common.exceptions import BusinessException
    from ..models import Emp
    
    # 1. 判断部门下是否有员工
    count = Emp.objects.filter(dept_id=id).count()
    if count > 0:
        raise BusinessException("部门下有员工，不能删除")
    
    # 2. 删除部门
    Dept.objects.filter(pk=id).delete()
```

**Service 层示例（分页查询）：**
```python
@staticmethod
def page(params: dict) -> dict:
    """分页条件查询 - 对标 Java PageHelper + 动态 SQL"""
    name = params.get('name')
    page = int(params.get('page', 1))
    pageSize = int(params.get('pageSize', 10))
    
    queryset = Emp.objects.all()
    if name:
        queryset = queryset.filter(name__icontains=name)
    
    total = queryset.count()
    start = (page - 1) * pageSize
    empList = queryset[start:start + pageSize]
    
    return {'total': total, 'rows': empList}
```

## 10）输出要求（AI 交付标准）

修改/新增代码时，必须同时给出：
- views / services / serializers 的对应变更
- 文件路径与完整可复制代码块
- 若涉及接口变更，给出对应的请求示例与返回示例（JSON）
- 若涉及业务异常，说明异常场景和错误提示
