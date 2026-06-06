"""Local SANDBOX_MODEL_ONLY broker interface modeling for Sprint 9."""

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import (
    BrokerReadinessCheck,
    BrokerReadinessStatus,
    BrokerSandboxMode,
    EngineMode,
    SandboxAccountState,
    SandboxOrderRequest,
    SandboxOrderResponse,
    SandboxOrderSide,
    SandboxOrderStatus,
    SandboxOrderType,
    SandboxRejectReason,
)


PLACEHOLDER_PRICES = {
    "EURUSD": 1.0800,
    "GBPUSD": 1.2700,
    "USDJPY": 155.00,
    "XAUUSD": 2350.00,
}

CREDENTIAL_METADATA_KEYS = {"api_key", "token", "secret", "password", "account_id", "broker_token"}
ALLOWED_MODES = {BrokerSandboxMode.SANDBOX_MODEL_ONLY, BrokerSandboxMode.PAPER_ONLY_COMPATIBLE, EngineMode.PAPER_ONLY}


class BrokerSandbox:
    def __init__(self, config: ForexEngineConfig):
        self.config = config
        self.account_state = SandboxAccountState(
            mode=BrokerSandboxMode.SANDBOX_MODEL_ONLY,
            starting_balance_usd=config.starting_balance_usd,
            current_balance_usd=config.starting_balance_usd,
            live_trading_enabled=False,
            credentials_loaded=False,
            network_enabled=False,
            metadata={"fill_model": "SIMULATED", "price_source": "deterministic placeholders"},
        )
        self._pending_orders = {}
        self._sequence = 0

    def submit_order(self, request: SandboxOrderRequest) -> SandboxOrderResponse:
        allowed, reject_reason, message = self.validate_order_request(request)
        if not allowed:
            self.account_state.rejected_order_count += 1
            return self._response(
                request,
                status=(
                    SandboxOrderStatus.LIVE_BLOCKED
                    if reject_reason == SandboxRejectReason.LIVE_TRADING_BLOCKED
                    else SandboxOrderStatus.REJECTED
                ),
                reject_reason=reject_reason,
                message=message,
            )
        if request.order_type == SandboxOrderType.MARKET:
            return self.simulate_fill(request)

        self.account_state.open_order_count += 1
        response = self._response(
            request,
            status=SandboxOrderStatus.PENDING,
            reject_reason=SandboxRejectReason.NONE,
            message=f"{request.order_type} order accepted as local model-only pending state.",
            fill_price=None,
        )
        self._pending_orders[request.client_order_id] = response
        return response

    def validate_order_request(self, request: SandboxOrderRequest):
        if request.mode not in ALLOWED_MODES:
            if "LIVE" in str(request.mode).upper():
                return False, SandboxRejectReason.LIVE_TRADING_BLOCKED, "Live trading is blocked in Sprint 9."
            return False, SandboxRejectReason.INVALID_MODE, "Only SANDBOX_MODEL_ONLY or PAPER_ONLY compatible modes are allowed."
        if self._has_credential_metadata(request.metadata):
            return False, SandboxRejectReason.CREDENTIALS_NOT_ALLOWED, "Credential-like metadata is not allowed."
        if request.symbol not in self.config.symbols:
            return False, SandboxRejectReason.INVALID_SYMBOL, "Symbol is not configured for the sandbox model."
        if request.side not in (SandboxOrderSide.BUY, SandboxOrderSide.SELL):
            return False, SandboxRejectReason.INVALID_SIDE, "Order side must be BUY or SELL."
        if request.order_type not in (SandboxOrderType.MARKET, SandboxOrderType.LIMIT, SandboxOrderType.STOP):
            return False, SandboxRejectReason.INVALID_ORDER_TYPE, "Order type must be MARKET, LIMIT, or STOP."
        if request.units <= 0:
            return False, SandboxRejectReason.INVALID_UNITS, "Units must be positive."
        if request.order_type == SandboxOrderType.MARKET:
            if request.requested_price is not None and request.requested_price <= 0:
                return False, SandboxRejectReason.INVALID_PRICE, "MARKET requested_price must be positive when supplied."
        elif request.requested_price is None or request.requested_price <= 0:
            return False, SandboxRejectReason.INVALID_PRICE, "LIMIT and STOP orders require a positive requested_price."
        return True, SandboxRejectReason.NONE, "Sandbox model request accepted."

    def simulate_fill(self, request: SandboxOrderRequest) -> SandboxOrderResponse:
        fill_price = request.requested_price if request.requested_price is not None else PLACEHOLDER_PRICES[request.symbol]
        self.account_state.filled_order_count += 1
        return self._response(
            request,
            status=SandboxOrderStatus.FILLED,
            reject_reason=SandboxRejectReason.NONE,
            message="MARKET order filled by deterministic local sandbox model.",
            filled_units=request.units,
            fill_price=fill_price,
        )

    def cancel_order(self, client_order_id: str) -> SandboxOrderResponse:
        response = self._pending_orders.pop(client_order_id, None)
        if response is None:
            request = SandboxOrderRequest(
                mode=BrokerSandboxMode.SANDBOX_MODEL_ONLY,
                symbol="",
                side="",
                order_type=SandboxOrderType.LIMIT,
                units=0,
                client_order_id=client_order_id,
            )
            self.account_state.rejected_order_count += 1
            return self._response(
                request,
                status=SandboxOrderStatus.REJECTED,
                reject_reason=SandboxRejectReason.INVALID_SYMBOL,
                message="No matching local pending sandbox order exists.",
            )
        self.account_state.open_order_count = max(0, self.account_state.open_order_count - 1)
        return SandboxOrderResponse(
            mode=response.mode,
            client_order_id=response.client_order_id,
            sandbox_order_id=response.sandbox_order_id,
            symbol=response.symbol,
            side=response.side,
            order_type=response.order_type,
            requested_units=response.requested_units,
            filled_units=0.0,
            requested_price=response.requested_price,
            fill_price=None,
            status=SandboxOrderStatus.CANCELLED,
            reject_reason=SandboxRejectReason.NONE,
            message="Local sandbox pending order cancelled.",
            metadata={"sandbox_model_only": True},
        )

    def build_readiness_check(self) -> BrokerReadinessCheck:
        return BrokerReadinessCheck(
            mode=BrokerSandboxMode.SANDBOX_MODEL_ONLY,
            status=BrokerReadinessStatus.NOT_LIVE_READY,
            checks=[
                "broker sandbox model exists",
                "credentials not loaded",
                "network disabled",
                "live trading disabled",
                "order request validation exists",
                "fill simulation exists",
            ],
            blocked_reasons=[
                "no real broker API configured",
                "no credentials allowed",
                "no live authorization",
                "no production execution approval",
            ],
            next_safe_action="Continue with risk management and sandbox modeling before any broker integration.",
            metadata={"connectivity": "DISABLED", "credentials_required": False},
        )

    def format_readiness_check(self, check) -> str:
        return "\n".join(
            [
                f"Sandbox mode: {check.mode}",
                f"Readiness status: {check.status}",
                f"Checks: {', '.join(check.checks)}",
                f"Blocked reasons: {', '.join(check.blocked_reasons)}",
                f"Next safe action: {check.next_safe_action}",
            ]
        )

    def _has_credential_metadata(self, metadata):
        return bool(CREDENTIAL_METADATA_KEYS & {str(key).lower() for key in metadata.keys()})

    def _response(
        self,
        request,
        status,
        reject_reason,
        message,
        filled_units=0.0,
        fill_price=None,
    ) -> SandboxOrderResponse:
        self._sequence += 1
        return SandboxOrderResponse(
            mode=BrokerSandboxMode.SANDBOX_MODEL_ONLY,
            client_order_id=request.client_order_id,
            sandbox_order_id=f"SBOX-{self._sequence:06d}",
            symbol=request.symbol,
            side=request.side,
            order_type=request.order_type,
            requested_units=request.units,
            filled_units=filled_units,
            requested_price=request.requested_price,
            fill_price=fill_price,
            status=status,
            reject_reason=reject_reason,
            message=message,
            metadata={"sandbox_model_only": True, "live_trading_enabled": False, "network_enabled": False},
        )
