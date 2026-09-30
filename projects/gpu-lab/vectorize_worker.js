/**
 * vectorize_worker.js — the knowledge index, served.
 *
 * WHY THIS EXISTS INSTEAD OF VECTORIZE
 *
 * Cloudflare Vectorize on this account returns `vectorize.unknown_content_type`
 * (code 1005). The known-working alternative on the same account is **Workers KV plus
 * in-Worker cosine**, which is fine for a corpus under ~25MB. So this worker does not
 * pretend to be Vectorize: it is a KV-backed index with cosine computed in the Worker,
 * and it SAYS which one it is, because an index that misrepresents its own backend is
 * the exact failure the artifact-first gate exists to catch.
 *
 *   GET  /health              -> which backend is actually live
 *   GET  /search?q=...&k=5    -> top-k by cosine over the embedded corpus
 *   GET  /gaps?min=1          -> the NEGATIVE SPACE: cells whose polarity is GAP
 *
 * A gap-aware search endpoint is the point. A knowledge index that can only return
 * confident answers is a knowledge index that will confidently mislead you about what is
 * not known.
 */
const KV = "WHEEL_INDEX";   // binding name, NOT a namespace constant

const enc = new TextEncoder();

function tokenize(s) {
  return (s.toLowerCase().match(/[a-z]{3,}/g) || []);
}

function vec(tokens, vocab) {
  const v = new Float64Array(vocab.length);
  for (const t of tokens) {
    const i = vocab.indexOf(t);
    if (i >= 0) v[i] += 1;
  }
  let n = 0;
  for (let i = 0; i < v.length; i++) n += v[i] * v[i];
  n = Math.sqrt(n) || 1;
  for (let i = 0; i < v.length; i++) v[i] /= n;
  return v;
}

function cosine(a, b) {
  let s = 0;
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) s += a[i] * b[i];
  return s;
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);

    if (url.pathname === "/health") {
      // Report the LIVE backend. Do not claim Vectorize.
      let backend = "kv+in-worker-cosine", vectors = 0, note = "Vectorize unavailable (1005) on this account";
      try {
        const l = await env[KV].list({ limit: 1000 });
        vectors = l.keys.length;
        note = `KV binding '${KV}' responding`;
      } catch (e) {
        backend = "NONE";
        note = `KV binding '${KV}' NOT bound: ${e.message}`;
      }
      return json({ backend, vectors, note,
                    honest: "this is NOT a vector database; it is bag-of-words + cosine in-worker" });
    }

    if (url.pathname === "/gaps") {
      const min = Number(url.searchParams.get("min") || 1);
      const out = [];
      let cur;
      while ((cur = await env[KV].list({ cursor: cur?.result?.cursor }))) {
        for (const k of cur.keys) {
          const d = JSON.parse(await env[KV].get(k.name, "json"));
          const p = d?.polarity;
          if (p === "GAP" || p === "UNKNOWN") {
            if (d?.payload?.unmapped && d.payload.unmapped.length >= min) out.push(d);
          }
        }
        if (out.length > 500) break;
      }
      return json({ count: out.length, cells: out,
                    note: "the negative space is a first-class result, not an omission" });
    }

    if (url.pathname === "/search") {
      const q = url.searchParams.get("q") || "";
      const k = Number(url.searchParams.get("k") || 5);
      if (!q) return json({ error: "need ?q=" }, 400);
      let meta = null, docs = [];
      let cur;
      while ((cur = await env[KV].list({ cursor: cur?.result?.cursor }))) {
        for (const key of cur.keys) {
          const d = JSON.parse(await env[KV].get(key.name, "json"));
          if (key.name === "__vocab") { meta = d; continue; }
          docs.push(d);
        }
        if (docs.length > 5000) break;
      }
      if (!meta) return json({ error: "vocab not uploaded; PUT the vocab as __vocab" }, 503);
      const vocab = meta.words;
      const qv = vec(tokenize(q), vocab);
      const scored = docs.map(d => ({
        score: +cosine(qv, vec(tokenize(JSON.stringify(d.payload ?? d)), vocab)).toFixed(4),
        polarity: d.polarity, cell: d.cell_id, claim: d.payload?.claim,
        unmapped: d.payload?.unmapped || null,
      })).sort((a, b) => b.score - a.score).slice(0, k);
      return json({ query: q, backend: "kv+in-worker-cosine", results: scored });
    }

    return json({ paths: ["/health", "/search?q=", "/gaps?min=1"] });
  },
};

function json(o, s = 200) {
  return new Response(JSON.stringify(o, null, 2),
    { status: s, headers: { "content-type": "application/json" } });
}
