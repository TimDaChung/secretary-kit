---
name: secretary-setup
description: 個人 Slack 秘書安裝精靈。引導使用者從零裝好自己的秘書(建 Slack bot、設 token、連 MCP、填設定、試跑)。每次啟動先自動診斷目前卡在哪一關,只給下一步的操作與連結。觸發詞:「安裝秘書」「秘書安裝」「裝秘書」「檢查安裝進度」「setup secretary」。
---

# 秘書安裝精靈

目的:讓組員在自己的電腦上裝好個人版 Slack 秘書(`secretary` skill)。
核心原則:**每次啟動先跑進度診斷,找出第一個沒過的關卡,只教那一關**——不一次倒完全部步驟。能替使用者做的直接做(查 ID、寫檔、測 token),要去網頁點的給連結+逐步操作。

## 前置說明(第一次啟動時講一次)

- 秘書跑在**你自己的 Claude Code 終端**裡:終端關閉=排程全停,上班時間電腦與該視窗要開著
- 每 30-60 分鐘掃一輪會消耗 Claude 用量,方案等級低的建議把掃描頻率調低
- 全程用的是**你自己的** Slack 帳號與 bot,和別人的秘書互不相干

## 進度診斷(每次啟動先跑,依序檢查)

第一個 ❌ 就是當前關卡,輸出 checklist 後直接進入該關教學:

1. **技能檔案**:`~/.claude/skills/secretary/SKILL.md` 與 `config.json` 存在?
2. **Bot token**:環境變數 `SLACK_BOT_TOKEN` 讀得到?`curl auth.test` 回 `ok:true`?(順手記下 bot 的 `user_id`)
3. **Slack MCP**:ToolSearch 查 `mcp__claude_ai_Slack__slack_search_users` 可用?可用就搜自己名字驗證+記下自己的 user ID
4. **Google Calendar MCP**(選配):ToolSearch 查 `mcp__claude_ai_Google_Calendar__list_calendars`;沒連只提醒「日曆功能停用」,不擋關
5. **Bot DM 通道**:用 bot token `conversations.open`(users=自己的 user ID)→ 發一句測試訊息成功?
6. **config.json 完成度**:必填欄位(user_id / bot 資訊 / watchlist / 作息時間)都有值?
7. 全過 → 進「試跑」

輸出格式:
```
✅ 1. 技能檔案
✅ 2. Bot token
❌ 3. Slack MCP ← 你卡在這
⬜ 4-7 (後面的關卡)
```

## 關卡教學

### 關卡 1:安裝技能檔案(git 安裝法)

