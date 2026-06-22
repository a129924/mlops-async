## Implementation Steps

- [ ] 凍結 `start_job` planning baseline，確認只指向 `jobExecution/jobRequests/jobs`
- [ ] 確認四個 planning artifacts 的 exact paths、locked decisions 與 strict analysis routing 一致
- [ ] 確認 future test directory 名稱固定為 `tests/unit/request_contract/job_requests_jobs_request_gate/`
- [ ] 將 legacy source 缺失與 installed `sasctl` 路徑未解析記錄為 human-check 邊界
- [ ] 本 topic 停在 human-check，不進入 implementation
