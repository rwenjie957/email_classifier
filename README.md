# email_classifier 使用说明
一个基于LLM的邮件分类器


## 配置步骤

### 1. IMAP 邮箱配置
编辑 `config_example.json`，填写您的邮箱信息：
```json
"userCredentials": {
    "imap_server": "imap.qq.com",      // 邮箱 IMAP 服务器
    "user": "your_email@qq.com",        // 邮箱账号
    "password": "your_password"         // 邮箱密码或授权码
}
```
- `default_directory`: 监听的邮箱文件夹（默认 INBOX）
- `policy`: 邮件过滤策略（UNSEEN = 仅未读邮件）

### 2. 分类类别
自定义要分类的邮件类型：
```json
"enabled_categories": [
    "bill",           // 账单
    "advertisment",   // 广告
    "reminder",       // 提醒
    "update",         // 更新
    "verification",   // 验证码
    "others"          // 其他
]
```

### 3. LLM 服务配置
配置分类使用的大模型服务：
```json
"llm_service": {
    "provider": "deepseek",                    // 服务商
    "base_url": "https://api.deepseek.com",    // API 地址
    "api_key": "your_api_key",                 // API 密钥
    "model": "deepseek-v4-flash",              // 模型名称
    "thinking": false                          // 是否启用思考模式
}
```

### 4. 日志配置
```json
"logs": {
    "log_dir": "log",              // 日志文件夹
    "file_log_level": "INFO",      // 文件日志级别
    "console_log_level": "DEBUG"   // 控制台日志级别
}
```

## 快速开始

1. 将 `config_example.json` 复制并重命名为 `config.json`
2. 按上述说明填写配置信息
3. 运行分类程序即可自动识别和分类邮件

## 支持的LLM厂商
目前仅支持
- DeepSeek

未来会支持更多模型