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

## 7. 字段空值处理与数据库 NULL

### 业务场景
班级管理、学生管理中，部分字段为非必填（如教室、班主任ID、联系地址、毕业时间等）。前端提交时，这些字段可能为空字符串 `""`，需要正确转换为数据库的 `NULL` 值。

### Django 实现

**问题背景**：
- 前端空表单字段提交时，后端接收到的是空字符串 `""`
- 数据库字段允许 `NULL`，但不允许空字符串
- 需要在保存前统一处理：空字符串 → `None`（Python 的 NULL）

**解决方案1：整数字段辅助方法**
```python
@staticmethod
def _parse_int(value):
    """将空字符串转为 None，否则转为整数"""
    if value is None or value == '':
        return None
    return int(value)

# 使用示例
Clazz.objects.create(
    name=data.get('name'),
    master_id=ClazzService._parse_int(data.get('masterId')),  # 可能为 None
    room=data.get('room') or None,  # 空字符串转 None
    ...
)
```

**解决方案2：字符串字段 `or None`**
```python
Student.objects.create(
    name=data.get('name'),
    address=data.get('address') or None,  # 空字符串 → None
    graduation_date=data.get('graduationDate') or None,
    ...
)
```

### Java 对标

**方式1：实体类字段默认值**
```java
public class Clazz {
    private String room;  // 引用类型，默认 null
    private Integer masterId;  // 包装类型，默认 null
}
```

**方式2：手动判断**
```java
if (StringUtils.isEmpty(room)) {
    clazz.setRoom(null);
}
```

### 技术对比
| 维度 | Django | Java |
|------|--------|------|
| 整数空值 | `_parse_int()` 辅助方法 | 包装类型（`Integer`）默认 null |
| 字符串空值 | `value or None` | `StringUtils.isEmpty()` 判断 |
| 数据库映射 | ORM 自动处理 `None` → `NULL` | MyBatis 自动处理 `null` → `NULL` |

---

## 8. AOP 日志记录（装饰器实现）

### 业务场景
记录所有业务操作的日志，包括：操作人ID、操作时间、类名、方法名、请求参数、返回值、耗时（毫秒）。

### Django 实现

**日志装饰器（对标 Java AOP `@Around`）：**
```python
# common/log_decorator.py
import json
import time
from datetime import datetime
from functools import wraps

def log_operation(func):
    """
    操作日志装饰器 - 对标 Java @LogOperation + OperationLogAspect
    """
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        from management.models.operate_log import OperateLog
        
        # 1. 记录开始时间
        start_time = time.time()
        
        # 2. 执行原方法
        result = func(self, request, *args, **kwargs)
        
        # 3. 计算耗时
        cost_time = int((time.time() - start_time) * 1000)
        
        # 4. 获取当前用户ID（从中间件注入的 request.emp_id）
        emp_id = getattr(request, 'emp_id', None)
        
        # 5. 获取请求参数
        method_params = json.dumps(request.data, ensure_ascii=False, default=str)
        
        # 6. 获取返回值
        return_value = json.dumps(result.data, ensure_ascii=False, default=str)
        
        # 7. 保存日志
        OperateLog.objects.create(
            operate_emp_id=emp_id,
            operate_time=datetime.now(),
            class_name=self.__class__.__name__,
            method_name=request.method,
            method_params=method_params[:2000],
            return_value=return_value[:2000],
            cost_time=cost_time
        )
        
        return result
    
    return wrapper
```

**使用方式：**
```python
from common.log_decorator import log_operation

class DeptListView(APIView):
    @log_operation  # 添加装饰器
    def post(self, request):
        # 业务逻辑
        result = DeptService.page(params)
        return Response(Result.success(result))
```

### Java 对标

**自定义注解：**
```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface LogOperation {
}
```

