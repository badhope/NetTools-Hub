# 维护者手册 · Maintainers

给有仓库写权限的协作者看的操作说明。

## 五个仓库与推送

| 远程名 | 地址 | 说明 |
|---|---|---|
| `gh-badhope` | github.com/badhope/mashang | 主仓，CI 在此实跑 |
| `gh-x33834` | github.com/x33834/mashang | 镜像 |
| `gh-morningstar` | github.com/Morningstar202604/mashang | 镜像 |
| `gitee` | gitee.com/badhope/mashang | 镜像 |
| `gitcode` | gitcode.com/badhope/mashang | 镜像（**main 受保护**） |

推送全部：

```bash
for r in gh-badhope gh-x33834 gh-morningstar gitee gitcode; do
  git push $r main
done
```

## GitCode 的 main 分支保护

GitCode 仓库的 `main` 是**保护分支**，`git push` 会被 `pre-receive hook` 拒绝：

```
remote: GitCode: You are not allowed to push code to protected branches on this project.
```

两种处理方式：

1. **网页放开保护**（推荐，一次性）
   仓库 → 设置 → 分支保护 → 删除 `main` 的保护规则。
   之后 `git push gitcode main` 可正常使用。

2. **走 PR 流程**
   ```bash
   git push gitcode HEAD:refs/heads/sync/<sha>
   ```
   然后在网页创建 MR 并合并。注意：即使有 admin 权限，
   API 合并也会被拒（`not allowed to merge code into protected branches`），
   需先在网页临时放开保护。

## 提权与权限

- 仓库写权限需要在**仓库设置 → Collaborators** 添加（个人仓库无法用组织 team 授权）
- 组织成员身份不等于仓库权限
