package main

import (
	"context"
	"fmt"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/autoscaling"
	"github.com/aws/aws-sdk-go-v2/service/autoscaling/types"
)

// AutoScalingAPI is the subset of the AWS autoscaling client used by this tool.
type AutoScalingAPI interface {
	StartInstanceRefresh(ctx context.Context, params *autoscaling.StartInstanceRefreshInput, optFns ...func(*autoscaling.Options)) (*autoscaling.StartInstanceRefreshOutput, error)
	DescribeInstanceRefreshes(ctx context.Context, params *autoscaling.DescribeInstanceRefreshesInput, optFns ...func(*autoscaling.Options)) (*autoscaling.DescribeInstanceRefreshesOutput, error)
}

// RefreshOptions configures an instance refresh.
type RefreshOptions struct {
	MinHealthyPercentage int
	MaxHealthyPercentage *int32 // nil = use AWS default (100); >100 enables launch-before-termination
	InstanceWarmup       *int32
	SkipMatching         bool
}

// StartResult is the JSON output of the start subcommand.
type StartResult struct {
	InstanceRefreshId    string `json:"InstanceRefreshId"`
	AutoScalingGroupName string `json:"AutoScalingGroupName"`
}

// terminalStates are refresh statuses that will not progress further.
var terminalStates = map[string]bool{
	"Successful":        true,
	"Failed":            true,
	"Cancelled":         true,
	"RollbackSuccessful": true,
	"RollbackFailed":    true,
}

// ASGRefresher initiates and monitors AWS Auto Scaling Group instance refreshes.
type ASGRefresher struct {
	client AutoScalingAPI
	sleep  func(time.Duration)
}

// NewASGRefresher creates an ASGRefresher backed by the given AWS client.
func NewASGRefresher(client AutoScalingAPI) *ASGRefresher {
	return &ASGRefresher{client: client, sleep: time.Sleep}
}

// StartRefresh initiates a rolling instance refresh on the named ASG.
func (r *ASGRefresher) StartRefresh(ctx context.Context, asgName string, opts RefreshOptions) (*StartResult, error) {
	prefs := &types.RefreshPreferences{
		MinHealthyPercentage: aws.Int32(int32(opts.MinHealthyPercentage)),
		SkipMatching:         aws.Bool(opts.SkipMatching),
	}
	if opts.InstanceWarmup != nil {
		prefs.InstanceWarmup = opts.InstanceWarmup
	}
	if opts.MaxHealthyPercentage != nil {
		prefs.MaxHealthyPercentage = opts.MaxHealthyPercentage
	}

	out, err := r.client.StartInstanceRefresh(ctx, &autoscaling.StartInstanceRefreshInput{
		AutoScalingGroupName: aws.String(asgName),
		Strategy:             types.RefreshStrategyRolling,
		Preferences:          prefs,
	})
	if err != nil {
		return nil, fmt.Errorf("start instance refresh: %w", err)
	}

	return &StartResult{
		InstanceRefreshId:    aws.ToString(out.InstanceRefreshId),
		AutoScalingGroupName: asgName,
	}, nil
}

// DescribeRefresh returns the current status of an instance refresh, or nil if not found.
func (r *ASGRefresher) DescribeRefresh(ctx context.Context, asgName, refreshID string) (*types.InstanceRefresh, error) {
	out, err := r.client.DescribeInstanceRefreshes(ctx, &autoscaling.DescribeInstanceRefreshesInput{
		AutoScalingGroupName: aws.String(asgName),
		InstanceRefreshIds:   []string{refreshID},
	})
	if err != nil {
		return nil, fmt.Errorf("describe instance refresh: %w", err)
	}
	if len(out.InstanceRefreshes) == 0 {
		return nil, nil
	}
	return &out.InstanceRefreshes[0], nil
}

// WaitForRefresh polls DescribeRefresh until a terminal state or the timeout elapses.
// statusCallback, if non-nil, is called after each poll.
func (r *ASGRefresher) WaitForRefresh(
	ctx context.Context,
	asgName, refreshID string,
	interval, timeout time.Duration,
	statusCallback func(*types.InstanceRefresh),
) (*types.InstanceRefresh, error) {
	start := time.Now()
	for {
		result, err := r.DescribeRefresh(ctx, asgName, refreshID)
		if err != nil {
			return nil, err
		}
		if result != nil {
			if statusCallback != nil {
				statusCallback(result)
			}
			if terminalStates[string(result.Status)] {
				return result, nil
			}
		}
		if time.Since(start) >= timeout {
			return nil, fmt.Errorf("timed out after %.0fs waiting for refresh %s", timeout.Seconds(), refreshID)
		}
		r.sleep(interval)
	}
}
