"""
Tests for the ASG refresh core module.
"""

from unittest.mock import MagicMock, patch
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