**AOP 切面类：**
```java
@Slf4j
@Aspect
@Component
public class OperationLogAspect {
    
    @Around("@annotation(com.itheima.anno.LogOperation)")
    public Object recordLog(ProceedingJoinPoint pjp) throws Throwable {
        // 1. 记录开始时间
        long begin = System.currentTimeMillis();
        
        // 2. 执行原方法
        Object result = pjp.proceed();
        
        // 3. 记录结束时间
        long end = System.currentTimeMillis();
        
        // 4. 记录操作日志
        OperateLog log = new OperateLog();
        log.setOperateEmpId(empId);
        log.setOperateTime(LocalDateTime.now());
        log.setClassName(pjp.getTarget().getClass().getName());
        log.setMethodName(pjp.getSignature().getName());
        log.setMethodParams(Arrays.toString(pjp.getArgs()));
        log.setCostTime(end - begin);
        
        operateLogMapper.insert(log);
        return result;
    }
}
```

**使用方式：**
```java
@RestController
public class DeptController {
    @PostMapping("/list")
    @LogOperation  // 添加注解
    public Result<PageResult> list(@RequestBody DeptQueryParam param) {
        // 业务逻辑
    }
}
```

### 技术对比
| 维度 | Django | Java Spring AOP |
|------|--------|-----------------|
| 声明方式 | `@log_operation` 装饰器 | `@LogOperation` 注解 |
| 切面实现 | 装饰器函数（显式包装） | AOP 切面类（动态代理） |
| 织入时机 | 编译时（装饰器语法） | 运行时（Spring AOP） |
| 用户信息获取 | `request.emp_id`（中间件注入） | `BaseContext.getCurrentId()`（ThreadLocal） |

---

## 9. JWT 认证中间件

### 业务场景
拦截所有 HTTP 请求，验证 JWT Token。未认证的请求返回 401，已认证请求将用户信息注入到 `request` 对象供后续使用。

### Django 实现

**认证中间件（对标 Java `TokenFilter`）：**
```python
# common/auth_middleware.py
import logging
from django.http import JsonResponse
from .jwt_utils import parse_jwt

class TokenAuthMiddleware:
    """Token 认证中间件 - 对标 Java TokenFilter"""
    
    # 白名单（包含即放行）
    WHITELIST = ['/login', '/media/', '/static/']
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 1. 判断是否在白名单中
        path = request.path
        for pattern in self.WHITELIST:
            if pattern in path:
                return self.get_response(request)
        
        # 2. 获取请求头中的 token
        token = request.headers.get('token')
        if not token:
            return JsonResponse({'code': 0, 'msg': '未登录'}, status=401)
        
        # 3. 解析 token
        try:
            claims = parse_jwt(token)
            emp_id = claims.get('id')
            # 将用户信息注入 request，供后续视图使用
            request.emp_id = emp_id
            request.emp_username = claims.get('username')
        except Exception as e:
            return JsonResponse({'code': 0, 'msg': '登录已过期'}, status=401)
        
        # 4. 放行
        return self.get_response(request)
```

**注册中间件（settings.py）：**
```python
MIDDLEWARE = [
    ...
    'common.auth_middleware.TokenAuthMiddleware',  # 添加认证中间件
]
```

### Java 对标

**Token 过滤器：**
```java
@Slf4j
@WebFilter(urlPatterns = "/*")
public class TokenFilter implements Filter {
    
    @Override
    public void doFilter(ServletRequest req, ServletResponse resp, FilterChain chain) 
            throws IOException, ServletException {
        HttpServletRequest request = (HttpServletRequest) req;
        HttpServletResponse response = (HttpServletResponse) resp;
        
        // 1. 获取请求路径
        String url = request.getRequestURL().toString();
        
        // 2. 判断是否包含 /login，是则放行
        if (url.contains("/login")) {
            chain.doFilter(request, response);
            return;
        }
        
        // 3. 获取请求头中的令牌
        String token = request.getHeader("token");
        
        // 4. 判断令牌是否存在
        if (!StringUtils.hasLength(token)) {
            Result error = Result.error("未登录");
            response.setStatus(401);
            response.getWriter().write(JSONObject.toJSONString(error));
            return;
        }
        
        // 5. 解析 token
        try {
            Claims claims = JwtUtils.parseJWT(token);
            Integer empId = (Integer) claims.get("id");
            // 存入 ThreadLocal
            BaseContext.setCurrentId(empId);
        } catch (Exception e) {
            Result error = Result.error("登录已过期");
            response.setStatus(401);
            response.getWriter().write(JSONObject.toJSONString(error));
            return;
        }
        
        // 6. 放行
        chain.doFilter(request, response);
    }
}
```

