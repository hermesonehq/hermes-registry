# Theme Detector Tests

## Unit Tests (Phase 1)
- test_industry_ranker.py
- test_theme_classifier.py
- test_heat_calculator.py
- test_lifecycle_calculator.py
- test_scorer.py
- test_report_generator.py
- test_uptrend_client.py

## Unit Tests (Phase 2)
- test_representative_stock_selector.py (dynamic stock selection, FINVIZ/FMP fallback, circuit breaker)

## Integration Tests
- test_theme_detector_e2e.py (full pipeline, mocked I/O, no network required)

## Network Integration Tests (Phase 2 TODO)
- test_finviz_performance_client.py (requires network)
- test_etf_scanner.py (requires network)
- test_uptrend_client_integration.py (requires network)
