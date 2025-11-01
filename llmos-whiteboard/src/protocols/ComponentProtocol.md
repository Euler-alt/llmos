# 动态组件协议规范

## 概述
本协议定义了前端和后端之间的动态组件通信规范，支持后端配置驱动的窗口动态生成。

## 协议版本
- 版本: 1.0
- 类型: JSON over SSE/HTTP

## 数据结构

### 1. 后端配置格式
```json
{
  "version": "1.0",
  "windowConfigs": [
    {
      "id": "kernel-001",
      "type": "kernel",
      "title": "内核窗口",
      "description": "系统规则和工作流程",
      "color": "blue",
      "icon": "kernel",
      "order": 0,
      "tabs": ["meta", "state"],
      "customConfig": {
        // 组件特定的配置
      }
    },
    {
      "id": "custom-module-001",
      "type": "custom",
      "title": "自定义模块",
      "description": "业务特定功能",
      "color": "purple",
      "icon": "custom",
      "order": 1,
      "tabs": ["config", "data"],
      "customConfig": {
        "maxHeight": "500px",
        "editable": true
      }
    }
  ],
  "windows": {
    "kernel": {
      "meta": "系统核心配置...",
      "state": "当前状态..."
    },
    "custom": {
      "config": "自定义配置...",
      "data": "业务数据..."
    }
  }
}
```

### 2. 字段说明

#### 根级字段
- `version`: 协议版本号 (必需)
- `windowConfigs`: 窗口配置数组 (必需)
- `windows`: 窗口数据对象 (可选)

#### 窗口配置字段
- `id`: 窗口唯一标识符 (必需)
- `type`: 组件类型，必须在前端注册表中存在 (必需)
- `title`: 窗口显示标题 (必需)
- `description`: 窗口描述信息 (可选)
- `color`: 主题颜色 (可选，默认根据类型)
- `icon`: 图标标识 (可选)
- `order`: 显示顺序 (可选，默认按数组顺序)
- `tabs`: 支持的标签页 (可选，默认["meta", "state"])
- `customConfig`: 组件特定配置 (可选)

#### 窗口数据字段
- 键名: 对应窗口配置的 `type` 字段
- 值: 窗口的具体数据内容

### 3. 前端组件注册表

前端维护一个组件注册表，支持以下操作：

```javascript
// 注册新组件
registerComponent('custom', CustomComponent, {
  title: '自定义组件',
  color: 'purple',
  tabs: ['config', 'data']
});

// 获取组件配置
const config = getComponentConfig('kernel', backendConfig);

// 验证后端配置
const isValid = validateBackendConfig(backendConfig);
```

### 4. 通信流程

#### 初始化流程
1. 前端启动，注册内置组件
2. 前端连接后端 SSE 接口
3. 后端推送初始配置和数据
4. 前端根据配置动态渲染窗口

#### 动态更新流程
1. 后端推送新的配置数据
2. 前端验证配置有效性
3. 前端重新渲染窗口
4. 保持用户状态和编辑内容

### 5. 错误处理

#### 配置验证错误
- 未知组件类型: 显示占位符组件
- 配置格式错误: 使用默认配置
- 数据格式错误: 显示错误提示

#### 连接错误
- SSE 连接失败: 显示重连界面
- 数据解析失败: 保持上次有效状态

### 6. 向后兼容

协议支持传统数据格式，确保平滑升级：

```json
// 传统格式 (向后兼容)
{
  "kernel": { "meta": "...", "state": "..." },
  "heap": { "meta": "...", "state": "..." }
}

// 新格式 (推荐)
{
  "windowConfigs": [...],
  "windows": {...}
}
```

### 7. 扩展性设计

#### 组件类型扩展
- 支持动态注册新组件类型
- 支持组件热更新和替换

#### 配置扩展
- 支持自定义配置字段
- 支持组件特定验证规则

#### 数据扩展
- 支持复杂数据结构
- 支持实时数据流

## 示例配置

### 基础配置
```json
{
  "version": "1.0",
  "windowConfigs": [
    {
      "id": "kernel-001",
      "type": "kernel",
      "title": "系统内核",
      "order": 0
    },
    {
      "id": "heap-001", 
      "type": "heap",
      "title": "持久化存储",
      "order": 1
    }
  ],
  "windows": {
    "kernel": {
      "meta": "系统规则定义...",
      "state": "运行状态..."
    },
    "heap": {
      "meta": "存储配置...", 
      "state": "当前数据..."
    }
  }
}
```

### 高级配置
```json
{
  "version": "1.0",
  "windowConfigs": [
    {
      "id": "ai-agent-001",
      "type": "ai-agent",
      "title": "AI代理管理",
      "description": "管理和配置AI代理实例",
      "color": "indigo",
      "icon": "robot",
      "order": 2,
      "tabs": ["agents", "tasks", "logs"],
      "customConfig": {
        "maxAgents": 10,
        "autoStart": true
      }
    }
  ],
  "windows": {
    "ai-agent": {
      "agents": ["agent1", "agent2"],
      "tasks": ["task1", "task2"],
      "logs": "运行日志..."
    }
  }
}
```

## 实施建议

1. **渐进式迁移**: 从传统格式逐步迁移到新格式
2. **配置验证**: 实施严格的配置验证机制
3. **错误恢复**: 设计完善的错误恢复策略
4. **性能优化**: 考虑大规模配置的性能影响
5. **安全考虑**: 验证配置来源的安全性