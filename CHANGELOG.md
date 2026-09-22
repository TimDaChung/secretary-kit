# CHANGELOG

## v1.15.0 (2026-09-22)

- **新功能:Thread 續追**(修架構漏洞)——原本候選收集只靠 `to:me` 搜尋,**只命中有 @ 你的那一則**;對方在同一 thread 後續繼續討論但沒再 tag 你,秘書完全看不到。更糟的是你只要在那串回過一次,「同對話有發言 = 已回」的機械規則就把整組剔除,之後那串再長也不會回來。新增 `watched_threads[]`:來源是 thread 的待辦項、以及你發過言的 thread 自動入列,每輪用 `slack_read_thread` 帶 `oldest=<上次看過的 ts>` + `concise` **只取新訊息**(不重讀整串,這是成本關鍵),逐則判斷是否在等你 → 復活或新建待辦項。「銷 N」只銷該次,不停追那串;口令「停追串 N」才移出
- **三層降頻**(不是追/不追二分):① **活躍**(`active_hours` 72 小時內有人講話)跟著主掃描每輪追,上限 `max_threads` 50 串;② **觀察名單**(3 天沒動靜)降到**只在開工包與下班結算各查一次**(做法見 daily.md),有人講話就復活回 ①,上限 `observe_max` 50 串;③ 在觀察名單躺滿 `observe_days` 14 天仍無新發言 → 移出真正不追(純過期,之後被 tag 照樣重新入列)。設計理由:睡了三天的串不值得每 30 分查,但也不該就此失聯——放長假、擱置兩週再續的討論都接得回來
- **可調**:`config.thread_watch` = `{enabled, active_hours: 72, max_threads: 50, observe_days: 14, observe_max: 50}`。**刻意不設 thread 專屬掃描頻率**(兩套頻率會很亂):層 ① 跟主掃描走,層 ② 固定掛兩大輪。要省量調 `schedule.scan_interval_min` 或把兩個上限調小;省量模式(eco)下兩上限自動減半
- **停追的兩種待遇**:TTL 自然退場的串,對方再 tag 你自動恢復續追(睡著的串被叫醒);**手動「停追串 N」記進 `thread_watch_optout[]`**,之後被 tag 那則照常進清單但不恢復追整串——否則停追口令被一次 tag 架空。口令「重新追這串 N」可放回
- 追蹤數超過上限時清單尾註「thread 續追已滿,N 串未追」,不靜默截斷

⚙️ **升級動作**:`git pull` 後,**舊 config.json 缺 `thread_watch` 鍵會用預設值頂上並在整合健檢提示一次**,不會靜默失效;想改參數自行加進 config.json,或跟秘書說「thread 只追 10 串」「觀察名單留一週就好」。無新 scope。**額度增量**:層 ① 50 串 × 每 30 分一輪約 +100~170k tokens/天,層 ② 50 串 × 一天 2 次約 +15k/天(多數查詢回 0 則新訊息);Pro 方案建議 `max_threads` 8 / `observe_max` 20

## v1.14.1 (2026-09-17)

- **跨日重開提醒(省量)**:「上班/onduty」啟動時 state.json 記 `duty_started`;下班結算發現值班對話已跨日 → DM 提醒關視窗、明天自啟新 session。背景:值班對話越長每輪重讀的歷史越大,維護者實測跨 2 天 session 的每請求重讀量是單日的 2 倍,重開歸零最省。無升級動作,git pull 生效

## v1.14.0 (2026-09-17)

- **新功能:發會議邀請**——口令「幫我發會議邀請」「幫我邀請 X 和 Y」(語意判斷):秘書從 Slack profile 抓與會人公司信箱,`update_event` 加 attendees(通知留預設 ALL),Google 自動寄行事曆邀請信。profile 有 email 直接發;查不到才用網域規則推測並先列出確認。與會人判斷:被 tag 的全列入;@here 場合逐則看 thread 誰回了時間討論(明確說不參加的排除);口令「X 不用邀/加邀 Y」事後修名單。預設建檔行為不變(仍不邀他人),只有口令才邀。無新 scope、無升級動作,git pull 生效

## v1.13.1 (2026-09-17)

組員異常回報收單(2 項驗證 2 採納):

