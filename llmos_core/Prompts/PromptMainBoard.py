import json
import re
from .Modules import SystemPromptModule,BasePromptModule

def parse_response(response:str):
    """
    :param response:
    :return:
    """

    try:
        parsed = json.loads(response)
        if isinstance(parsed,dict) and "call_type" in parsed:
            return [parsed]
        elif isinstance(parsed,list) and "call_type" in parsed:
            return parsed

    except json.JSONDecodeError:
        pass

    matches = re.finditer(r"\[(\w+):(\w+)\((.*?)\)\]", response)
    calls = []
    for match in matches:
        call_type, func_name, args = match.groups()
        kwargs = {kv.split("=")[0]: kv.split("=")[1]
                  for kv in args.split(",") if "=" in kv}
        calls.append({
            "call_type": call_type,
            "func_name": func_name,
            "kwargs": kwargs
        })
    return calls



class PromptMainBoard:
    def __init__(self, code_file=None):
        """
        :param modules: 一个字典，key 是模块名，value 是模块实例
        """
        self.system_modules = SystemPromptModule(code_file=code_file)
        self.modules = [self.system_modules]
        self.handlers = {}
        self.handlers.update(self.system_modules.export_handlers())

    def assemble_prompt(self, context=None):
        """
        拼接所有模块的 forward() 输出
        """
        desc =''
        for module in self.modules:
            desc += module.forward()
        return desc

    def extend_module(self,module:BasePromptModule):
        self.modules.append(module)


    def handle_call(self, func_name: str, **kwargs):
        """
        内核调用入口，分发到对应的模块 handler
        """
        self.system_modules.handle_call(func_name, **kwargs)

    def show_state(self):
        """
        打印或返回提示词的当前状态
        """
        return self.assemble_prompt()




