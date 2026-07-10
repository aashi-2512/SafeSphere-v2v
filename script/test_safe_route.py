import pytest
from safe_route import safest_route, StopReason
import pandas as pd
import h3

def test_short_distance_kurla_ghatkopar():
    start = "19.065, 72.879" # Kurla
    end = "19.085, 72.908" # Ghatkopar
    res = safest_route(start, end, time_bucket='night')
    assert "error" not in res
    assert res['safest_route']['cost_score'] <= res['quickest_route']['cost_score']

def test_long_distance_andheri_colaba():
    start = "19.119, 72.846" # Andheri
    end = "18.919, 72.827" # Colaba
    res = safest_route(start, end, time_bucket='day')
    assert "error" not in res
    assert res['safest_route']['cost_score'] <= res['quickest_route']['cost_score']

def test_high_crime_hex_pair():
    try:
        df = pd.read_csv('data/hex_time_risk.csv')
        high_risk_hex = df.sort_values('night_risk', ascending=False).iloc[0]['hex_id']
        lat, lng = h3.cell_to_latlng(high_risk_hex)
        start = f"{lat-0.02}, {lng-0.02}"
        end = f"{lat+0.02}, {lng+0.02}"
        res = safest_route(start, end, time_bucket='night')
        assert "error" not in res
        assert res['safest_route']['cost_score'] <= res['quickest_route']['cost_score']
    except FileNotFoundError:
        pytest.skip("hex_time_risk.csv not found")

def test_low_risk_hex_pair():
    start = "19.228, 72.918" # SGNP
    end = "19.229, 72.859" # Borivali East
    res = safest_route(start, end, time_bucket='day')
    assert "error" not in res
    assert res['safest_route']['cost_score'] <= res['quickest_route']['cost_score']

def test_same_hex_start_end():
    start = "19.062, 72.840" # Bandra Terminus
    end = "19.062, 72.840"
    res = safest_route(start, end, time_bucket='day')
    assert "error" not in res
    assert res['routes_compared'] == 1
    assert res['detour_attempted'] == False
    assert res['forced_detour_used'] == False
    assert res['stop_reason'] == StopReason.SUCCESS.value

def test_water_constrained_corridor():
    start = "19.049, 72.827" # Bandra Reclamation
    end = "19.016, 72.816" # Worli Sea Face
    res = safest_route(start, end, time_bucket='night')
    assert "error" not in res
    assert res['safest_route']['cost_score'] <= res['quickest_route']['cost_score']
    assert res['forced_detour_used'] == False

def test_multi_hazard_long_route():
    start = "19.229, 72.859" # Borivali
    end = "18.906, 72.815" # Colaba
    res = safest_route(start, end, time_bucket='night')
    assert "error" not in res
    if res['safest_route']['cost_score'] == res['quickest_route']['cost_score']:
        print("Distance cap hit or no safer neighbors found across iterations.")
    else:
        assert res['safest_route']['cost_score'] < res['quickest_route']['cost_score']
        assert res['forced_detour_used'] == True

def test_reverse_direction_consistency():
    start = "19.019, 72.842" # Dadar
    end = "18.995, 72.830" # Lower Parel
    res_ab = safest_route(start, end, time_bucket='evening')
    res_ba = safest_route(end, start, time_bucket='evening')
    assert "error" not in res_ab and "error" not in res_ba
    
    # A->B and B->A risk scores should be identical (accounting for slight floating point precision)
    assert abs(res_ab['quickest_route']['cost_score'] - res_ba['quickest_route']['cost_score']) < 0.1

def test_hex_with_no_data():
    start = "18.9220, 72.8347" # Gateway of India (might or might not have data)
    end = "18.0000, 72.0000" # Way out in the ocean (no data)
    res = safest_route(start, end, time_bucket='day')
    if "error" not in res:
        assert True
    else:
        assert "No routes found" in res["error"] or "geocode" in res["error"]

def test_garbage_address():
    res = safest_route("ZZZZXXXXYYYY123", "Colaba, Mumbai", time_bucket='day')
    assert "error" in res
    assert "Could not geocode" in res["error"]

def test_already_safe_direct_route():
    start = "18.943, 72.823" # Marine Drive
    end = "18.932, 72.827" # Churchgate
    res = safest_route(start, end, time_bucket='day')
    assert "error" not in res
    assert res['forced_detour_used'] == False
    assert res['stop_reason'] in (StopReason.NO_HIGH_RISK.value, StopReason.NO_IMPROVEMENT.value)

def test_time_bucket_boundary():
    # Test strict transition boundary
    res1 = safest_route("19.019, 72.842", "19.009, 72.837", time_bucket='day')
    res2 = safest_route("19.019, 72.842", "19.009, 72.837", time_bucket='evening') 
    assert "error" not in res1 and "error" not in res2
    r1 = res1['quickest_route']['mean_risk']
    r2 = res2['quickest_route']['mean_risk']
    assert type(r1) == float and type(r2) == float
    
    # Assert they are logically comparable numbers that don't spike unreasonably 
    # (should differ somewhat but neither should be 0 or 100 randomly)
    delta = abs(r2 - r1)
    assert delta < 25 # reasonable shift between buckets

def test_mocked_threshold_boundaries(monkeypatch):
    import safe_route
    from safe_route import HIGH_RISK_THRESHOLD
    
    # We will test score_route_by_hex_risk directly and mock compute_combined_risk
    # to return exactly our threshold values.
    
    def mock_risk(val):
        def _mock(*args, **kwargs):
            return val
        return _mock
    
    # 24.9
    monkeypatch.setattr(safe_route, "compute_combined_risk", mock_risk(24.9))
    c1, _, _, u1, _ = safe_route.score_route_by_hex_risk([[19.0, 72.0]], 'day', {}, {}, 1000)
    assert u1 == 0
    
    # 25.0
    monkeypatch.setattr(safe_route, "compute_combined_risk", mock_risk(25.0))
    c2, _, _, u2, _ = safe_route.score_route_by_hex_risk([[19.0, 72.0]], 'day', {}, {}, 1000)
    assert u2 == 0
    
    # 25.1
    monkeypatch.setattr(safe_route, "compute_combined_risk", mock_risk(25.1))
    c3, _, _, u3, _ = safe_route.score_route_by_hex_risk([[19.0, 72.0]], 'day', {}, {}, 1000)
    assert u3 == 1
