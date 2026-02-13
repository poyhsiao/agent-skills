#!/usr/bin/env bash
# GitLab MR 详情查询脚本
# 用法: ./scripts/gitlab-mr-detail.sh <mr-id>

set -euo pipefail

GITLAB_URL="${GITLAB_URL:-https://gitlab.com}"
GITLAB_TOKEN="${GITLAB_TOKEN:-}"
PROJECT_ID="${PROJECT_ID:-}"
MR_ID="${1:-}"

# 检查参数
if [[ -z "$MR_ID" ]]; then
    echo "用法: $0 <mr-id>"
    exit 1
fi

if [[ -z "$GITLAB_TOKEN" ]]; then
    echo "错误: 请设置 GITLAB_TOKEN 环境变量"
    exit 1
fi

if [[ -z "$PROJECT_ID" ]]; then
    echo "错误: 请设置 PROJECT_ID 环境变量"
    exit 1
fi

echo "获取 MR #$MR_ID 的详细信息..."
echo ""

# 获取 MR 详情
MR_INFO=$(curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    "$GITLAB_URL/api/v4/projects/$PROJECT_ID/merge_requests/$MR_ID")

echo "#MR 标题"
echo "$(echo "$MR_INFO" | jq -r '.title')"
echo ""

echo "## 基本信息"
echo "- 作者: $(echo "$MR_INFO" | jq -r '.author.username')"
echo "- 分支: $(echo "$MR_INFO" | jq -r '.source_branch') → $(echo "$MR_INFO" | jq -r '.target_branch')"
echo "- 状态: $(echo "$MR_INFO" | jq -r '.state')"
echo "- 创建时间: $(echo "$MR_INFO" | jq -r '.created_at')"
echo "- 更新时间: $(echo "$MR_INFO" | jq -r '.updated_at')"
echo "- 变更文件数: $(echo "$MR_INFO" | jq -r '.changes_count')"
echo "- 代码行数: +$(echo "$MR_INFO" | jq -r '.additions') -$(echo "$MR_INFO" | jq -r '.deletions')"
echo ""

echo "## 描述"
echo "$(echo "$MR_INFO" | jq -r '.description')"
echo ""

echo "## 参与者"
echo "- Assignee: $(echo "$MR_INFO" | jq -r '.assignees[0].username // "无")"
echo "- Reviewers: $(echo "$MR_INFO" | jq -r '.reviewers[].username' | tr '\n' ', ' | sed 's/,$/\n/')"
echo ""

echo "## 标签"
echo "$(echo "$MR_INFO" | jq -r '.labels[]' | tr '\n' ', ' | sed 's/,$/\n/')"
echo ""

# 获取代码差异
echo "## 代码差异"
echo "---"
curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    "$GITLAB_URL/api/v4/projects/$PROJECT_ID/merge_requests/$MR_ID/diffs" \
    | jq -r '.[] |
        "文件: \(.old_path) → \(.new_path)",
        "---",
        .diff,
        "",
        "---"'