- **react 銷帳不再綁 `to:me`**:改搜 `hasmy::<emoji>:` 後比對 `open[]` 的 channel:ts 銷帳——`to:me` 只涵蓋 DM/@提及,watchlist、@here、純頻道貼文來源的項目按了 react 也搜不到,架構性漏銷(回報方以 reactions.get 實測確認,採納)。註:銷帳仍以 `config.style.ack_emojis` 白名單為準,想用的 emoji 記得先加白名單(口令「我慣用的 react 是 X」)
- **已回判斷禁止整段下結論**:同一對話有發言 = 已回是機械規則,明文禁止再做內容語意過濾(夾在閒聊裡的短回應也算);凡需語意判斷的場合(跨層回覆、點名追蹤 thread)訊息混雜時逐則檢視,拿不準備註保留,不判未回(回報方 DM 實測誤升 P0,採納)

純 prompt 修正,git pull 生效,無升級動作。

## v1.13.0 (2026-09-17)

- **個人語意字典 semantics.md**:emoji/用詞/句型的個人含意(是否銷帳/繼續追/暫回)與口令別名,寫在個人檔(gitignore,升級不蓋;首跑自動從 semantics.example.md 複製)。判讀優先序:字典 > config 清單 > 預設。口令「以後 X 代表 Y」即寫入;個人語意一律進字典,絕不改 SKILL.md——防止本機分叉再度發生

## v1.12.1 (2026-09-17)

組員升級回報收單(4 項驗證 2 採納 1 部分採納 1 不採納):

- **config 選填鍵缺失容錯**:`style` 底下缺鍵(如舊 config 缺 ack_emojis)→ 用 example 預設值頂上+整合健檢提示,不再靜默失效
- **冒號 lint 補第二條**:`:xxx:` 夾非法短碼字元(如「:大會14:」)也全形化;合法 emoji 短碼不誤傷
- **bot DM 發送明文禁用 PowerShell 組稿**(管線夾 PSPath 中繼資料致亂碼,組員實測重現)
- **「秘書升級」加髒污防護**:pull 前查未提交修改,有 → 停下說明+建議走 issue-triage,堅持升級才 stash 保存
- 不採納「from: 角括號 ID 格式失效」:維護者實測兩格式回傳相同結果,屬回報方環境問題(疑 config user_id 或變數未代入),回報方請重測

## v1.12.0 (2026-09-17)

- **新功能:點名回覆追蹤(roll_calls)**——你發「請大家回覆/按 done」的訊息(含 tag),秘書自動偵測並問要不要追(確認制);追蹤中每輪比對 react+thread 回覆,清單列「已完成 x/y,未完成:名單」,全到齊自動銷,2 天無進展提醒催。口令:「追這則 <連結>」「誰沒回 N」「停追 N」。**判定=完成不是已回**:react 白名單制(`config.style.rollcall_done_emojis`,預設 收到/done,其他 emoji 不算);thread 回覆看內容語意,只知悉未完成的列「已回未確認完成」
- manifest user scopes 補 `reactions:read`(react 判定用;缺時退化為只看 thread 回覆,功能不中斷)

⚙️ 升級動作(AI 自動執行,冪等):
1. 驗 user token 有無 `reactions:read`(打一次 `reactions.get` 或看 auth.test scopes):有 → 跳過;缺 → 問「點名追蹤的 react 判定需要補 reactions:read scope,要現在補嗎?」——要 → 走關卡 2 雙路線(自動代操作/手動)加 scope + Reinstall;不要 → 告知「react 判定退化為只看 thread 回覆,之後想補說『補 scope』」
2. state.json 寫 `kit_version: "1.12.0"`

## v1.11.0 (2026-09-17)

- **SKILL 拆檔省 token**:開工包/結算限定的內容(開工包組成/會前提醒排程/Gmail/整合健檢/週報/report_lists/my_todos 顯示/里程碑提醒節奏)抽到 `secretary/daily.md`,掃描 agent 平時輪只讀 SKILL.md(-16%),開工包/結算輪才加讀 daily.md。純搬移無語意變更;git pull 自動生效,無升級動作
- **state 清理**:結算時移除 `dismissed[]` 中訊息時間超過 14 天的項目(掃描窗上限 7 天,已不可能比對到),防 state.json 隨使用月數變肥
- **eco 模式加碼**:平時輪掃描 agent 降級用 Haiku(開工包/結算仍用 session 模型);誤判變多切回標準模式即恢復

## v1.10.0 (2026-09-17)

