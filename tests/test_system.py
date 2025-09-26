from llmos_core.Prompts import PromptMainBoard
from pathlib import Path
if __name__ == "__main__":
    file_code = Path(__file__).parent / 'prompt_code' / 'engage_agent.txt'
    promptMainBoard = PromptMainBoard(code_file=file_code)
    prompt = promptMainBoard.assemble_prompt()
    print(prompt)