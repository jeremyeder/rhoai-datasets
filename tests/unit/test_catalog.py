"""tests/unit/test_catalog.py"""

from __future__ import annotations

import yaml

from datasets.metadata.catalog import CatalogEntry, DatasetCatalog


def test_catalog_entry_from_yaml(tmp_path):
    entry_data = {
        "name": "terminal-bench-2",
        "source": "harbor",
        "source_url": "https://hub.harborframework.com/terminal-bench/terminal-bench-2",
        "task_count": 89,
        "domain": ["terminal", "cli", "system-administration"],
        "difficulty_profile": "hard",
        "format": "harbor",
        "applicability": "High -- directly tests agent terminal skills relevant to RHOAI CLI tooling and operator debugging.",
    }
    entry = CatalogEntry(**entry_data)
    assert entry.name == "terminal-bench-2"
    assert entry.task_count == 89
    assert "terminal" in entry.domain


def test_catalog_load_from_directory(tmp_path):
    entry1 = {
        "name": "swe-bench-pro",
        "source": "harbor",
        "source_url": "https://hub.harborframework.com/scale-ai/swe-bench-pro",
        "task_count": 731,
        "domain": ["software-engineering"],
        "difficulty_profile": "hard",
        "format": "harbor",
        "applicability": "Core benchmark for coding agents.",
    }
    (tmp_path / "swe-bench-pro.yaml").write_text(yaml.dump(entry1))

    catalog = DatasetCatalog.load(tmp_path)
    assert len(catalog.entries) == 1
    assert catalog.entries[0].name == "swe-bench-pro"


def test_catalog_filter_by_domain(tmp_path):
    entries = [
        {
            "name": "a",
            "source": "harbor",
            "source_url": "u",
            "task_count": 10,
            "domain": ["security"],
            "difficulty_profile": "medium",
            "format": "harbor",
            "applicability": "x",
        },
        {
            "name": "b",
            "source": "skillsbench",
            "source_url": "u",
            "task_count": 5,
            "domain": ["data-science"],
            "difficulty_profile": "easy",
            "format": "skillsbench",
            "applicability": "x",
        },
    ]
    for i, e in enumerate(entries):
        (tmp_path / f"entry{i}.yaml").write_text(yaml.dump(e))

    catalog = DatasetCatalog.load(tmp_path)
    security = catalog.filter(domain="security")
    assert len(security) == 1
    assert security[0].name == "a"


def test_catalog_filter_by_format(tmp_path):
    entries = [
        {
            "name": "a",
            "source": "harbor",
            "source_url": "u",
            "task_count": 10,
            "domain": ["x"],
            "difficulty_profile": "medium",
            "format": "harbor",
            "applicability": "x",
        },
        {
            "name": "b",
            "source": "skillsbench",
            "source_url": "u",
            "task_count": 5,
            "domain": ["x"],
            "difficulty_profile": "easy",
            "format": "skillsbench",
            "applicability": "x",
        },
    ]
    for i, e in enumerate(entries):
        (tmp_path / f"entry{i}.yaml").write_text(yaml.dump(e))

    catalog = DatasetCatalog.load(tmp_path)
    sb = catalog.filter(format="skillsbench")
    assert len(sb) == 1
    assert sb[0].name == "b"
