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

第一個 ❌ 就是當前卡點,輸出 checklist 後直接進入對應教學(診斷編號與關卡編號不是同一套:診斷 1→關卡 1、2→關卡 2–3、3→關卡 4、4→關卡 5、5→回關卡 2/3 查 bot token 與 `im:write`、6→關卡 6、7→關卡 7、8→關卡 8):

1. **技能檔案**:`~/.claude/skills/secretary/SKILL.md` 與 `config.json` 存在?
2. **Bot token**:環境變數 `SLACK_BOT_TOKEN` 讀得到?`curl auth.test` 回 `ok:true`?(順手記下 bot 的 `user_id`)
3. **Slack MCP**:ToolSearch 查 `mcp__claude_ai_Slack__slack_search_users` 可用?可用就搜自己名字驗證+記下自己的 user ID
4. **Google Calendar MCP**(選配):ToolSearch 查 `mcp__claude_ai_Google_Calendar__list_calendars`;沒連只提醒「日曆功能停用」,不擋關
5. **Bot DM 通道**:用 bot token `conversations.open`(users=自己的 user ID)→ 發一句測試訊息成功?
6. **config.json 完成度**:必填欄位 `user.user_id`、`user.name`、`workspace_url`、`schedule` 都有值?(與 secretary/SKILL.md 啟動檢查同一份清單)`bot` 三欄要嘛全填、要嘛全空——全空 = 停用 bot DM 報告,不擋關;`watchlist` 建議至少一個但非必填
7. **權限白名單**:`~/.claude/settings.json` 的 `permissions.allow` 陣列含 `CronCreate`、`CronList`、`CronDelete`、`PushNotification`、`ToolSearch` 五條?(**用 Read 讀檔判定,不能用 ToolSearch**——有無白名單工具都查得到,差別只在呼叫時跳不跳允許提示)
8. 全過 → 進「試跑」

輸出格式:
```
✅ 1. 技能檔案
✅ 2. Bot token
❌ 3. Slack MCP ← 你卡在這
⬜ 4-8 (後面的關卡)
```

## 關卡教學

### 關卡 1:安裝技能檔案(git 安裝法)

