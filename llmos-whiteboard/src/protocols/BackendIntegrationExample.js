/**
 * 后端集成示例
 * 演示如何与后端配合实现动态组件协议
 */

/**
 * 模拟后端SSE数据流
 * 后端应该按照这个格式推送数据
 */
export const mockBackendSSEData = {
  // 传统格式 (向后兼容)
  legacyFormat: {
    kernel: {
      meta: '系统核心规则配置',
      state: '当前运行状态'
    },
    heap: {
      meta: '持久化存储配置', 
      state: '存储数据内容'
    },
    stack: {
      meta: '临时工作区配置',
      state: '当前任务栈'
    },
    code: {
      meta: '代码模块配置',
      state: '可执行代码'
    }
  },
  
  // 新协议格式 (推荐)
  protocolFormat: {
    version: '1.0',
    windowConfigs: [
      {
        id: 'kernel-001',
        type: 'kernel',
        title: '系统内核',
        description: '核心系统规则和工作流程',
        color: 'blue',
        icon: 'kernel',
        order: 0,
        tabs: ['meta', 'state']
      },
      {
        id: 'heap-001',
        type: 'heap', 
        title: '持久化存储',
        description: '跨会话数据持久化',
        color: 'green',
        icon: 'heap',
        order: 1,
        tabs: ['meta', 'state']
      },
      {
        id: 'stack-001',
        type: 'stack',
        title: '任务栈',
        description: '临时工作区域管理',
        color: 'yellow',
        icon: 'stack',
        order: 2,
        tabs: ['meta', 'state']
      },
      {
        id: 'code-001',
        type: 'code',
        title: '代码执行',
        description: '可执行代码模块',
        color: 'red',
        icon: 'code',
        order: 3,
        tabs: ['meta', 'state']
      }
    ],
    windows: {
      kernel: {
        meta: '系统核心规则配置',
        state: '当前运行状态'
      },
      heap: {
        meta: '持久化存储配置',
        state: '存储数据内容'
      },
      stack: {
        meta: '临时工作区配置',
        state: '当前任务栈'
      },
      code: {
        meta: '代码模块配置',
        state: '可执行代码'
      }
    }
  },
  
  // 动态扩展示例
  dynamicExtension: {
    version: '1.0',
    windowConfigs: [
      {
        id: 'kernel-001',
        type: 'kernel',
        title: '系统内核',
        order: 0
      },
      {
        id: 'custom-module-001',
        type: 'custom-analytics',
        title: '数据分析面板',
        description: '实时数据分析和可视化',
        color: 'purple',
        icon: 'analytics',
        order: 1,
        tabs: ['dashboard', 'metrics', 'reports'],
        customConfig: {
          refreshInterval: 5000,
          maxDataPoints: 1000
        }
      },
      {
        id: 'custom-module-002',
        type: 'workflow-editor',
        title: '工作流编辑器',
        description: '可视化工作流设计',
        color: 'indigo',
        icon: 'workflow',
        order: 2,
        tabs: ['designer', 'preview', 'settings'],
        customConfig: {
          snapToGrid: true,
          autoSave: true
        }
      }
    ],
    windows: {
      kernel: {
        meta: '系统核心规则',
        state: '运行状态'
      },
      'custom-analytics': {
        dashboard: '数据分析仪表板',
        metrics: '关键指标数据',
        reports: '分析报告'
      },
      'workflow-editor': {
        designer: '工作流设计界面',
        preview: '预览模式',
        settings: '编辑器设置'
      }
    }
  }
};

/**
 * 后端API接口规范
 */
