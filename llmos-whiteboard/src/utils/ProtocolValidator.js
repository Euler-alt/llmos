/**
 * 动态组件协议验证器
 * 用于测试和验证协议实现
 */

import { validateBackendConfig, getAvailableComponentTypes } from '../components/ComponentRegistry';

/**
 * 验证协议实现
 */
export const validateProtocolImplementation = () => {
  const results = {
    componentRegistry: validateComponentRegistry(),
    configValidation: validateConfigValidation(),
    dataFlow: validateDataFlow(),
    errorHandling: validateErrorHandling()
  };
  
  const allPassed = Object.values(results).every(result => result.passed);
  
  return {
    passed: allPassed,
    results,
    summary: allPassed ? '✅ 协议实现验证通过' : '❌ 协议实现存在问题'
  };
};

/**
 * 验证组件注册表
 */
const validateComponentRegistry = () => {
  const availableTypes = getAvailableComponentTypes();
  const expectedTypes = ['kernel', 'heap', 'stack', 'code'];
  
  const missingTypes = expectedTypes.filter(type => !availableTypes.includes(type));
  const extraTypes = availableTypes.filter(type => !expectedTypes.includes(type));
  
  const passed = missingTypes.length === 0;
  
  return {
    passed,
    message: passed 
      ? '✅ 组件注册表正常' 
      : `❌ 组件注册表异常: 缺少类型 ${missingTypes.join(', ')}`,
    details: {
      availableTypes,
      expectedTypes,
      missingTypes,
      extraTypes
    }
  };
};

/**
 * 验证配置验证功能
 */
const validateConfigValidation = () => {
  const testCases = [
    {
      name: '有效配置',
      config: {
        version: '1.0',
        windowConfigs: [
          { id: 'test-1', type: 'kernel' },
          { id: 'test-2', type: 'heap' }
        ]
      },
      expected: true
    },
    {
      name: '无效配置 - 缺少windowConfigs',
      config: {
        version: '1.0',
        windows: { kernel: {} }
      },
      expected: false
    },
    {
      name: '无效配置 - 未知组件类型',
      config: {
        version: '1.0',
        windowConfigs: [
          { id: 'test-1', type: 'unknown-type' }
        ]
      },
      expected: false
    },
    {
      name: '传统格式配置',
      config: {
        kernel: { meta: 'test' },
        heap: { meta: 'test' }
      },
      expected: true
    }
  ];
  
  const results = testCases.map(testCase => {
    const isValid = validateBackendConfig(testCase.config);
    const passed = isValid === testCase.expected;
    
    return {
      name: testCase.name,
      passed,
      expected: testCase.expected,
      actual: isValid
    };
  });
  
  const allPassed = results.every(result => result.passed);
  
  return {
    passed: allPassed,
    message: allPassed ? '✅ 配置验证正常' : '❌ 配置验证异常',
    details: {
      testCases: results
    }
  };
};

/**
 * 验证数据流
 */
const validateDataFlow = () => {
  // 模拟数据流测试
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
        meta: '测试元数据',
        state: '测试状态数据'
      }
    }
  };
  
  try {
    // 验证配置
    const isValid = validateBackendConfig(testData);
    
    // 验证数据结构
    const hasRequiredFields = testData.windowConfigs && 
                              testData.windowConfigs.every(wc => wc.id && wc.type);
    
    const passed = isValid && hasRequiredFields;
    
    return {
      passed,
      message: passed ? '✅ 数据流正常' : '❌ 数据流异常',
      details: {
        configValid: isValid,
        structureValid: hasRequiredFields,
        testData
      }
    };
  } catch (error) {
    return {
      passed: false,
      message: '❌ 数据流验证出错',
      details: {
        error: error.message
      }
    };
  }
};

/**
 * 验证错误处理
 */
const validateErrorHandling = () => {
  const testCases = [
    {
      name: '空配置',
      config: null,
      shouldHandle: true
    },
    {
      name: '无效JSON',
      config: 'invalid-json',
      shouldHandle: true
    },
    {
      name: '未定义配置',
      config: undefined,
      shouldHandle: true
    }
  ];
  
  const results = testCases.map(testCase => {
    try {
      const isValid = validateBackendConfig(testCase.config);
      // 对于无效配置，应该返回false而不是抛出错误
      const passed = isValid === false;
      
      return {
        name: testCase.name,
        passed,
        handled: true
      };
    } catch (error) {
      return {
        name: testCase.name,
        passed: false,
        handled: false,
        error: error.message
      };
    }
  });
  
  const allPassed = results.every(result => result.passed);
  const allHandled = results.every(result => result.handled !== false);
  
  return {
    passed: allPassed && allHandled,
    message: allPassed && allHandled ? '✅ 错误处理正常' : '❌ 错误处理异常',
    details: {
      testResults: results
    }
  };
};

/**
 * 运行完整验证
 */
export const runFullValidation = () => {
  console.log('🚀 开始动态组件协议验证...\n');
  
  const validationResult = validateProtocolImplementation();
  
  console.log('📊 验证结果:');
  console.log(`总体状态: ${validationResult.summary}\n`);
  
  Object.entries(validationResult.results).forEach(([category, result]) => {
    console.log(`${category}: ${result.message}`);
    if (!result.passed && result.details) {
      console.log('详细信息:', JSON.stringify(result.details, null, 2));
    }
    console.log('');
  });
  
  if (validationResult.passed) {
    console.log('🎉 所有验证通过！动态组件协议实现正确。');
  } else {
    console.log('⚠️ 发现一些问题，请检查上述详细信息。');
  }
  
  return validationResult;
};

// 如果直接运行此文件，执行验证
if (typeof window !== 'undefined' && window.location.pathname.includes('test')) {
  runFullValidation();
}

export default {
  validateProtocolImplementation,
  runFullValidation
};