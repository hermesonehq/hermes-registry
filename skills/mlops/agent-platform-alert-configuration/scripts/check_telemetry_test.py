# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for check_telemetry.py."""

import os
import sys
import types
import unittest
from unittest import mock

script_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "check_telemetry.py"
)
with open(script_path, "r") as f:
  code_content = f.read()

check_telemetry = types.ModuleType("check_telemetry")
check_telemetry.__file__ = script_path
sys.modules["check_telemetry"] = check_telemetry
exec(code_content, check_telemetry.__dict__)


class CheckTelemetryTest(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self.project_id = "test-project"
    self.location = "us-central1"
    self.agent_id = "123456789"
    self.agent_resource_name = (
        f"projects/{self.project_id}/locations/{self.location}/"
        f"reasoningEngines/{self.agent_id}"
    )

  @mock.patch("check_telemetry.aiplatform_v1beta1.ReasoningEngineServiceClient")
  def test_check_agent_telemetry_enabled(self, mock_client_class):
    mock_client = mock_client_class.return_value
    mock_engine = mock.Mock()

    env_var_1 = mock.Mock()
    env_var_1.name = "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY"
    env_var_1.value = "true"

    env_var_2 = mock.Mock()
    env_var_2.name = "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"
    env_var_2.value = "EVENT_ONLY"

    mock_engine.spec.deployment_spec.env = [env_var_1, env_var_2]
    mock_client.get_reasoning_engine.return_value = mock_engine

    result = check_telemetry.check_agent_telemetry(
        project_id=self.project_id,
        location=self.location,
        agent_resource_name=self.agent_id,
    )

    self.assertTrue(result)
    mock_client.get_reasoning_engine.assert_called_once_with(
        name=self.agent_resource_name
    )

  @mock.patch("check_telemetry.aiplatform_v1beta1.ReasoningEngineServiceClient")
  def test_check_agent_telemetry_disabled_missing_telemetry_toggle(
      self, mock_client_class
  ):
    mock_client = mock_client_class.return_value
    mock_engine = mock.Mock()

    env_var_1 = mock.Mock()
    env_var_1.name = "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY"
    env_var_1.value = "false"

    env_var_2 = mock.Mock()
    env_var_2.name = "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"
    env_var_2.value = "EVENT_ONLY"

    mock_engine.spec.deployment_spec.env = [env_var_1, env_var_2]
    mock_client.get_reasoning_engine.return_value = mock_engine

    result = check_telemetry.check_agent_telemetry(
        project_id=self.project_id,
        location=self.location,
        agent_resource_name=self.agent_id,
    )

    self.assertFalse(result)

  @mock.patch("check_telemetry.aiplatform_v1beta1.ReasoningEngineServiceClient")
  def test_check_agent_telemetry_disabled_missing_capture_toggle(
      self, mock_client_class
  ):
    mock_client = mock_client_class.return_value
    mock_engine = mock.Mock()

    env_var_1 = mock.Mock()
    env_var_1.name = "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY"
    env_var_1.value = "true"

    mock_engine.spec.deployment_spec.env = [env_var_1]
    mock_client.get_reasoning_engine.return_value = mock_engine

    result = check_telemetry.check_agent_telemetry(
        project_id=self.project_id,
        location=self.location,
        agent_resource_name=self.agent_id,
    )

    self.assertFalse(result)


if __name__ == "__main__":
  unittest.main()