export const backendAPISpecification = {
  // SSE端点 - 实时数据推送
  sse: {
    endpoint: '/api/sse',
    method: 'GET',
    description: '服务器发送事件端点，用于实时推送配置和数据',
    headers: {
      'Accept': 'text/event-stream',
      'Cache-Control': 'no-cache'
    },
    events: {
      'message': '配置和数据更新事件',
      'error': '连接错误事件'
    }
  },
  
  // 配置获取端点
  config: {
    endpoint: '/api/config',
    method: 'GET',
    description: '获取当前窗口配置',
    response: {
      type: 'object',
      properties: {
        version: { type: 'string' },
        windowConfigs: { type: 'array' },
        windows: { type: 'object' }
      }
    }
  },
  
  // 数据更新端点
  update: {
    endpoint: '/api/modules/update',
    method: 'POST',
    description: '更新模块数据',
    request: {
      type: 'object',
      properties: {
        moduleName: { type: 'string' },
        newData: { type: 'object' }
      }
    },
    response: {
      type: 'object',
      properties: {
        success: { type: 'boolean' },
        message: { type: 'string' }
      }
    }
  }
};

/**
 * 后端集成测试用例
 */
export const integrationTestCases = [
  {
    name: '基础配置测试',
    description: '测试传统格式和新协议的兼容性',
    input: mockBackendSSEData.legacyFormat,
    expected: {
      shouldRender: true,
      windowCount: 4,
      components: ['kernel', 'heap', 'stack', 'code']
    }
  },
  {
    name: '协议格式测试',
    description: '测试新协议格式的正确解析',
    input: mockBackendSSEData.protocolFormat,
    expected: {
      shouldRender: true,
      windowCount: 4,
      hasConfig: true,
      components: ['kernel', 'heap', 'stack', 'code']
    }
  },
  {
    name: '动态扩展测试',
    description: '测试自定义组件的动态加载',
    input: mockBackendSSEData.dynamicExtension,
    expected: {
      shouldRender: true,
      windowCount: 3,
      hasCustomComponents: true,
      components: ['kernel', 'custom-analytics', 'workflow-editor']
    }
  },
  {
    name: '错误配置测试',
    description: '测试无效配置的错误处理',
    input: {
      windowConfigs: [
        {
          id: 'invalid-001',
          type: 'unknown-component', // 未知组件类型
          title: '无效组件'
        }
      ]
    },
    expected: {
      shouldRender: true,
      hasFallback: true,
      errorHandled: true
    }
  }
];

/**
 * 后端集成助手函数
 */
export const backendIntegrationHelpers = {
  /**
   * 验证后端配置格式
   */
  validateConfig: (config) => {
    if (!config) return false;
    
    // 检查传统格式
    if (typeof config === 'object' && !config.version) {
      const validKeys = ['kernel', 'heap', 'stack', 'code'];
      return Object.keys(config).some(key => validKeys.includes(key));
    }
    
    // 检查新协议格式
    if (config.version && config.windowConfigs) {
      return Array.isArray(config.windowConfigs) && 
             config.windowConfigs.every(wc => wc.id && wc.type);
    }
    
    return false;
  },
  
  /**
   * 标准化配置格式
   */
  normalizeConfig: (config) => {
    if (!config) return null;
    
    // 如果是传统格式，转换为新协议格式
    if (typeof config === 'object' && !config.version) {
      const windowConfigs = Object.keys(config).map((type, index) => ({
        id: `${type}-${index}`,
        type: type,
        title: type.charAt(0).toUpperCase() + type.slice(1),
        order: index
      }));
      
      return {
        version: '1.0',
        windowConfigs,
        windows: config
      };
    }
    
    return config;
  },
  
  /**
   * 生成测试配置
   */
  generateTestConfig: (components = ['kernel', 'heap', 'stack', 'code']) => {
    return {
      version: '1.0',
      windowConfigs: components.map((type, index) => ({
        id: `${type}-${Date.now()}`,
        type: type,
        title: type.charAt(0).toUpperCase() + type.slice(1),
        order: index,
        tabs: ['meta', 'state']
      })),
      windows: components.reduce((acc, type) => {
        acc[type] = {
          meta: `${type} 配置信息`,
          state: `${type} 当前状态`
        };
        return acc;
      }, {})
    };
  }
};

export default {
  mockBackendSSEData,
  backendAPISpecification,
  integrationTestCases,
  backendIntegrationHelpers
};