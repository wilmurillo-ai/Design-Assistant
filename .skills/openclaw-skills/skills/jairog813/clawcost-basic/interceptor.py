import functools
import time
from tracker import log_call

PRICES = {
    "claude-opus-4-6":           {"in": 15.00, "out": 75.00},
    "claude-sonnet-4-6":         {"in":  3.00, "out": 15.00},
    "claude-haiku-4-5-20251001": {"in":  0.80, "out":  4.00},
    "gpt-4o":                    {"in":  2.50, "out": 10.00},
    "gpt-4o-mini":               {"in":  0.15, "out":  0.60},
    "gemini-2.0-flash":          {"in":  0.10, "out":  0.40},
    "mistral-large":             {"in":  2.00, "out":  6.00},
}

def calc_cost(model, input_tokens, output_tokens):
    p = PRICES.get(model, {"in": 1.00, "out": 3.00})
    return (input_tokens * p["in"] + output_tokens * p["out"]) / 1_000_000

def intercept(original_llm_call):
    @functools.wraps(original_llm_call)
    async def wrapper(*args, **kwargs):
        start = time.time()
        response = await original_llm_call(*args, **kwargs)
        elapsed = round(time.time() - start, 3)

        usage = getattr(response, "usage", {})
        model = kwargs.get("model", "unknown")
        t_in  = getattr(usage, "input_tokens",  0)
        t_out = getattr(usage, "output_tokens", 0)
        cost  = calc_cost(model, t_in, t_out)

        log_call({
            "model":    model,
            "skill":    kwargs.get("skill_name", "unknown"),
            "t_in":     t_in,
            "t_out":    t_out,
            "cost_usd": cost,
            "latency":  elapsed,
        })

        return response
    return wrapper

def register(openclaw_context):
    print("[ClawCost] Interceptor active — tracking all API calls.")
    openclaw_context.llm_client.call = intercept(
        openclaw_context.llm_client.call
    )
