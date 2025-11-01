import React, { useState, useEffect } from 'react';

const SystemMonitor = ({ darkMode }) => {
  const [systemStats, setSystemStats] = useState({
    cpu: 0,
    memory: 0,
    requests: 0,
    uptime: 0,
    latency: 0,
    activeConnections: 0
  });
  
  const [logs, setLogs] = useState([]);
  
  // 模拟获取系统数据
  useEffect(() => {
    // 初始化数据
    setSystemStats({
      cpu: Math.floor(Math.random() * 30) + 10,
      memory: Math.floor(Math.random() * 40) + 30,
      requests: Math.floor(Math.random() * 100) + 50,
      uptime: Math.floor(Math.random() * 24) + 1,
      latency: Math.floor(Math.random() * 200) + 50,
      activeConnections: Math.floor(Math.random() * 10) + 1
    });
    
    setLogs([
      { time: '2025-09-28 18:45:23', level: 'info', message: '系统启动成功' },
      { time: '2025-09-28 18:46:05', level: 'info', message: '连接到LLM服务' },
      { time: '2025-09-28 18:50:12', level: 'warning', message: '响应时间超过阈值 (350ms)' },
      { time: '2025-09-28 18:55:30', level: 'error', message: 'API调用失败: 连接超时' },
      { time: '2025-09-28 19:00:01', level: 'info', message: '自动保存状态成功' }
    ]);
    
    // 模拟数据更新
    const interval = setInterval(() => {
      setSystemStats(prev => ({
        cpu: Math.min(100, Math.max(0, prev.cpu + (Math.random() * 10 - 5))),
        memory: Math.min(100, Math.max(0, prev.memory + (Math.random() * 8 - 4))),
        requests: prev.requests + Math.floor(Math.random() * 5),
        uptime: prev.uptime + 1/60, // 每分钟增加
        latency: Math.max(10, prev.latency + (Math.random() * 40 - 20)),
        activeConnections: Math.max(1, Math.min(20, prev.activeConnections + (Math.random() > 0.7 ? 1 : -1)))
      }));
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* 系统状态卡片 */}
      <div className={`col-span-2 rounded-lg p-6 ${darkMode ? 'bg-gray-800 text-gray-300' : 'bg-white text-gray-700'} shadow-lg transition-colors duration-300`}>
        <h3 className="text-xl font-semibold mb-4">系统状态</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* CPU使用率 */}
          <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">CPU使用率</span>
              <span className={`${getCpuColor(systemStats.cpu)}`}>{systemStats.cpu.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-300 rounded-full h-2.5">
              <div 
                className={`h-2.5 rounded-full ${getCpuBarColor(systemStats.cpu)}`}
                style={{ width: `${systemStats.cpu}%` }}
              ></div>
            </div>
          </div>
          
          {/* 内存使用率 */}
          <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">内存使用率</span>
              <span className={`${getMemoryColor(systemStats.memory)}`}>{systemStats.memory.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-gray-300 rounded-full h-2.5">
              <div 
                className={`h-2.5 rounded-full ${getMemoryBarColor(systemStats.memory)}`}
                style={{ width: `${systemStats.memory}%` }}
              ></div>
            </div>
          </div>
          
          {/* 请求数 */}
          <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
            <div className="flex justify-between items-center">
              <span className="font-medium">总请求数</span>
              <span className="text-xl">{systemStats.requests}</span>
            </div>
          </div>
          
          {/* 运行时间 */}
          <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
            <div className="flex justify-between items-center">
              <span className="font-medium">运行时间</span>
              <span className="text-xl">{formatUptime(systemStats.uptime)}</span>
            </div>
          </div>
          
          {/* 响应延迟 */}
          <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
            <div className="flex justify-between items-center">
              <span className="font-medium">平均响应时间</span>
              <span className={`${getLatencyColor(systemStats.latency)}`}>{systemStats.latency.toFixed(0)} ms</span>
            </div>
          </div>
          
          {/* 活跃连接 */}
          <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
            <div className="flex justify-between items-center">
              <span className="font-medium">活跃连接数</span>
              <span className="text-xl">{systemStats.activeConnections}</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* 系统日志 */}
      <div className={`rounded-lg p-6 ${darkMode ? 'bg-gray-800 text-gray-300' : 'bg-white text-gray-700'} shadow-lg transition-colors duration-300`}>
        <h3 className="text-xl font-semibold mb-4">系统日志</h3>
        
        <div className={`rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'} p-2 max-h-96 overflow-y-auto`}>
          <table className="w-full">
            <thead>
              <tr className={`text-left ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                <th className="p-2">时间</th>
                <th className="p-2">级别</th>
                <th className="p-2">消息</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, index) => (
                <tr 
                  key={index}
                  className={`${index % 2 === 0 ? (darkMode ? 'bg-gray-800' : 'bg-white') : ''}`}
                >
                  <td className="p-2 text-sm">{log.time}</td>
                  <td className="p-2">
                    <span className={`px-2 py-1 rounded text-xs ${getLogLevelColor(log.level, darkMode)}`}>
                      {log.level}
                    </span>
                  </td>
                  <td className="p-2">{log.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      
      {/* 模块状态 */}
      <div className={`col-span-3 rounded-lg p-6 ${darkMode ? 'bg-gray-800 text-gray-300' : 'bg-white text-gray-700'} shadow-lg transition-colors duration-300`}>
        <h3 className="text-xl font-semibold mb-4">模块状态</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {['内核模块', '堆模块', '栈模块', '代码模块'].map((module, index) => (
            <div 
              key={index}
              className={`p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'} flex flex-col`}
            >
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium">{module}</span>
                <span className={`px-2 py-1 rounded-full text-xs ${
                  index === 3 
                    ? (darkMode ? 'bg-yellow-800 text-yellow-200' : 'bg-yellow-100 text-yellow-800') 
                    : (darkMode ? 'bg-green-800 text-green-200' : 'bg-green-100 text-green-800')
                }`}>
                  {index === 3 ? '警告' : '正常'}
                </span>
              </div>
              
              <div className="text-sm mb-2">
                {index === 3 ? '发现潜在问题' : '运行正常'}
              </div>
              
              <div className="mt-auto text-right">
                <button 
                  className={`text-sm px-3 py-1 rounded ${
                    darkMode 
                      ? 'bg-blue-700 hover:bg-blue-600 text-white' 
                      : 'bg-blue-100 hover:bg-blue-200 text-blue-800'
                  }`}
                >
                  查看详情
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// 辅助函数
const getCpuColor = (value) => {
  if (value < 50) return 'text-green-500';
  if (value < 80) return 'text-yellow-500';
  return 'text-red-500';
};

const getCpuBarColor = (value) => {
  if (value < 50) return 'bg-green-500';
  if (value < 80) return 'bg-yellow-500';
  return 'bg-red-500';
};

const getMemoryColor = (value) => {
  if (value < 60) return 'text-green-500';
  if (value < 85) return 'text-yellow-500';
  return 'text-red-500';
};

const getMemoryBarColor = (value) => {
  if (value < 60) return 'bg-green-500';
  if (value < 85) return 'bg-yellow-500';
  return 'bg-red-500';
};

const getLatencyColor = (value) => {
  if (value < 100) return 'text-green-500';
  if (value < 200) return 'text-yellow-500';
  return 'text-red-500';
};

const getLogLevelColor = (level, darkMode) => {
  switch (level.toLowerCase()) {
    case 'info':
      return darkMode ? 'bg-blue-900 text-blue-200' : 'bg-blue-100 text-blue-800';
    case 'warning':
      return darkMode ? 'bg-yellow-900 text-yellow-200' : 'bg-yellow-100 text-yellow-800';
    case 'error':
      return darkMode ? 'bg-red-900 text-red-200' : 'bg-red-100 text-red-800';
    default:
      return darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-800';
  }
};

const formatUptime = (hours) => {
  const h = Math.floor(hours);
  const m = Math.floor((hours - h) * 60);
  
  return `${h}小时 ${m}分钟`;
};

export default SystemMonitor;