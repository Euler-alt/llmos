# 动态组件协议 - 使用指南

## 概述

本协议实现了前端动态组件加载系统，支持后端配置驱动的窗口动态生成。解决了硬编码窗口管理的问题，提供了灵活的扩展能力。

## 核心特性

### 🚀 动态配置
- 后端可动态配置前端窗口布局
- 支持运行时组件注册和替换
- 配置驱动的界面生成

### 🔄 向后兼容
- 支持传统数据格式平滑迁移
- 自动检测和转换配置格式
- 保持现有功能完整性

### 🎨 灵活扩展
- 支持自定义组件类型
- 可配置的主题和样式
- 动态标签页管理

## 快速开始

### 1. 基本使用

```javascript
// App.js - 使用动态窗口工厂
import DynamicWindowFactory from './components/DynamicWindowFactory';

// 替换硬编码的窗口渲染
<DynamicWindowFactory
  windowConfigs={windowConfigs}  // 后端配置的窗口列表
  windowsData={windows}          // 窗口数据
  onUpdate={handleUpdate}        // 更新回调
  darkMode={darkMode}            // 主题模式
/>
```

### 2. 后端配置格式

#### 传统格式 (向后兼容)
```json
{
  "kernel": { "meta": "...", "state": "..." },
  "heap": { "meta": "...", "state": "..." }
}
```

#### 新协议格式 (推荐)
```json
{
  "version": "1.0",
  "windowConfigs": [
    {
      "id": "kernel-001",
      "type": "kernel",
      "title": "系统内核",
      "description": "核心系统规则",
      "color": "blue",
      "order": 0,
      "tabs": ["meta", "state"]
    }
  ],
  "windows": {
    "kernel": {
      "meta": "系统规则...",
      "state": "运行状态..."
    }
  }
}
```

### 3. 注册自定义组件

```javascript
import { registerComponent } from './components/ComponentRegistry';

// 注册新组件类型
registerComponent('custom-analytics', CustomAnalyticsComponent, {
  title: '数据分析',
  color: 'purple',
  tabs: ['dashboard', 'metrics']
});
```

## 组件注册表

### 内置组件类型
- `kernel` - 内核窗口
- `heap` - 堆窗口  
- `stack` - 栈窗口
- `code` - 代码窗口

### 注册表 API

```javascript
import { 
  registerComponent,
  getComponent,
  getComponentConfig,
  getAvailableComponentTypes,
  validateBackendConfig
} from './components/ComponentRegistry';

// 注册新组件
registerComponent('type', Component, config);

// 获取组件
const Component = getComponent('type');

// 获取配置
const config = getComponentConfig('type', backendConfig);

// 验证配置
const isValid = validateBackendConfig(backendConfig);
```

## 后端集成

### SSE 数据格式

后端通过 SSE 推送配置和数据：

```javascript
// 事件数据格式
{
  "version": "1.0",
  "windowConfigs": [...],
  "windows": {...}
}
```

### API 端点
- `GET /api/sse` - SSE 实时数据流
- `GET /api/config` - 获取当前配置
- `POST /api/modules/update` - 更新模块数据

## 配置验证

### 必需字段
- `windowConfigs` - 窗口配置数组
- 每个配置需要 `id` 和 `type` 字段
- `type` 必须在前端注册表中存在

### 错误处理
- 未知组件类型：显示占位符
- 配置格式错误：使用默认配置
- 数据解析失败：保持上次状态

## 主题和样式

### 颜色主题
每个组件类型支持自定义颜色主题：
- `blue` - 内核窗口
- `green` - 堆窗口
- `yellow` - 栈窗口  
- `red` - 代码窗口
- `purple` - 自定义组件

### 暗黑模式
自动支持暗黑模式，组件会根据主题自动适配样式。

## 扩展开发

### 创建自定义组件

```javascript
const CustomComponent = ({ data, onUpdate, darkMode }) => {
  // 接收配置信息
  const { config } = data || {};
  
  return (
    <div className={/* 使用配置的颜色主题 */}>
      {/* 组件内容 */}
    </div>
  );
};

// 注册组件
registerComponent('custom', CustomComponent, {
  title: '自定义组件',
  color: 'indigo',
  tabs: ['tab1', 'tab2']
});
```

### 配置驱动开发
组件应该：
1. 接收 `data` 包含配置和内容
2. 使用配置中的主题颜色
3. 支持动态标签页
4. 处理配置变化

## 演示和测试

### 运行演示
```bash
# 启动演示（如果配置了演示路由）
npm start
```

访问演示页面查看不同配置模式的效果。

### 测试用例
参考 `src/protocols/BackendIntegrationExample.js` 中的测试用例：

```javascript
import { integrationTestCases } from './protocols/BackendIntegrationExample';

// 运行配置验证测试
integrationTestCases.forEach(testCase => {
  const result = validateBackendConfig(testCase.input);
  console.log(`${testCase.name}:`, result === testCase.expected.shouldRender);
});
```

## 迁移指南

### 从传统格式迁移

1. **阶段一：兼容模式**
   - 后端继续使用传统格式
   - 前端自动检测并转换
   - 功能保持不变

2. **阶段二：混合模式**  
   - 后端开始提供新格式配置
   - 前端支持两种格式
   - 逐步测试新功能

3. **阶段三：新协议模式**
   - 完全切换到新协议格式
   - 利用动态配置能力
   - 支持自定义组件

### 配置文件示例

```json
{
  "version": "1.0",
  "windowConfigs": [
    {
      "id": "kernel-001",
      "type": "kernel",
      "title": "系统内核",
      "description": "核心系统规则和工作流程",
      "color": "blue",
      "order": 0,
      "tabs": ["meta", "state"],
      "customConfig": {
        "maxHeight": "600px",
        "collapsible": true
      }
    },
    {
      "id": "custom-module-001", 
      "type": "custom-analytics",
      "title": "数据分析",
      "color": "purple",
      "order": 1,
      "tabs": ["dashboard", "metrics", "reports"]
    }
  ],
  "windows": {
    "kernel": {
      "meta": "系统规则定义...",
      "state": "运行状态..."
    },
    "custom-analytics": {
      "dashboard": "仪表板数据...",
      "metrics": "指标数据...",
      "reports": "分析报告..."
    }
  }
}
```

## 故障排除

### 常见问题

1. **组件不显示**
   - 检查组件类型是否注册
   - 验证配置格式是否正确
   - 查看浏览器控制台错误

2. **配置不生效**
   - 确认后端推送了正确格式
   - 检查配置验证结果
   - 验证网络连接

3. **样式异常**
   - 检查颜色主题配置
   - 确认暗黑模式支持
   - 验证 CSS 类名正确性

### 调试工具

使用浏览器开发者工具：
- 查看 Network 标签的 SSE 连接
- 检查 Console 的错误信息
- 使用 React DevTools 查看组件状态

## 性能优化

### 配置优化
- 避免过大的配置数据
- 使用增量更新策略
- 缓存常用配置

### 组件优化  
- 实现 shouldComponentUpdate
- 使用 React.memo 包装组件
- 避免不必要的重渲染

## 安全考虑

### 配置安全
- 验证配置来源可信性
- 限制配置数据大小
- 实施输入验证和清理

### 组件安全
- 只加载可信组件
- 实施代码签名验证
- 限制组件权限

## 版本历史

### v1.0.0
- 初始版本发布
- 支持动态组件注册
- 向后兼容传统格式
- 配置驱动界面生成

## 支持与贡献

如有问题或建议，请：
1. 查看演示代码示例
2. 参考协议文档
3. 提交 Issue 或 PR

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。