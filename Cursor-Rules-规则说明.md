# Cursor Rules（规则）说明

> 官方文档：https://cursor.com/cn/docs/context/rules

---

## 什么是 Rules（规则）

Rules 为 Cursor 的 AI Agent 提供**系统级指令**。由于大语言模型在不同对话之间不保留记忆，Rules 在提示级别提供**持久、可重用的上下文**，应用后会被注入到模型上下文的开头，为 AI 在生成代码、理解编辑、协助工作流时提供一致的指导。

简单来说：**Rules = 你告诉 AI "在这个项目里应该怎么做事" 的持久化说明书。**

---

## 四种规则类型

| 类型 | 存放位置 | 适用范围 | 说明 |
|------|----------|----------|------|
| **Project Rules** | `.cursor/rules/` 目录 | 当前项目 | 受版本控制，可提交到 git，团队共享 |
| **User Rules** | Cursor Settings > Rules | 全局所有项目 | 个人偏好，如语言风格、编码习惯 |
| **Team Rules** | Cursor Dashboard 控制台 | 团队所有成员 | Team/Enterprise 方案，管理员集中管理 |
| **AGENTS.md** | 项目根目录或子目录 | 当前项目 | 纯 Markdown，`.cursor/rules` 的简洁替代方案 |

---

## Project Rules 详解

### 文件结构

```
.cursor/rules/
├── react-patterns.mdc       # 带 frontmatter 的规则（可指定 globs）
├── api-guidelines.md         # 简单 markdown 规则
└── frontend/
    └── components.md         # 可用文件夹组织
```

### 规则的四种应用方式

| 类型 | 行为 |
|------|------|
| **Always Apply** | 每个聊天会话都自动应用 |
| **Apply Intelligently** | Agent 根据描述判断是否相关，自动决定 |
| **Apply to Specific Files** | 文件匹配指定 glob 模式时应用（如 `*.tsx`） |
| **Apply Manually** | 在对话中通过 `@规则名` 手动引用时才应用 |

### 规则文件格式示例

```markdown
---
description: "前端组件开发规范"
globs: "src/components/**/*.tsx"
alwaysApply: false
---

- 使用 TypeScript 编写所有组件
- 优先使用函数式组件
- 组件文件名使用 PascalCase
- 每个组件需要导出 Props 类型定义
```

- `alwaysApply: true` 则每次对话都生效
- `alwaysApply: false` 则 Agent 根据 `description` 智能判断是否需要

### 创建方式

- 命令面板输入 `New Cursor Rule`
- 或在 `Cursor Settings > Rules, Commands` 中创建

---

## AGENTS.md（简洁替代方案）

放在项目根目录，纯 Markdown，无需 frontmatter：

```markdown
# Project Instructions

## Code Style
- Use TypeScript for all new files
- Prefer functional components in React
- Use snake_case for database columns

## Architecture
- Follow the repository pattern
- Keep business logic in service layers
```

支持嵌套：子目录中也可以放 `AGENTS.md`，对该目录下的代码生效。

---

## User Rules（用户规则）

在 `Cursor Settings > Rules` 中定义，全局生效，例如：

```
请以简洁风格回复。避免不必要的重复或冗余语言。
始终使用中文与我交流。
```

---

## 最佳实践

### 应该做的

- 规则控制在 500 行以内
- 大规则拆分为多个可组合的小规则
- 提供具体示例或引用参考文件
- 像写清晰的内部文档那样写规则
- 提交到 git，团队共享
- 发现 Agent 反复犯错时再添加规则

### 不应该做的

- 整篇照搬风格指南（用 linter 代替）
- 逐条列出所有 CLI 命令（Agent 已经知道 npm、git 等）
- 为极少出现的边缘情况添加说明
- 复制代码到规则中（应引用文件路径）

---

## 优先级顺序

```
Team Rules > Project Rules > User Rules
```

当多条规则存在冲突时，排在前面的来源优先级更高。

---

## 总结

如果你想在 NL2SQL 项目中让 AI 遵循特定编码规范或工作流，可以在 `.cursor/rules/` 中创建规则文件，例如指定技术栈、代码风格、项目结构约定等。
