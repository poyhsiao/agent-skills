#!/usr/bin/env bash
# GitHub PR 详情查询脚本
# 用法: ./scripts/github-pr-detail.sh <pr-id>

set -euo pipefail

GITHUB_TOKEN="${GITHUB_TOKEN:-}"
REPO="${GITHUB_REPOSITORY:-}"
PR_ID="${1:-}"

# 检查参数
if [[ -z "$PR_ID" ]]; then
    echo "用法: $0 <pr-id>"
    exit 1
fi

if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "错误: 请设置 GITHUB_TOKEN 环境变量"
    exit 1
fi

if [[ -z "$REPO" ]]; then
    echo "错误: 请设置 GITHUB_REPOSITORY 环境变量 (格式: owner/repo)"
    exit 1
fi

echo "获取 PR #$PR_ID 的详细信息..."
echo ""

# 获取 PR 详情
PR_INFO=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO/pulls/$PR_ID")

echo "#PR 标题"
echo "$(echo "$PR_INFO" | jq -r '.title')"
echo ""

echo "## 基本信息"
echo "- 作者: $(echo "$PR_INFO" | jq -r '.user.login')"
echo "- 分支: $(echo "$PR_INFO" | jq -r '.head.ref') → $(echo "$PR_INFO" | jq -r '.base.ref')"
echo "- 状态: $(echo "$PR_INFO" | jq -r '.state')"
echo $(echo "$PR_INFO" | jq -r 'if .merged then "- 已合并: \(.merged_at)" else "" end')
echo "- 创建时间: $(echo "$PR_INFO" | jq -r '.created_at')"
echo "- 更新时间: $(echo "$PR_INFO" | jq -r '.updated_at')"
echo "- 变更文件数: $(echo "$PR_INFO" | jq -r '.changed_files')"
echo "- 代码行数: +$(echo "$PR_INFO" | jq -r '.additions') -$(echo "$PR_INFO" | jq -r '.deletions')"
echo ""

echo "## 描述"
echo "$(echo "$PR_INFO" | jq -r '.body // "无描述"')"
echo ""

echo "## 参与者"
echo "- Assignee: $(echo "$PR_INFO" | jq -r '.assignees[0].login // "无")'"
REVIEWERS=$(echo "$PR_INFO" | jq -r '.requested_reviewers[]?.login' | tr '\n' ', ' | sed 's/,$//')
echo "- Requested Reviewers: ${REVIEWERS:-无}"
echo ""

echo "## 标签"
LABELS=$(echo "$PR_INFO" | jq -r '.labels[].name' | tr '\n' ', ' | sed 's/,$//')
echo "${LABELS:-无标签}"
echo ""

# 获取代码差异
echo "## 代码差异"
echo "---"
curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO/pulls/$PR_ID/files" \
    | jq -r '.[] |
        "文件: \(.filename)",
        "---",
        .patch // "(二进制文件)",
        "",
        "---"'