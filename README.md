# Agent Skills

A collection of Claude AI skills for automating development workflows and code review processes.

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

---

### github-pr-review

GitHub Pull Request (PR) review tool with AI-powered code analysis. 用于审查特定 PR、列出所有待审查 PR、分析代码变更并提供改进建议、添加审查评论到 PR 或生成 Markdown 报告。

#### 功能特性

- **PR 列表与详情获取** - 通过 GitHub CLI 和 API 获取 PR 信息
- **全面的代码质量审查** - 基于严重程度的多维度分析
- **多种审查模板** - 简洁、标准、详细三种模板满足不同需求
- **质量评分系统** - A+ 到 D 的等级评分机制
- **审查状态跟踪** - pending → in-progress → completed 的状态流转
- **自动审查摘要管理** - 项目级别的审查统计与跟踪
- **问题解决跟踪** - 记录每个问题的解决状态

#### 快速开始

```bash
# 前置要求 - 安装 GitHub CLI
# macOS
brew install gh

# Linux
# 访问 https://cli.github.com/ 获取安装说明

# 配置认证
gh auth login

# 列出所有开放的 PR
gh pr list --state open

# 获取特定 PR 详情
gh pr view <pr-id> --web=false

# 获取代码差异
gh pr diff <pr-id>
```

#### 目录结构

```
github-pr-review/
├── SKILL.md                          # Skill 完整文档
└── scripts/
    ├── github-pr-list.sh              # 列出 PR（支持状态筛选）
    └── github-pr-detail.sh            # 获取 PR 详情
```

#### 环境变量

- `GITHUB_TOKEN` - GitHub personal access token（或通过 `gh auth login` 配置）
- `GITHUB_REPOSITORY` - 仓库标识（格式：`owner/repo`，位于 git 仓库中自动检测）

#### 使用示例

**审查特定 PR**
```
"Review #123 PR code changes"
"Help me review PR #456 for potential issues"
```

**选择审查模板**
```
"Review #123 with brief template"
"Review PR #456 in detailed mode"
"Generate standard review for #789"
```

**批量审查**
```
"Review #123 and #456"
"List all pending PRs"
"Review all open PRs in repository"
```

#### 审查模板

1. **Brief Template** - 简洁模板，聚焦关键问题
2. **Standard Template** - 标准模板，平衡细节与可读性（默认）
3. **Detailed Template** - 详细模板，包含扩展上下文和代码片段

#### 质量评分系统

- **基础分**: 10.0（满分）
- **关键问题** (🔴): -1 到 -3 分（根据严重程度）
- **代码质量问题** (🟡): -0.5 分/个
- **优点** (✅): +0.5 到 +1 分/个
- **额外奖励**: 文档、测试覆盖率、架构（各 +1 分）

**评分等级**:
- **A+**: 9.0-10.0 (优秀)
- **A**: 8.5-8.9 (很好)
- **B+**: 8.0-8.4 (良好)
- **B**: 7.0-7.9 (可接受)
- **C**: 6.0-6.9 (需要改进)
- **D**: < 6.0 (需要重大修改)

#### 审查状态跟踪

审查文件保存到 `.issues/review/{pr_number}/r{review_count}-{status}.md`

**状态类型**:
- `pending` - 审查已创建，问题已识别，等待修复
- `in-progress` - 开发者正在解决问题
- `completed` - 所有问题已解决，审查已满足

**文件名示例**:
- `r01-pending.md` - 首次审查，有问题待解决
- `r02-in-progress.md` - 第二次审查，正在修复
- `r03-completed.md` - 第三次审查，已满足要求

#### 审查摘要管理

维护 `.issues/review/summary.md` 进行项目级审查跟踪，包含：
- 总体统计（总审查数、开放/合并/关闭 PR、平均评分）
- 所有审查列表表格
- 按分数统计分布
- 优先分级别的待处理问题
- 待执行审查行动表
- 最近活动日志

---

### gitlab-mr-review

