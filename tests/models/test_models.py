# UPSTREAM SYNC: if any new models are added to this file, add them
# to test_models_logprobs.py as well
"""Compare the outputs of HF and vLLM when using greedy sampling.

This test only tests small models. Big models such as 7B should be tested from
test_big_models.py because it could use a larger instance to run tests.

Run `pytest tests/models/test_models.py`.
"""
import pytest

MODELS = [
    "facebook/opt-125m",
    "gpt2",
    "bigcode/tiny_starcoder_py",
    "EleutherAI/pythia-70m",
    "bigscience/bloom-560m",  # Testing alibi slopes.
    "microsoft/phi-2",
    "stabilityai/stablelm-3b-4e1t",
    # "allenai/OLMo-1B",  # Broken
    "bigcode/starcoder2-3b",
]


# UPSTREAM SYNC: we run OOM on the A10g instances.
@pytest.mark.skip("Not enough memory in automation testing.")
@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("dtype", ["float"])
@pytest.mark.parametrize("max_tokens", [96])
def test_models(
    hf_runner,
    vllm_runner,
    example_prompts,
    model: str,
    dtype: str,
    max_tokens: int,
) -> None:
    # To pass the small model tests, we need full precision.
    assert dtype == "float"

    hf_model = hf_runner(model, dtype=dtype)
    hf_outputs = hf_model.generate_greedy(example_prompts, max_tokens)
    del hf_model

    vllm_model = vllm_runner(model, dtype=dtype)
    vllm_outputs = vllm_model.generate_greedy(example_prompts, max_tokens)
    del vllm_model

    for i in range(len(example_prompts)):
        hf_output_ids, hf_output_str = hf_outputs[i]
        vllm_output_ids, vllm_output_str = vllm_outputs[i]
        assert hf_output_str == vllm_output_str, (
            f"Test{i}:\nHF: {hf_output_str!r}\nvLLM: {vllm_output_str!r}")
        assert hf_output_ids == vllm_output_ids, (
            f"Test{i}:\nHF: {hf_output_ids}\nvLLM: {vllm_output_ids}")


@pytest.mark.skip("Slow and not useful (just prints model).")
@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("dtype", ["float"])
def test_model_print(
    vllm_runner,
    model: str,
    dtype: str,
) -> None:
    vllm_model = vllm_runner(model, dtype=dtype)
    # This test is for verifying whether the model's extra_repr
    # can be printed correctly.
    print(vllm_model.model.llm_engine.model_executor.driver_worker.
          model_runner.model)
    del vllm_model
