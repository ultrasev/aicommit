Git 提交信息自动生成器

<img src="https://github.com/ultrasev/aicommit/assets/51262739/549d63da-c66b-400c-8a2b-4c26953d524a" width="789px">

根据 git 仓库中检测到的更改，使用 GPT 自动生成合适的提交信息。

## 功能

根据 `git diff` 自动生成 5 条候选提交信息，用户从建议的提交信息列表中进行选择，选择后将提交信息添加到 git commit 中。 Demo:

<img src="https://github.com/ultrasev/aicommit/assets/51262739/601afec0-b0cb-4ab7-b36a-cb274247169c" width="789px">

## 使用方法

```bash
pip3 install git+https://github.com/ultrasev/aicommit
```

在 git 仓库中运行，通过 `git add xxx` 后执行 `aicommit` 命令，即可生成提交信息。

使用前需要配置 OpenAI API 密钥，将密钥放到 `~/.openai_api_key` 文件中。示例

```bash
echo 'OPENAI_API_KEY=your-api-key' > ~/.openai_api_key
```

## TODO

- [ ] 变更过多时，自动分批提交
