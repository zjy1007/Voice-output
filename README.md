# Voice-output 智能语音输入法 MVP

## 一、项目简介

本项目是一款面向学习、办公和日常输入场景的智能语音输入法产品，目标是帮助用户通过语音快速完成文本输入，提高文本输入效率。

系统支持用户通过网页端录制语音，并将语音上传至后端进行识别。后端完成语音转文字后，会进一步进行自动标点、文本优化、场景化整理和热词纠错，最终将更自然、更易读的文本结果返回给用户。

本项目不仅实现了基础的“语音转文字”功能，还围绕实际输入法使用体验，设计了场景模式、自定义热词、输入历史、快捷复制等功能，形成了从语音输入到文本编辑的完整闭环。

---

## 二、功能亮点

### 1. 语音输入闭环完整

系统支持完整的语音输入流程：

```text
开始录音 → 停止录音 → 上传音频 → 语音识别 → 文本优化 → 展示结果 → 编辑/复制/保存
```

用户可以通过点击按钮完成语音录入，并在页面中查看识别后的文本结果。

---

### 2. 自动标点与断句

系统会对识别出的原始文本进行自动标点和断句处理，使输出结果更符合正常阅读习惯。

示例：

```text
原始识别：
今天下午三点我们开会讨论语音输入法开发计划然后整理需求

优化后：
今天下午三点，我们开会讨论语音输入法开发计划，并整理相关需求。
```

---

### 3. 场景化文本优化

系统支持不同输入场景，根据用户选择的模式输出不同风格的文本。

| 模式 | 适用场景 | 输出特点 |
|---|---|---|
| 普通输入 | 聊天、搜索、日常记录 | 保留自然表达 |
| 办公模式 | 会议纪要、工作汇报 | 表达更正式、语句更完整 |
| 学习笔记 | 课堂记录、知识整理 | 自动整理为条目化内容 |

示例：

```text
用户语音：
语音输入法主要要考虑准确率速度成本还有易用性

学习笔记模式输出：
语音输入法需要重点考虑以下因素：
1. 准确率；
2. 响应速度；
3. 使用成本；
4. 易用性。
```

---

### 4. 自定义热词

用户可以添加常用词、专业词、人名、项目名等热词，用于提升特定场景下的识别和纠错效果。

例如：

```text
语音输入法
ASR
Whisper
开发计划书
人工智能
```

---

### 5. 快捷编辑与历史记录

系统支持对识别结果进行快捷操作：

- 一键复制；
- 一键清空；
- 继续追加输入；
- 删除上一段；
- 保存输入历史；
- 查看历史记录。

---

## 三、技术架构

本项目采用前后端分离架构。

```text
用户
 ↓
前端 Web 页面
 ↓
音频采集与上传
 ↓
后端 FastAPI 服务
 ↓
ASR 语音识别模块
 ↓
文本优化模块
 ↓
热词纠错 / 场景化整理
 ↓
返回最终文本
 ↓
前端展示与编辑
```

### 1. 前端

前端主要负责：

- 麦克风权限申请；
- 音频录制；
- 录音状态展示；
- 音频上传；
- 识别结果展示；
- 场景模式选择；
- 热词管理；
- 历史记录展示；
- 复制、清空、编辑等交互。

推荐技术栈：

```text
React / Vue
TypeScript
Axios
Web Audio API / MediaRecorder API
Vite
```

### 2. 后端

后端主要负责：

- 接收前端上传的音频；
- 调用语音识别服务；
- 对识别结果进行文本优化；
- 管理用户热词；
- 保存输入历史；
- 统一返回接口结果。

推荐技术栈：

```text
Python
FastAPI
Uvicorn
Pydantic
SQLite
Whisper / Faster-Whisper / FunASR / 第三方 ASR API
```

---

## 四、目录结构