1. **前置**:`git --version` 檢查;沒裝 → `winget install --id Git.Git`(或到 https://git-scm.com 下載)
2. **Clone repo**:
   ```
   git clone https://github.com/TimDaChung/secretary-kit.git %USERPROFILE%\secretary-kit
   ```
3. **建 junction**(讓 skills 資料夾直接指向 repo 內的資料夾,之後 `git pull` 即升級,不用重複複製)。二擇一:
   - cmd(`mklink` 只在 cmd 有效):
     ```
     mklink /J "%USERPROFILE%\.claude\skills\secretary" "%USERPROFILE%\secretary-kit\secretary"
     mklink /J "%USERPROFILE%\.claude\skills\secretary-setup" "%USERPROFILE%\secretary-kit\secretary-setup"
     ```
   - PowerShell:
     ```powershell
     New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\secretary" -Target "$env:USERPROFILE\secretary-kit\secretary"
     New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\secretary-setup" -Target "$env:USERPROFILE\secretary-kit\secretary-setup"
     ```
4. **首裝初始化**(在 `secretary\` 內複製,兩個個人檔都已 gitignore,不會被 pull 覆蓋):
   - `templates.example.md` → 複製成 `templates.md`
   - `config.example.json` → 複製成 `config.json`(內容由後續關卡問答式代填)

**zip 備援**:沒有 git 也能裝——跟 Tim 要最新版 zip,解壓後把 `secretary/` 與 `secretary-setup/` 複製到 `~/.claude/skills/`,再做上面第 4 步;差別只在不能用「秘書升級」一鍵升級,更新要重新拿 zip。

### 關卡 2:建立 Slack Bot 並拿 token
1. 開 https://api.slack.com/apps → **Create New App** → **From an app manifest** → workspace 選 **Gamesofa** → 貼下方 manifest(app 名稱把 `<你的名字>` 改掉):
```yaml
display_information:
  name: <你的名字>-secretary
  description: personal secretary bot
features:
  bot_user:
    display_name: <你的名字>-secretary
    always_online: true
oauth_config:
  scopes:
    bot:
      - chat:write
      - im:write
      - users:read
    user:
      - users.profile:write
      - reactions:write
settings:
  org_deploy_enabled: false
  socket_mode_enabled: false
```
2. 建立後 → 左側 **Install App** → **Install to Workspace** → 授權
   - 若顯示「Request to install / 需要管理員核准」→ 送出申請,等核准信再回來繼續(這是全流程唯一可能要等人的地方)
3. 安裝完成後複製兩個 token → 進關卡 3:**Bot User OAuth Token**(`xoxb-` 開頭)與 **User OAuth Token**(`xoxp-` 開頭,會議/請假自動切狀態與 react 口令用)

### 關卡 3:設 token 環境變數
PowerShell 執行(token 換成自己的):
```powershell
setx SLACK_BOT_TOKEN "xoxb-你的token"
setx SLACK_USER_TOKEN "xoxp-你的token"
```
然後**完全關掉 Claude Code 終端重開**(setx 只對新視窗生效)。重開後回來說「檢查安裝進度」,我會用 `auth.test` 驗證。

### 關卡 4:連 Slack MCP(你的個人帳號)
1. 在 Claude Code 輸入 `/mcp` 看 claude.ai Slack 連線狀態
2. 未連線 → 到 https://claude.ai/settings/connectors 把 **Slack** 連上,登入自己的 Gamesofa 帳號並授權
3. 回終端 `/mcp` 確認已連,回來說「檢查安裝進度」驗證

### 關卡 5:連 Google Calendar 與 Gmail MCP(皆選配)
同關卡 4,在 https://claude.ai/settings/connectors 連 **Google Calendar** 與 **Gmail**,登入公司 Google 帳號。跳過 Calendar → 行程提醒只吃手動備忘,不吃日曆;跳過 Gmail → 下班結算沒有「限時信」段,其餘照常。

### 關卡 6:填 config.json
問答式逐項幫使用者填 `~/.claude/skills/secretary/config.json`(格式見 kit 內 `config.example.json`):
- `user_id`:我用 Slack MCP 搜你名字直接填
- `bot`:app ID / bot user ID(從 auth.test 拿)/ bot DM 頻道 ID(關卡 5 診斷時 conversations.open 拿到的)
- `watchlist`:問「哪些頻道的訊息你一定要知道?」(建議 2-4 個,我幫查頻道 ID)
- `schedule`:開工包/下班結算時間、掃描頻率(預設 09:03 / 18:27 / 30 分)
- `deputies`:請假時的代理人對照(可留空)
- `style`:語氣微調幾行(可留空 = 預設官方客氣語氣)+慣用 ack emoji

### 關卡 7:試跑
1. 發 bot DM:「🤖 你的秘書裝好了」→ 請使用者確認手機有跳通知
2. 跑一次完整掃描,產出第一份待回覆清單
3. 教三個口令就好:**「上班」**(開自動掃描)、**「下班」**、**「銷 N」**;其餘讓他用了再學

## 原則

- 一關驗證通過才給下一關;使用者跳著問也先跑診斷對齊現況
- 同一關卡住兩次(操作照做仍失敗)→ 停止重試,整理錯誤訊息與已試步驟,請使用者找 Tim
- 不碰使用者的既有 skills/settings,只寫 `skills/secretary/` 底下的檔案