### 技术对比
| 维度 | Django | Java Servlet |
|------|--------|--------------|
| 拦截器类型 | Middleware | Filter |
| 配置方式 | `settings.MIDDLEWARE` 列表 | `@WebFilter` 注解 |
| 白名单判断 | 列表遍历 `path in WHITELIST` | 字符串包含 `url.contains()` |
| 用户信息传递 | 注入到 `request` 对象 | ThreadLocal（`BaseContext`） |
| 返回401 | `JsonResponse(..., status=401)` | `response.setStatus(401)` |

---

## 10. 数据聚合统计

### 业务场景
报表统计需求：
1. 员工性别分布（饼图数据）
2. 员工职位分布（柱状图数据）
3. 学生学历分布（饼图数据）
4. 班级学生人数统计（柱状图数据）

### Django 实现

**示例1：员工性别统计**
```python
from django.db.models import Count

@staticmethod
def getEmpGenderData() -> list:
    """
    员工性别统计 - 对标 Java ReportServiceImpl.getEmpGenderData()
    返回：[{"name": "男", "value": 10}, {"name": "女", "value": 5}]
    """
    result = Emp.objects.values('gender').annotate(value=Count('id'))
    
    gender_data = []
    for item in result:
        gender_data.append({
            'name': '男' if item['gender'] == 1 else '女',
            'value': item['value']
        })
    return gender_data
```
**生成SQL：**
```sql
SELECT gender, COUNT(id) AS value 
FROM emp 
GROUP BY gender;
```

**示例2：员工职位分布**
```python
@staticmethod
def getEmpJobData() -> dict:
    """
    员工职位统计
    返回：{"jobList": ["班主任", "讲师", ...], "dataList": [10, 20, ...]}
    """
    JOB_MAP = {1: '班主任', 2: '讲师', 3: '学工主管', 4: '教研主管', 5: '咨询师'}
    
    result = Emp.objects.exclude(job__isnull=True).values('job').annotate(emp_count=Count('id'))
    
    jobList = []
    dataList = []
    for item in result:
        job_name = JOB_MAP.get(item['job'], '其他')
        jobList.append(job_name)
        dataList.append(item['emp_count'])
    
    return {'jobList': jobList, 'dataList': dataList}
```

**示例3：班级学生人数统计（多表关联）**
```python
@staticmethod
def getStudentCountData() -> dict:
    """
    班级学生人数统计
    返回：{"clazzList": ["Java班", "前端班"], "dataList": [30, 25]}
    """
    # 1. 统计每个班级的学生数量
    result = Student.objects.exclude(clazz_id__isnull=True).values('clazz_id').annotate(
        student_count=Count('id')
    )
    
    # 2. 获取班级名称
    clazzList = []
    dataList = []
    for item in result:
        clazz = Clazz.objects.get(pk=item['clazz_id'])
        clazzList.append(clazz.name)
        dataList.append(item['student_count'])
    
    return {'clazzList': clazzList, 'dataList': dataList}
```

### Java 对标

**MyBatis Mapper XML：**
```xml
<!-- 员工性别统计 -->
<select id="getEmpGenderData" resultType="com.itheima.pojo.ReportData">
    select 
        case gender when 1 then '男' else '女' end as name,
        count(*) as value
    from emp
    group by gender
</select>

<!-- 员工职位统计 -->
<select id="getEmpJobData" resultType="com.itheima.pojo.JobData">
    select job, count(*) as emp_count
    from emp
    where job is not null
    group by job
</select>

<!-- 班级学生人数统计 -->
<select id="getStudentCountData" resultType="com.itheima.pojo.ClazzData">
    select c.name as clazz_name, count(s.id) as student_count
    from student s
    left join clazz c on s.clazz_id = c.id
    where s.clazz_id is not null
    group by s.clazz_id, c.name
</select>
```

