#!/usr/bin/env bash
# 一键全量检查 —— 提交前 / 发布前跑这一条就够了。
#
# 设计原则：
#   1. 每一步都真实执行并检查退出码，不吞错
#   2. 失败不中断，跑完所有步骤后汇总（方便一次看到全部问题）
#   3. 末尾明确「全绿」或「有失败」
#
# 用法：
#   bash scripts/ci/check_all.sh            # 全部
#   bash scripts/ci/check_all.sh --fast     # 只跑 Python / 内容侧
#   bash scripts/ci/check_all.sh --android  # 只跑 Android 侧

set -uo pipefail

cd "$(dirname "$0")/../.." || exit 1

FAST=0
ANDROID_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --fast) FAST=1 ;;
    --android) ANDROID_ONLY=1 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
  esac
done

PASSED=0
FAILED=0
FAILED_NAMES=""

ok()   { PASSED=$((PASSED + 1)); printf '  [OK]   %s\n' "$1"; }
bad()  { FAILED=$((FAILED + 1)); FAILED_NAMES="$FAILED_NAMES\n  - $1"; printf '  [FAIL] %s\n' "$1"; }
skip() { printf '  [SKIP] %s\n' "$1"; }

# 有未提交改动时，产物比对没有意义（基准是 HEAD）
has_uncommitted() { ! git diff --quiet HEAD -- "$@" 2>/dev/null; }

if [ "$ANDROID_ONLY" -eq 0 ]; then
  printf '\n== Python / 内容侧 ==\n'

  printf '\n>> Python 单元测试\n'
  if python -m unittest discover -s tests; then ok "Python 单元测试"; else bad "Python 单元测试"; fi

  printf '\n>> 课程 × 参考答案校验\n'
  if python tests/validate_content.py; then ok "课程内容校验"; else bad "课程内容校验"; fi

  printf '\n>> Pages 资产同步\n'
  if has_uncommitted docs web; then
    skip "工作区有未提交改动，跳过产物比对"
    python tools/sync_pages_assets.py >/dev/null && ok "资产同步执行" || bad "资产同步执行"
  else
    if python tools/sync_pages_assets.py >/dev/null && \
       git diff --exit-code -- docs/catalog.json docs/content_packs docs/web >/dev/null; then
      ok "资产可复现"
    else
      bad "资产不可复现（同步后仍有差异）"
    fi
  fi

  printf '\n>> 页面链接检查\n'
  if python tools/check_links.py; then ok "页面链接"; else bad "页面链接"; fi

  printf '\n>> 网页端 JS 语法\n'
  if node --check web/app.js && node --check web/data.js && node --check web/engine.js; then
    ok "JS 语法"
  else
    bad "JS 语法"
  fi

  printf '\n>> web 数据生成幂等\n'
  if has_uncommitted web; then
    skip "工作区有未提交改动，跳过幂等比对"
    python web/gen_data.py >/dev/null && ok "gen_data 执行" || bad "gen_data 执行"
  else
    if python web/gen_data.py >/dev/null && git diff --exit-code -- web/data.js web/engine.js >/dev/null; then
      ok "gen_data 幂等"
    else
      bad "gen_data 不幂等"
    fi
  fi

  printf '\n>> catalog 签名与包哈希\n'
  if python tools/verify_catalog.py; then ok "catalog 校验"; else bad "catalog 校验"; fi
fi

if [ "$FAST" -eq 0 ]; then
  printf '\n== Android 侧 ==\n'
  export ANDROID_HOME="${ANDROID_HOME:-/c/Dev/android-sdk}"
  export JAVA_HOME="${JAVA_HOME:-/c/Dev/jdk-21}"
  export GRADLE_USER_HOME="${GRADLE_USER_HOME:-/c/Dev/gradle-home-mashang}"

  printf '\n>> Android lint\n'
  if ./gradlew :app:lintDebug --no-daemon -q; then ok "lint"; else bad "lint"; fi

  printf '\n>> JVM 单元测试\n'
  if ./gradlew :app:testDebugUnitTest --no-daemon -q; then ok "JVM 单测"; else bad "JVM 单测"; fi

  printf '\n>> Debug APK\n'
  if ./gradlew :app:assembleDebug --no-daemon -q; then ok "assembleDebug"; else bad "assembleDebug"; fi

  printf '\n>> APK 探针\n'
  if python tests/ci_apk_probe.py app/build/outputs/apk/debug/app-debug.apk; then
    ok "APK 探针"
  else
    bad "APK 探针"
  fi

  printf '\n>> Instrumented 测试编译（执行需真机/模拟器）\n'
  if ./gradlew :app:assembleDebugAndroidTest --no-daemon -q; then
    ok "androidTest 编译"
  else
    bad "androidTest 编译"
  fi

  printf '\n>> localRelease 构建（本地可装、R8 生效、debug 证书签名）\n'
  if ./gradlew :app:assembleLocalRelease --no-daemon -q 2>/dev/null; then
    ok "localRelease 构建"
  else
    bad "localRelease 构建"
  fi
fi

printf '\n========== 汇总 ==========\n'
printf '通过：%d 项\n' "$PASSED"
if [ "$FAILED" -gt 0 ]; then
  printf '失败：%d 项%s\n' "$FAILED" "$FAILED_NAMES"
  printf '\n结果：未通过，请先修复\n'
  exit 1
fi
printf '\n结果：全部通过\n'
