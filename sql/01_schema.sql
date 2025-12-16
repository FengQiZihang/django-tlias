-- 创建数据库
create database if not exists tlias default charset utf8mb4 collate utf8mb4_general_ci;
-- 使用数据库
use tlias;

-- 删除已有表（注意顺序：先删子表再删父表）
drop table if exists emp;
drop table if exists dept;
drop table if exists emp_expr;
drop table if exists emp_log;
drop table if exists clazz;
drop table if exists student;
drop table if exists operate_log;
drop table if exists emp_login_log;

-- 部门表
create table dept (
                      id int unsigned primary key auto_increment comment 'ID, 主键',
                      name varchar(10) not null unique comment '部门名称',
                      create_time datetime default null comment '创建时间',
                      update_time datetime default null comment '修改时间'
) comment '部门表';

-- 员工表
create table emp(
                    id int unsigned primary key auto_increment comment 'ID,主键',
                    username varchar(20) not null unique comment '用户名',
                    password varchar(32) comment '密码(默认为123456)',
                    name varchar(10) not null comment '姓名',
                    gender tinyint unsigned not null comment '性别, 1:男, 2:女',
                    phone char(11) not null unique comment '手机号',
                    job tinyint unsigned comment '职位, 1 班主任, 2 讲师 , 3 学工主管, 4 教研主管, 5 咨询师',
                    salary int unsigned comment '薪资',
                    image varchar(255) comment '头像',
                    entry_date date comment '入职日期',
                    dept_id int unsigned comment '部门ID',
                    create_time datetime comment '创建时间',
                    update_time datetime comment '修改时间'
) comment '员工表';

-- 员工工作经历信息
create table emp_expr(
                         id int unsigned primary key auto_increment comment 'ID, 主键',
                         emp_id int unsigned comment '员工ID',
                         begin date comment '开始时间',
                         end  date comment '结束时间',
                         company varchar(50) comment '公司名称',
                         job varchar(50) comment '职位'
)comment '工作经历';

-- 创建员工日志表
create table emp_log(
                        id int unsigned primary key auto_increment comment 'ID, 主键',
                        operate_time datetime comment '操作时间',
                        info varchar(2000) comment '日志信息'
) comment '员工日志表';

-- 创建班级表
create table clazz(
                      id   int unsigned primary key auto_increment comment 'ID,主键',
                      name  varchar(30) not null unique  comment '班级名称',
                      room  varchar(20) comment '班级教室',
                      begin_date date not null comment '开课时间',
                      end_date date not null comment '结课时间',
                      master_id int unsigned null comment '班主任ID, 关联员工表ID',
                      subject tinyint unsigned not null comment '学科, 1:java, 2:前端, 3:大数据, 4:Python, 5:Go, 6: 嵌入式',
                      create_time datetime  comment '创建时间',
                      update_time datetime  comment '修改时间'
)comment '班级表';

-- 创建学员表
create table student(
                        id int unsigned primary key auto_increment comment 'ID,主键',
                        name varchar(10)  not null comment '姓名',
                        no char(10)  not null unique comment '学号',
                        gender tinyint unsigned  not null comment '性别, 1: 男, 2: 女',
                        phone  varchar(11)  not null unique comment '手机号',
                        id_card  char(18)  not null unique comment '身份证号',
                        is_college tinyint unsigned  not null comment '是否来自于院校, 1:是, 0:否',
                        address  varchar(100)  comment '联系地址',
                        degree  tinyint unsigned  comment '最高学历, 1:初中, 2:高中, 3:大专, 4:本科, 5:硕士, 6:博士',
                        graduation_date date comment '毕业时间',
                        clazz_id  int unsigned not null comment '班级ID, 关联班级表ID',
                        violation_count tinyint unsigned default '0' not null comment '违纪次数',
                        violation_score tinyint unsigned default '0' not null comment '违纪扣分',
                        create_time  datetime  comment '创建时间',
                        update_time  datetime  comment '修改时间'
) comment '学员表';

-- 操作日志表
create table operate_log(
                            id int unsigned primary key auto_increment comment 'ID',
                            operate_emp_id int unsigned comment '操作人ID',
                            operate_time datetime comment '操作时间',
                            class_name varchar(100) comment '操作的类名',
                            method_name varchar(100) comment '操作的方法名',
                            method_params varchar(2000) comment '方法参数',
                            return_value varchar(2000) comment '返回值',
                            cost_time bigint unsigned comment '方法执行耗时, 单位:ms'
) comment '操作日志表';

-- 登录日志表
create table emp_login_log(
                              id int unsigned primary key auto_increment comment 'ID',
                              username varchar(20) comment '用户名',
                              password varchar(32) comment '密码',
                              login_time datetime comment '登录时间',
                              is_success tinyint unsigned comment '是否成功, 1:成功, 0:失败',
                              jwt varchar(1000) comment 'JWT令牌',
                              cost_time bigint unsigned comment '耗时, 单位:ms'
) comment '登录日志表';