### 技术对比
| 维度 | Django ORM | Java MyBatis |
|------|------------|--------------|
| 分组聚合 | `values('field').annotate(Count('id'))` | `GROUP BY field` |
| 聚合函数 | `Count`, `Sum`, `Avg`, `Max`, `Min` | `COUNT()`, `SUM()`, `AVG()` |
| 过滤空值 | `exclude(field__isnull=True)` | `WHERE field IS NOT NULL` |
| 字段映射 | Python 字典手动映射 | SQL `CASE WHEN` 或 Java 代码映射 |
| 多表关联 | 二次查询组装 | `LEFT JOIN` 一次查询 |

---

## 11. 文件上传（本地存储 vs 阿里云 OSS）

### 业务场景
上传员工照片、学生照片等图片文件。

> [!IMPORTANT]
> **存储方案差异**：
> - **Java 项目**：已采用阿里云 OSS 对象存储
> - **Django 项目**：当前阶段使用本地存储（保存到 `media` 目录）
> - 两者实现思路相同（UUID 文件名 + 日期目录），仅存储位置不同

### Django 实现（本地存储）

```python
# management/services/upload_service.py
import os
import uuid
from datetime import datetime
from pathlib import Path
from django.conf import settings

class UploadService:
    
    @staticmethod
    def upload(file) -> str:
        """
        上传文件到本地 media/YYYY/MM 目录
        返回：可访问的 URL
        """
        # 1. 获取原始文件名和扩展名
        original_name = file.name
        extension = os.path.splitext(original_name)[1]
        
        # 2. 生成新文件名（UUID + 扩展名）
        new_filename = f"{uuid.uuid4()}{extension}"
        
        # 3. 创建日期目录（按年/月组织）
        date_path = datetime.now().strftime('%Y/%m')
        upload_dir = Path(settings.MEDIA_ROOT) / date_path
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 4. 保存文件
        file_path = upload_dir / new_filename
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # 5. 返回可访问的 URL
        # 格式：http://localhost:8000/media/2025/12/xxx.png
        return f"{settings.MEDIA_URL}{date_path}/{new_filename}"
```

**配置（settings.py）：**
```python
# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**URL 配置（urls.py）：**
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Java 对标（阿里云 OSS）

```java
@Service
public class UploadServiceImpl implements UploadService {
    
    @Autowired
    private AliOSSUtils aliOSSUtils;
    
    @Override
    public String upload(MultipartFile file) throws IOException {
        // 1. 获取原始文件名
        String originalFilename = file.getOriginalFilename();
        String extension = originalFilename.substring(originalFilename.lastIndexOf("."));
        
        // 2. 生成新文件名（UUID）
        String newFilename = UUID.randomUUID().toString() + extension;
        
        // 3. 创建日期路径
        String datePath = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy/MM"));
        String objectName = datePath + "/" + newFilename;
        
        // 4. 上传到阿里云 OSS
        String url = aliOSSUtils.upload(file.getBytes(), objectName);
        
        // 5. 返回 OSS 公网访问 URL
        // 格式：https://xxx.oss-cn-hangzhou.aliyuncs.com/2025/12/xxx.png
        return url;
    }
}
```

### 技术对比
| 维度 | Django（本地） | Java（OSS） |
|------|----------------|-------------|
| 文件名生成 | `uuid.uuid4()` | `UUID.randomUUID()` |
| 目录组织 | `YYYY/MM` | `YYYY/MM` |
| 保存方式 | `file.chunks()` 分块写入本地 | OSS SDK 上传到云端 |
| URL 返回 | 本地相对路径（需配置静态资源） | OSS 公网绝对路径 |
| 优缺点 | ✅ 简单，无成本<br>❌ 扩展性差 | ✅ 高可用，CDN 加速<br>❌ 有费用 |

---

## 12. 违纪处理（F 表达式原子更新）

### 业务场景
学生违纪处理：违纪次数 +1，违纪扣分累加指定分数。要求操作原子性，避免并发问题。

### Django 实现

**使用 F 表达式（数据库层面原子更新）：**
```python
from django.db.models import F

