# 用户和主人识别插件

## 安装

配置完成 [LangBot](https://github.com/RockChinQ/LangBot) 主程序后使用管理员账号向机器人发送命令即可安装：

```
!plugin get https://github.com/sanxianxiaohuntun/QunID.git
```

或查看详细的[插件安装说明](https://docs.langbot.app/plugin/plugin-intro.html#%E6%8F%92%E4%BB%B6%E7%94%A8%E6%B3%95)

## 功能说明

本插件可以在用户发送消息时自动添加用户身份信息，使大模型能够识别发送者的身份和昵称，还可以设置主人身份标识。

主要功能：
- 在群聊中显示用户的群昵称
- 在私聊中显示用户的备注名或昵称
- 支持通过YAML配置文件设置私聊白名单
- 支持开启/关闭群聊和私聊识别功能
- 白名单中的用户在私聊时消息不会被修改（可选添加时间提示）
- 可以设置主人ID，让AI知道谁是主人

### 配置说明

插件会在`plugins/QunID`目录下创建`settings.yaml`配置文件，用于设置插件的行为。你可以手动编辑此文件以自定义插件功能。

#### 完整配置参考

```yaml
# 私聊白名单用户ID列表（白名单中的用户在私聊时不会被添加用户标识格式）
private_whitelist:
  - '123456789'  # 第一个白名单用户，请替换为实际QQ号
  - '987654321'  # 第二个白名单用户，请替换为实际QQ号
# 群聊识别开关（true开启，false关闭）
group_enable: true
# 私聊识别开关（true开启，false关闭）
private_enable: true
# 忽略的消息前缀列表（以这些前缀开头的消息不会被添加用户标识）
ignore_prefixes:
  - "!"
  - "！"
  - "/"
  - "搜漫画"
  - "看漫画"
  - "&"
  - "漫画帮助"
  - "视频帮助"
  - "视频"
  - "里番帮助"
  - "里番"
# 白名单用户时间提示开关（true开启，false关闭）
whitelist_time_hint: true
# 私聊识别关闭时是否添加时间提示开关（true开启，false关闭）
private_disable_time_hint: true
# 主人ID设置（用于标识主人身份）
master_id: '123456789'
```

#### 私聊白名单设置

在`private_whitelist`列表中添加用户QQ号，这些用户在私聊时消息将不会被添加用户标识格式。可以根据`whitelist_time_hint`设置决定是否添加时间提示。

#### 功能开关

- `group_enable`: 控制群聊识别功能（true开启，false关闭）
- `private_enable`: 控制私聊识别功能（true开启，false关闭）

#### 忽略前缀设置

`ignore_prefixes`列表中的前缀，如果消息以这些前缀开头，将不会被添加用户标识。适用于命令、特殊功能触发词等。

#### 时间提示设置

- `whitelist_time_hint`: 控制白名单用户是否接收时间提示（true开启，false关闭）
- `private_disable_time_hint`: 当私聊识别功能关闭时，是否仍添加时间提示（true开启，false关闭）

#### 主人设置

`master_id`：设置主人的QQ号，设置后AI将能够识别谁是主人。消息末尾会添加以下提示之一：
- 当前是主人(昵称)和你对话 — 当消息发送者是主人时
- 当前并非主人(主人)和你对话 — 当消息发送者不是主人时

### 注意事项

1. 修改配置文件后，需要重新启动插件才能生效
2. 数字ID建议用引号包裹（如'123456789'）以避免大数字被科学计数法表示
3. 保持YAML格式的正确性，特别是缩进和冒号后的空格
4. 不要删除配置项，如果不需要某功能，将其设置为false或空列表[]即可

## 使用场景

1. **普通聊天**: 自动标识不同用户的身份，方便AI区分对话者
2. **主人识别**: 设置主人ID后，AI能够识别主人身份，可以据此提供不同的服务
3. **特殊用户**: 将需要直接与AI对话的用户添加到私聊白名单
4. **命令前缀**: 自定义忽略前缀，确保命令和特殊功能不受影响

## 截图

![使用效果](https://raw.githubusercontent.com/sanxianxiaohuntun/wodecuntu12/refs/heads/main/f732bba4b68fca26c49f0558da77e408.png)

## 更新日志
- v0.3: 解决不能识图问题。
- v0.2: 新增主人识别功能，支持在对话中标识主人身份。
- v0.1: 初始版本，支持用户身份识别和时间提示。

<!--
## 插件开发者详阅

### 开始

此仓库是 LangBot 插件模板，您可以直接在 GitHub 仓库中点击右上角的 "Use this template" 以创建你的插件。  
接下来按照以下步骤修改模板代码：

#### 修改模板代码

- 修改此文档顶部插件名称信息
- 将此文档下方的`<插件发布仓库地址>`改为你的插件在 GitHub· 上的地址
- 补充下方的`使用`章节内容
- 修改`main.py`中的`@register`中的插件 名称、描述、版本、作者 等信息
- 修改`main.py`中的`MyPlugin`类名为你的插件类名
- 将插件所需依赖库写到`requirements.txt`中
- 根据[插件开发教程](https://docs.langbot.app/plugin/dev/tutor.html)编写插件代码
- 删除 README.md 中的注释内容


#### 发布插件

推荐将插件上传到 GitHub 代码仓库，以便用户通过下方方式安装。   
欢迎[提issue](https://github.com/RockChinQ/LangBot/issues/new?assignees=&labels=%E7%8B%AC%E7%AB%8B%E6%8F%92%E4%BB%B6&projects=&template=submit-plugin.yml&title=%5BPlugin%5D%3A+%E8%AF%B7%E6%B1%82%E7%99%BB%E8%AE%B0%E6%96%B0%E6%8F%92%E4%BB%B6)，将您的插件提交到[插件列表](https://github.com/stars/RockChinQ/lists/qchatgpt-%E6%8F%92%E4%BB%B6)

下方是给用户看的内容，按需修改
-->
