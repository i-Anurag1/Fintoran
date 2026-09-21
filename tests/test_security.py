import pytest
from security.input_validation import validate_filename

def test_path_traversal_rejected():
    with pytest.raises(ValueError):validate_filename('../secret.txt')

def test_unsupported_extension_rejected():
    with pytest.raises(ValueError):validate_filename('file.exe')