@staticmethod
def violationHandle(id: int, score: int) -> None:
    """
    违纪处理 - 对标 Java StudentServiceImpl.violationHandle()
    违纪次数 +1，违纪扣分 +score
    """
    Student.objects.filter(pk=id).update(
        violation_count=F('violation_count') + 1,
        violation_score=F('violation_score') + score,
        update_time=datetime.now()
    )
```

**生成 SQL：**
```sql
UPDATE student 
SET violation_count = violation_count + 1,
    violation_score = violation_score + 10,
    update_time = '2025-12-16 09:00:00'
WHERE id = 1;
```

**为什么不能"先查后改"？**
```python
# ❌ 错误示例（存在并发问题）
student = Student.objects.get(pk=id)
student.violation_count += 1  # 线程不安全
student.violation_score += score
student.save()
```

**并发问题演示：**
```
时刻1：线程A 查询到 violation_count = 5
时刻2：线程B 查询到 violation_count = 5
时刻3：线程A 计算 5+1=6，保存
时刻4：线程B 计算 5+1=6，保存  ← 应该是7，实际是6（丢失更新）
```

### Java 对标

**MyBatis Mapper XML：**
```xml
<update id="violationHandle">
    UPDATE student
    SET violation_count = violation_count + 1,
        violation_score = violation_score + #{score},
        update_time = now()
    WHERE id = #{id}
</update>
```

**Service 层调用：**
```java
@Override
public void violationHandle(Integer id, Integer score) {
    studentMapper.violationHandle(id, score);
}
```

### 技术对比
| 维度 | Django | Java MyBatis |
|------|--------|--------------|
| 原子更新 | `F('field') + value` | SQL 表达式 `field = field + #{value}` |
| 线程安全 | ✅ 数据库层面保证 | ✅ 数据库层面保证 |
| 可读性 | ✅ Python 语法简洁 | ✅ SQL 直观 |
| 应用场景 | 计数器、库存扣减、积分累加 | 同左 |

---

## 13. 外键关联查询优化

### 业务场景
1. 操作日志列表查询，需要关联显示操作人姓名（`OperateLog.operate_emp_id` → `Emp.name`）
2. 班级人数统计，需要关联查询班级名称（`Student.clazz_id` → `Clazz.name`）

### Django 实现

**方式1：手动关联查询（当前实现）**
```python
@staticmethod
def page(page: int, pageSize: int) -> dict:
    """操作日志分页查询"""
    queryset = OperateLog.objects.all().order_by('-operate_time')
    total = queryset.count()
    logs = queryset[start:start + pageSize]
    
    # 手动关联查询员工姓名
    rows = []
    for log in logs:
        emp_name = None
        if log.operate_emp_id:
            try:
                emp = Emp.objects.get(pk=log.operate_emp_id)  # N+1 查询问题
                emp_name = emp.name
            except Emp.DoesNotExist:
                pass
        
        rows.append({
            'id': log.id,
            'operateEmpName': emp_name,
            ...
        })
    
    return {'total': total, 'rows': rows}
```

**存在的问题：N+1 查询**
- 查询10条日志 → 执行1次查询日志 + 10次查询员工 = 共11次SQL

**方式2：优化 - 使用 `select_related()`（一对一、多对一）**
```python
# 前提：OperateLog 模型需定义外键
class OperateLog(models.Model):
    operate_emp = models.ForeignKey(Emp, on_delete=models.SET_NULL, null=True)

# 优化后的查询
queryset = OperateLog.objects.select_related('operate_emp').all()
for log in queryset:
    emp_name = log.operate_emp.name if log.operate_emp else None
```

**生成 SQL（LEFT JOIN）：**
```sql
SELECT operate_log.*, emp.name 
FROM operate_log 
LEFT JOIN emp ON operate_log.operate_emp_id = emp.id;
```

