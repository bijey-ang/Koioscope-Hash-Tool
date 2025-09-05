from koioscope.merge import merge_results

def test_merge_minimal():
    res = merge_results(
        "h", "", [],
        vt_api={"data":{"attributes":{"last_analysis_stats":{"malicious":1,"harmless":2},"names":["a","b"],"last_analysis_results":{"A":{"category":"malicious"}}}}},
        vt_html={"permalink":"https://vt/xyz"},
        urlhaus={"query_status":"no_results"},
        mb={"query_status":"no_results"},
        malshare={},
        hybrid={},
        hashlookup={},
        otx={},
        threatfox={"query_status":"no_results"}
    )
    assert res["hash"] == "h"
    assert res["vt_detection_ratio"].startswith("1/")
    assert "a" in res["filenames"]
    assert "https://vt/xyz" in res["source_links"]
