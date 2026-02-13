#!/usr/bin/env bash
# GitHub PR 列表查询脚本
# 用法: ./scripts/github-pr-list.sh [state]
# state: open (默认), closed, merged, all

set -euo pipefail

GITHUB_TOKEN="${GITHUB_TOKEN:-}"
STATE="${1:-open}"
REPO="${GITHUB_REPOSITORY:-}"

# 检查必要的变量
if [[ -z "$GITHUB_TOKEN" ]]; then
    echo "错误: 请设置 GITHUB_TOKEN 环境变量"
    exit 1
fi

if [[ -z "$REPO" ]]; then
    # 尝试从 git remote 获取仓库信息
    if git rev-parse --git-dir > /dev/null 2>&1; then
        GIT_REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
        # 支持 https 和 ssh 两种格式
        if [[ "$GIT_REMOTE_URL" =~ github\.com[:/]([^/]+/[^/]+)\.git$ ]]; then
            REPO="${BASH_REMATCH[1]}"
            echo "检测到仓库: $REPO"
        elif [[ "$GIT_REMOTE_URL" =~ github\.com[:/]([^/]+/[^/]+)$ ]]; then
            REPO="${BASH_REMATCH[1]}"
            echo "检测到仓库: $REPO"
        else
            echo "未检测到 GitHub 远程仓库，请设置 GITHUB_REPOSITORY 环境变量 (格式: owner/repo)"
            exit 1
        fi
    else
        echo "不是 Git 仓库，请设置 GITHUB_REPOSITORY 环境变量 (格式: owner/repo)"
        exit 1
    fi
fi

# 列出 PR
echo "列出状态为 '$STATE' 的 PR..."
echo ""

curl -s -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO/pulls?state=$STATE&sort=created&direction=desc&per_page=50" \
    | jq -r '.[] |
        "#\(.number) \(.title)",
        "  作者: \(.user.login)",
        "  分支: \(.head.ref) → \(.base.ref)",
        "  创建: \(.created_at)",
        "  状态: \(.state)" + if .merged then " (已合并)" else "" end,
        "  变更: +\(.additions) -\(.deletions)",
        ""'