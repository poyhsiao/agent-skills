#!/usr/bin/env bash
# GitLab MR 列表查询脚本
# 用法: ./scripts/gitlab-mr-list.sh [state]
# state: opened (默认), merged, closed, all

set -euo pipefail

GITLAB_URL="${GITLAB_URL:-https://gitlab.com}"
GITLAB_TOKEN="${GITLAB_TOKEN:-}"
STATE="${1:-opened}"
PROJECT_ID="${PROJECT_ID:-}"

# 检查必要的变量
if [[ -z "$GITLAB_TOKEN" ]]; then
    echo "错误: 请设置 GITLAB_TOKEN 环境变量"
    exit 1
fi

if [[ -z "$PROJECT_ID" ]]; then
    # 尝试从 git remote 获取项目路径
    if git rev-parse --git-dir > /dev/null 2>&1; then
        GIT_REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
        if [[ "$GIT_REMOTE_URL" =~ gitlab\.com[:/]([^/]+/[^/]+) ]]; then
            PROJECT_PATH="${BASH_REMATCH[1]}"
            echo "检测到项目路径: $PROJECT_PATH"
            echo "获取 Project ID..."
            PROJECT_ID=$(curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
                "$GITLAB_URL/api/v4/projects?search=$PROJECT_PATH" \
                | jq -r 'if .[0] != null then .[0].id else "" end')

            if [[ -z "$PROJECT_ID" ]]; then
                echo "无法自动获取 Project ID，请手动设置 PROJECT_ID 环境变量"
                exit 1
            fi
            echo "Project ID: $PROJECT_ID"
        else
            echo "未检测到 GitLab 远程仓库，请设置 PROJECT_ID 环境变量"
            exit 1
        fi
    else
        echo "不是 Git 仓库，请设置 PROJECT_ID 环境变量"
        exit 1
    fi
fi

# 列出 MR
echo "列出状态为 '$STATE' 的 MR..."
echo ""

curl -s --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    "$GITLAB_URL/api/v4/projects/$PROJECT_ID/merge_requests?state=$STATE&order_by=created_at&sort=desc&per_page=50" \
    | jq -r '.[] |
        "#\(.iid) \(.title)",
        "  作者: \(.author.username)",
        "  分支: \(.source_branch) → \(.target_branch)",
        "  创建: \(.created_at)",
        "  状态: \(.state), 合并: \(.merged)",
        "  变更: +\(.additions) -\(.deletions)",
        ""'