from types import SimpleNamespace
from contextlib import redirect_stdout
from io import StringIO
import os
import unittest
from unittest.mock import patch

import bedrock
from agent import ToolCallingAgent
from evaluation import EvalSuite, build_bedrock_judge, build_candidate_models


class FakeAgent:
    def __init__(self, answer: str, model_id: str = "candidate-model") -> None:
        self.answer = answer
        self.model = SimpleNamespace(model_id=model_id)
        self.memory = SimpleNamespace(steps=[])

    def run(self, question: str, reset: bool = True, stream: bool = False):
        self.memory.steps = [
            SimpleNamespace(
                step_number=1,
                token_usage=SimpleNamespace(input_tokens=100, output_tokens=20),
                tool_calls=[object()],
                model_output_message=None,
            )
        ]
        events = iter(
            [
                self.memory.steps[0],
                SimpleNamespace(output=self.answer),
            ]
        )
        return events if stream else self.answer


class FakeJudge:
    model_id = "judge-model"

    def generate(self, messages):
        return SimpleNamespace(
            content='{"passed": true, "score": 4, "reason": "Correct."}',
            token_usage=SimpleNamespace(input_tokens=50, output_tokens=10),
            raw=None,
        )


class BrokenJudge:
    model_id = "broken-judge"

    def generate(self, messages):
        raise RuntimeError("judge unavailable")


class EvalSuiteTest(unittest.TestCase):
    def test_primary_bedrock_model_does_not_rewrite_messages(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=False),
            patch("bedrock.getpass.getpass", return_value="test-key"),
            patch("builtins.input", side_effect=["", ""]),
            patch("bedrock.LiteLLMModel") as model_class,
        ):
            bedrock.build_bedrock_model()

        self.assertNotIn("modify_params", model_class.call_args.kwargs)

    def test_judge_uses_bedrock_compatible_parameters(self) -> None:
        with (
            patch.dict(
                os.environ,
                {
                    "AWS_BEARER_TOKEN_BEDROCK": "test-key",
                    "AWS_REGION_NAME": "eu-north-1",
                },
            ),
            patch("evaluation.boto3.client") as client,
        ):
            client.return_value.converse.return_value = {
                "output": {
                    "message": {
                        "content": [
                            {
                                "text": (
                                    '{"passed": true, "score": 4, '
                                    '"reason": "Correct."}'
                                )
                            }
                        ]
                    }
                },
                "usage": {"inputTokens": 50, "outputTokens": 10},
            }
            judge = build_bedrock_judge()
            response = judge.generate([{"role": "user", "content": "Judge this"}])

        client.assert_called_once_with("bedrock-runtime", region_name="eu-north-1")
        self.assertEqual(judge.max_tokens, 700)
        client.return_value.converse.assert_called_once_with(
            modelId="eu.anthropic.claude-opus-4-5-20251101-v1:0",
            messages=[
                {"role": "user", "content": [{"text": "Judge this"}]}
            ],
            inferenceConfig={"maxTokens": 700},
        )
        self.assertEqual(response.token_usage.input_tokens, 50)
        self.assertGreater(response.cost_usd, 0)

    def test_candidate_models_share_generation_settings(self) -> None:
        model_ids = {
            "small": "bedrock/example-small",
            "large": "bedrock/example-large",
        }
        with (
            patch.dict(os.environ, {"AWS_BEARER_TOKEN_BEDROCK": "test-key"}),
            patch("evaluation.LiteLLMModel") as model_class,
        ):
            candidates = build_candidate_models(model_ids)

        self.assertEqual(list(candidates), ["small", "large"])
        self.assertEqual(model_class.call_count, 2)
        for call in model_class.call_args_list:
            self.assertEqual(call.kwargs["max_tokens"], 1200)
            self.assertEqual(call.kwargs["tool_choice"], "auto")
            self.assertEqual(call.kwargs["reasoning_effort"], "low")
            self.assertNotIn("modify_params", call.kwargs)

    def test_workshop_agents_serialize_tool_calls(self) -> None:
        agent = ToolCallingAgent(
            tools=[],
            model=SimpleNamespace(model_id="fake-model"),
        )

        self.assertEqual(agent.max_tool_threads, 1)

    def test_eval_and_summary(self) -> None:
        suite = EvalSuite(
            candidates={"minimal": FakeAgent("Expected result")},
            judge_model=FakeJudge(),
        )

        output = StringIO()
        with redirect_stdout(output):
            result = suite.eval(
                "Question?",
                "Expected result",
                scenario="demo",
                display_results=False,
            )
            suite.eval(
                "Question?",
                "Expected result",
                scenario="demo",
                display_results=False,
            )
        summary = suite.summary(display_results=False)

        self.assertTrue(bool(result.loc[0, "passed"]))
        self.assertEqual(result.loc[0, "score"], 4)
        self.assertEqual(result.loc[0, "steps"], 1)
        self.assertEqual(result.loc[0, "tool_calls"], 1)
        self.assertEqual(result.loc[0, "input_tokens"], 100)
        self.assertEqual(len(suite.results), 1)
        self.assertEqual(summary.loc[0, "pass_rate"], 100.0)
        self.assertIn("[1/1] minimal: step 1 complete, 1 tool call", output.getvalue())
        self.assertIn("[1/1] minimal: PASS (4/4)", output.getvalue())

    def test_judge_error_is_not_reported_as_candidate_failure(self) -> None:
        suite = EvalSuite(
            candidates={"minimal": FakeAgent("Expected result")},
            judge_model=BrokenJudge(),
        )

        result = suite.eval(
            "Question?",
            "Expected result",
            display_results=False,
        )

        self.assertEqual(result.loc[0, "status"], "judge_error")
        self.assertIsNone(result.loc[0, "passed"])
        self.assertIsNone(result.loc[0, "score"])


if __name__ == "__main__":
    unittest.main()
