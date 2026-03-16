from typing import Optional, Dict

from pydantic import BaseModel


class WindowConfig(BaseModel):
    """窗口配置模型"""
    windowId: str
    windowType: str
    windowTitle: str
    description: Optional[str] = None
    order: int = 0
    windowTheme: Optional[str] = None
    data:Dict[str,str] = {}