# 開工包/下班結算 加碼規範(daily.md)

**本檔只在開工包與下班結算輪讀取**(平時輪不讀,省 token)。掃描主流程、bot DM 骨架與自檢見 SKILL.md;本檔定義兩個大輪的加碼項與專屬區塊。

## 晨間開工包(`config.schedule.morning_time`)

bot 完整清單+隔夜變化+今日行程。**今日行程 = notes 今天的 ∪ Google 日曆今天的 events**(`list_events`,含週期事件如每週固定會議);會前提醒與切狀態 cron 以聯集排,重複的只排一次。**撞期偵測**:行程聯集內時間重疊的,行程段頂部標「⚠️ 撞期:<場次A> × <場次B>」,取捨由使用者決定,秘書不代決;**當天是請假日**(notes 有 auto_status)→ 行程段改標「🌴 請假日但有 N 場行程」並逐一列出,問要改期/取消/照開。「上班」在上班時間後才喊 → 第一掃直接當開工包。

**會前 15 分提醒**:今日每個行程排一次性 cron(開始前 15 分),prompt「bot 提醒使用者:<行程>」。**成對鐵則:每排一顆會前提醒,必同排同行程的「會議開始」切狀態 cron**(做法見 SKILL.md〈會議狀態自動切換〉)——只排提醒沒排切狀態 = 漏排(2026-09-11 兩場會議均因此沒自動切狀態)。

## 下班結算(`config.schedule.evening_time`)

完整 open 清單+今天新答應的事、還沒回的、明天第一件事;**週五加碼**本週 dismissed 大事清單(週報素材)。結算後主掃描停(排程核對自然達成),bot DM 末尾提「已下班,晚間有事在終端打『上班』」+**當日運轉摘要一行**(掃描 N 輪、發 DM N 則、自動回覆 N 則——當日輪數記在 state.json `today_stats`,開工包歸零)。

**Gmail 信箱檢查(每天只在結算做這一次)**:`mcp__claude_ai_Gmail__search_threads` query `in:inbox newer_than:<N>d -category:promotions -category:social -category:updates`,N = 距上次成功檢查的天數(state.json `last_mail_check`,本次跑完寫回今天;缺值=3——新裝或首次啟用自然回補近期積壓;上限 7)——週一補掃週末、假期後補掃整段。結算 DM 的「📧 信箱」段分兩類列(**疑似釣魚不列**——公司天天有,MIS 自會提醒):

- **要行動/有期限**:回覆時限、活動報名、考核/評核、會議邀請、表單填寫、「請於 X 日前」句型。**出勤類簽核(加班/請假/補卡)不列**——公司另有系統管;期限 3 天內的同時寫進 notes(到期前照備忘提醒)
- **值得知道(FYI,不寫 notes)**:主管/HR/財務/法務等重要來源的非例行信、與使用者負責產品直接相關的非例行信(如平台審核結果、上架/發佈通知)

每天固定自動寄的報表/系統通知/廣告/純群發 FYI 一律不列;兩類都沒命中就不出現這段。**只讀不回**,回信仍由使用者自己處理;Gmail MCP 未連線/不可用 → 整段靜默跳過,不報錯。

**state 清理(結算時做,不進 DM)**:`dismissed[]` 中訊息時間超過 14 天的項目移除——id 格式 `<channel_id>:<message_ts>`,直接用 ts 判齡;掃描起點上限 7 天前,這些 id 永遠不可能再被比對到,留著只是每輪陪讀陪寫。`dismissed_patterns[]`(文字黑名單)**不清**,那是永久偏好。

**整合健檢(結算尾段,一項一行)**:檢查五條整合——Slack MCP(必備)、bot token(`auth.test`)、user token 及其 scopes(`users.profile:write`/`reactions:write`,看 auth.test 回應標頭)、Calendar MCP、Gmail MCP。缺的列「⚙️ 未串:<項目>(<失效的功能>)——要裝打『檢查安裝進度』,不想用回『<項目> 不用了』」;使用者回「X 不用了」→ 寫入 `config.disabled_integrations[]`,之後不再提醒。**故意關的不提醒**:bot 三欄全空、auto_reply 開關 false、已列入 disabled_integrations 的一律跳過;全部健康 → 這段不出現。

