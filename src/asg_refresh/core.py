"""
Core functionality for AWS ASG instance refresh.
"""

import boto3
from dataclasses import dataclass
from typing import Optional


@dataclass
class RefreshOptions:
    """Configuration options for ASG instance refresh."""

    min_healthy_percentage: int = 90
    instance_warmup: Optional[int] = None
    skip_matching: bool = False


class ASGRefresh:
    """Initiates and describes AWS Auto Scaling Group instance refreshes."""

    def __init__(self, region: Optional[str] = None):
        self.client = boto3.client("autoscaling", region_name=region)

    def start_refresh(self, asg_name: str, options: RefreshOptions) -> dict:
        """Start an instance refresh on the specified ASG."""
        preferences = {
            "MinHealthyPercentage": options.min_healthy_percentage,
            "SkipMatching": options.skip_matching,
        }
        if options.instance_warmup is not None:
            preferences["InstanceWarmup"] = options.instance_warmup

        response = self.client.start_instance_refresh(
            AutoScalingGroupName=asg_name,
            Strategy="Rolling",
            Preferences=preferences,
        )
        return {
            "InstanceRefreshId": response["InstanceRefreshId"],
            "AutoScalingGroupName": asg_name,
        }

    def describe_refresh(self, asg_name: str, refresh_id: str) -> dict:
        """Describe the status of an instance refresh."""
        response = self.client.describe_instance_refreshes(
            AutoScalingGroupName=asg_name,
            InstanceRefreshIds=[refresh_id],
        )
        if response["InstanceRefreshes"]:
            return response["InstanceRefreshes"][0]
        return {}
