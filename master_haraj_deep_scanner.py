import httpx
import re
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_HEADERS = {
    'User-Agent': 'HarajServer',
    'BETWEEN-SERVERS-KEY': 'haraj_server_8472965246285103',
    'Content-Type': 'application/json'
}

CLIENT = httpx.Client(headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}, timeout=12.0)

def extract_manifest_chunks():
    print("[*] Fetching Haraj web client manifest...")
    resp = CLIENT.get('https://v8-cdn.haraj.com.sa/ext_v11/assets/manifest-a1fa6232.js')
    chunks = list(set(re.findall(r'https://v8-cdn\.haraj\.com\.sa/ext_v11/assets/[^\"]+\.js', resp.text)))
    print(f"[+] Total unique JS chunks in manifest: {len(chunks)}")
    return chunks

def scan_single_chunk(url):
    try:
        r = CLIENT.get(url)
        if r.status_code != 200:
            return None
        text = r.text
        
        # Extract GraphQL operations
        queries = re.findall(r'`([^`]*query\s+([A-Za-z0-9_]+)[^`]*)`', text)
        mutations = re.findall(r'`([^`]*mutation\s+([A-Za-z0-9_]+)[^`]*)`', text)
        fragments = re.findall(r'`([^`]*fragment\s+([A-Za-z0-9_]+)\s+on\s+([A-Za-z0-9_]+)[^`]*)`', text)
        
        # Extract API domains and endpoints
        domains = set(re.findall(r'https?://[a-zA-Z0-9_\-\.]+\.haraj\.com\.sa[^\s\"\'\<\>]*', text))
        
        # Extract REST paths
        rest_paths = set(re.findall(r'[\"\']/(?:api|streams|v1|v2|auth|web|upload)/[^\s\"\'\<\>]+[\"\']', text))
        
        # Extract feature flags or config keys
        flags = set(re.findall(r'checkFlag\([\"\']([^\"\']+)[\"\']', text))
        
        return {
            'url': url,
            'queries': [(name, full.strip()) for full, name in queries],
            'mutations': [(name, full.strip()) for full, name in mutations],
            'fragments': [(name, target, full.strip()) for full, name, target in fragments],
            'domains': list(domains),
            'rest_paths': [p.strip('"\'') for p in rest_paths],
            'flags': list(flags)
        }
    except Exception as e:
        return None

def run_deep_scan():
    start_time = time.time()
    chunks = extract_manifest_chunks()
    
    print(f"[*] Launching concurrent scanner across all {len(chunks)} chunks...")
    all_queries = {}
    all_mutations = {}
    all_fragments = {}
    all_domains = set()
    all_rest_paths = set()
    all_flags = set()
    
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(scan_single_chunk, c): c for c in chunks}
        completed = 0
        for f in as_completed(futures):
            res = f.result()
            completed += 1
            if completed % 100 == 0 or completed == len(chunks):
                print(f"    Scanned {completed}/{len(chunks)} chunks ({(completed/len(chunks))*100:.1f}%)...")
            if res:
                for q_name, q_body in res['queries']:
                    if q_name not in all_queries:
                        all_queries[q_name] = q_body
                for m_name, m_body in res['mutations']:
                    if m_name not in all_mutations:
                        all_mutations[m_name] = m_body
                for f_name, f_target, f_body in res['fragments']:
                    if f_name not in all_fragments:
                        all_fragments[f_name] = {'type': f_target, 'body': f_body}
                all_domains.update(res['domains'])
                all_rest_paths.update(res['rest_paths'])
                all_flags.update(res['flags'])

    print("\n" + "=" * 60)
    print("🎯 DEEP SCAN HARVEST RESULTS:")
    print(f"   • Total Unique GraphQL Queries Found: {len(all_queries)}")
    print(f"   • Total Unique GraphQL Mutations Found: {len(all_mutations)}")
    print(f"   • Total Unique GraphQL Fragments Found: {len(all_fragments)}")
    print(f"   • Total Platform Subdomains Discovered: {len(all_domains)}")
    print(f"   • Total REST API Endpoints Discovered: {len(all_rest_paths)}")
    print(f"   • Total Feature Flags Discovered: {len(all_flags)}")
    print("=" * 60)

    # Compile into structured report
    master_catalog = {
        'scan_timestamp': time.time(),
        'total_chunks_scanned': len(chunks),
        'queries': all_queries,
        'mutations': all_mutations,
        'fragments': all_fragments,
        'domains': sorted(list(all_domains)),
        'rest_paths': sorted(list(all_rest_paths)),
        'feature_flags': sorted(list(all_flags))
    }

    with open('haraj_full_platform_catalog.json', 'w', encoding='utf-8') as f:
        json.dump(master_catalog, f, ensure_ascii=False, indent=2)
    print("[+] Saved complete platform catalog to 'haraj_full_platform_catalog.json'")

    # Now run live query tests against the endpoints to see what responds
    print("\n[*] Testing discovered queries against live API...")
    live_results = {}
    for q_name, q_body in list(all_queries.items()):
        # Try simple execution if it takes few or no required args
        if '!' not in q_body[:q_body.find('{')]:
            try:
                r = CLIENT.post(f"https://graphql.haraj.com.sa/?queryName={q_name}", headers=BASE_HEADERS, json={'query': q_body}, timeout=4.0)
                live_results[q_name] = {'status': r.status_code, 'has_data': 'data' in r.json() if r.status_code == 200 else False}
            except:
                pass

    print(f"[+] Tested parameterless queries. Responding queries: {len(live_results)}")
    
    elapsed = time.time() - start_time
    print(f"[*] Deep scan finished in {elapsed:.2f} seconds.")

if __name__ == '__main__':
    run_deep_scan()