```text
voice-input-method/
├── frontend/                         # 前端项目
│   ├── src/
│   │   ├── api/                       # 接口请求封装
│   │   │   ├── asr.ts
│   │   │   ├── hotword.ts
│   │   │   └── history.ts
│   │   ├── components/                # 页面组件
│   │   │   ├── RecorderButton.tsx     # 录音按钮
│   │   │   ├── TranscriptEditor.tsx   # 识别结果编辑区
│   │   │   ├── ModeSelector.tsx       # 场景模式选择
│   │   │   ├── HotwordPanel.tsx       # 热词管理面板
│   │   │   ├── HistoryList.tsx        # 历史记录列表
│   │   │   └── ResultToolbar.tsx      # 复制、清空、保存工具栏
│   │   ├── hooks/                     # 自定义 Hook
│   │   │   └── useRecorder.ts         # 录音逻辑封装
│   │   ├── pages/                     # 页面
│   │   │   └── HomePage.tsx
│   │   ├── utils/                     # 工具函数
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                          # 后端项目
│   ├── app/
│   │   ├── main.py                    # FastAPI 入口
│   │   ├── routers/                   # 路由模块
│   │   │   ├── asr.py                 # 语音识别接口
│   │   │   ├── text.py                # 文本优化接口
│   │   │   ├── hotword.py             # 热词接口
│   │   │   └── history.py             # 历史记录接口
│   │   ├── services/                  # 业务服务
│   │   │   ├── asr_service.py         # ASR 识别服务
│   │   │   ├── text_service.py        # 文本优化服务
│   │   │   ├── hotword_service.py     # 热词服务
│   │   │   └── history_service.py     # 历史记录服务
│   │   ├── schemas/                   # 请求与响应模型
│   │   ├── utils/                     # 音频处理、通用工具
│   │   └── database.py                # 数据库连接
│   ├── tests/                         # 测试用例
│   ├── requirements.txt
│   └── README.md
│
├── docs/                             # 项目文档
│   ├── product_design.md              # 产品设计文档
│   ├── technical_design.md            # 技术架构文档
│   └── demo_script.md                 # Demo 演示脚本
│
├── README.md                         # 项目总说明
├── .gitignore
└── LICENSE
```

---

## 五、环境依赖

### 1. 前端环境

```bash
Node.js >= 18
npm >= 9
```

### 2. 后端环境

```bash
Python >= 3.9
FastAPI
Uvicorn
Pydantic
python-multipart
SQLite
```

### 3. ASR 依赖

根据实际选择的语音识别方案安装依赖。

如果使用 Whisper / Faster-Whisper：

```bash
pip install faster-whisper
```

如果使用第三方 ASR API，需要在环境变量中配置 API Key：

```bash
ASR_API_KEY=your_api_key
ASR_API_URL=your_api_url
```

---

## 六、启动方式

### 1. 克隆项目

```bash
git clone https://github.com/your-name/voice-input-method.git
cd voice-input-method
```

---

### 2. 启动后端

```bash
cd backend

python -m venv venv

source venv/bin/activate
# Windows 用户可使用：
# venv\Scripts\activate

pip install -r requirements.txt

cd /Users/zhangjinyang/Desktop/voice-output/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端启动成功后，访问：

```text
http://localhost:8000/docs
```

可以查看 FastAPI 自动生成的接口文档。

---

### 3. 启动前端

```bash
cd frontend

npm install

npm run dev
```

前端启动成功后，访问：

```text
http://localhost:5173
```

---

## 七、接口说明

### 1. 语音识别接口

```http
POST /api/asr/transcribe
```

功能：上传音频文件，返回语音识别结果。

请求参数：

| 参数名 | 类型 | 说明 |
|---|---|---|
| file | File | 用户录制的音频文件 |
| mode | string | 输入模式，如 normal、office、study |

返回示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "raw_text": "今天下午三点我们开会讨论语音输入法开发计划",
    "optimized_text": "今天下午三点，我们开会讨论语音输入法开发计划。"
  }
}
```

---

### 2. 文本优化接口

```http
POST /api/text/optimize
```

功能：对识别文本进行标点、断句和场景化优化。

请求示例：

```json
{
  "text": "语音输入法主要要考虑准确率速度成本还有易用性",
  "mode": "study"
}
```

返回示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "optimized_text": "语音输入法需要重点考虑以下因素：\n1. 准确率；\n2. 响应速度；\n3. 使用成本；\n4. 易用性。"
  }
}
```

---

### 3. 获取热词列表

```http
GET /api/hotwords
```

返回示例：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    "语音输入法",
    "ASR",
    "Whisper",
    "人工智能"
  ]
}
```

---

### 4. 添加热词

```http
POST /api/hotwords
```

请求示例：

```json
{
  "word": "开发计划书"
}
```

返回示例：

```json
{
  "code": 200,
  "message": "hotword added",
  "data": {
    "word": "开发计划书"
  }
}
```

---

### 5. 获取历史记录

```http
GET /api/history
```

