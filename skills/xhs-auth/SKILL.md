---
name: xhs-auth
description: |
  小红书认证管理技能。检查登录状态、登录（二维码或手机号）、多账号管理。
  当用户要求登录小红书、检查登录状态、切换账号时触发。
version: 0.0.1.dev
---

# xhs-auth

## 命令列表

所有命令支持全局参数 `--account <名称>`（写在子命令之前）来指定账号。

| 命令 | 主要参数 | 返回 |
|------|----------|------|
| `check-login` | — | `{logged_in, login_method?, qrcode_image_url?, qr_login_url?, qrcode_path?}` |
| `get-qrcode` | — | `{qrcode_image_url, qr_login_url}` |
| `wait-login` | — | `{logged_in}` |
| `login` | — | `{logged_in}`（阻塞等待，适合本地终端） |
| `send-code` | `--phone` | `{status: "code_sent"}` 或频率限制时返回二维码字段 |
| `verify-code` | `--code` | `{logged_in}` |
| `phone-login` | — | 交互式，仅适合本地终端 |
| `delete-cookies` | — | `{success}` |
| `add-account` | `--name`，`[--description]` | `{success, name, port, profile_dir}` |
| `list-accounts` | — | `{count, accounts: [{name, port}]}` |
| `remove-account` | `--name` | `{success}` |
| `set-default-account` | `--name` | `{success}` |

## 登录流程

### 第一步：检查登录状态

```bash
uv run python scripts/cli.py check-login
```

- `logged_in: true` → 已登录，直接继续
- `login_method: "qrcode"` → 有显示器，响应中已自动包含二维码字段
- `login_method: "both"` → 无显示器/无头环境，询问用户选择二维码还是手机验证码

**`check-login` 未登录时会自动返回二维码，无需单独调用 `get-qrcode`。**

### 二维码登录

从 `check-login` 响应中取出以下两个字段，**必须同时展示**：

- `qrcode_image_url` → 嵌入为图片
- `qr_login_url` → 展示为可点击链接（"也可在手机浏览器直接访问此链接"）

然后等待登录（单次阻塞调用，无需轮询）：

```bash
uv run python scripts/cli.py wait-login   # 最多阻塞 120 秒
```

二维码过期后调用 `get-qrcode` 刷新，再重新运行 `wait-login`。

### 手机验证码登录（分两步）

```bash
uv run python scripts/cli.py send-code --phone <手机号>
uv run python scripts/cli.py verify-code --code <6位验证码>
```

若 `send-code` 返回频率限制，响应中会包含二维码字段，改用二维码登录并调用 `wait-login`。

## 必须向用户询问

- 调用 `send-code` 前：**必须询问用户手机号**，禁止从上下文或历史记录中自动推断
- 调用 `verify-code` 前：询问用户收到的短信验证码

## 退出码

`0` 成功 · `1` 未登录 · `2` 错误
