export default {
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
            {role:"system", content:"You are OpenManus, a helpful assistant. Answer in Chinese, friendly, not just OK. You are built from FoundationAgents/OpenManus 4041 objects, Qwen, DeepSeek, GitHub Models."},
            {role:"user", content: prompt}
          ],
          max_tokens: 1024,
          temperature: 0.7
        }),
        signal:c.signal
      });
      clearTimeout(to);
      let txt = await r.text();
      if(!r.ok){
        return new Response(JSON.stringify({error:"GitHub API "+r.status, body:txt}),{status:r.status, headers:{...CORS,"Content-Type":"application/json"}});
      }
      return new Response(txt,{headers:{...CORS,"Content-Type":"application/json"}});
    }catch(e){
      clearTimeout(to);
      return new Response(JSON.stringify({error:"timeout", detail:e.message}),{status:504,headers:{...CORS,"Content-Type":"application/json"}});
    }
  }
}
