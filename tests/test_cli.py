"""
Tests for the ASG refresh CLI.
"""

import json
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from src.aws_asg.cli import main


class TestStartCommand:
    """Test cases for the start subcommand."""

    def setup_method(self):
        self.runner = CliRunner()

    @patch("src.aws_asg.cli.ASGRefresh")
    def test_basic_invocation(self, mock_refresher_class):
        mock_refresher = MagicMock()
        mock_refresher.start_refresh.return_value = {
            "InstanceRefreshId": "test-id-123",
            "AutoScalingGroupName": "my-asg",
        }
        mock_refresher_class.return_value = mock_refresher

        result = self.runner.invoke(main, ["start", "my-asg"])

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["InstanceRefreshId"] == "test-id-123"
        assert output["AutoScalingGroupName"] == "my-asg"
        mock_refresher_class.assert_called_once_with(region=None)

    @patch("src.aws_asg.cli.ASGRefresh")
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
                "start",
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

    def test_start_help_output(self):
        result = self.runner.invoke(main, ["start", "--help"])
        assert result.exit_code == 0
        assert "Auto Scaling Group" in result.output
        assert "ASG_NAME" in result.output

    @patch("src.aws_asg.cli.ASGRefresh")
    def test_env_var_asg_name(self, mock_refresher_class):
        mock_refresher = MagicMock()
        mock_refresher.start_refresh.return_value = {
            "InstanceRefreshId": "env-test-id",
            "AutoScalingGroupName": "env-asg",
        }
        mock_refresher_class.return_value = mock_refresher

        result = self.runner.invoke(main, ["start"], env={"ASG_NAME": "env-asg"})

        assert result.exit_code == 0

    @patch("src.aws_asg.cli.ASGRefresh")
    def test_default_options_passed_to_refresh(self, mock_refresher_class):
        mock_refresher = MagicMock()
        mock_refresher.start_refresh.return_value = {
            "InstanceRefreshId": "test-id",
            "AutoScalingGroupName": "test-asg",
        }
        mock_refresher_class.return_value = mock_refresher

        self.runner.invoke(main, ["start", "test-asg"])

        call_args = mock_refresher.start_refresh.call_args
        options_arg = call_args[0][1]
        assert options_arg.min_healthy_percentage == 90
        assert options_arg.instance_warmup is None
        assert options_arg.skip_matching is False

    @patch("src.aws_asg.cli.ASGRefresh")
    def test_skip_matching_flag(self, mock_refresher_class):
        mock_refresher = MagicMock()
        mock_refresher.start_refresh.return_value = {
            "InstanceRefreshId": "test-id",
            "AutoScalingGroupName": "test-asg",
        }
        mock_refresher_class.return_value = mock_refresher

        result = self.runner.invoke(main, ["start", "test-asg", "--skip-matching"])

        assert result.exit_code == 0
        call_args = mock_refresher.start_refresh.call_args
        options_arg = call_args[0][1]
        assert options_arg.skip_matching is True


class TestCheckCommand:
    """Test cases for the check subcommand."""

    def setup_method(self):
        self.runner = CliRunner()

    @patch("src.aws_asg.cli.ASGRefresh")
    def test_check_success(self, mock_refresher_class):
        mock_refresher = MagicMock()
        mock_refresher.wait_for_refresh.return_value = {
            "InstanceRefreshId": "r-1",
            "Status": "Successful",
            "PercentageComplete": 100,
        }
        mock_refresher_class.return_value = mock_refresher

        result = self.runner.invoke(main, ["check", "my-asg", "r-1"])

        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["Status"] == "Successful"
        mock_refresher_class.assert_called_once_with(region=None)

    @patch("src.aws_asg.cli.ASGRefresh")
    def test_check_failure_exits_nonzero(self, mock_refresher_class):
        mock_refresher = MagicMock()
        mock_refresher.wait_for_refresh.return_value = {
            "InstanceRefreshId": "r-1",
            "Status": "Failed",
        }
        mock_refresher_class.return_value = mock_refresher

        result = self.runner.invoke(main, ["check", "my-asg", "r-1"])

        assert result.exit_code == 1

    @patch("src.aws_asg.cli.ASGRefresh")
    def test_check_timeout_exits_nonzero(self, mock_refresher_class):
        mock_refresher = MagicMock()
        mock_refresher.wait_for_refresh.side_effect = TimeoutError("Timed out")
        mock_refresher_class.return_value = mock_refresher

        result = self.runner.invoke(main, ["check", "my-asg", "r-1"])

        assert result.exit_code == 1

    def test_check_help_output(self):
        result = self.runner.invoke(main, ["check", "--help"])
        assert result.exit_code == 0
        assert "REFRESH_ID" in result.output
        assert "ASG_NAME" in result.output
        assert "--interval" in result.output
        assert "--timeout" in result.output

    @patch("src.aws_asg.cli.ASGRefresh")
    def test_check_with_options(self, mock_refresher_class):
        mock_refresher = MagicMock()
        mock_refresher.wait_for_refresh.return_value = {
            "Status": "Successful",
        }
        mock_refresher_class.return_value = mock_refresher

        result = self.runner.invoke(
            main,
            [
                "check",
                "my-asg",
                "r-1",
                "--interval",
                "10",
                "--timeout",
                "600",
                "--region",
                "us-west-2",
            ],
        )

        assert result.exit_code == 0
        mock_refresher_class.assert_called_once_with(region="us-west-2")
        mock_refresher.wait_for_refresh.assert_called_once()
        call_kwargs = mock_refresher.wait_for_refresh.call_args
        assert call_kwargs[1]["interval"] == 10
        assert call_kwargs[1]["timeout"] == 600

    def test_group_help_output(self):
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "start" in result.output
        assert "check" in result.output
