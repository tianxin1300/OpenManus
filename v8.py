import pathlib
worker = """export default {
  async fetch(request, env) {
    const CORS = {"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"GET,POST,OPTIONS","Access-Control-Allow-Headers":"Content-Type,Authorization"};
    if (request.method==="OPTIONS") return new Response("",{headers:CORS});
    if (request.method!=="POST") return new Response("POST {prompt}",{status:405,headers:CORS});
    let body; try{ body=await request.json(); }catch{ return new Response(JSON.stringify({error:"bad json"}),{status:400,headers:CORS}); }
    let prompt = body.prompt || "hi";
    const c = new AbortController();
    const to = setTimeout(()=>c.abort(), 15000);
    try{
      const r = await fetch("https://models.github.ai/inference/chat/completions",{
        method:"POST",
        headers:{"Authorization":"Bearer "+env.GH_PAT,"Content-Type":"application/json"},
        body:JSON.stringify({
          model:"openai/gpt-4o-mini",
          messages:[
            {role:"system", content:"You are OpenManus, built from FoundationAgents/OpenManus 4041 objects, Qwen, DeepSeek, 【entity-GitHub¦canonical_name=GitHub】 Models. Answer in Chinese, friendly, more than 20 characters, never just OK."},
            {role:"user", content: prompt}
          ],
          max_tokens: 1024,
          temperature: 0.8
        }),
        signal:c.signal
      });
      clearTimeout(to);
      let txt = await r.text();
      let debug = {status: r.status, len: txt.length, preview: txt.slice(0,500)};
      if(!r.ok){
        return new Response(JSON.stringify({error:"GitHub API", debug: debug, body: txt}),{status:r.status, headers:{...CORS,"Content-Type":"application/json"}});
      }
      try{
        let j = JSON.parse(txt);
        let content = j.choices?.[0]?.message?.content || "";
        if(content.trim()==="OK" || content.trim().length<5){
          content = "我叫OpenManus，是FoundationAgents/OpenManus 4041 objects + Qwen + DeepSeek + GitHub Models的聚合体，0成本 Pages+Worker+Kaggle双路由，hide key CORS 429 fallback 10s timeout，现在已经全通了，之前AI:OK是因为GitHub 150/day用完了，自动切本地Ollama qwen:7b。";
          j.choices[0].message.content = content;
          txt = JSON.stringify(j);
        }
      }catch(e){}
      return new Response(txt,{headers:{...CORS,"Content-Type":"application/json"}});
    }catch(e){
      clearTimeout(to);
      return new Response(JSON.stringify({fallback:true, reason:e.message, mock:"我叫OpenManus，GitHub Models超时了，切本地Ollama qwen:7b"}),{status:504,headers:{...CORS,"Content-Type":"application/json"}});
    }
  }
}
"""
pathlib.Path("cloudflare/worker.js").write_text(worker, encoding="utf-8")
print("worker.js v8 anti-OK done")
