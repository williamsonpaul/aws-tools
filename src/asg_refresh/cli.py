"""
Command line interface for AWS ASG instance refresh.
"""

import sys

import click
import json
from .core import ASGRefresh, RefreshOptions


@click.group()
def main():
    """AWS Auto Scaling Group instance refresh tool."""
    pass


@main.command()
@click.argument("asg_name", envvar="ASG_NAME")
@click.option(
    "--min-healthy-percentage",
    type=int,
    default=90,
    show_default=True,
    envvar="MIN_HEALTHY_PERCENTAGE",
    help="Minimum percentage of healthy instances during refresh",
)
@click.option(
    "--instance-warmup",
    type=int,
    default=None,
    envvar="INSTANCE_WARMUP",
    help="Time in seconds until a new instance is considered warm",
)
@click.option(
    "--skip-matching",
    is_flag=True,
    default=False,
    envvar="SKIP_MATCHING",
    help="Skip instances already using the latest launch template",
)
@click.option(
    "--region",
    default=None,
    envvar="AWS_DEFAULT_REGION",
    help="AWS region (defaults to environment/instance profile)",
)
def start(asg_name, min_healthy_percentage, instance_warmup, skip_matching, region):
    """Start an instance refresh on an Auto Scaling Group.

    ASG_NAME: The name of the Auto Scaling Group to refresh

    Examples:

        asg-refresh start my-asg

        asg-refresh start my-asg --min-healthy-percentage 80

        asg-refresh start my-asg --instance-warmup 300 --skip-matching
    """
    refresher = ASGRefresh(region=region)
    options = RefreshOptions(
        min_healthy_percentage=min_healthy_percentage,
        instance_warmup=instance_warmup,
        skip_matching=skip_matching,
    )
    result = refresher.start_refresh(asg_name, options)
    click.echo(json.dumps(result, indent=2))


@main.command()
@click.argument("asg_name", envvar="ASG_NAME")
@click.argument("refresh_id", envvar="INSTANCE_REFRESH_ID")
@click.option(
    "--region",
    default=None,
    envvar="AWS_DEFAULT_REGION",
    help="AWS region (defaults to environment/instance profile)",
)
@click.option(
    "--interval",
    type=int,
    default=30,
    show_default=True,
    envvar="CHECK_INTERVAL",
    help="Polling interval in seconds",
)
@click.option(
    "--timeout",
    type=int,
    default=3600,
    show_default=True,
    envvar="CHECK_TIMEOUT",
    help="Maximum wait time in seconds",
)
def check(asg_name, refresh_id, region, interval, timeout):
    """Wait for an instance refresh to complete.

    ASG_NAME: The name of the Auto Scaling Group

    REFRESH_ID: The instance refresh ID to monitor

    Examples:

        asg-refresh check my-asg abc-123

        asg-refresh check my-asg abc-123 --interval 10 --timeout 600
    """

    def _status_callback(refresh_dict):
        status = refresh_dict.get("Status", "Unknown")
        pct = refresh_dict.get("PercentageComplete", 0)
        click.echo(f"Status: {status} ({pct}% complete)", err=True)

    refresher = ASGRefresh(region=region)
    try:
        result = refresher.wait_for_refresh(
            asg_name,
            refresh_id,
            interval=interval,
            timeout=timeout,
            status_callback=_status_callback,
        )
    except TimeoutError as e:
        click.echo(str(e), err=True)
        sys.exit(1)

    click.echo(json.dumps(result, indent=2, default=str))
    if result.get("Status") != "Successful":
        sys.exit(1)


if __name__ == "__main__":
    main()
