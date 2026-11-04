export default {
  async fetch(request, env) {
    const CORS = {"Access-Control-Allow-Origin":"*","Access-Control-Allow-Methods":"GET,POST,OPTIONS","Access-Control-Allow-Headers":"Content-Type,Authorization"};
    if (request.method==="OPTIONS") return new Response("",{headers:CORS});
    if (request.method!=="POST") return new Response("POST prompt",{status:405,headers:CORS});
    const body = await request.json();
    const prompt = body.prompt || "write workspace";
    const c = new AbortController();
    const to = setTimeout(function(){c.abort()},10000);
    try{
      const r = await fetch("https://models.github.ai/inference/chat/completions",{method:"POST",headers:{"Authorization":"Bearer "+env.GH_PAT,"Content-Type":"application/json"},body:JSON.stringify({model:"gpt-4o-mini",messages:[{role:"user",content:prompt}],max_tokens:8192}),signal:c.signal});
      clearTimeout(to);
      if(r.status===429) return new Response(JSON.stringify({fallback:true}),{status:429,headers:CORS});
      return new Response(await r.text(),{headers:CORS});
    }catch(e){clearTimeout(to); return new Response(JSON.stringify({fallback:true,reason:"timeout"}),{status:504,headers:CORS});}
  }
}
