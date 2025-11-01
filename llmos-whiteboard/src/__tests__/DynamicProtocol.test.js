/**
 * 动态组件协议测试
 * 单元测试和集成测试
 */

import { validateBackendConfig, getAvailableComponentTypes, registerComponent } from '../components/ComponentRegistry';
import { validateProtocolImplementation } from '../utils/ProtocolValidator';

// 模拟测试组件
const TestComponent = () => <div>测试组件</div>;

describe('动态组件协议', () => {
  describe('组件注册表', () => {
    test('应该包含基础组件类型', () => {
      const types = getAvailableComponentTypes();
      expect(types).toContain('kernel');
      expect(types).toContain('heap');
      expect(types).toContain('stack');
      expect(types).toContain('code');
    });

    test('应该支持动态注册新组件', () => {
      registerComponent('test-component', TestComponent, {
        title: '测试组件',
        color: 'test'
      });
      
      const types = getAvailableComponentTypes();
      expect(types).toContain('test-component');
    });
  });

  describe('配置验证', () => {
    test('应该验证有效配置', () => {
      const validConfig = {
        version: '1.0',
        windowConfigs: [
          { id: 'test-1', type: 'kernel' },
          { id: 'test-2', type: 'heap' }
        ]
      };
      
      expect(validateBackendConfig(validConfig)).toBe(true);
    });

    test('应该拒绝无效配置', () => {
      const invalidConfig = {
        version: '1.0',
        windowConfigs: [
          { id: 'test-1', type: 'unknown-type' }
        ]
      };
      
      expect(validateBackendConfig(invalidConfig)).toBe(false);
    });

    test('应该支持传统格式配置', () => {
      const legacyConfig = {
        kernel: { meta: 'test' },
        heap: { meta: 'test' }
      };
      
      expect(validateBackendConfig(legacyConfig)).toBe(true);
    });
  });

  describe('协议完整性', () => {
    test('完整协议验证应该通过', () => {
      const result = validateProtocolImplementation();
      expect(result.passed).toBe(true);
    });

    test('应该处理错误配置', () => {
      // 测试空配置
      expect(validateBackendConfig(null)).toBe(false);
      
      // 测试未定义配置
      expect(validateBackendConfig(undefined)).toBe(false);
      
      // 测试无效JSON
      expect(validateBackendConfig('invalid-json')).toBe(false);
    });
  });

  describe('数据流测试', () => {
    test('应该正确处理配置数据流', () => {
      const testData = {
        version: '1.0',
        windowConfigs: [
          {
            id: 'kernel-001',
            type: 'kernel',
            title: '测试内核',
            order: 0
          }
        ],
        windows: {
          kernel: {
            meta: '测试数据',
            state: '测试状态'
          }
        }
      };
      
      const isValid = validateBackendConfig(testData);
      expect(isValid).toBe(true);
      
      // 验证数据结构
      expect(testData.windowConfigs).toHaveLength(1);
      expect(testData.windowConfigs[0].type).toBe('kernel');
      expect(testData.windows.kernel).toBeDefined();
    });
  });
});

// 集成测试示例
describe('集成测试', () => {
  test('端到端配置处理', () => {
    // 模拟后端配置
    const backendConfig = {
      version: '1.0',
      windowConfigs: [
        {
          id: 'kernel-001',
          type: 'kernel',
          title: '系统内核',
          order: 0
        },
        {
          id: 'heap-001',
          type: 'heap',
          title: '持久化存储',
          order: 1
        }
      ],
      windows: {
        kernel: {
          meta: '系统规则...',
          state: '运行状态...'
        },
        heap: {
          meta: '存储配置...',
          state: '存储数据...'
        }
      }
    };
    
    // 验证配置
    const isValid = validateBackendConfig(backendConfig);
    expect(isValid).toBe(true);
    
    // 验证组件类型
    const availableTypes = getAvailableComponentTypes();
    backendConfig.windowConfigs.forEach(config => {
      expect(availableTypes).toContain(config.type);
    });
    
    // 验证数据完整性
    backendConfig.windowConfigs.forEach(config => {
      expect(backendConfig.windows[config.type]).toBeDefined();
    });
  });
});

// 性能测试
describe('性能测试', () => {
  test('配置验证性能', () => {
    const largeConfig = {
      version: '1.0',
      windowConfigs: Array.from({ length: 100 }, (_, i) => ({
        id: `window-${i}`,
        type: i % 4 === 0 ? 'kernel' : 
              i % 4 === 1 ? 'heap' : 
              i % 4 === 2 ? 'stack' : 'code',
        title: `窗口 ${i}`,
        order: i
      })),
      windows: {
        kernel: { meta: 'test', state: 'test' },
        heap: { meta: 'test', state: 'test' },
        stack: { meta: 'test', state: 'test' },
        code: { meta: 'test', state: 'test' }
      }
    };
    
    const startTime = performance.now();
    const isValid = validateBackendConfig(largeConfig);
    const endTime = performance.now();
    
    expect(isValid).toBe(true);
    expect(endTime - startTime).toBeLessThan(100); // 应该在100ms内完成
  });
});

export {
  validateProtocolImplementation
};