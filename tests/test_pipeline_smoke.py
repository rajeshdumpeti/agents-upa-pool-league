from utils.config import load_config, ConfigError
import pytest

def test_load_config_ok():
    cfg = load_config("configs/upa.yaml")
    assert isinstance(cfg, dict)
    assert "outputs_dir" in cfg

def test_load_config_missing():
    with pytest.raises(ConfigError):
        load_config("configs/does-not-exist.yaml")
