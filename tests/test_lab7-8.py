import pytest
import asyncio
from pages.register_page import (
    mul, summ, UserMetricsService, user_metrics_factory,
    fetch_data, transform_data, run_data_pipeline
)

def test_mul():
    assert mul(2, 3) == 6

def test_summ():
    assert summ(2, 3) == 5

def test_compute_metric():
    service = user_metrics_factory()

    assert service.compute_metric(4, 2) == 12

def test_compute_metric_zero():
    service = user_metrics_factory()
    # (0*5)+0 = 0
    assert service.compute_metric(0, 5) == 0

def test_compute_metric_email_score():
    service = user_metrics_factory()

    assert service.compute_metric(5, 3) == 20


@pytest.mark.asyncio
async def test_fetch_data():
    data = await fetch_data(1)
    assert data == "data_1"

@pytest.mark.asyncio
async def test_transform_data():
    result = await transform_data("data_2")
    assert result == "DATA_2"

@pytest.mark.asyncio
async def test_pipeline():
    raw = await asyncio.gather(*(fetch_data(i) for i in range(3)))
    processed = await asyncio.gather(*(transform_data(d) for d in raw))
    assert processed == ["DATA_0", "DATA_1", "DATA_2"]

@pytest.mark.asyncio
async def test_pipeline_length():
    raw = await asyncio.gather(*(fetch_data(i) for i in range(4)))
    processed = await asyncio.gather(*(transform_data(d) for d in raw))
    assert len(processed) == 4

@pytest.mark.asyncio
async def test_pipeline_content():
    raw = await fetch_data(5)
    processed = await transform_data(raw)
    assert processed.startswith("DATA_")

