import pytest
from app.integrations.hindsight import HindsightClient, _mock_memory_store
from app.integrations.gemini import GeminiClient
from app.services.assistant_service import is_persistent_memory_candidate


@pytest.mark.asyncio
async def test_hindsight_client_mock_remember_and_recall():
    client = HindsightClient(api_key="mock_hindsight_key")
    assert client.is_live is False

    shop_id = "test_shop_123"
    _mock_memory_store.pop(shop_id, None)

    # 1. Remember persistent preference
    remember_ok = await client.remember(
        shop_id=shop_id,
        memory_type="OWNER_PREFERENCE",
        content="Main Maggi ek baar mein 35 se zyada order nahi karta."
    )
    assert remember_ok is True

    # 2. Recall memory for related query
    memories = await client.recall(shop_id=shop_id, query="Maggi order quantity", limit=5)
    assert len(memories) >= 1
    assert any("35" in m["content"] for m in memories)


@pytest.mark.asyncio
async def test_hindsight_client_live_mode_init():
    client = HindsightClient(api_key="real_hindsight_test_key", api_url="https://api.hindsight.ai/v1")
    assert client.is_live is True
    assert client.headers["Authorization"] == "Bearer real_hindsight_test_key"


@pytest.mark.asyncio
async def test_gemini_client_mock_and_live_init():
    client_mock = GeminiClient(api_key="mock_gemini_key")
    assert client_mock.is_live is False

    client_live = GeminiClient(api_key="real_gemini_test_key")
    assert client_live.is_live is True


def test_settings_integration_configuration():
    from app.core.config import settings
    from app.integrations.sarvam import SarvamClient
    from app.integrations.hindsight import HindsightClient
    from app.integrations.gemini import GeminiClient

    assert hasattr(settings, "GEMINI_API_KEY")
    assert hasattr(settings, "HINDSIGHT_API_KEY")
    assert hasattr(settings, "HINDSIGHT_BASE_URL")
    assert hasattr(settings, "SARVAM_API_KEY")
    assert hasattr(settings, "SARVAM_BASE_URL")

    h_client = HindsightClient()
    g_client = GeminiClient()
    s_client = SarvamClient()

    assert h_client.api_url is not None
    assert g_client.model is not None
    assert s_client.base_url is not None


@pytest.mark.asyncio
async def test_gemini_client_generate_response_mock():
    client = GeminiClient(api_key="mock_gemini_key")

    context = {
        "db_facts": {
            "shop_name": "Gupta Kirana",
            "matched_product": {"name": "Maggi 2-Min", "stock": 12}
        }
    }
    memories = [
        {"memory_type": "OWNER_PREFERENCE", "content": "Owner preference limit: 35 units max per order."}
    ]
    ml_outputs = {"forecast_7d_demand": 50, "stockout_risk": 0.85}

    response = await client.generate_response(
        prompt="Maggi ka stock check karo aur batao kitna order karna chahiye.",
        context=context,
        memories=memories,
        ml_outputs=ml_outputs
    )

    assert "Maggi" in response or "stock" in response
    assert "12" in response or "30" in response or "35" in response


def test_persistent_memory_quality_filter():
    # Transient banter should be rejected
    assert is_persistent_memory_candidate("hello") is False
    assert is_persistent_memory_candidate("show dashboard") is False
    assert is_persistent_memory_candidate("what are today's sales") is False

    # Persistent rules & preferences should be accepted
    assert is_persistent_memory_candidate("Main Maggi ek baar mein 35 se zyada order nahi karta.") is True
    assert is_persistent_memory_candidate("My preference is smaller dairy orders.") is True
    assert is_persistent_memory_candidate("Sharma supplier always delivers 2 days late.") is True
