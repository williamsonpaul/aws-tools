"""
Tests for the ASG refresh core module.
"""

import pytest
from unittest.mock import MagicMock, patch, call
from src.asg_refresh.core import ASGRefresh, RefreshOptions


class TestRefreshOptions:
    """Test cases for the RefreshOptions dataclass."""

    def test_default_options(self):
        opts = RefreshOptions()
        assert opts.min_healthy_percentage == 90
        assert opts.instance_warmup is None
        assert opts.skip_matching is False

    def test_custom_options(self):
        opts = RefreshOptions(
            min_healthy_percentage=75,
            instance_warmup=300,
            skip_matching=True,
        )
        assert opts.min_healthy_percentage == 75
        assert opts.instance_warmup == 300
        assert opts.skip_matching is True


class TestASGRefresh:
    """Test cases for the ASGRefresh class."""

    @patch("src.asg_refresh.core.boto3.client")
    def test_init_default_region(self, mock_client):
        ASGRefresh()
        mock_client.assert_called_once_with("autoscaling", region_name=None)

    @patch("src.asg_refresh.core.boto3.client")
    def test_init_with_region(self, mock_client):
        ASGRefresh(region="eu-west-1")
        mock_client.assert_called_once_with("autoscaling", region_name="eu-west-1")

    @patch("src.asg_refresh.core.boto3.client")
    def test_start_refresh_default_options(self, mock_client):
        mock_asg = MagicMock()
        mock_asg.start_instance_refresh.return_value = {
            "InstanceRefreshId": "refresh-abc-123",
        }
        mock_client.return_value = mock_asg

        refresher = ASGRefresh(region="us-east-1")
        options = RefreshOptions()
        result = refresher.start_refresh("my-asg", options)

        assert result["InstanceRefreshId"] == "refresh-abc-123"
        assert result["AutoScalingGroupName"] == "my-asg"
        mock_asg.start_instance_refresh.assert_called_once_with(
            AutoScalingGroupName="my-asg",
            Strategy="Rolling",
            Preferences={
                "MinHealthyPercentage": 90,
                "SkipMatching": False,
            },
        )

    @patch("src.asg_refresh.core.boto3.client")
    def test_start_refresh_with_instance_warmup(self, mock_client):
        mock_asg = MagicMock()
        mock_asg.start_instance_refresh.return_value = {
            "InstanceRefreshId": "refresh-def-456",
        }
        mock_client.return_value = mock_asg

        refresher = ASGRefresh(region="us-east-1")
        options = RefreshOptions(
            min_healthy_percentage=80,
            instance_warmup=300,
            skip_matching=True,
        )
        result = refresher.start_refresh("prod-asg", options)

        assert result["InstanceRefreshId"] == "refresh-def-456"
        assert result["AutoScalingGroupName"] == "prod-asg"
        mock_asg.start_instance_refresh.assert_called_once_with(
            AutoScalingGroupName="prod-asg",
            Strategy="Rolling",
            Preferences={
                "MinHealthyPercentage": 80,
                "SkipMatching": True,
                "InstanceWarmup": 300,
            },
        )

    @patch("src.asg_refresh.core.boto3.client")
    def test_describe_refresh_found(self, mock_client):
        mock_asg = MagicMock()
        mock_asg.describe_instance_refreshes.return_value = {
            "InstanceRefreshes": [
                {
                    "InstanceRefreshId": "refresh-abc-123",
                    "AutoScalingGroupName": "my-asg",
                    "Status": "InProgress",
                    "PercentageComplete": 50,
                }
            ]
        }
        mock_client.return_value = mock_asg

        refresher = ASGRefresh(region="us-east-1")
        result = refresher.describe_refresh("my-asg", "refresh-abc-123")

        assert result["Status"] == "InProgress"
        assert result["PercentageComplete"] == 50
        mock_asg.describe_instance_refreshes.assert_called_once_with(
            AutoScalingGroupName="my-asg",
            InstanceRefreshIds=["refresh-abc-123"],
        )

    @patch("src.asg_refresh.core.boto3.client")
    def test_describe_refresh_not_found(self, mock_client):
        mock_asg = MagicMock()
        mock_asg.describe_instance_refreshes.return_value = {"InstanceRefreshes": []}
        mock_client.return_value = mock_asg

        refresher = ASGRefresh(region="us-east-1")
        result = refresher.describe_refresh("my-asg", "nonexistent-id")

        assert result == {}