- **新功能:我的待辦(my_todos)**——口令「加待辦/看待辦/待辦完成 N/刪待辦 N」自記常駐待辦,開工包/結算顯示區塊,到期前 3 天提醒;預設開,`config.my_todos.enabled=false` 停用(Sandy 提案)
- **新功能:Slack List 回報單掃描(report_lists,選配)**——開工包/結算彙整「指派給你本人、狀態未結案」的 List 項目;每人 List/欄位/排除狀態由安裝精靈問答偵測寫入,預設空陣列不啟用;需 user token 加 `lists:read`+`files:read`(Sandy 提案)
- **「記一下」與待辦合併為單一入口**——要做的事不分有無時程一律進待辦、追到完成才消(含秘書明確看到已完成的自動銷帳);純事件記錄(請假/會議)仍過期自清(Tim 拍板)
- manifest user scopes 內建 `lists:read`+`files:read`(新裝機免二次 reinstall);回報單選配關卡先驗 scope,舊裝機才走補 scope 雙路線(自動代操作/手動)
- bot DM 連結固定用 `<url|連結>` 兩字藍連結格式,禁止裸 URL(自檢第 3 條同步改)
- 「秘書升級」正式化:pull 完自動執行 CHANGELOG 的「⚙️ 升級動作」(冪等,`kit_version` 記進度;要使用者選擇的問一句才做)

⚙️ 升級動作(AI 自動執行,冪等):
1. config.json 缺 `my_todos` → 補 `{"enabled": true, "section_title": "【我的待辦】", "show_in": ["morning", "evening"]}`,並告知新口令「加待辦/看待辦/待辦完成 N/刪待辦 N」與「記一下已改單一入口分流」
2. config.json 缺 `report_lists` → 補 `[]`
3. skill 目錄有 `team-defaults.json` 且 config.report_lists 為空 → 問「要啟用團隊預設回報單掃描嗎?(指派給你的未結案單會進開工包/結算)」——要 → 走 secretary-setup「回報單掃描」選配關卡步驟 0(含 scope 檢查,缺 `lists:read`/`files:read` 代補或引導 Reinstall);不要 → 記下不再問(config 加 `"report_lists_declined": true`)
4. state.json 寫 `kit_version: "1.10.0"`

## v1.9.3 (2026-09-15)

- 加「異常回報」節：秘書異常不自行改 SKILL,走 starter-kit 的 issue-triage 產標準回報;未裝 starter kit 會提醒可裝

## v1.9.2 (2026-09-11)

- **修正:會議開始切狀態 cron 漏排**——開工包/補提醒排會前提醒時,現在明定**成對必排**「會議開始切狀態」cron(規則搬到動作處,掃描 agent 回報格式同步明定)
- 當天新增行程三情況補齊:開始前 15 分以上 → 成對排兩顆;15 分內開始 → 立刻提醒+排切狀態 cron;**得知時已開場 → 立刻提醒+當場切狀態至結束時間**

## v1.9.1 (2026-09-11)

- **修正:會議開始自動切狀態失效**——原流程用 curl `users.profile.get` 讀現況防蓋,但 manifest 沒列 `users.profile:read`,get 失敗導致整段中止、狀態沒切。改為:讀現況優先走 Slack MCP `slack_read_user_profile`(不吃 xoxp scope),MCP 不可用退 curl,兩路都失敗跳過防蓋直接切(bot DM 附註)
- manifest user scopes 補 `users.profile:read`(備援用);舊裝機不補也不影響切狀態

## v1.9.0 (2026-09-10)

- **下班結算加整合健檢**:未串的選配整合(Google Calendar / Gmail 等)會在結算時提醒一句;口令「X 不用了」記入 `config.disabled_integrations` 後永久不吵
- 信箱檢查剔除「出勤/請假簽核」與「釣魚演練警示」兩類(前者有專屬系統、後者天天出現屬噪音),不再列入下班結算的限時信
- bot DM 組稿規範重構(§4.4):組稿→自檢→發送三段式,每輪必列完整待辦清單(增量式僅限終端輸出與省量模式),發送前自檢冒號 emoji / 裸 URL

## v1.8.1 (2026-09-10)

- manifest user scopes 補 `chat:write`(秘書用 chat.update 修自己發錯的訊息用);已依舊 manifest 裝機者不影響現有功能,遇到要修訊息時秘書會引導補 scope

## v1.8.0 (2026-09-10)

- **省量模式(給 Pro 方案)**:口令「省量模式/標準模式」——掃描間隔×2、bot 訊息平時只列變化;額度撞牆時自動降頻一天並通知
- 文件加 Pro 省量建議(Sonnet 值班/省量模式/無視吵群);安裝精靈試跑關卡加 Sonnet 提醒
- **附啟動器 `secretary-start.bat`**(內建 Sonnet+退出碼紀錄):精靈裝機收尾放到桌面,並詢問是否設開機自動值班(shell:startup)

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
