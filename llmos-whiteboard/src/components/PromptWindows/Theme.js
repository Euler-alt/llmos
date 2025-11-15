// --- 1. 主题颜色映射表 (THEME_MAP) ---
// 这是核心的主题配置，将主题名称（如 'red'）映射到所需的 Tailwind CSS 类名。
// 每个属性都包含 'light'（浅色模式）和 'dark'（深色模式）两种配置。
export const THEME_MAP = {
    // --- 原有主题 ---

    // 红色主题 (Red Theme) - 适合代码/警告窗口
    'red': {
        // header: 窗口头部背景色
        header: {light: 'bg-red-600', dark: 'bg-red-900'},
        // bgAccent: 窗口主体背景色 (浅色模式下带微弱主题色，深色模式下为深灰)
        bgAccent: {light: 'bg-red-50', dark: 'bg-gray-800'},
        // accent: 强调色 (用于标签页激活文本等)
        accent: {light: 'text-red-600', dark: 'text-red-400'},
        // focus: 聚焦环颜色 (用于输入框获得焦点时)
        focus: {light: 'focus:ring-red-400', dark: 'focus:ring-red-500'},
        // ring: 更新提示环颜色 (用于整个窗口有更新时)
        ring: {light: 'ring-red-400', dark: 'ring-red-500'},
        // border: 外部边框颜色
        border: {light: 'border-red-200', dark: 'border-gray-700'},
    },
    // 蓝色主题 (Blue Theme) - 适合聊天/交互窗口
    'blue': {
        header: {light: 'bg-blue-600', dark: 'bg-blue-900'},
        bgAccent: {light: 'bg-blue-50', dark: 'bg-gray-800'},
        accent: {light: 'text-blue-600', dark: 'text-blue-400'},
        focus: {light: 'focus:ring-blue-400', dark: 'focus:ring-blue-500'},
        ring: {light: 'ring-blue-400', dark: 'ring-blue-500'},
        border: {light: 'border-blue-200', dark: 'border-gray-700'},
    },
    // 绿色主题 (Green Theme) - 适合日志/成功窗口
    'green': {
        header: {light: 'bg-green-600', dark: 'bg-green-900'},
        bgAccent: {light: 'bg-green-50', dark: 'bg-gray-800'},
        accent: {light: 'text-green-600', dark: 'text-green-400'},
        focus: {light: 'focus:ring-green-400', dark: 'focus:ring-green-500'},
        ring: {light: 'ring-green-400', dark: 'ring-green-500'},
        border: {light: 'border-green-200', dark: 'border-gray-700'},
    },

    // --- 新增主题 ---

    // 1. 紫色主题 (Purple Theme) - 适合配置/设置窗口
    'purple': {
        header: {light: 'bg-purple-600', dark: 'bg-purple-900'},
        bgAccent: {light: 'bg-purple-50', dark: 'bg-gray-800'},
        accent: {light: 'text-purple-600', dark: 'text-purple-400'},
        focus: {light: 'focus:ring-purple-400', dark: 'focus:ring-purple-500'},
        ring: {light: 'ring-purple-400', dark: 'ring-purple-500'},
        border: {light: 'border-purple-200', dark: 'border-gray-700'},
    },

    // 2. 黄色主题 (Yellow Theme) - 适合待办/提示窗口 (注意：深色模式头部颜色略有调整以提高可读性)
    'yellow': {
        header: {light: 'bg-yellow-600', dark: 'bg-yellow-800'}, // 深色模式下用 800，避免太暗
        bgAccent: {light: 'bg-yellow-50', dark: 'bg-gray-800'},
        accent: {light: 'text-yellow-600', dark: 'text-yellow-400'},
        focus: {light: 'focus:ring-yellow-400', dark: 'focus:ring-yellow-500'},
        ring: {light: 'ring-yellow-400', dark: 'ring-yellow-500'},
        border: {light: 'border-yellow-200', dark: 'border-gray-700'},
    },

    // 3. 青色主题 (Cyan Theme) - 适合通知/信息流窗口
    'cyan': {
        header: {light: 'bg-cyan-600', dark: 'bg-cyan-900'},
        bgAccent: {light: 'bg-cyan-50', dark: 'bg-gray-800'},
        accent: {light: 'text-cyan-600', dark: 'text-cyan-400'},
        focus: {light: 'focus:ring-cyan-400', dark: 'focus:ring-cyan-500'},
        ring: {light: 'ring-cyan-400', dark: 'ring-cyan-500'},
        border: {light: 'border-cyan-200', dark: 'border-gray-700'},
    },

    // 4. 灰色主题 (Gray Theme) - 适合默认/不强调的窗口
    'gray': {
        header: {light: 'bg-gray-600', dark: 'bg-gray-900'},
        bgAccent: {light: 'bg-gray-50', dark: 'bg-gray-800'},
        accent: {light: 'text-gray-600', dark: 'text-gray-400'},
        focus: {light: 'focus:ring-gray-400', dark: 'focus:ring-gray-500'},
        ring: {light: 'ring-gray-400', dark: 'ring-gray-500'},
        border: {light: 'border-gray-200', dark: 'border-gray-700'},
    },
};
export const SUPPORTED_THEMES = Object.keys(THEME_MAP); // --- 2. 主题 Hook (useThemeClasses) ---
// 这个自定义 Hook 负责根据传入的主题名称和深色模式状态，返回一个包含所有所需 CSS 类名的对象。
export const useThemeClasses = (themeName, darkMode) => {
    // 尝试获取指定主题，如果主题不存在，则默认使用 'red' 主题
    const theme = THEME_MAP[themeName] || THEME_MAP['red'];
    // 确定当前是 'dark' 还是 'light' 模式
    const mode = darkMode ? 'dark' : 'light';

    // 返回一个包含所有解析后的 Tailwind 类名对象
    return {
        // 组合背景色和文本色类
        containerBgTextClass: `${theme.bgAccent[mode]} ${darkMode ? 'text-gray-200' : 'text-gray-800'}`,
        headerClass: theme.header[mode],
        accentClass: theme.accent[mode],
        focusRingClass: theme.focus[mode],
        updateRingClass: theme.ring[mode],
        containerBorderClass: theme.border[mode],
    };
};