## Slack List 回報單掃描(report_lists,骨架 ③.5)

用途:掃指定 Slack List,篩出**指派給本人**、且狀態未被排除的項目,輸出成 bot DM 一個區塊。List、欄位、排除狀態都因人而異,由 secretary-setup 的選配關卡問答寫入 config;`config.example.json` 預設空陣列 = 不啟用。

執行條件:本輪為開工包或下班結算、且 `config.report_lists[]` 有 `enabled: true` 的項。平時輪不跑(省額度)。

資料來源:Slack Web API,非 MCP。token 讀 `$SLACK_USER_TOKEN`(讀不到用 `[Environment]::GetEnvironmentVariable("SLACK_USER_TOKEN","User")`);都沒有 → 整段靜默跳過,不報錯。需該 token 具 `lists:read` + `files:read` scope(缺 → API 回 missing_scope,靜默跳過並在整合健檢提示一次)。

每個 report_lists 項的處理(Bash curl):
1. 取欄位對照:GET `files.info?file=<list_id>`,從 `file.list_metadata.schema` 建 status_col 的 option value → label 對照表
2. 翻頁取全部項目:GET `slackLists.items.list?list_id=<list_id>&limit=100`,用 `response_metadata.next_cursor` 續頁(`&cursor=<urlencoded>`)直到無 cursor(上限 ~50 頁)
3. 篩選(每個 item 的 `fields[]` 依 `column_id` 取值):
   - 指派:assignee_col 那格的 `user[]` 含「本人 ID」→ 留。本人 ID = report_lists 項的 `assignee_user_id`,**空則用 `config.user.user_id`(每人 config 都是自己,不寫死任何人)**。**多欄指派**:config 也可給 `assignee_cols`(陣列,如受託人+pm 兩欄)取代 `assignee_col`,任一欄含本人即留
   - 狀態:status_col 那格的 `select[0]` 經對照表轉 label,label ∈ `exclude_status` → 丟
4. 輸出區塊(標題用 `section_title`;無符合項則整段不出現):
   `• <摘要>｜<狀態>｜連結`
   - 摘要 = name_col 那格的 text;狀態 = 轉出的 label
   - 連結 URL = `<config.workspace_url>/lists/<team_id>/<list_id>?record_id=<item.id>`(格式待實測;跳不到單筆退用整表連結),**格式依 SKILL.md §4.4 自檢第 3 條用 `<url|連結>` 兩字藍連結**;全形冒號規範同 §4.4 自檢

注意:API 呼叫較重(每項 List 約 1 次 files.info + 數次翻頁),故只在開工包/結算跑。

## 我的待辦顯示(my_todos,骨架 ③.6)

資料結構與口令見 SKILL.md〈我的待辦〉。`config.my_todos.enabled` 且本輪為開工包/結算時顯示:

```
【我的待辦】
• #N <內容>［｜到期 M/D］
```
- 列所有 done=false 項,依 due 有無、早晚排序(無 due 排後);全部完成 → 整段不出現
- 到期提醒:due 在今天或 3 天內的未完成待辦,在 ④提醒行加一句「⏳ 待辦 #N <內容> M/D 到期」;逾期標 🔴

## 專案里程碑提醒節奏

資料結構與口令見 SKILL.md〈專案里程碑管理〉。**只在開工包與下班結算出現,絕不進主掃描——平時完全沉默**:

- 距里程碑 >7 天:不提
- T-7:開工包首次浮出一行;T-3、T-1、當天:開工包+結算連續列,當天標 🔴
- 週一開工包附「本週里程碑」彙總一行
- **逾期追認**:日期過了未標完成 → 每天結算問一句「<專案> <里程碑>完成了嗎?」(note 標 `asked`+1),連 2 天無回應建 P1 追蹤項
- **連鎖檢查(改期或逾期時)**:重算該案後續里程碑的間距,比原間距壓縮 → 提示「<下游里程碑>只剩 N 天(原 M 天),要連動調整嗎?」。**秘書只提示,不自動改任何日期**
