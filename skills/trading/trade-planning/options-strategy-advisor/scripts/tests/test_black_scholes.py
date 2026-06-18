"""Tests for Black-Scholes option pricing engine.

Covers:
- OptionPricer initialization and input validation
- Call/put pricing (known-value checks and put-call parity)
- Greeks: delta, gamma, theta, vega, rho
- Historical volatility calculation
- Utility methods: intrinsic value, time value, moneyness
"""

import numpy as np
import pytest
from black_scholes import OptionPricer, calculate_historical_volatility

# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def atm_pricer():
    """ATM call/put pricer with standard parameters."""
    return OptionPricer(S=100, K=100, T=30 / 365, r=0.05, sigma=0.20)


@pytest.fixture
def itm_call_pricer():
    """ITM call pricer: S > K."""
    return OptionPricer(S=110, K=100, T=30 / 365, r=0.05, sigma=0.25)


@pytest.fixture
def otm_call_pricer():
    """OTM call pricer: S < K."""
    return OptionPricer(S=90, K=100, T=30 / 365, r=0.05, sigma=0.25)


@pytest.fixture
def dividend_pricer():
    """Pricer with continuous dividend yield."""
    return OptionPricer(S=180, K=185, T=30 / 365, r=0.053, sigma=0.25, q=0.01)


# ── Input validation ──────────────────────────────────────────────────


class TestInputValidation:
    def test_negative_stock_price(self):
        with pytest.raises(ValueError, match="Stock price must be positive"):
            OptionPricer(S=-10, K=100, T=0.1, r=0.05, sigma=0.2)

    def test_zero_strike(self):
        with pytest.raises(ValueError, match="Strike price must be positive"):
            OptionPricer(S=100, K=0, T=0.1, r=0.05, sigma=0.2)

    def test_negative_time(self):
        with pytest.raises(ValueError, match="Time to expiration must be positive"):
            OptionPricer(S=100, K=100, T=-1, r=0.05, sigma=0.2)

    def test_zero_volatility(self):
        with pytest.raises(ValueError, match="Volatility must be positive"):
            OptionPricer(S=100, K=100, T=0.1, r=0.05, sigma=0)


# ── Option pricing ────────────────────────────────────────────────────


class TestOptionPricing:
    def test_call_price_positive(self, atm_pricer):
        assert atm_pricer.call_price() > 0

    def test_put_price_positive(self, atm_pricer):
        assert atm_pricer.put_price() > 0

    def test_itm_call_has_intrinsic(self, itm_call_pricer):
        """ITM call should be worth at least intrinsic value."""
        assert itm_call_pricer.call_price() >= itm_call_pricer.S - itm_call_pricer.K

    def test_otm_call_less_than_stock(self, otm_call_pricer):
        """OTM call should be worth less than the stock."""
        assert otm_call_pricer.call_price() < otm_call_pricer.S

    def test_put_call_parity(self, atm_pricer):
        """Put-call parity: C - P = S*e^(-qT) - K*e^(-rT)."""
        p = atm_pricer
        call = p.call_price()
        put = p.put_price()
        expected_diff = p.S * np.exp(-p.q * p.T) - p.K * np.exp(-p.r * p.T)
        assert abs((call - put) - expected_diff) < 0.01

    def test_put_call_parity_with_dividend(self, dividend_pricer):
        """Put-call parity should also hold with dividends."""
        p = dividend_pricer
        call = p.call_price()
        put = p.put_price()
        expected_diff = p.S * np.exp(-p.q * p.T) - p.K * np.exp(-p.r * p.T)
        assert abs((call - put) - expected_diff) < 0.01

    def test_longer_expiry_more_expensive(self):
        """Option with longer time should be more expensive (all else equal)."""
        short = OptionPricer(S=100, K=100, T=15 / 365, r=0.05, sigma=0.20)
        long = OptionPricer(S=100, K=100, T=60 / 365, r=0.05, sigma=0.20)
        assert long.call_price() > short.call_price()
        assert long.put_price() > short.put_price()

    def test_higher_vol_more_expensive(self):
        """Higher volatility should increase option price."""
        low_vol = OptionPricer(S=100, K=100, T=30 / 365, r=0.05, sigma=0.10)
        high_vol = OptionPricer(S=100, K=100, T=30 / 365, r=0.05, sigma=0.40)
        assert high_vol.call_price() > low_vol.call_price()


# ── Greeks ────────────────────────────────────────────────────────────


