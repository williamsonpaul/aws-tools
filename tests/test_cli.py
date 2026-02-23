"""
Tests for the ASG refresh CLI.
"""

import json
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from src.asg_refresh.cli import main


class TestCLI:
    """Test cases for the CLI interface."""

    def setup_method(self):
        self.runner = CliRunner()

    @patch("src.asg_refresh.cli.ASGRefresh")
    def test_basic_invocation(self, mock_refresher_class):
        mock_refresher = MagicMock()
        mock_refresher.start_refresh.return_value = {
            "InstanceRefreshId": "test-id-123",
            "AutoScalingGroupName": "my-asg",
        }
        mock_refresher_class.return_value = mock_refresher

        result = self.runner.invoke(main, ["my-asg"])

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["InstanceRefreshId"] == "test-id-123"
        assert output["AutoScalingGroupName"] == "my-asg"
        mock_refresher_class.assert_called_once_with(region=None)

    @patch("src.asg_refresh.cli.ASGRefresh")
    def test_with_all_options(self, mock_refresher_class):
        mock_refresher = MagicMock()
        mock_refresher.start_refresh.return_value = {
            "InstanceRefreshId": "test-id-456",
            "AutoScalingGroupName": "prod-asg",
        }
        mock_refresher_class.return_value = mock_refresher

        result = self.runner.invoke(
            main,
            [
                "prod-asg",
                "--min-healthy-percentage",
                "80",
                "--instance-warmup",
                "300",
                "--skip-matching",
                "--region",
                "eu-west-1",
            ],
        )

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["InstanceRefreshId"] == "test-id-456"
        mock_refresher_class.assert_called_once_with(region="eu-west-1")

    def test_help_output(self):
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Auto Scaling Group" in result.output
        assert "ASG_NAME" in result.output

    @patch("src.asg_refresh.cli.ASGRefresh")
    def test_env_var_asg_name(self, mock_refresher_class):
        mock_refresher = MagicMock()
        mock_refresher.start_refresh.return_value = {
            "InstanceRefreshId": "env-test-id",
            "AutoScalingGroupName": "env-asg",
        }
        mock_refresher_class.return_value = mock_refresher

        result = self.runner.invoke(main, [], env={"ASG_NAME": "env-asg"})

        assert result.exit_code == 0

    @patch("src.asg_refresh.cli.ASGRefresh")
    def test_default_options_passed_to_refresh(self, mock_refresher_class):
        mock_refresher = MagicMock()
        mock_refresher.start_refresh.return_value = {
            "InstanceRefreshId": "test-id",
            "AutoScalingGroupName": "test-asg",
        }
        mock_refresher_class.return_value = mock_refresher

        self.runner.invoke(main, ["test-asg"])

        call_args = mock_refresher.start_refresh.call_args
        options_arg = call_args[0][1]
        assert options_arg.min_healthy_percentage == 90
        assert options_arg.instance_warmup is None
        assert options_arg.skip_matching is False

    @patch("src.asg_refresh.cli.ASGRefresh")
    def test_skip_matching_flag(self, mock_refresher_class):
        mock_refresher = MagicMock()
        mock_refresher.start_refresh.return_value = {
            "InstanceRefreshId": "test-id",
            "AutoScalingGroupName": "test-asg",
        }
        mock_refresher_class.return_value = mock_refresher

        result = self.runner.invoke(main, ["test-asg", "--skip-matching"])

        assert result.exit_code == 0
        call_args = mock_refresher.start_refresh.call_args
        options_arg = call_args[0][1]
        assert options_arg.skip_matching is True
