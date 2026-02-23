"""
Command line interface for AWS ASG instance refresh.
"""

import click
import json
from .core import ASGRefresh, RefreshOptions


@click.command()
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
def main(asg_name, min_healthy_percentage, instance_warmup, skip_matching, region):
    """Initiate an AWS Auto Scaling Group instance refresh.

    ASG_NAME: The name of the Auto Scaling Group to refresh

    Examples:

        asg-refresh my-asg

        asg-refresh my-asg --min-healthy-percentage 80

        asg-refresh my-asg --instance-warmup 300 --skip-matching
    """
    refresher = ASGRefresh(region=region)
    options = RefreshOptions(
        min_healthy_percentage=min_healthy_percentage,
        instance_warmup=instance_warmup,
        skip_matching=skip_matching,
    )
    result = refresher.start_refresh(asg_name, options)
    click.echo(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