class TestGreeks:
    def test_call_delta_range(self, atm_pricer):
        """Call delta should be between 0 and 1."""
        delta = atm_pricer.call_delta()
        assert 0 < delta < 1

    def test_put_delta_range(self, atm_pricer):
        """Put delta should be between -1 and 0."""
        delta = atm_pricer.put_delta()
        assert -1 < delta < 0

    def test_atm_call_delta_near_05(self, atm_pricer):
        """ATM call delta should be close to 0.5."""
        assert abs(atm_pricer.call_delta() - 0.5) < 0.1

    def test_delta_put_call_relationship(self, atm_pricer):
        """call_delta - put_delta should equal e^(-qT)."""
        diff = atm_pricer.call_delta() - atm_pricer.put_delta()
        expected = np.exp(-atm_pricer.q * atm_pricer.T)
        assert abs(diff - expected) < 0.01

    def test_gamma_positive(self, atm_pricer):
        """Gamma is always positive."""
        assert atm_pricer.gamma() > 0

    def test_atm_gamma_highest(self):
        """ATM gamma should be higher than OTM or ITM gamma."""
        atm = OptionPricer(S=100, K=100, T=30 / 365, r=0.05, sigma=0.20)
        itm = OptionPricer(S=120, K=100, T=30 / 365, r=0.05, sigma=0.20)
        otm = OptionPricer(S=80, K=100, T=30 / 365, r=0.05, sigma=0.20)
        assert atm.gamma() > itm.gamma()
        assert atm.gamma() > otm.gamma()

    def test_vega_positive(self, atm_pricer):
        """Vega is always positive (options gain value with higher vol)."""
        assert atm_pricer.vega() > 0

    def test_call_theta_negative(self, atm_pricer):
        """Call theta is typically negative (time decay)."""
        assert atm_pricer.call_theta() < 0

    def test_put_theta_negative(self, atm_pricer):
        """Put theta is typically negative."""
        assert atm_pricer.put_theta() < 0

    def test_call_rho_positive(self, atm_pricer):
        """Call rho is positive (calls gain value with higher rates)."""
        assert atm_pricer.call_rho() > 0

    def test_put_rho_negative(self, atm_pricer):
        """Put rho is negative (puts lose value with higher rates)."""
        assert atm_pricer.put_rho() < 0


# ── Utility methods ───────────────────────────────────────────────────


class TestUtilityMethods:
    def test_intrinsic_value_itm_call(self, itm_call_pricer):
        assert itm_call_pricer.intrinsic_value("call") == 10.0

    def test_intrinsic_value_otm_call(self, otm_call_pricer):
        assert otm_call_pricer.intrinsic_value("call") == 0.0

    def test_intrinsic_value_itm_put(self, otm_call_pricer):
        """OTM call is ITM put."""
        assert otm_call_pricer.intrinsic_value("put") == 10.0

    def test_time_value_positive(self, atm_pricer):
        """Time value should be positive for ATM options."""
        assert atm_pricer.time_value("call") > 0
        assert atm_pricer.time_value("put") > 0

    def test_moneyness_atm(self, atm_pricer):
        assert atm_pricer.moneyness() == "ATM"

    def test_moneyness_itm(self, itm_call_pricer):
        assert "ITM" in itm_call_pricer.moneyness()

    def test_moneyness_otm(self, otm_call_pricer):
        assert "OTM" in otm_call_pricer.moneyness()

    def test_get_all_greeks_call(self, atm_pricer):
        greeks = atm_pricer.get_all_greeks("call")
        assert "price" in greeks
        assert "delta" in greeks
        assert "gamma" in greeks
        assert "theta" in greeks
        assert "vega" in greeks
        assert "rho" in greeks

    def test_get_all_greeks_put(self, atm_pricer):
        greeks = atm_pricer.get_all_greeks("put")
        assert greeks["delta"] < 0  # put delta negative


# ── Historical volatility ─────────────────────────────────────────────


class TestHistoricalVolatility:
    def test_constant_prices_zero_vol(self):
        """Constant prices should give zero volatility."""
        prices = [100.0] * 40
        hv = calculate_historical_volatility(prices, window=30)
        assert hv == 0.0

    def test_insufficient_data(self):
        """Should raise when not enough data for the window."""
        prices = [100.0] * 10
        with pytest.raises(ValueError, match="Need at least"):
            calculate_historical_volatility(prices, window=30)

    def test_reasonable_volatility_range(self):
        """Simulated data should produce a reasonable annualized vol."""
        np.random.seed(42)
        prices = [100.0]
        for _ in range(60):
            prices.append(prices[-1] * (1 + np.random.randn() * 0.01))
        hv = calculate_historical_volatility(prices, window=30)
        # Should be in a reasonable range for ~1% daily moves
        assert 0.05 < hv < 0.50

    def test_higher_moves_higher_vol(self):
        """Larger daily moves should produce higher volatility."""
        np.random.seed(42)
        small_moves = [100.0]
        large_moves = [100.0]
        for _ in range(60):
            r = np.random.randn()
            small_moves.append(small_moves[-1] * (1 + r * 0.005))
            large_moves.append(large_moves[-1] * (1 + r * 0.03))
        hv_small = calculate_historical_volatility(small_moves, window=30)
        hv_large = calculate_historical_volatility(large_moves, window=30)
        assert hv_large > hv_small
