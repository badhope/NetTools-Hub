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

## 组织成员与仓库权限（重要）

`mashang` 仓库位于 **badhope 个人账号**下，不在组织内。这带来一个 GitHub 的硬约束：

- **组织成员身份 ≠ 仓库权限**。邀请进组织后，对方仍看不到这个仓库。
- **组织 team 无法授权个人仓库**（API 返回 `Validation Failed / TeamRepository`）。
- 给个人仓库授权只能走：仓库 → Settings → Collaborators → Add people（需知道对方 **GitHub 用户名**，不能用邮箱）。

因此新成员接入需要两步：

1. 接受组织邀请（`Nailong-Studio`）
2. 告知其 GitHub 用户名 → 加到 `badhope/mashang` 的 Collaborators，权限选 **Write**

如需彻底简化（一次授权覆盖所有仓库），可把 mashang 转移到 `Nailong-Studio` 组织：
仓库 → Settings → 最下方 Danger Zone → Transfer ownership。
**注意**：转移会改变仓库 URL、GitHub Pages 地址、Actions 徽章链接，
需要同步修改 README、`AppConstants.REPO_URL`、CI 中的仓库名判断。

## GitCode 保护分支（已解决，留档）

GitCode 的 `main` 默认是保护分支，`git push` 会被拒。放开方式：

```bash
curl -X DELETE \
  -H "Authorization: Bearer <gitcode_token>" \
  "https://api.gitcode.com/api/v5/repos/badhope/mashang/branches/main/protection"
```

注意路径是 `branches/<name>/protection`（Gitee 风格），不是 `protected_branches` 或 `branches/<name>/protect`。
删除后 `branches/main` 返回 `"protected": false`，即可正常推送。
