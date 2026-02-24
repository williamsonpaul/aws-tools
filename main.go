package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"strconv"
	"time"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/autoscaling"
	"github.com/aws/aws-sdk-go-v2/service/autoscaling/types"
	"github.com/spf13/cobra"
)

// errNonSuccessful is returned by the check command when a refresh ends in a non-Successful state.
var errNonSuccessful = errors.New("instance refresh did not complete successfully")

func main() {
	root := newRootCmd(nil)
	root.SilenceErrors = true
	root.SilenceUsage = true
	if err := root.Execute(); err != nil {
		if !errors.Is(err, errNonSuccessful) {
			fmt.Fprintln(os.Stderr, err)
		}
		os.Exit(1)
	}
}

// refresherFactory creates an ASGRefresher for the given region.
type refresherFactory func(region string) (*ASGRefresher, error)

// defaultFactory creates an ASGRefresher using the default AWS credential chain.
func defaultFactory(region string) (*ASGRefresher, error) {
	opts := []func(*config.LoadOptions) error{}
	if region != "" {
		opts = append(opts, config.WithRegion(region))
	}
	cfg, err := config.LoadDefaultConfig(context.Background(), opts...)
	if err != nil {
		return nil, fmt.Errorf("load AWS config: %w", err)
	}
	return NewASGRefresher(autoscaling.NewFromConfig(cfg)), nil
}

// newRootCmd builds the root cobra command. factory is used to create the refresher;
// if nil, defaultFactory is used.
func newRootCmd(factory refresherFactory) *cobra.Command {
	if factory == nil {
		factory = defaultFactory
	}
	root := &cobra.Command{
		Use:           "aws-asg",
		Short:         "AWS Auto Scaling Group instance refresh tool",
		SilenceErrors: true,
		SilenceUsage:  true,
	}
	root.AddCommand(newStartCmd(factory))
	root.AddCommand(newCheckCmd(factory))
	return root
}

func newStartCmd(factory refresherFactory) *cobra.Command {
	var (
		minHealthyPct  int
		instanceWarmup int
		skipMatching   bool
		region         string
	)

	cmd := &cobra.Command{
		Use:   "start ASG_NAME",
		Short: "Start an instance refresh on an Auto Scaling Group",
		Long: `Start an instance refresh on an Auto Scaling Group.

ASG_NAME can also be set via the ASG_NAME environment variable.

Examples:
  asg-refresh start my-asg
  asg-refresh start my-asg --min-healthy-percentage 80
  asg-refresh start my-asg --instance-warmup 300 --skip-matching`,
		Args: cobra.RangeArgs(0, 1),
		RunE: func(cmd *cobra.Command, args []string) error {
			asgName := argOrEnv(args, 0, "ASG_NAME")
			if asgName == "" {
				return fmt.Errorf("ASG_NAME argument or environment variable required")
			}

			r, err := factory(region)
			if err != nil {
				return err
			}

			opts := RefreshOptions{
				MinHealthyPercentage: minHealthyPct,
				SkipMatching:         skipMatching,
			}
			if cmd.Flags().Changed("instance-warmup") {
				w := int32(instanceWarmup)
				opts.InstanceWarmup = &w
			}

			result, err := r.StartRefresh(cmd.Context(), asgName, opts)
			if err != nil {
				return err
			}
			return writeJSON(cmd.OutOrStdout(), result)
		},
	}

	cmd.Flags().IntVar(&minHealthyPct, "min-healthy-percentage", envIntOrDefault("MIN_HEALTHY_PERCENTAGE", 90), "Minimum percentage of healthy instances during refresh")
	cmd.Flags().IntVar(&instanceWarmup, "instance-warmup", 0, "Time in seconds until a new instance is considered warm")
	cmd.Flags().BoolVar(&skipMatching, "skip-matching", false, "Skip instances already using the latest launch template")
	cmd.Flags().StringVar(&region, "region", "", "AWS region (defaults to environment/instance profile)")

	return cmd
}

func newCheckCmd(factory refresherFactory) *cobra.Command {
	var (
		region   string
		interval int
		timeout  int
	)

	cmd := &cobra.Command{
		Use:   "check ASG_NAME REFRESH_ID",
		Short: "Wait for an instance refresh to complete",
		Long: `Wait for an instance refresh to complete.

ASG_NAME and REFRESH_ID can also be set via ASG_NAME and INSTANCE_REFRESH_ID
environment variables. Exits 1 if the refresh does not end in a Successful state.

Examples:
  asg-refresh check my-asg abc-123
  asg-refresh check my-asg abc-123 --interval 10 --timeout 600`,
		Args: cobra.RangeArgs(0, 2),
		RunE: func(cmd *cobra.Command, args []string) error {
			asgName := argOrEnv(args, 0, "ASG_NAME")
			refreshID := argOrEnv(args, 1, "INSTANCE_REFRESH_ID")
			if asgName == "" {
				return fmt.Errorf("ASG_NAME argument or environment variable required")
			}
			if refreshID == "" {
				return fmt.Errorf("REFRESH_ID argument or INSTANCE_REFRESH_ID environment variable required")
			}

			r, err := factory(region)
			if err != nil {
				return err
			}

			statusCallback := func(refresh *types.InstanceRefresh) {
				pct := int32(0)
				if refresh.PercentageComplete != nil {
					pct = *refresh.PercentageComplete
				}
				fmt.Fprintf(cmd.ErrOrStderr(), "Status: %s (%d%% complete)\n", refresh.Status, pct)
			}

			result, err := r.WaitForRefresh(
				cmd.Context(),
				asgName,
				refreshID,
				time.Duration(interval)*time.Second,
				time.Duration(timeout)*time.Second,
				statusCallback,
			)
			if err != nil {
				return err
			}

			if err := writeJSON(cmd.OutOrStdout(), result); err != nil {
				return err
			}
			if string(result.Status) != "Successful" {
				return errNonSuccessful
			}
			return nil
		},
	}

	cmd.Flags().StringVar(&region, "region", "", "AWS region (defaults to environment/instance profile)")
	cmd.Flags().IntVar(&interval, "interval", envIntOrDefault("CHECK_INTERVAL", 30), "Polling interval in seconds")
	cmd.Flags().IntVar(&timeout, "timeout", envIntOrDefault("CHECK_TIMEOUT", 3600), "Maximum wait time in seconds")

	return cmd
}

// argOrEnv returns args[i] if available, otherwise the named environment variable.
func argOrEnv(args []string, i int, envKey string) string {
	if i < len(args) {
		return args[i]
	}
	return os.Getenv(envKey)
}

// envIntOrDefault returns the integer value of an env var, or def if unset or invalid.
func envIntOrDefault(key string, def int) int {
	if v := os.Getenv(key); v != "" {
		if n, err := strconv.Atoi(v); err == nil {
			return n
		}
	}
	return def
}

// writeJSON encodes v as indented JSON to w.
func writeJSON(w io.Writer, v any) error {
	enc := json.NewEncoder(w)
	enc.SetIndent("", "  ")
	return enc.Encode(v)
}

// Ensure the autoscaling client satisfies AutoScalingAPI at compile time.
var _ AutoScalingAPI = (*autoscaling.Client)(nil)
