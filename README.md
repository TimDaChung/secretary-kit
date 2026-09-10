# secretary-kit

個人 Slack 秘書:跑在你自己的 Claude Code 終端裡,自動掃描待回覆訊息、分級提醒、擬稿回覆的 skill 套件。

- **安裝**:見 [安裝說明.md](安裝說明.md)(git clone + 打「安裝秘書」由精靈帶完)。最快的方式是把下面整段貼給你的 Claude Code:

  > 幫我安裝 Slack 秘書:git clone https://github.com/TimDaChung/secretary-kit.git 到 %USERPROFILE%\secretary-kit,照 repo 裡「安裝說明.md」的 Step 1 建好兩個 junction。完成後提醒我重開 Claude Code,重開後打「安裝秘書」繼續裝機精靈。
- **功能**:見 [功能說明.md](功能說明.md)
- **升級**:對秘書打口令「**秘書升級**」= 自動 `git pull` + 摘要更新內容(見 [CHANGELOG.md](CHANGELOG.md))
- **隱私**:個人資料(`config.json`、`state.json`、個人版 `templates.md`)已 gitignore,只存在你自己的電腦,不進 repo
