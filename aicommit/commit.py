#!/usr/bin/env python3
from rich.console import Console
from rich.text import Text
import random
import typing
import os
import re
import subprocess
import json
from openai import OpenAI
from loguru import logger
from dotenv import load_dotenv

load_dotenv()
console = Console()

PROMPT_TEMPLATE = '''
根据下面 `git diff` 的输出，选择合适的提交类型，并用一句英文描述相应的变化。

提交类型可以是以下的选项之一：
feat:     新功能（feature）
fix:      修补 bug
docs:     文档（documentation）
style:    格式（不影响代码运行的变动）
refactor: 代码重构
test:     增加测试
chore:    构建过程或辅助工具的变动

输出限制：
1. 以 `json` 格式返回结果，包含五条候选 commit 信息，每条包含`类型：信息`的格式，示例如下：
```json
{{
    "c1":"feat: add xxx",
    "c2":"chore: xxx",
    "c3":"fix: xxx",
    "c4":"feat: xxx",
    "c5":"feat: xxx"
}}
```
2. 严格遵守上述要求，不允许在结果中添加其他信息。
3. 每条 commit 信息不能超过 50 个字符，也不能特别短，不能是简单的描述更改了哪些文件，要精准的概述 diff 的内容。

git diff 输出：
```
{}
```
'''


def shell(command: str) -> str:
    return subprocess.check_output(command, shell=True).decode('utf-8')


class CommitGenerator(object):
    def __init__(self, diff: str):
        self.diff = diff
        self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

    def __str__(self) -> str:
        resp = self.client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'assistant', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': PROMPT_TEMPLATE.format(
                    self.diff)},
            ]
        )
        return resp.choices[0].message.content


class NoChangesException(Exception):
    pass


class AICommitter(object):
    def __init__(self):
        self.diff = shell('git diff --cached')

    def __enter__(self):
        if not self.diff:
            raise NoChangesException
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_choices(self, message: str) -> str:
        message = re.sub(r'^.*?```json\n(.*?)\n```.*$',
                         r'\1', message, flags=re.DOTALL)
        js = json.loads(message).values()
        return list(js)

    def print_rich_hint(self, choices: typing.List[str]) -> None:
        rich_colors = [
            "red", "green", "yellow", "blue", "magenta", "cyan", "white",
            "bright_black", "bright_red", "bright_green", "bright_yellow",
            "bright_blue", "bright_magenta", "bright_cyan", "bright_white"
        ]
        colored_choices = []
        for i, c in enumerate(choices):
            color = random.choice(rich_colors)
            text = Text(f'{i+1}. {c}', style=color)
            console.print(text)

    def run(self) -> bool:
        logger.info("git diff is: \n {}\n...\n".format(self.diff[:500]))
        message = str(CommitGenerator(self.diff))
        choices = self.get_choices(message)
        self.print_rich_hint(choices)
        answer = input('\nWhich one do you prefer? Or 0 to abort: ')
        if answer == '0':
            logger.info('Commit aborted')
            return False
        elif answer.isdigit() and int(answer) < len(choices):
            cmsg = choices[int(answer)-1]
            shell(f'git commit -m "{cmsg}"')
            return True
        else:
            logger.info('Invalid choice')
            return False


def main():
    try:
        with AICommitter() as committer:
            committer.run()
    except NoChangesException:
        logger.warning('No changes to commit')


if __name__ == '__main__':
    main()
