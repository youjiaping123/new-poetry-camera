# GitHub 发布步骤

## 1. 初始化 Git 仓库

```bash
cd /Users/roe/Documents/Code/pi/new-poetry-camera

# 初始化 git 仓库
git init

# 添加所有文件
git add .

# 查看将要提交的文件
git status

# 首次提交
git commit -m "Initial commit: Poetry Camera project"
```

## 2. 在 GitHub 上创建仓库

1. 访问 https://github.com
2. 点击右上角的 "+" 按钮
3. 选择 "New repository"
4. 填写信息：
   - Repository name: `poetry-camera`
   - Description: `一个能看懂世界并创作诗歌的智能相机 / An intelligent camera that sees the world and writes poetry`
   - 设置为 **Public** (或 Private，根据你的需求)
   - **不要** 勾选 "Initialize this repository with a README" (我们已经有了)
5. 点击 "Create repository"

## 3. 连接到 GitHub 仓库

复制 GitHub 给你的仓库 URL (形如 `https://github.com/yourusername/poetry-camera.git`)

```bash
# 添加远程仓库
git remote add origin https://github.com/你的用户名/poetry-camera.git

# 验证远程仓库
git remote -v

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## 4. 如果推送失败（需要认证）

### 方法 A: 使用 Personal Access Token (推荐)

1. 访问 GitHub Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 生成后复制 token (只显示一次！)
5. 推送时使用 token 作为密码

### 方法 B: 使用 SSH Key

```bash
# 生成 SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# 复制公钥
cat ~/.ssh/id_ed25519.pub

# 在 GitHub Settings -> SSH and GPG keys 中添加
```

然后使用 SSH URL:
```bash
git remote set-url origin git@github.com:你的用户名/poetry-camera.git
git push -u origin main
```

## 5. 后续更新

每次修改后：

```bash
# 查看修改
git status

# 添加修改的文件
git add .

# 提交
git commit -m "描述你的修改"

# 推送到 GitHub
git push
```

## 6. 可选：添加 GitHub Actions

创建 `.github/workflows/python-app.yml` 用于自动测试（如需要）

## 7. 可选：添加 License

GitHub 上可以直接添加 MIT License:
1. 在仓库页面点击 "Add file" -> "Create new file"
2. 文件名输入 `LICENSE`
3. GitHub 会提示选择 license 模板
4. 选择 "MIT License"

## 8. 完善仓库

在 GitHub 仓库页面：
- 添加 Topics: `raspberry-pi`, `poetry`, `ai`, `camera`, `thermal-printer`, `python`
- 添加项目描述
- 固定重要的 Issues/Discussions
- 添加 Wiki（如需要）

## 完成！

你的项目现在已经在 GitHub 上了！🎉
