from __future__ import annotations
from typing import Any, Dict, List, Tuple

def _vt_extract(api: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    try:
        data = (api or {}).get("data") or {}
        attrs = data.get("attributes") or {}

        # Detection ratio
        stats = attrs.get("last_analysis_stats") or {}
        pos = int(stats.get("malicious", 0)) + int(stats.get("suspicious", 0))
        total = sum(int(v) for v in stats.values()) or 0
        out["vt_detection_ratio"] = f"{pos}/{total}" if total else ""

        # Filenames seen
        names = attrs.get("names") or []
        out["filenames"] = list(dict.fromkeys(names))[:5]

        # PE info
        pe = attrs.get("pe_info") or {}
        sigcheck = attrs.get("signature_info") or {}
        out["pe_description"] = (attrs.get("signature_description") or
                                 (sigcheck.get("description") if isinstance(sigcheck, dict) else None) or "")
        out["pe_original_filename"] = (attrs.get("pe_original_filename") or
                                       (sigcheck.get("original name") if isinstance(sigcheck, dict) else None) or "")
        out["pe_copyright"] = (sigcheck.get("copyright") if isinstance(sigcheck, dict) else None) or ""

        # Signer
        out["signer"] = (attrs.get("authentihash") and attrs.get("signature_info",{}).get("signers")) or ""

        # First/last seen
        out["first_seen"] = attrs.get("first_submission_date") or ""
        out["last_seen"] = attrs.get("last_submission_date") or ""

        # Tags
        tags = set(attrs.get("tags") or [])
        ptc = attrs.get("popular_threat_classification") or {}
        if isinstance(ptc, dict):
            stl = ptc.get("suggested_threat_label")
            if isinstance(stl, list):
                tags |= set(stl)
            elif isinstance(stl, str):
                tags.add(stl)
        out["tags"] = sorted(tags)[:8]

        # Vendors
        vendors = attrs.get("last_analysis_results") or {}
        out["vendors"] = {k:v.get("category","") for k,v in vendors.items() if isinstance(v, dict)}
    except Exception:
        pass
    return out

def _collect_source_links(h: str, vt_permalink: str, extra_links: List[str]) -> List[str]:
    links = []
    if vt_permalink:
        links.append(vt_permalink)
    links.extend([x for x in extra_links if x])
    return list(dict.fromkeys(links))

def merge_results(file_hash: str, comment: str, vendor_allowlist: List[str], vt_api: Dict[str, Any], vt_html: Dict[str, Any],
                  urlhaus: Dict[str, Any], mb: Dict[str, Any], malshare: Dict[str, Any], hybrid: Dict[str, Any], hashlookup: Dict[str, Any], otx: Dict[str, Any], threatfox: Dict[str, Any]) -> Dict[str, Any]:
    vt = _vt_extract(vt_api)
    vt_permalink = (vt_html or {}).get("permalink","")

    vendors = vt.get("vendors", {})
    if vendor_allowlist:
        vendors = {k:v for k,v in vendors.items() if k in set(vendor_allowlist)}

    filenames = vt.get("filenames", [])

    first_seen = vt.get("first_seen") or ""
    last_seen = vt.get("last_seen") or ""

    tags = set(vt.get("tags", []))

    extra_links: List[str] = []

    # URLHaus
    if (urlhaus or {}).get("query_status") == "ok":
        pl = urlhaus.get("payloads") or []
        for p in pl:
            fn = p.get("filename")
            if fn:
                filenames.append(fn)
            fs = p.get("firstseen")
            if fs and not first_seen:
                first_seen = fs
        extra_links.append("https://urlhaus.abuse.ch/")
        tags.add("URLHaus")

    # MalwareBazaar
    if (mb or {}).get("query_status") == "ok":
        data = (mb.get("data") or [])
        for row in data:
            if not first_seen and row.get("first_seen"):
                first_seen = row.get("first_seen")
            if row.get("signature"):
                tags.add(row["signature"])
        extra_links.append("https://bazaar.abuse.ch/")
        tags.add("MalwareBazaar")

    # MalShare
    if malshare:
        tags.add("MalShare")
        extra_links.append("https://malshare.com/")
        if isinstance(malshare, dict):
            for k in ("filename","name"):
                if k in malshare and malshare[k]:
                    filenames.append(str(malshare[k]))

    # Hybrid Analysis
    if hybrid:
        tags.add("HybridAnalysis")
        extra_links.append("https://www.hybrid-analysis.com/")
        try:
            if isinstance(hybrid, dict) and 'result' in hybrid and isinstance(hybrid['result'], list) and hybrid['result']:
                r0 = hybrid['result'][0]
                if r0.get('verdict'):
                    tags.add(str(r0['verdict']))
                if r0.get('type'):
                    tags.add(str(r0['type']))
                if r0.get('submit_name'):
                    filenames.append(str(r0['submit_name']))
        except Exception:
            pass

    # Hashlookup (CIRCL)
    if hashlookup:
        tags.add("CIRCL-Hashlookup")
        extra_links.append("https://hashlookup.circl.lu/")
        try:
            if isinstance(hashlookup, dict):
                if 'name' in hashlookup and hashlookup['name']:
                    filenames.append(str(hashlookup['name']))
                if 'names' in hashlookup and isinstance(hashlookup['names'], list):
                    filenames.extend([str(x) for x in hashlookup['names'][:3]])
                if not first_seen and hashlookup.get('first_seen'):
                    first_seen = hashlookup['first_seen']
        except Exception:
            pass

    # OTX
    if otx:
        pulses = (otx.get("pulse_info") or {}).get("pulses") or []
        if pulses:
            tags.add("OTX")
            extra_links.append("https://otx.alienvault.com/")
        general = otx.get("general") or {}
        if isinstance(general, dict):
            name = general.get("file_type")
            if name:
                tags.add(name)

    # ThreatFox
    if (threatfox or {}).get("query_status") == "ok":
        extra_links.append("https://threatfox.abuse.ch/")
        tags.add("ThreatFox")

    # Indicator tags heuristic
    indicator_tags = []
    if "Microsoft" in " ".join(filenames):
        indicator_tags.append("MSSoftware")
    if vt.get("vt_detection_ratio"):
        if vt.get("vt_detection_ratio").startswith("0/"):
            indicator_tags.append("Harmless")

    result = {
        "hash": file_hash,
        "comment": comment or "",
        "av_vendor_matches": ";".join([f"{k}:{v}" for k,v in vendors.items()]) if vendors else "",
        "filenames": ";".join(list(dict.fromkeys(filenames))) if filenames else "",
        "pe_description": vt.get("pe_description",""),
        "pe_original_filename": vt.get("pe_original_filename",""),
        "pe_copyright": vt.get("pe_copyright",""),
        "signer": vt.get("signer","") or ("yes" if (vt_html or {}).get("signer_hint") else ""),
        "vt_detection_ratio": vt.get("vt_detection_ratio",""),
        "first_seen": first_seen or "",
        "last_seen": last_seen or "",
        "indicator_tags": ";".join(sorted(set(indicator_tags) | tags)) if (indicator_tags or tags) else "",
        "source_links": ";".join(_collect_source_links(file_hash, vt_permalink, extra_links)),
    }
    return result