**方式3：`prefetch_related()`（多对多、反向外键）**
```python
# 查询部门及其所有员工（反向外键）
depts = Dept.objects.prefetch_related('emp_set').all()
for dept in depts:
    employees = dept.emp_set.all()  # 不会触发额外查询
```

### Java 对标

**MyBatis ResultMap 关联查询：**
```xml
<resultMap id="OperateLogMap" type="com.itheima.pojo.OperateLog">
    <id property="id" column="id"/>
    <result property="operateEmpId" column="operate_emp_id"/>
    <result property="operateTime" column="operate_time"/>
    <!-- 一对一关联 -->
    <association property="operator" javaType="com.itheima.pojo.Emp">
        <result property="name" column="emp_name"/>
    </association>
</resultMap>

<select id="page" resultMap="OperateLogMap">
    SELECT ol.*, e.name AS emp_name
    FROM operate_log ol
    LEFT JOIN emp e ON ol.operate_emp_id = e.id
    ORDER BY ol.operate_time DESC
</select>
```

### 技术对比
| 维度 | Django | Java MyBatis |
|------|--------|--------------|
| 关联方式 | `select_related()` / `prefetch_related()` | `<association>` / `<collection>` |
| 一对一/多对一 | `select_related()` 生成 JOIN  | `<association>` + JOIN |
| 一对多/多对多 | `prefetch_related()` 分两次查询 | `<collection>` + JOIN |
| N+1问题 | 手动查询易触发，需主动优化 | MyBatis 易触发，需显式配置 JOIN |

---

## 总结

Django 以 **ORM 链式调用**、**装饰器** 和 **中间件** 为核心，实现了与 Java Spring + MyBatis 相似的企业级功能。本文档涵盖了从基础的 CRUD 到高级的 AOP、JWT 认证、数据聚合等13个核心技术点。

### 核心技术对比表

| 功能 | Django | Java | 相似度 |
|------|--------|------|--------|
| 事务管理 | `@transaction.atomic` | `@Transactional` | ⭐⭐⭐⭐⭐ |
| 全局异常 | `EXCEPTION_HANDLER` | `@RestControllerAdvice` | ⭐⭐⭐⭐ |
| 动态查询 | QuerySet 链式调用 | MyBatis 动态 SQL | ⭐⭐⭐⭐ |
| 分页 | 切片 `[start:end]` | PageHelper 插件 | ⭐⭐⭐⭐ |
| 批量操作 | `bulk_create()` / `filter().delete()` | MyBatis `<foreach>` | ⭐⭐⭐⭐⭐ |
| 关联查询 | `select_related()` / `prefetch_related()` | MyBatis `<association>` | ⭐⭐⭐⭐ |
| 空值处理 | `value or None` / `_parse_int()` | 包装类型 / `StringUtils` | ⭐⭐⭐ |
| AOP 日志 | `@log_operation` 装饰器 | `@Aspect` + `@Around` | ⭐⭐⭐⭐ |
| JWT 认证 | `TokenAuthMiddleware` | `TokenFilter` | ⭐⭐⭐⭐⭐ |
| 数据聚合 | `annotate(Count())` | SQL `GROUP BY` | ⭐⭐⭐⭐ |
| 文件上传 | 本地存储（`uuid` + `file.chunks()`） | 阿里云 OSS | ⭐⭐⭐ |
| 原子更新 | `F()` 表达式 | SQL 表达式 | ⭐⭐⭐⭐⭐ |
| 关联优化 | `select_related()` | MyBatis JOIN | ⭐⭐⭐⭐ |

### 设计理念一致性

两者在以下方面高度一致：
- **分层架构**：View（Controller） → Service → Model（Mapper）
- **声明式编程**：装饰器（Decorator） ≈ 注解（Annotation）
- **ORM思想**：QuerySet ≈ MyBatis 动态SQL
- **中间件/过滤器**：请求拦截、认证授权

唯一的差异在于语法和工具选择，核心设计模式相通。

