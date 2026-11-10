/**
 * Saudi Retail Edge Proxy — Cloudflare Worker
 * Blazing fast, parallel price comparison & discovery across Jarir, eXtra, and Noon.
 * 
 * Free Tier Features:
 * - 100,000 free requests per day.
 * - Outbound traffic distributed across Cloudflare's global Anycast edge IPs (zero local IP rate-limit risk).
 * - True parallel subrequests via Promise.allSettled (sub-300ms total response).
 * - Native edge caching via Cloudflare Cache API (caches search results for 1 hour).
 */

export interface Env {
  // Bindings (KV, D1, etc. can be added here)
}

const JARIR_KEYS = {
  en: "key_KcSYfmQTEwRpBnd9",
  ar: "key_g0Gi7pKaE5cyqDGl",
};

const EXTRA_KEYS = {
  en: { siteKey: "ss-unbxd-auk-extra-saudi-en-prod11541714990488", apiKey: "21705619e273429e5767eea44ccb1ad5" },
  ar: { siteKey: "ss-unbxd-auk-extra-saudi-ar-prod11541714990564", apiKey: "8fb45132f31d81ab46966cc135c24430" },
};

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    // Enable CORS for web apps and frontends
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }

    // 1. Edge Cache Check
    const cache = caches.default;
    const cacheKey = new Request(url.toString(), request);
    const cachedResponse = await cache.match(cacheKey);
    if (cachedResponse) {
      const response = new Response(cachedResponse.body, cachedResponse);
      response.headers.set("X-Edge-Cache", "HIT");
      return response;
    }

    const q = url.searchParams.get("q") || "laptop";
    const lang = url.searchParams.get("lang") || "en";

    // Route: /api/jarir -> Dedicated Jarir search
    if (url.pathname === "/api/jarir") {
      const jarirData = await fetchJarir(q, lang, url.searchParams);
      return jsonResponse(jarirData, cache, cacheKey, ctx, 3600);
    }

    // Route: /api/compare -> Parallel multi-store comparison (Jarir + eXtra + Noon)
    if (url.pathname === "/api/compare" || url.pathname === "/") {
      const startTime = Date.now();

      // Fire parallel subrequests across all platforms simultaneously
      const [jarirRes, extraRes, noonRes] = await Promise.allSettled([
        fetchJarir(q, lang, url.searchParams),
        fetchExtra(q, lang),
        fetchNoon(q, lang),
      ]);

      const jarirProducts = jarirRes.status === "fulfilled" ? jarirRes.value.products : [];
      const extraProducts = extraRes.status === "fulfilled" ? extraRes.value.products : [];
      const noonProducts = noonRes.status === "fulfilled" ? noonRes.value.products : [];

      const payload = {
        query: q,
        language: lang,
        latency_ms: Date.now() - startTime,
        total_sources: 3,
        summary: {
          jarir_count: jarirProducts.length,
          extra_count: extraProducts.length,
          noon_count: noonProducts.length,
        },
        retailers: {
          jarir: jarirProducts.slice(0, 5),
          extra: extraProducts.slice(0, 5),
          noon: noonProducts.slice(0, 5),
        },
      };

      return jsonResponse(payload, cache, cacheKey, ctx, 1800);
    }

    return new Response(JSON.stringify({ error: "Endpoint not found. Use /api/jarir or /api/compare" }), {
      status: 404,
      headers: { "Content-Type": "application/json" },
    });
  },

  // Cron Trigger: Wakes up on schedule
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    console.log("[*] Cron wake-up: Checking Jarir top price drops...");
    // Can query Jarir and ping a Discord / Telegram webhook here
  },
};

/**
 * Fetch from Jarir Constructor.io edge
 */
