# Agent Skills

A collection of Claude AI skills for automating development workflows.

## 📦 Skills

### git-workflow-automation

一个完整的 Git 工作流自动化 Skill，支持从提交到 PR 创建的全流程自动化，并自动关联和关闭 GitHub Issues。

#### 功能特性

- **自动生成 Conventional Commits 规范的提交信息**
- **智能分析代码变更**，自动识别提交类型（feat、fix、docs 等）
- **自动提取 Issue 编号**，识别需要关闭或引用的 Issue
- **自动生成 PR 描述**，包含变更摘要、文件列表和 Issue 关联
- **自动创建 GitHub PR** 并关联相关 Issue
- **自动评论 Issue**，通知 Issue 将在 PR 中解决

#### 快速开始

```bash
# 1. 暂存变更
git add <files>

# 2. 生成提交信息
python3 git-workflow-automation/scripts/generate_commit_message.py

# 3. 提交变更
git commit -m "<生成的消息>"

# 4. 推送到远程
git push -u origin <branch>

# 5. 提取 Issue 编号
ISSUES=$(python3 git-workflow-automation/scripts/extract_issue_numbers.py main)

# 6. 生成 PR 描述
PR_DESC=$(python3 git-workflow-automation/scripts/generate_pr_description.py main "$ISSUES")

# 7. 创建 PR
gh pr create --title "<标题>" --body "$PR_DESC" --base main
```

#### 目录结构

```
git-workflow-automation/
├── SKILL.md                          # Skill 完整文档
├── scripts/
│   ├── generate_commit_message.py    # 生成 Conventional Commits 消息
│   ├── extract_issue_numbers.py     # 从提交信息提取 Issue 编号
│   └── generate_pr_description.py   # 生成 PR 描述
└── references/
    ├── conventional-commits.md      # Conventional Commits 规范参考
    └── issue-keywords.md            # GitHub Issue 关键字参考
```

#### 前置要求

- Git 仓库已初始化并配置远程仓库
- GitHub CLI (`gh`) 已安装并认证
- Python 3.x
- 用户具有仓库推送权限

## 📋 其他资源

- `.spec-workflow/` - 规范工作流模板
- `.serena/` - 项目配置

## 📄 许可证

[Apache License 2.0](LICENSE)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这些 Skills。
