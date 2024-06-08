Git 提交信息生成器

根据 git 仓库中检测到的更改，使用 GPT 自动生成合适的提交信息。

## 功能

根据 `git diff` 自动生成 5 条候选提交信息，用户从建议的提交信息列表中进行选择，选择后将提交信息添加到 git commit 中。



## 使用方法

```bash
pip3 install -r requirements.txt
```
在 git 仓库中运行，通过 `git add xxx` 后执行 `aicommit` 命令，即可生成提交信息。

使用前需要配置 OpenAI API 密钥，将密钥放到 `.env` 文件中。示例

```bash
OPENAI_API_KEY=your-api-key
```