1. **前置**:`git --version` 檢查;沒裝 → **直接問一次「要不要我幫你裝?」**,同意就代跑 `winget install --id Git.Git`(或到 https://git-scm.com 下載)。`python --version` 同樣檢查(部分輔助腳本會用到):缺 → 一樣問一次,同意代跑 `winget install Python.Python.3.12`。任一 runtime 裝完提醒**完全重開終端**再打「檢查安裝進度」續關
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

**先問使用者走哪條路**:

**A. 自動路線**(使用者裝了 Claude in Chrome 擴充才可選):先告知「我會用你的 Chrome 開 Slack 設定頁代你操作;安裝授權(Allow)那一步是 OAuth 授權,會請你本人按」。步驟:
1. 確認 Chrome 已登入公司 Slack workspace
2. 開 https://api.slack.com/apps → 代按 **Create New App** → **From an app manifest** → 選 workspace → 代貼下方 manifest(`<你的名字>` 代填)→ Create
3. 左側 **Install App** → 代按 **Install to Workspace** → 跳出的**授權頁請使用者本人確認內容後自己按 Allow**(精靈不代按授權)
4. 授權完成後到 **OAuth & Permissions** 頁讀出兩顆 token → 直接代跑關卡 3 的 setx → 提醒重開終端
5. 若出現「Request to install / 需管理員核准」→ 代送申請即收工,等核准信後回來打「檢查安裝進度」續關

**B. 手動路線**(無擴充或不想被代操作):
1. 用**平常登入 Slack 的瀏覽器**開 https://api.slack.com/apps → 右上 **Create New App** → 選 **From an app manifest**(注意:不是 from scratch)→ workspace 下拉選公司的 → Next
2. 先把 manifest 裡兩處 `<你的名字>` 改成自己的英文名,整段貼進 YAML 框 → Next → Review 頁確認權限清單 → **Create**
3. 左側選單 **Install App** → **Install to Workspace** → 看完權限按 **Allow**
   - 顯示「Request to install / 需要管理員核准」→ 送出申請,等核准信再回來續關(全流程唯一可能等人的地方)
4. 安裝完成後左側 **OAuth & Permissions** 頁會有**兩顆 token,都要複製**:
   - **User OAuth Token**(`xoxp-` 開頭,頁面靠上)——切狀態、react 口令用
   - **Bot User OAuth Token**(`xoxb-` 開頭)——bot DM 報告用
   - 只看到一顆或空白 = Install 沒完成,回步驟 3

manifest(兩條路共用):
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
      - users.profile:read
      - reactions:write
      - reactions:read
      - chat:write
      - lists:read
      - files:read
settings:
  org_deploy_enabled: false
  socket_mode_enabled: false
```

**常見卡點**:
- 兩顆 token 分不清 → 看開頭:`xoxp`=User、`xoxb`=Bot;設反了關卡 3 驗證會抓出來
- token 頁一直顯示等待核准 → 管理員還沒按,催 IT
- manifest 貼上報錯 → 多半是 `<你的名字>` 沒改、或複製時縮排跑掉,整段重貼
- 授權後找不到 token → 重新整理 OAuth & Permissions 頁

### 關卡 3:設 token 環境變數
使用者把兩顆 token 貼到對話裡,精靈**直接代跑**(或使用者自己執行):
```powershell
setx SLACK_BOT_TOKEN "xoxb-你的token"
setx SLACK_USER_TOKEN "xoxp-你的token"
```
然後**完全關掉 Claude Code 終端重開**(setx 只對新視窗生效)。重開後打「檢查安裝進度」,精靈用 `auth.test` 分別驗兩顆:xoxb 應回 bot 名、xoxp 應回本人帳號,並檢查 xoxp 的 `x-oauth-scopes` 含 `reactions:write`、`reactions:read`、`users.profile:write`、`users.profile:read`、`chat:write`(舊裝機缺 `users.profile:read` 或 `reactions:read` 不擋關——前者切狀態改走 Slack MCP 讀現況、後者點名追蹤退化為只看 thread 回覆,結算整合健檢會提示補);驗證失敗最常見原因是兩顆設反——對調重設即可。

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
- `schedule`:開工包/下班結算時間、掃描頻率(預設 09:03 / 18:27 / 每 60 分;要固定幾點掃的改 `scan_mode: fixed` + `scan_times`,見 config.example.json 說明)
- `deputies`:請假時的代理人對照(可留空)
- `style`:語氣微調幾行(可留空 = 預設官方客氣語氣)+慣用 ack emoji

### 關卡 7:Claude Code 權限白名單

值班每輪都呼叫 `CronCreate` / `CronList` / `CronDelete` / `PushNotification` / `ToolSearch`(Claude Code 內建工具,排程與推播用)。沒進白名單就每次跳「允許?」,人不在終端前時整輪卡死(Tim 端掃 50 份值班 transcript:CronCreate 152 次、ToolSearch 178 次,每次都在等人按)。這 5 個只建排程、發推播、查工具 schema,不寫檔、不對外發送、不執行任意程式。

1. Read `~/.claude/settings.json`,看 `permissions.allow` 陣列(檔或陣列不存在 = 全缺);5 條都在 → ✅ 直接過
2. 缺 → **先講一句再動手**:「我要把 5 個排程工具加進 Claude Code 白名單(改 `~/.claude/settings.json`),接下來會跳允許提示,請按允許。如果你在 **auto 模式**,AI 改這個檔會被分類器直接擋、不會給你按允許的機會,請先按 Shift+Tab 切到 default 再跟我說『繼續』」
3. 用 Edit 把缺的條目補進 `permissions.allow`(**只補缺的、不動既有條目、不刪任何東西**;陣列或 `permissions` 物件不存在就建):
   ```json
   "CronCreate",
   "CronList",
   "CronDelete",
   "PushNotification",
   "ToolSearch",
   ```
4. 寫入被擋(auto 模式回 Self-Modification)或使用者不想讓 AI 碰 settings → **退手動,不重試、不繞**:印出上面 5 行,說明貼進 `permissions.allow` 陣列內任一位置即可;或請使用者打 `/permissions` → Allow 分頁逐條加
5. 改完**必須重開 Claude Code session 才生效**。重開後打「檢查安裝進度」,精靈重讀檔驗 5 條都在才算過

### 關卡 8:試跑

先提醒使用者:值班是長時間自動任務,值班終端的模型**固定由 `config.model.session` 決定,預設 sonnet**(啟動器 bat 讀取;精靈不代改,使用者自己想換才跟秘書說「秘書用 <模型>」);不用 bat、手動 `claude` 啟動的人要自己帶 `--model sonnet`。Pro 方案另可用口令「省量模式」降低用量。

1. 發 bot DM:「🤖 你的秘書裝好了」→ 請使用者確認手機有跳通知
2. 跑一次完整掃描,產出第一份待回覆清單
3. 教三個口令就好:**「上班」**(開自動掃描)、**「下班」**、**「銷 N」**;其餘讓他用了再學

**啟動器安裝(以上三步通過後收尾,精靈代做)**:
4. 複製 repo 根的 `secretary-start.bat` 到使用者桌面(**模型讀 `config.model.session`,預設 Sonnet**,之後換模型改 config 即可、不用重新複製 bat;含退出紀錄。檔名可改但**必須保持英數**——中文檔名+編碼問題會讓 cmd 閃退)
5. 問使用者「要不要開機自動值班?」要 → 再複製一份到 `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`;不要 → 跳過,之後隨時可補
6. 告知:之後上班雙擊桌面 bat 即可;視窗若異常關閉,死因記錄在 `~/.claude/secretary-exit.log`

### 選配關卡:回報單掃描(Slack List)

不在進度診斷 1-8 內、不擋裝機。時機:試跑通過後問一句「有沒有指派給你的 Slack List 回報單要一起盯?」,或使用者事後說「加回報單」「掃 List」時進入。**每一項都要問安裝者本人,不可沿用別人的設定值**:

0. **團隊預設捷徑**:`~/.claude/skills/secretary/team-defaults.json` 存在(隨 repo 發佈,只含 ID 不含內部名稱)→ 列出裡面的 report_lists(用 `_list_name`)問「要不要啟用團隊預設回報單?」,要 → 整包抄進 config.report_lists(assignee_user_id 留空 = 本人),跳到步驟 3 驗 scope 後直接步驟 7 試撈,步驟 1-2、4-6 全免
1. 問要不要啟用;**不要 → 寫 `report_lists: []` 跳過**
2. 要 → 請安裝者貼 List 網址 → 從網址解析 `team_id`(T 開頭)與 `list_id`(F 開頭)
3. **先驗 scope 再說**:用 user token 打一次 `files.info?file=<list_id>`——成功 = scope 已有(v1.10 後新裝的 manifest 內建),直接跳步驟 4;回 `missing_scope` = 舊裝機要補,走雙路線(同關卡 2 慣例):
   - **A. 自動**(有 Claude in Chrome):精靈代開該 App 的 OAuth & Permissions → 代加 User Token Scopes `lists:read` + `files:read` → 代按 Reinstall → **授權頁請使用者本人按 Allow** → 代讀新 token,字串有變就代跑 setx 並提醒重開終端
   - **B. 手動**:引導使用者自己到 OAuth & Permissions → User Token Scopes 加兩個 scope → Reinstall to Workspace → 更新 `SLACK_USER_TOKEN`(token 字串沒變則免)
4. 呼叫 `files.info?file=<list_id>` 讀 schema:
   - `assignee_col`:自動抓 `type=todo_assignee` 的欄;有多個或抓不到 → 列欄名讓安裝者選。**表上另有 user 型欄位(pm/client 等)→ 問一句要不要一併算指派**,要就改寫成 `assignee_cols` 陣列(任一欄含本人即列)
   - `status_col`:列出 `type=select` 的欄與其選項,讓安裝者指認哪欄是「狀態」
   - `name_col`:抓 `key=name`(摘要欄)
5. 列出 status 欄的選項,問**要排除哪些狀態**(如 修復完成/列觀察)→ 寫入 `exclude_status`
6. **指派對象預設 = 安裝者本人**(`assignee_user_id` 留空,runtime 用他自己的 `config.user.user_id`);只有要看別人的才填
7. 寫入 `config.report_lists`,試跑一次確認能撈到。寫入結構(值為佔位範例):

```json
"report_lists": [
  {
    "enabled": true,
    "section_title": "【回報單待處理】",
    "list_id": "F0XXXXXXXXX",
    "team_id": "T0XXXXXXXXX",
    "assignee_col": "ColXX",
    "status_col": "ColXX",
    "name_col": "ColXX",
    "assignee_user_id": "",
    "exclude_status": ["修復完成", "列觀察"],
    "show_in": ["morning", "evening"]
  }
]
```

## 原則

- 一關驗證通過才給下一關;使用者跳著問也先跑診斷對齊現況
- 同一關卡住兩次(操作照做仍失敗)→ 停止重試,整理錯誤訊息與已試步驟,請使用者找 Tim
- 不碰使用者的既有 skills/settings,只寫 `skills/secretary/` 底下的檔案。**唯一例外**:關卡 7 補 `~/.claude/settings.json` 的 5 條排程工具白名單——只增不刪、先講再改、被擋就退手動
