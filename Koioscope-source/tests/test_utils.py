from koioscope.utils import detect_hash_type, normalize_hash

def test_detect_hash_type():
    assert detect_hash_type("44d88612fea8a8f36de82e1278abb02f") == "md5"
    assert detect_hash_type("da39a3ee5e6b4b0d3255bfef95601890afd80709") == "sha1"
    assert detect_hash_type("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855") == "sha256"
    assert detect_hash_type("notahash") is None

def test_normalize_hash():
    assert normalize_hash("ABC123") == "abc123"
