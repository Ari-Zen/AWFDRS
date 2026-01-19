# AI Analysis Module

## Overview

The `ai/` module provides AI-assisted error classification, root cause analysis, and similarity search. **All implementations are mocked** to ensure zero API costs during development.

## Purpose

- **Error classification** - Categorize failures using LLM analysis (mock)
- **Root cause analysis** - Identify underlying issues (mock)
- **Similarity search** - Find similar historical incidents (mock)
- **Decision auditing** - Record AI decisions for transparency

---

## ⚠️ IMPORTANT: Mock-Only Implementation

**This module uses 100% mock implementations:**
- **No real API calls** to OpenAI, Pinecone, or any external service
- **Zero API costs** - Completely free to run
- **Deterministic responses** - Same input always returns same output
- **Offline capable** - Works without internet connection

**Enforcement:**
```python
# config.py validates AI mode
@field_validator('mode')
def validate_mode(cls, v: str) -> str:
    if v != "mock":
        raise ValueError("AI mode must be 'mock'")
    return v
```

---

## Components

### `llm/client.py` - LLM Client Factory
**Purpose:** Create mock OpenAI clients.

```python
def create_llm_client() -> MockOpenAIClient:
    """
    Create LLM client (always returns mock).

    Returns deterministic mock responses for:
    - Error classification
    - Root cause analysis
    - Remediation suggestions
    """
```

**Mock Response Format:**
```json
{
  "analysis": {
    "category": "payment_failure",
    "confidence": 0.95,
    "reasoning": "Error code and message indicate payment gateway timeout"
  }
}
```

---

### `vectorstore/client.py` - Vector Database Factory
**Purpose:** Create mock Pinecone clients.

```python
def create_vectorstore_client() -> MockPineconeClient:
    """
    Create vector store client (always returns mock).

    Returns deterministic similar incidents based on:
    - Error signature matching
    - Workflow similarity
    - Historical patterns
    """
```

**Mock Response Format:**
```json
{
  "matches": [
    {
      "id": "inc-123",
      "score": 0.95,
      "metadata": {
        "signature": "payment.failed:timeout",
        "resolution": "Increased timeout threshold"
      }
    }
  ]
}
```

---

### `agents/detector.py` - Error Classification Agent
**Purpose:** Classify errors into categories (mock LLM analysis).

**Class: AIDetectionAgent**

```python
async def classify_error(
    self,
    event: Event
) -> dict:
    """
    Classify error using mock LLM.

    Returns:
    {
      "category": "payment_gateway_failure",
      "subcategory": "timeout",
      "confidence": 0.92,
      "recommended_action": "retry",
      "reasoning": "Transient network error pattern"
    }
    """
```

**Mock Classification Logic:**
- Matches error_code to predefined patterns
- Returns deterministic confidence scores
- Suggests actions based on error pattern

---

### `agents/rca.py` - Root Cause Analysis Agent
**Purpose:** Analyze root causes (mock LLM reasoning).

**Class: AIRCAAgent**

```python
async def analyze_root_cause(
    self,
    incident: Incident,
    correlated_events: List[Event]
) -> dict:
    """
    Perform root cause analysis using mock LLM.

    Returns:
    {
      "root_cause": "Payment gateway timeout",
      "contributing_factors": [
        "High traffic volume",
        "Network latency spike"
      ],
      "evidence": ["Event pattern", "Timing correlation"],
      "confidence": 0.88,
      "recommended_remediation": "Retry with exponential backoff"
    }
    """
```

**Mock RCA Logic:**
- Analyzes event patterns
- Correlates timing and frequency
- Returns plausible mock reasoning

---

### `similarity/search.py` - Similarity Search
**Purpose:** Find similar historical incidents (mock vector search).

**Class: SimilaritySearch**

```python
async def find_similar_incidents(
    self,
    incident: Incident,
    limit: int = 5
) -> List[dict]:
    """
    Find similar incidents using mock vector search.

    Returns:
    [
      {
        "incident_id": "inc-456",
        "similarity_score": 0.93,
        "signature": "payment.failed:timeout",
        "resolution": "Retry succeeded",
        "resolution_time_minutes": 15
      }
    ]
    """
```

**Mock Similarity Logic:**
- Matches signatures (exact and fuzzy)
- Returns deterministic results
- Includes mock resolution information

---

### `decision_service.py` - AI Decision Orchestration
**Purpose:** Coordinate all AI analysis components.

**Class: AIDecisionService**

```python
async def make_decision(
    self,
    incident: Incident
) -> Decision:
    """
    Orchestrate AI analysis and create decision record.

    Steps:
    1. Classify error (AIDetectionAgent)
    2. Analyze root cause (AIRCAAgent)
    3. Search similar incidents (SimilaritySearch)
    4. Synthesize recommendation
    5. Record decision (audit trail)

    Returns:
        Decision record with AI analysis
    """
```

