from services.import_pipeline import safe_export_csv
from providers.base import Provenance
from security.input_validation import validate_filename


def test_csv_export_neutralizes_formula_prefixes():
    data=safe_export_csv([{'description':'=SUM(A1:A2)','amount':100}]).decode('utf-8-sig')
    assert "'=SUM(A1:A2)" in data


def test_provenance_contains_required_fields():
    p=Provenance.now('test','https://example.test',dataset_date_range='2026',license_note='test').as_dict()
    assert p['provider']=='test'
    assert p['source']=='https://example.test'
    assert p['retrieved_at']
    assert p['dataset_date_range']=='2026'


def test_document_filename_controls():
    assert validate_filename('annual_report.pdf')=='annual_report.pdf'


def test_release_audit_script():
    import subprocess, sys
    result = subprocess.run([sys.executable, "scripts/master_prompt_audit.py"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
