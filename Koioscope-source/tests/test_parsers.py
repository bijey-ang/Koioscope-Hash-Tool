from koioscope.merge import _vt_extract

def test_vt_extract_handles_missing():
    out = _vt_extract({})
    assert isinstance(out, dict)