GitLab Merge Request (MR) review tool with AI-powered code analysis. 用于审查特定 MR、列出所有待审查 MR、分析代码变更并提供改进建议、添加审查评论到 MR 或生成 Markdown 报告。

#### 功能特性

- **MR 列表与详情获取** - 通过 GitLab CLI 和 API 获取 MR 信息
- **全面的代码质量审查** - 基于严重程度的多维度分析
- **多种审查模板** - 简洁、标准、详细三种模板满足不同需求
- **质量评分系统** - A+ 到 D 的等级评分机制
- **审查状态跟踪** - pending → in-progress → completed 的状态流转
- **自动审查摘要管理** - 项目级别的审查统计与跟踪
- **问题解决跟踪** - 记录每个问题的解决状态

#### 快速开始

```bash
# 前置要求 - 安装 GitLab CLI
# macOS
brew install glab

# Linux
curl -s https://raw.githubusercontent.com/cli/cli/main/scripts/install.sh | sh

# 配置认证
glab auth login

# 列出所有开放的 MR
glab mr list --state opened

# 获取特定 MR 详情
glab mr view <mr-id> --web=false

# 获取代码差异
glab mr diff <mr-id>
```

#### 目录结构

```
gitlab-mr-review/
├── SKILL.md                          # Skill 完整文档
└── scripts/
    ├── gitlab-mr-list.sh              # 列出 MR（支持状态筛选）
    └── gitlab-mr-detail.sh            # 获取 MR 详情
```

#### 环境变量

- `GITLAB_TOKEN` - GitLab personal access token（或通过 `glab auth login` 配置）
- `GITLAB_URL` - GitLab 实例 URL（自定义实例需要，默认使用 gitlab.com）
- `GITLAB_PROJECT_ID` - GitLab 项目 ID（从项目页面获取或 `glab api projects` 查询）

#### 使用示例

**审查特定 MR**
```
"Review !123 MR code changes"
"Help me review MR !456 for potential issues"
```

**选择审查模板**
```
"Review !123 with brief template"
"Review MR !456 in detailed mode"
"Generate standard review for !789"
```

**批量审查**
```
"Review !123 and !456"
"List all pending MRs"
"Review all open MRs in project A"
```

#### 审查模板

1. **Brief Template** - 简洁模板，聚焦关键问题
2. **Standard Template** - 标准模板，平衡细节与可读性（默认）
3. **Detailed Template** - 详细模板，包含扩展上下文和代码片段

#### 质量评分系统

- **基础分**: 10.0（满分）
- **关键问题** (🔴): -1 到 -3 分（根据严重程度）
- **代码质量问题** (🟡): -0.5 分/个
- **优点** (✅): +0.5 到 +1 分/个
- **额外奖励**: 文档、测试覆盖率、架构（各 +1 分）

**评分等级**:
- **A+**: 9.0-10.0 (优秀)
- **A**: 8.5-8.9 (很好)
- **B+**: 8.0-8.4 (良好)
- **B**: 7.0-7.9 (可接受)
- **C**: 6.0-6.9 (需要改进)
- **D**: < 6.0 (需要重大修改)

#### 审查状态跟踪

审查文件保存到 `.issues/review/{mr_number}/r{review_count}-{status}.md`

**状态类型**:
- `pending` - 审查已创建，问题已识别，等待修复
- `in-progress` - 开发者正在解决问题
- `completed` - 所有问题已解决，审查已满足

**文件名示例**:
- `r01-pending.md` - 首次审查，有问题待解决
- `r02-in-progress.md` - 第二次审查，正在修复
- `r03-completed.md` - 第三次审查，已满足要求

#### 审查摘要管理

维护 `.issues/review/summary.md` 进行项目级审查跟踪，包含：
- 总体统计（总审查数、开放/合并/关闭 MR、平均评分）
- 所有审查列表表格
- 按分数统计分布
- 优先分级别的待处理问题
- 待执行审查行动表
- 最近活动日志

---

## 📋 其他资源

- `.spec-workflow/` - 规范工作流模板
- `.serena/` - 项目配置

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这些 Skills。

## 📄 许可证

[Apache License 2.0](LICENSE)