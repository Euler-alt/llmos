import React, { useEffect, useRef, useState } from 'react';

const DataFlowDiagram = ({ modules, darkMode }) => {
  const [isMaximized, setIsMaximized] = useState(false);
  const canvasRef = useRef(null);
  
  useEffect(() => {
    if (!canvasRef.current || Object.keys(modules).length === 0) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // 清空画布
    ctx.clearRect(0, 0, width, height);
    
    // 设置颜色主题
    const colors = darkMode ? {
      background: '#1f2937',
      node: {
        kernel: '#3b82f6',
        heap: '#10b981',
        stack: '#f59e0b',
        code: '#ef4444'
      },
      text: '#f3f4f6',
      line: '#6b7280',
      arrow: '#9ca3af',
      highlight: '#60a5fa'
    } : {
      background: '#f9fafb',
      node: {
        kernel: '#3b82f6',
        heap: '#10b981',
        stack: '#f59e0b',
        code: '#ef4444'
      },
      text: '#1f2937',
      line: '#9ca3af',
      arrow: '#4b5563',
      highlight: '#2563eb'
    };
    
    // 填充背景
    ctx.fillStyle = colors.background;
    ctx.fillRect(0, 0, width, height);
    
    // 定义节点位置
    const nodes = {
      kernel: { x: width / 2, y: 80, radius: 60, color: colors.node.kernel, name: '内核模块' },
      heap: { x: width / 4, y: height / 2, radius: 50, color: colors.node.heap, name: '堆模块' },
      stack: { x: width * 3 / 4, y: height / 2, radius: 50, color: colors.node.stack, name: '栈模块' },
      code: { x: width / 2, y: height - 80, radius: 60, color: colors.node.code, name: '代码模块' }
    };
    
    // 定义连接
    const connections = [
      { from: 'kernel', to: 'heap', label: '状态存储' },
      { from: 'kernel', to: 'stack', label: '任务管理' },
      { from: 'kernel', to: 'code', label: '执行指令' },
      { from: 'heap', to: 'stack', label: '数据读取' },
      { from: 'stack', to: 'code', label: '调用函数' },
      { from: 'code', to: 'heap', label: '结果存储' }
    ];
    
    // 绘制连接线
    connections.forEach(conn => {
      const from = nodes[conn.from];
      const to = nodes[conn.to];
      
      // 计算方向向量
      const dx = to.x - from.x;
      const dy = to.y - from.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      
      // 计算起点和终点（考虑节点半径）
      const startX = from.x + (dx / distance) * from.radius;
      const startY = from.y + (dy / distance) * from.radius;
      const endX = to.x - (dx / distance) * to.radius;
      const endY = to.y - (dy / distance) * to.radius;
      
      // 绘制线条
      ctx.beginPath();
      ctx.moveTo(startX, startY);
      ctx.lineTo(endX, endY);
      ctx.strokeStyle = colors.line;
      ctx.lineWidth = 2;
      ctx.stroke();
      
      // 绘制箭头
      const arrowSize = 10;
      const angle = Math.atan2(dy, dx);
      ctx.beginPath();
      ctx.moveTo(endX, endY);
      ctx.lineTo(
        endX - arrowSize * Math.cos(angle - Math.PI / 6),
        endY - arrowSize * Math.sin(angle - Math.PI / 6)
      );
      ctx.lineTo(
        endX - arrowSize * Math.cos(angle + Math.PI / 6),
        endY - arrowSize * Math.sin(angle + Math.PI / 6)
      );
      ctx.closePath();
      ctx.fillStyle = colors.arrow;
      ctx.fill();
      
      // 绘制连接标签
      const labelX = (startX + endX) / 2;
      const labelY = (startY + endY) / 2;
      ctx.fillStyle = colors.background;
      ctx.fillRect(labelX - ctx.measureText(conn.label).width / 2 - 5, labelY - 10, ctx.measureText(conn.label).width + 10, 20);
      ctx.fillStyle = colors.text;
      ctx.font = '12px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(conn.label, labelX, labelY);
    });
    
    // 绘制节点
    Object.values(nodes).forEach(node => {
      // 绘制节点圆形
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
      ctx.fillStyle = node.color;
      ctx.fill();
      
      // 绘制节点边框
      ctx.strokeStyle = darkMode ? '#ffffff33' : '#00000033';
      ctx.lineWidth = 2;
      ctx.stroke();
      
      // 绘制节点名称
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 14px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(node.name, node.x, node.y);
      
      // 绘制数据大小指示
      const dataSize = modules[node.name.split(' ')[0].toLowerCase()]?.length || 0;
      const sizeText = `${dataSize} 字节`;
      ctx.font = '12px Arial';
      ctx.fillText(sizeText, node.x, node.y + 20);
    });
    
    // 绘制标题
    ctx.fillStyle = colors.text;
    ctx.font = 'bold 18px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText('LLMOS 模块数据流', width / 2, 20);
    
  }, [modules, darkMode]);
  
  return (
    <div 
      className={`
        rounded-lg p-6 shadow-lg transition-all duration-300
        ${darkMode ? 'bg-gray-800 text-gray-300' : 'bg-white text-gray-700'}
        ${isMaximized ? 'fixed z-50 !rounded-lg' : 'relative'}
      `}
      onDoubleClick={() => setIsMaximized(!isMaximized)}
      style={isMaximized ? { 
        position: 'fixed', 
        top: '10%', 
        left: '25%', 
        right: '25%', 
        bottom: '10%', 
        zIndex: 50,
        borderRadius: '0.5rem'
      } : {}}
    >
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold">数据流图</h3>
        <button 
          className="p-2 rounded-full transition-all duration-200 hover:bg-gray-700 hover:bg-opacity-20"
          onClick={(e) => {
            e.stopPropagation();
            setIsMaximized(!isMaximized);
          }}
          title={isMaximized ? "恢复窗口大小" : "最大化窗口"}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" style={{ width: '16px', height: '16px' }} viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d={isMaximized ? "M3 7a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 6a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" : "M3 4a1 1 0 011-1h12a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm2 1v10h10V5H5z"} clipRule="evenodd" />
          </svg>
        </button>
      </div>
      
      <div className="flex justify-center">
        <canvas 
          ref={canvasRef} 
          width={800} 
          height={500} 
          className="border rounded-lg"
          style={{ maxWidth: '100%', height: 'auto' }}
        />
      </div>
      
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
        {['kernel', 'heap', 'stack', 'code'].map(key => (
          <div 
            key={key}
            className={`p-3 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}
          >
            <div className="flex items-center">
              <div 
                className="w-4 h-4 rounded-full mr-2"
                style={{ 
                  backgroundColor: darkMode ? {
                    kernel: '#3b82f6',
                    heap: '#10b981',
                    stack: '#f59e0b',
                    code: '#ef4444'
                  }[key] : {
                    kernel: '#3b82f6',
                    heap: '#10b981',
                    stack: '#f59e0b',
                    code: '#ef4444'
                  }[key]
                }}
              />
              <span className="capitalize">{key} 模块</span>
            </div>
            <div className="mt-1 text-sm">
              {modules[key] ? `${modules[key].length} 字节` : '无数据'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DataFlowDiagram;