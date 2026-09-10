# CHANGELOG

## v1.8.0 (2026-09-10)

- **省量模式(給 Pro 方案)**:口令「省量模式/標準模式」——掃描間隔×2、bot 訊息平時只列變化;額度撞牆時自動降頻一天並通知
- 文件加 Pro 省量建議(Sonnet 值班/省量模式/無視吵群);安裝精靈試跑關卡加 Sonnet 提醒

## v1.7.0 (2026-09-10)

- **專案里程碑管理**:多 ETA 時程(美術/工程/內測/上線)口令建案;T-7 才浮出、T-3/T-1/當天連續提醒、逾期追認;改期/逾期自動算下游壓縮(「內測只剩 N 天,原 M 天」);只出現在開工包/結算,平時沉默
- **安裝精靈關卡 2/3 重寫**:新增 Chrome 代操作路線(建 app/貼 manifest/讀 token 全代辦,唯 OAuth 授權 Allow 由本人按);手動路線步驟加細+常見卡點(token 分不清/等核准/manifest 報錯);token 驗證改分顆檢查+scope 檢查

## v1.6.0 (2026-09-10)

- **秘書喊話偵測放寬**(原「秘書筆記偵測」):除「記一下」家族外,新認「秘書+任意委派動詞」(分析/查/整理/處理等)→ 依產出去向分級:對內(分析/整理給你看)直接做完發 DM;對外(以你名義發言)擬好等確認才送

## v1.5.1 (2026-09-10)

- 修 Slack 掃描週末漏洞:起點一律 = last_run(上限 7 天),不再固定 24 小時
- 信箱檢查首次啟用預設回補 3 天積壓
- 掃描 subagent 改讀整份 SKILL(原漏「狀態自動回覆」「會議同步日曆」「欠款逾時」等節,恐默默失效)
- P0 推播改由主 session 發(subagent 發可能推不到終端)
- open 清單為空時跳過全部 react 搜尋(每輪省 4 次 search)

## v1.5.0 (2026-09-10)

- **信箱檢查改寬版三段式**(原「限時信檢查」):要行動/有期限(近期到期寫備忘)+值得知道 FYI(重要來源/自家產品非例行信)+疑似釣魚單獨警示;動態天數補週末假期;簽核/審批類自動信不再被誤殺

## v1.4.0 (2026-09-10)

- **react 口令**:「react N :emoji:」「按 N 讚」以使用者身分按 react(需 user token 有 `reactions:write`);ack 類 emoji 順帶銷帳、pending 類標暫回;「按 N 確認中/請稍候」= 按 pending_emojis 第一顆(如 :loading:)
- 安裝精靈:manifest 加 user scopes(`users.profile:write`、`reactions:write`),關卡 2/3 改為同時拿 bot + user 兩個 token(舊裝機戶要補:app OAuth 設定加 scope → Reinstall → setx SLACK_USER_TOKEN)

## v1.3.0 (2026-09-10)

- **「確認中」暫回追蹤**:回「確認中/請稍等/請稍候」或按 pending emoji(config.style.pending_emojis,如 :loading:)不再視為已回——待辦標 ⏳ 掛著,超過 pending_timeout_hours(預設 4h)無實質回覆 → bot 提醒;下班結算列所有未結暫回項。config.style 新增 pending_emojis / pending_patterns / pending_timeout_hours

## v1.2.0 (2026-09-10)

- **行程撞期偵測**:開工包比對今日行程時間重疊,標「⚠️ 撞期:A × B」;中途新增行程撞到既有行程,提醒訊息同標
- **請假×會議比對**:預約請假當下查該日 Google 日曆,有行程就列出問要改期/取消/照開;請假日開工包標「🌴 請假日但有 N 場行程」。代改期/刪除僅限秘書自建([秘書] 前綴)的事件

## v1.1.0 (2026-09-10)

- **掃描改派 subagent 執行**(流程新增第 0 節):Slack 搜尋結果不再進主 session context,值班一整天 context 保持輕量、不觸發壓縮,token 用量明顯下降。主 session 只負責排程核對、讀 agent 摘要、補排 cron 與使用者口令
- 口令與掃描的寫檔衝突規則:agent 掃描中收到口令,等該輪寫完 state.json 再執行(單一寫者)

## v1.0.0 (2026-09-10)

首發:

- 核心掃描:DM + mentions + watchlist + 全 workspace @here,四路收集
- P0/P1/P2 分級與增量分流輸出、編號銷帳、React 銷帳、承諾偵測
- 狀態自動回覆(會議/請假模式)+ 代理人對照 + 模式結束補掃
- 回覆範本庫(templates)+ 秘書擬稿、使用者確認才發
- 每日節奏:晨間開工包 / 下班結算 / 午休排程(lunch_break 邊界掃)/ 假日不上班
- Google 日曆同步與會前提醒、bot DM 同步報告、P0 推播
- 安裝精靈(secretary-setup):進度診斷 + 逐關教學 + git 安裝
