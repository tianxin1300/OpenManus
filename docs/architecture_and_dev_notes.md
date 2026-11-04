# OpenManus 医疗 AI Agent - 0成本原型架构与开发笔记

## 1. 总架构
Cloudflare Pages (前端) -> Cloudflare Worker (API网关 隐藏key CORS 429兜底 10s超时不能跑Agent长循环) -> Kaggle/Codespaces (OpenManus Agent长循环) -> 双模型路由

前端 Pages -> Worker网关 -> 后端 Agent -> 模型层
- Pages: 静态托管，0成本
- Worker: 隐藏 `github_pat_93位` `GROQ 401` 拦截，CORS，429熔断，150次/天 UTC 0:00 = 北京8点重置
- 后端: Kaggle Notebook / Codespaces 120 core-hours/月 15GB存储 按账单周期重置 不是每天，防休眠
- 模型: 本地 Ollama Qwen/DeepSeek-R1:8b 免费兜底 + 云 【entity-GitHub¦canonical_name=GitHub】 Models / NVIDIA NIM 复杂推理

## 2. 模块归属
- `app/llm.py`: 统一封装，`str object has no attribute choices` 包装 `SimpleNamespace(choices=[...], usage=SimpleNamespace(prompt_tokens=0, completion_tokens=0))`，`usage` 缺失补0，支持 【entity-GitHub¦canonical_name=GitHub】 Models `https://models.github.ai/inference` `gpt-4o-mini` / `meta-llama/Llama-3.3-70B-Instruct` `gpt-40-mini` 数字0 typo `gpt-4o-mini` 字母o
- `app/agent/base.py`: `SANDBOX_CLIENT is not defined` line 153/807 `try: await SANDBOX_CLIENT.cleanup() except: pass`
- `app/config.py`: `config.toml` 解析，`Expected newline line 4 col 104` token含换行引号，用 `github_pat_[A-Za-z0-9_]+` 清洗
- `config/config.toml`: `base_url = "https://models.github.ai/inference"` `model = "gpt-4o-mini"` `api_key = github_pat_93/103` 长PAT需 `Models Read-only` Account权限，短 `GITHUB_TOKEN` 40位无Models权限，`daytona_api_key = "dummy"` 不能 `""dummy""` `daytona_daytona_api_key`
- `main.py --prompt "读取当前目录，生成项目结构总结"` -> `workspace/summary.md` `str_replace_editor.create` 0 tools stuck_state prompt太简单需具体

## 3. 双配额熔断
- GitHub Models: 150次/天，429 -> 切 Ollama本地 Qwen，Worker层拦截
- Codespaces: 120核时/月，15GB，超限删Codespace `【entity-github¦canonical_name=GitHub】.com/codespaces` -> Delete，别修旧容器
- Groq: Codespaces出口IP被封，免费key 401，废弃

## 4. 容器卫生
- 只留 `config/config.toml M` `workspace/summary.md` 成果 `app/llm.py M` `app/agent/base.py M` 小补丁
- 删 `a.py dump.py final.py fix_*.py one.py real.py r.py f.py g.py h.py c.py d.py e.py t.py t2.py s.py clean.py all.py reset.py run.sh o.py v.py` `run.sh A` 含 `GROQ_API_KEY` `export GROQ_API_KEY="gsk_..."` `401` `U` `A` `!` 全清，`.pre-commit-config.yaml !` `放弃更改` `git checkout -- app/ run.sh`
- 平板无键盘 `--` 变 `—` `"` `=` `:` 全角，终端不能粘贴，粘编辑器 `v.py` `o.py` 终端手打 `python v.py`

## 5. Key泄露防护
- 截图 `github_pat_11BU...` GitHub自动revoke，需删重建93/103位 `one.py` `final len 93` `status 200 OK` 验证
- `.env` 不提交，`run.sh` 不带key

## 6. Kaggle休眠
- Notebook定时心跳，存 `workspace/` 持久化，`max_context_tokens 2048->8192`

## 7. API Spec
- Worker: `POST /api/chat {prompt, history}` -> `GET /api/status` -> `GET /api/result` 轮询，10s超时返回 `job_id`
- 后端: `POST /run {prompt}` 长循环

## 8. 医疗合规
- 不自动诊断，仅信息参考，日志留痕，免责声明，去标识化

## 9. Worker生产代码
```js
export default {
 async fetch(req, env){
  const cors={"Access-Control-Allow-Origin":"*"}
  if(req.method==="OPTIONS") return new Response("",{headers:cors})
  try{
   const r=await fetch("https://models.github.ai/inference/chat/completions",{method:"POST",headers:{"Authorization":`Bearer ${env.GH_PAT}`,"Content-Type":"application/json"},body:await req.text()})
   if(r.status===429) return new Response(JSON.stringify({fallback:"ollama"}),{status:429,headers:cors})
   return new Response(await r.text(),{headers:{...cors,"Content-Type":"application/json"}})
  }catch(e){return new Response(e.message,{status:500,headers:cors})}
 }
}
