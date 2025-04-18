#!/usr/bin/env python3
from rich.console import Console
from rich.text import Text
import random
import typing
import os
import re
import subprocess
import json
import httpx
import asyncio
from loguru import logger
from codefast import getenv

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

git diff 输出：
```
{}
```
'''

SYSTEM_PROMPT = '''You are a professional coding coach with extensive expertise in using Git for version control.
You have a strong background in teaching and guiding others in best coding practices, ensuring efficient collaboration and code management.
Your proficiency in Git includes branching, merging, resolving conflicts, and leveraging advanced features to optimize workflow.'''


def shell(command: str) -> str:
    return subprocess.check_output(command, shell=True).decode('utf-8')


class CommitGenerator:
    def __init__(self, diff: str):
        self.diff = diff
        self.api_key = getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is not set")

    async def __call__(self) -> str:
        """
        Generate commit message using OpenRouter API asynchronously
        """
        query = PROMPT_TEMPLATE.format(self.diff)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [
                        {
                            "role": "user",
                            "content": query
                        }
                    ]
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]


class NoChangesException(Exception):
    pass


class AICommitter:
    def __init__(self):
        self.diff = shell('git diff --cached')

    def __enter__(self):
        if not self.diff:
            raise NoChangesException
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_choices(self, message: str) -> typing.List[str]:
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
        for i, c in enumerate(choices):
            color = random.choice(rich_colors)
            text = Text(f'{i+1}. {c}', style=color)
            console.print(text)

    async def run(self) -> bool:
        logger.info("git diff is: \n {}\n...\n".format(self.diff[:500]))
        generator = CommitGenerator(self.diff)
        message = await generator()
        choices = self.get_choices(message)
        self.print_rich_hint(choices)

        answer = input('\nWhich one do you prefer? Or 0 to abort: ')
        if answer == '0':
            logger.info('Commit aborted')
            return False
        elif answer.isdigit() and int(answer) <= len(choices):
            cmsg = choices[int(answer)-1]
            shell(f'git commit -m "{cmsg}"')
            return True
        else:
            logger.info('Invalid choice')
            return False


async def __aicommit():
    try:
        with AICommitter() as committer:
            await committer.run()
    except NoChangesException:
        logger.warning('No changes to commit')


def main():
    asyncio.run(__aicommit())


if __name__ == '__main__':
    main()
