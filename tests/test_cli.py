import subprocess
import sys


def test_cli_stdin():
    result = subprocess.run(
        [sys.executable, "-m", "json2pystmt"],
        input='{"key": "value"}',
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "root = {}" in result.stdout
    assert "root['key'] = 'value'" in result.stdout


def test_cli_custom_root():
    result = subprocess.run(
        [sys.executable, "-m", "json2pystmt", "-r", "data"],
        input='{"key": "value"}',
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "data = {}" in result.stdout
    assert "data['key'] = 'value'" in result.stdout


def test_cli_invalid_json():
    result = subprocess.run(
        [sys.executable, "-m", "json2pystmt"],
        input="not valid json",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Error: Invalid JSON" in result.stderr