返回示例：

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "text": "今天下午三点，我们开会讨论语音输入法开发计划。",
      "mode": "office",
      "created_at": "2026-05-23 10:00:00"
    }
  ]
}
```

---

### 6. 保存历史记录

```http
POST /api/history
```

请求示例：

```json
{
  "text": "今天下午三点，我们开会讨论语音输入法开发计划。",
  "mode": "office"
}
```

返回示例：

```json
{
  "code": 200,
  "message": "history saved",
  "data": {
    "id": 1
  }
}
```

---

## 八、测试方法

### 1. 后端测试

进入后端目录：

```bash
cd backend
pytest tests/
```

建议测试内容包括：

- 语音上传接口是否正常；
- 文本优化接口是否正常；
- 热词添加和查询是否正常；
- 历史记录保存和查询是否正常；
- 异常输入是否能正确返回错误信息。

---

### 2. 前端测试

前端主要测试页面交互流程：

```text
1. 打开首页；
2. 点击开始录音；
3. 授权麦克风权限；
4. 说一段测试语音；
5. 点击停止录音；
6. 查看识别结果；
7. 切换不同场景模式；
8. 添加热词；
9. 测试复制、清空、保存历史功能。
```

---

### 3. 接口测试

可以使用 FastAPI 文档页面测试：

```text
http://localhost:8000/docs
```

也可以使用 curl 测试：

```bash
curl -X POST "http://localhost:8000/api/text/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "语音输入法主要要考虑准确率速度成本还有易用性",
    "mode": "study"
  }'
```

---

### 4. 功能测试用例

| 测试项 | 输入 | 预期结果 |
|---|---|---|
| 普通语音识别 | 一句普通话语音 | 返回对应文字 |
| 自动标点 | 无标点长句 | 自动添加逗号、句号 |
| 办公模式 | 口语化会议内容 | 输出更正式文本 |
| 学习笔记模式 | 知识点描述 | 输出条目化内容 |
| 热词识别 | 包含专业词的语音 | 优先保留热词 |
| 清空文本 | 点击清空按钮 | 文本框内容为空 |
| 保存历史 | 点击保存按钮 | 历史记录中出现该文本 |
| 异常录音 | 未授权麦克风 | 提示用户开启权限 |

---

## 九、Demo 展示

### 1. Demo 展示流程

Demo 视频建议按照以下顺序展示：

```text
1. 打开系统首页；
2. 简要介绍产品目标；
3. 展示普通语音输入；
4. 展示识别结果自动标点；
5. 切换办公模式并展示正式化输出；
6. 切换学习笔记模式并展示条目化输出；
7. 添加自定义热词；
8. 再次输入包含热词的语音；
9. 展示复制、清空、保存历史功能；
10. 简要展示代码结构和接口文档；
11. 总结作品亮点。
```

---

### 2. Demo 讲解重点

本项目 Demo 主要展示以下能力：

- 完整语音输入流程；
- 语音识别与文本优化效果；
- 场景化输入模式；
- 自定义热词提升识别效果；
- 前后端分离架构；
- 清晰的接口设计；
- 可运行、可测试、可扩展的工程结构。

---

## 十、后续优化方向

### 1. 支持实时流式识别

当前 MVP 可以先采用“录音结束后上传识别”的方式。后续可引入 WebSocket，实现边说边识别，降低用户等待时间。

---

### 2. 支持离线识别

为了提升隐私性和降低云端调用成本，后续可以接入本地 ASR 模型，例如：

```text
Faster-Whisper
FunASR
Sherpa-ONNX
Vosk
```

实现本地语音识别。

---

### 3. 优化热词机制

后续可以将热词机制从简单文本替换升级为更智能的上下文纠错，例如：

- 根据拼音相似度纠错；
- 根据用户历史输入纠错；
- 根据场景词库纠错；
- 支持行业词库导入。

---

### 4. 支持真正的系统输入法

当前版本主要是 Web MVP。后续可以开发 Android 输入法版本，将识别结果直接输入到任意文本框中。

---

### 5. 增加多语言和中英文混合输入

后续可以支持：

- 普通话；
- 英文；
- 中英文混合；
- 方言识别；
- 专业术语识别。

---

### 6. 增加用户系统

后续可以加入用户登录能力，实现：

- 个人热词同步；
- 输入历史同步；
- 用户偏好保存；
- 多设备使用。

---

### 7. 增加评估指标面板

为了更好展示作品质量，可以增加一个评估页面，展示：

- 平均识别耗时；
- 字错误率；
- 使用次数；
- 热词命中次数；
- 不同模式使用比例。

---

## 十一、项目亮点总结

本项目围绕“提高文本输入效率”这一目标，完成了一款智能语音输入法 MVP。系统不仅实现了语音识别基础能力，还进一步加入自动标点、场景化文本优化、自定义热词和输入历史等功能，使产品更加完整、实用和具有创新性。

在工程实现上，项目采用前后端分离架构，模块划分清晰，接口设计规范，具备良好的可维护性和扩展性。后续可继续扩展实时流式识别、离线识别、移动端输入法和多语言输入等能力。
