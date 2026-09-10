# CHANGELOG

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