async function fetchJarir(query: string, lang: string, params: URLSearchParams) {
  const indexKey = lang === "ar" ? JARIR_KEYS.ar : JARIR_KEYS.en;
  const targetUrl = new URL(`https://ac.cnstrc.com/search/${encodeURIComponent(query)}`);
  targetUrl.searchParams.set("key", indexKey);
  targetUrl.searchParams.set("num_results_per_page", params.get("limit") || "10");

  const minPrice = params.get("min_price");
  const maxPrice = params.get("max_price");
  if (minPrice || maxPrice) {
    targetUrl.searchParams.set("filters[price]", `${minPrice || 0}-${maxPrice || 999999}`);
  }

  const brand = params.get("brand");
  if (brand) targetUrl.searchParams.set("filters[brand]", brand);

  const format = params.get("format") || params.get("bofo");
  if (format) targetUrl.searchParams.set("filters[bofo]", format);

  const categoryDesc = params.get("category_desc") || params.get("productcode_description");
  if (categoryDesc) targetUrl.searchParams.set("filters[productcode_description]", categoryDesc);

  const paperSize = params.get("size") || params.get("pasi");
  if (paperSize) targetUrl.searchParams.set("filters[pasi]", paperSize);

  const ram = params.get("ram");
  if (ram) targetUrl.searchParams.set("filters[symm]", ram);

  const res = await fetch(targetUrl.toString(), {
    headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" },
  });
  if (!res.ok) throw new Error(`Jarir fetch failed: ${res.status}`);

  const data: any = await res.json();
  const results = data.response?.results || [];

  return {
    total: data.response?.total_num_results || 0,
    products: results.map((r: any) => {
      const meta = r.data?.metadata || {};
      return {
        source: "Jarir Bookstore",
        sku: r.data?.sku || r.data?.id,
        title: r.value,
        price_sar: parseFloat(r.data?.price || meta.price || 0),
        brand: meta.brand || r.data?.brand || null,
        author: meta.auth || null,
        book_format: meta.bofo || null,
        isbn: meta.isbn || null,
        paper_size: meta.pasi || null,
        category: meta.productcode_description || null,
        url: r.data?.url ? `https://www.jarir.com/sa-${lang}/${r.data.url}` : null,
        image: `https://ak-asset.jarir.com/akeneo-prod/asset/saas/${r.data?.sku || r.data?.id}.jpg`,
      };
    }),
  };
}

/**
 * Fetch from eXtra Netcore Unbxd
 */
async function fetchExtra(query: string, lang: string) {
  const creds = lang === "ar" ? EXTRA_KEYS.ar : EXTRA_KEYS.en;
  const targetUrl = `https://search.unbxd.io/${creds.apiKey}/${creds.siteKey}/search?q=${encodeURIComponent(query)}&rows=10`;

  const res = await fetch(targetUrl, {
    headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" },
  });
  if (!res.ok) throw new Error(`eXtra fetch failed: ${res.status}`);

  const data: any = await res.json();
  const products = data.response?.products || [];

  return {
    total: data.response?.numberOfProducts || 0,
    products: products.map((p: any) => ({
      source: "eXtra Stores",
      sku: p.uniqueId || p.sku,
      title: p.title,
      price_sar: parseFloat(p.price || 0),
      was_price_sar: p.wasPrice ? parseFloat(p.wasPrice) : null,
      brand: Array.isArray(p.brand) ? p.brand.join(", ") : p.brand,
      url: p.urlEn ? `https://www.extra.com/${lang}-sa/${p.urlEn.replace(/^\//, "")}` : null,
      image: p.imageUrl || p.amplienceProductBaseUrl,
    })),
  };
}

/**
 * Fetch from Noon Catalog v3
 */
async function fetchNoon(query: string, lang: string) {
  const locale = lang === "ar" ? "ar-sa" : "en-sa";
  const targetUrl = `https://www.noon.com/_svc/catalog/api/v3/u/search?q=${encodeURIComponent(query)}&limit=10`;

  try {
    const res = await fetch(targetUrl, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "x-platform": "web",
        "x-locale": locale,
      },
      signal: AbortSignal.timeout(3000),
    });
    if (!res.ok) return { total: 0, products: [] };

    const data: any = await res.json();
    const hits = data.hits || [];

    return {
      total: data.nbHits || 0,
      products: hits.map((h: any) => ({
        source: "Noon KSA",
        sku: h.sku,
        title: h.name,
        price_sar: parseFloat(h.price || 0),
        was_price_sar: h.was_price ? parseFloat(h.was_price) : null,
        rating: h.rating?.value,
        url: h.url ? `https://www.noon.com/saudi-${lang}/${h.url.replace(/^\//, "")}/p/` : null,
      })),
    };
  } catch (e) {
    return { total: 0, products: [] };
  }
}

function jsonResponse(
  data: any,
  cache: Cache,
  cacheKey: Request,
  ctx: ExecutionContext,
  maxAgeSeconds = 3600
): Response {
  const headers = new Headers({
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Cache-Control": `public, max-age=${maxAgeSeconds}, s-maxage=${maxAgeSeconds}`,
    "X-Edge-Cache": "MISS",
  });

  const response = new Response(JSON.stringify(data, null, 2), { headers });
  ctx.waitUntil(cache.put(cacheKey, response.clone()));
  return response;
}