class TestWaitForRefresh:
    """Test cases for the wait_for_refresh method."""

    @patch("src.asg_refresh.core.time.sleep")
    @patch("src.asg_refresh.core.boto3.client")
    def test_immediate_success(self, mock_client, mock_sleep):
        mock_asg = MagicMock()
        mock_asg.describe_instance_refreshes.return_value = {
            "InstanceRefreshes": [
                {"InstanceRefreshId": "r-1", "Status": "Successful"}
            ]
        }
        mock_client.return_value = mock_asg

        refresher = ASGRefresh(region="us-east-1")
        result = refresher.wait_for_refresh("my-asg", "r-1")

        assert result["Status"] == "Successful"
        mock_sleep.assert_not_called()

    @patch("src.asg_refresh.core.time.sleep")
    @patch("src.asg_refresh.core.boto3.client")
    def test_poll_then_success(self, mock_client, mock_sleep):
        mock_asg = MagicMock()
        mock_asg.describe_instance_refreshes.side_effect = [
            {"InstanceRefreshes": [{"Status": "InProgress", "PercentageComplete": 50}]},
            {"InstanceRefreshes": [{"Status": "Successful", "PercentageComplete": 100}]},
        ]
        mock_client.return_value = mock_asg

        refresher = ASGRefresh(region="us-east-1")
        result = refresher.wait_for_refresh("my-asg", "r-1", interval=5, timeout=60)

        assert result["Status"] == "Successful"
        mock_sleep.assert_called_once_with(5)

    @patch("src.asg_refresh.core.time.sleep")
    @patch("src.asg_refresh.core.boto3.client")
    def test_poll_then_failure(self, mock_client, mock_sleep):
        mock_asg = MagicMock()
        mock_asg.describe_instance_refreshes.side_effect = [
            {"InstanceRefreshes": [{"Status": "InProgress"}]},
            {"InstanceRefreshes": [{"Status": "Failed"}]},
        ]
        mock_client.return_value = mock_asg

        refresher = ASGRefresh(region="us-east-1")
        result = refresher.wait_for_refresh("my-asg", "r-1", interval=5, timeout=60)

        assert result["Status"] == "Failed"

    @patch("src.asg_refresh.core.time.sleep")
    @patch("src.asg_refresh.core.boto3.client")
    def test_timeout(self, mock_client, mock_sleep):
        mock_asg = MagicMock()
        mock_asg.describe_instance_refreshes.return_value = {
            "InstanceRefreshes": [{"Status": "InProgress"}]
        }
        mock_client.return_value = mock_asg

        refresher = ASGRefresh(region="us-east-1")
        with pytest.raises(TimeoutError, match="Timed out after 10s"):
            refresher.wait_for_refresh("my-asg", "r-1", interval=5, timeout=10)

    @patch("src.asg_refresh.core.time.sleep")
    @patch("src.asg_refresh.core.boto3.client")
    def test_callback_invocation(self, mock_client, mock_sleep):
        mock_asg = MagicMock()
        mock_asg.describe_instance_refreshes.side_effect = [
            {"InstanceRefreshes": [{"Status": "InProgress"}]},
            {"InstanceRefreshes": [{"Status": "Successful"}]},
        ]
        mock_client.return_value = mock_asg

        callback = MagicMock()
        refresher = ASGRefresh(region="us-east-1")
        refresher.wait_for_refresh(
            "my-asg", "r-1", interval=5, timeout=60, status_callback=callback
        )

        assert callback.call_count == 2
        callback.assert_any_call({"Status": "InProgress"})
        callback.assert_any_call({"Status": "Successful"})

    @patch("src.asg_refresh.core.time.sleep")
    @patch("src.asg_refresh.core.boto3.client")
    def test_all_terminal_states(self, mock_client, mock_sleep):
        for state in [
            "Successful",
            "Failed",
            "Cancelled",
            "RollbackSuccessful",
            "RollbackFailed",
        ]:
            mock_asg = MagicMock()
            mock_asg.describe_instance_refreshes.return_value = {
                "InstanceRefreshes": [{"Status": state}]
            }
            mock_client.return_value = mock_asg

            refresher = ASGRefresh(region="us-east-1")
            result = refresher.wait_for_refresh("my-asg", "r-1")
            assert result["Status"] == state
            mock_sleep.assert_not_called()
