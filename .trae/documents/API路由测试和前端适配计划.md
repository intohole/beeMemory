# API路由测试和前端适配计划

## 1. API路由测试

### 测试目标
测试所有API路由，确保它们都能正常工作，返回预期的结果。

### 测试方法
使用curl命令测试每个API路由，验证其功能和响应格式。

### 测试范围

#### 核心功能
- ✅ 提交聊天历史：`POST /api/memory/submit`
- ✅ 查询相似记忆：`POST /api/memory/query`
- ✅ 删除记忆：`DELETE /api/memory/{memory_id}`
- ✅ 获取记忆列表：`GET /api/memory/list?user_id=xxx&app_name=xxx`

#### 配置管理
- ✅ 获取所有应用配置：`GET /api/memory/app/config`
- ✅ 获取单个应用配置：`GET /api/memory/app/config?app_name=xxx`
- ✅ 更新应用配置：`PUT /api/memory/app/config?app_name=xxx`
- ✅ 获取记忆配置：`GET /api/memory/config?user_id=xxx&app_name=xxx`
- ✅ 更新记忆配置：`PUT /api/memory/config?user_id=xxx&app_name=xxx`
- ✅ 获取用户应用配置：`GET /api/memory/user/app/config?user_id=xxx&app_name=xxx`
- ✅ 更新用户应用配置：`PUT /api/memory/user/app/config?user_id=xxx&app_name=xxx`

#### 模板管理
- ❌ 获取模板列表：`GET /api/memory/templates`
- ❌ 获取单个模板：`GET /api/memory/templates/{template_id}`
- ❌ 创建模板：`POST /api/memory/templates`
- ❌ 更新模板：`PUT /api/memory/templates/{template_id}`
- ❌ 删除模板：`DELETE /api/memory/templates/{template_id}`

#### 优先级管理
- ❌ 获取优先级列表：`GET /api/memory/priorities`
- ❌ 获取单个优先级：`GET /api/memory/priorities/{priority_id}`
- ❌ 创建优先级：`POST /api/memory/priorities`
- ❌ 更新优先级：`PUT /api/memory/priorities/{priority_id}`
- ❌ 删除优先级：`DELETE /api/memory/priorities/{priority_id}`

#### 手动管理
- ❌ 归档记忆：`PUT /api/memory/archive?memory_id=xxx`
- ❌ 取消归档记忆：`PUT /api/memory/unarchive?memory_id=xxx`
- ❌ 更新记忆优先级：`PUT /api/memory/priority?memory_id=xxx&priority_level=xxx`
- ❌ 更新记忆标签：`PUT /api/memory/tags?memory_id=xxx&tags=xxx`
- ❌ 获取记忆评分：`GET /api/memory/score/{memory_id}`

## 2. 前端适配检查

### 检查目标
检查前端代码是否适配所有API路由，特别是手动管理相关的路由。

### 检查范围

#### 已实现的前端功能
- ✅ 提交聊天历史（submit.js）
- ✅ 查询相似记忆（query.js）
- ✅ 管理记忆列表和删除记忆（manage.js）
- ✅ 配置管理（config.js）

#### 待适配的前端功能
- ❌ 记忆归档功能
- ❌ 记忆标签管理功能
- ❌ 记忆优先级调整功能
- ❌ 记忆评分查看功能

### 适配方法
更新`manage.js`文件，添加对新API路由的支持，包括：
- 归档/取消归档记忆
- 更新记忆标签
- 更新记忆优先级
- 查看记忆评分

## 3. 代码提交

### 提交目标
将所有更改提交到git仓库，包括API测试结果和前端适配代码。

### 提交内容
- API测试结果
- 前端适配代码
- 任何必要的修复和优化

## 4. 测试和适配步骤

1. 测试所有API路由，记录测试结果
2. 检查前端代码，识别需要适配的功能
3. 更新前端代码，添加对新API路由的支持
4. 测试前端功能，确保它们能正常工作
5. 将所有更改提交到git仓库

## 5. 预期结果

- 所有API路由都能正常工作
- 前端代码适配所有API路由
- 代码成功提交到git仓库