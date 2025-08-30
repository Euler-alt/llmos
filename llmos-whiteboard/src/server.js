const express = require('express');
const cors = require('cors');
const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());

// 模拟数据库中的数据
let moduleData = {
  kernel: "系统规则和工作流：\n- 始终优先调用工具函数来完成任务。\n- 使用栈模块管理多步任务。",
  heap: "持久化存储：\n- 当前用户：Alex\n- 任务目标：查找最新的AI新闻",
  stack: "任务执行栈：\n- [step 1] 调用搜索工具\n- [step 2] 汇总搜索结果",
  code: "可执行代码: \n```python\ndef get_latest_news(topic):\n    # 调用外部API...\n    pass\n```"
};

// 用于存储所有 SSE 客户端的引用
const clients = [];

// GET 接口：用于前端获取所有模块数据
app.get('/api/modules', (req, res) => {
  res.json(moduleData);
});

// POST 接口：用于前端更新特定模块数据
app.post('/api/modules/update', (req, res) => {
  const { moduleName, newData } = req.body;

  if (moduleData.hasOwnProperty(moduleName)) {
    moduleData[moduleName] = newData;

    // **核心改动：数据更新后，立即通过 SSE 推送给所有客户端**
    sendSseUpdate(moduleData);

    res.status(200).json({ message: 'Data updated successfully' });
  } else {
    res.status(400).json({ message: 'Invalid module name' });
  }
});

// **新增 SSE 接口**
app.get('/api/sse', (req, res) => {
  // 设置 SSE 响应头
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('Access-Control-Allow-Origin', '*'); // 允许跨域

  // 将客户端添加到列表中，以便后续推送
  clients.push(res);
  console.log('New SSE client connected.');

  // 立即发送一次完整的数据，确保新连接的客户端能获取当前状态
  res.write(`data: ${JSON.stringify(moduleData)}\n\n`);

  // 当客户端断开连接时，从列表中移除
  req.on('close', () => {
    const index = clients.indexOf(res);
    if (index > -1) {
      clients.splice(index, 1);
    }
    console.log('SSE client disconnected.');
  });
});

// **新增函数：向所有客户端推送数据**
function sendSseUpdate(data) {
  const payload = `data: ${JSON.stringify(data)}\n\n`;
  clients.forEach(client => client.write(payload));
  console.log('Pushed update to all connected clients.');
}

app.listen(port, () => {
  console.log(`Backend server listening at http://localhost:${port}`);
});