---

## Mock Implementation Details

### Mock OpenAI Client

**Located:** `tests/mocks/mock_openai.py` (used in production!)

```python
class MockOpenAIClient:
    """Deterministic OpenAI mock."""

    def __init__(self):
        self.chat = MockChatCompletion()

class MockChatCompletion:
    async def create(self, model: str, messages: list, **kwargs):
        """Return deterministic response based on prompt."""
        prompt = messages[-1]["content"]

        if "classify" in prompt.lower():
            return self._classification_response()
        elif "root cause" in prompt.lower():
            return self._rca_response()
        else:
            return self._generic_response()
```

**Response Patterns:**
- **Classification:** Returns category + confidence
- **RCA:** Returns root cause + factors + remediation
- **Generic:** Returns structured analysis

---

### Mock Pinecone Client

**Located:** `tests/mocks/mock_pinecone.py`

```python
class MockPineconeClient:
    """Deterministic Pinecone mock."""

    def __init__(self):
        self._mock_data = self._generate_mock_incidents()

    async def query(
        self,
        vector: list,
        top_k: int = 5,
        **kwargs
    ) -> dict:
        """Return deterministic similar incidents."""
        # Return top K from mock data
        return {
            "matches": self._mock_data[:top_k]
        }

    def _generate_mock_incidents(self):
        """Generate deterministic mock incident database."""
        return [
            {
                "id": "inc-001",
                "score": 0.95,
                "metadata": {"signature": "payment.failed:timeout"}
            },
            ...
        ]
```

---

## Decision Audit Trail

**Purpose:** Record all AI decisions for transparency and debugging.

**Model:** `Decision` (database)

```python
class Decision:
    id: UUID
    incident_id: UUID
    decision_type: str  # "classification", "rca", "recommendation"
    reasoning: str  # AI reasoning (from mock)
    confidence_score: float
    ai_model: str  # "mock-gpt-4", "mock-pinecone"
    created_at: datetime
```

**Benefits:**
- **Audit trail:** Track what AI "decided"
- **Debugging:** Understand why action was taken
- **Learning:** Analyze decision patterns over time

---

## Configuration

**All AI configuration in `.env`:**

```env
AI_MODE=mock  # MUST be "mock"
OPENAI_API_KEY=mock-key-no-real-calls  # Placeholder (not used)
PINECONE_API_KEY=mock-key-no-real-calls  # Placeholder (not used)
AI_CONFIDENCE_THRESHOLD=0.7  # Minimum confidence for auto-action
```

**Feature Flags:**
```env
ENABLE_AI_DETECTION=false  # Enable AI error classification
ENABLE_AI_RCA=false  # Enable AI root cause analysis
```

**When disabled:** System uses rule-based logic instead of AI agents.

---

## Testing

```python
def test_ai_detector_returns_mock_classification():
    agent = AIDetectionAgent()
    event = create_payment_failure_event()

    result = await agent.classify_error(event)

    assert result["category"] == "payment_failure"
    assert result["confidence"] > 0.7
    assert "reasoning" in result

def test_mock_openai_client_is_deterministic():
    client = MockOpenAIClient()
    prompt = "Classify error: payment timeout"

    # Call twice
    response1 = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    response2 = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    # Should be identical (deterministic)
    assert response1.content == response2.content
```

---

## Future: Real AI Integration (Optional)

**If/when switching to real AI APIs:**

1. **Update configuration validation** - Remove mock enforcement
2. **Implement real clients** - Replace mocks with actual API calls
3. **Add cost controls** - Token budgets, rate limiting
4. **Add caching** - Cache embeddings and responses
5. **Add monitoring** - Track API costs, latency, errors
6. **Add fallback** - Fall back to rule-based on API failure

**Cost Considerations:**
- OpenAI GPT-4: $0.03/1K tokens (input), $0.06/1K tokens (output)
- Pinecone: $0.096/hour for serverless index
- Typical incident: 5-10 API calls, ~$0.01-0.05 per incident

**Recommendation:** Start with mock, validate value, then enable real APIs if needed.

---

## Monitoring

### Metrics
- `ai_decisions_total{decision_type}` - AI decisions made
- `ai_confidence_distribution` - Histogram of confidence scores
- `ai_api_calls_total` - API calls (should be 0 in mock mode!)
- `ai_cost_dollars_total` - API costs (should be 0 in mock mode!)

### Alerts
- Alert if AI_MODE != "mock" (accidental real API usage!)
- Alert if ai_api_calls_total > 0 (should never happen)
- Alert if ai_cost_dollars_total > 0 (should never happen)

---

## See Also

- [ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) - AI layer design
- [tests/mocks/](../../../tests/mocks/) - Mock implementations
