package main

import (
	"bytes"
	"context"
	"errors"
	"fmt"
	"os"
	"testing"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/autoscaling"
	"github.com/aws/aws-sdk-go-v2/service/autoscaling/types"
)

// mockASClient implements AutoScalingAPI for testing.
type mockASClient struct {
	startFn    func(ctx context.Context, params *autoscaling.StartInstanceRefreshInput, optFns ...func(*autoscaling.Options)) (*autoscaling.StartInstanceRefreshOutput, error)
	describeFn func(ctx context.Context, params *autoscaling.DescribeInstanceRefreshesInput, optFns ...func(*autoscaling.Options)) (*autoscaling.DescribeInstanceRefreshesOutput, error)
}

func (m *mockASClient) StartInstanceRefresh(ctx context.Context, params *autoscaling.StartInstanceRefreshInput, optFns ...func(*autoscaling.Options)) (*autoscaling.StartInstanceRefreshOutput, error) {
	return m.startFn(ctx, params, optFns...)
}

func (m *mockASClient) DescribeInstanceRefreshes(ctx context.Context, params *autoscaling.DescribeInstanceRefreshesInput, optFns ...func(*autoscaling.Options)) (*autoscaling.DescribeInstanceRefreshesOutput, error) {
	return m.describeFn(ctx, params, optFns...)
}

// newTestRefresher creates an ASGRefresher with a no-op sleep suitable for unit tests.
func newTestRefresher(client AutoScalingAPI) *ASGRefresher {
	r := NewASGRefresher(client)
	r.sleep = func(time.Duration) {}
	return r
}

// makeFactory returns a refresherFactory that injects the given mock client.
func makeFactory(client AutoScalingAPI) refresherFactory {
	return func(region string) (*ASGRefresher, error) {
		return newTestRefresher(client), nil
	}
}

// ── StartRefresh ─────────────────────────────────────────────────────────────

func TestStartRefresh_Success(t *testing.T) {
	mock := &mockASClient{
		startFn: func(_ context.Context, _ *autoscaling.StartInstanceRefreshInput, _ ...func(*autoscaling.Options)) (*autoscaling.StartInstanceRefreshOutput, error) {
			return &autoscaling.StartInstanceRefreshOutput{InstanceRefreshId: aws.String("id-123")}, nil
		},
	}
	result, err := newTestRefresher(mock).StartRefresh(context.Background(), "my-asg", RefreshOptions{MinHealthyPercentage: 90})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result.InstanceRefreshId != "id-123" {
		t.Errorf("expected id-123, got %s", result.InstanceRefreshId)
	}
	if result.AutoScalingGroupName != "my-asg" {
		t.Errorf("expected my-asg, got %s", result.AutoScalingGroupName)
	}
}

func TestStartRefresh_DefaultPreferences(t *testing.T) {
	var got *autoscaling.StartInstanceRefreshInput
	mock := &mockASClient{
		startFn: func(_ context.Context, params *autoscaling.StartInstanceRefreshInput, _ ...func(*autoscaling.Options)) (*autoscaling.StartInstanceRefreshOutput, error) {
			got = params
			return &autoscaling.StartInstanceRefreshOutput{InstanceRefreshId: aws.String("id")}, nil
		},
	}
	_, err := newTestRefresher(mock).StartRefresh(context.Background(), "asg", RefreshOptions{MinHealthyPercentage: 90, SkipMatching: true})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if *got.Preferences.MinHealthyPercentage != 90 {
		t.Errorf("expected 90, got %d", *got.Preferences.MinHealthyPercentage)
	}
	if !*got.Preferences.SkipMatching {
		t.Error("expected SkipMatching=true")
	}
	if got.Preferences.InstanceWarmup != nil {
		t.Errorf("expected nil InstanceWarmup, got %v", got.Preferences.InstanceWarmup)
	}
	if got.Preferences.MaxHealthyPercentage != nil {
		t.Errorf("expected nil MaxHealthyPercentage, got %v", got.Preferences.MaxHealthyPercentage)
	}
}

func TestStartRefresh_WithAllOptions(t *testing.T) {
	var got *autoscaling.StartInstanceRefreshInput
	mock := &mockASClient{
		startFn: func(_ context.Context, params *autoscaling.StartInstanceRefreshInput, _ ...func(*autoscaling.Options)) (*autoscaling.StartInstanceRefreshOutput, error) {
			got = params
			return &autoscaling.StartInstanceRefreshOutput{InstanceRefreshId: aws.String("id")}, nil
		},
	}
	warmup := int32(300)
	maxPct := int32(110)
	_, err := newTestRefresher(mock).StartRefresh(context.Background(), "asg", RefreshOptions{
		MinHealthyPercentage: 80,
		MaxHealthyPercentage: &maxPct,
		InstanceWarmup:       &warmup,
		SkipMatching:         true,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if *got.Preferences.MinHealthyPercentage != 80 {
		t.Errorf("expected 80, got %d", *got.Preferences.MinHealthyPercentage)
	}
	if got.Preferences.MaxHealthyPercentage == nil || *got.Preferences.MaxHealthyPercentage != 110 {
		t.Errorf("expected MaxHealthyPercentage=110, got %v", got.Preferences.MaxHealthyPercentage)
	}
	if got.Preferences.InstanceWarmup == nil || *got.Preferences.InstanceWarmup != 300 {
		t.Errorf("expected InstanceWarmup=300, got %v", got.Preferences.InstanceWarmup)
	}
	if !*got.Preferences.SkipMatching {
		t.Error("expected SkipMatching=true")
	}
}

func TestStartRefresh_WithMaxHealthyPercentage(t *testing.T) {
	var got *autoscaling.StartInstanceRefreshInput
	mock := &mockASClient{
		startFn: func(_ context.Context, params *autoscaling.StartInstanceRefreshInput, _ ...func(*autoscaling.Options)) (*autoscaling.StartInstanceRefreshOutput, error) {
			got = params
			return &autoscaling.StartInstanceRefreshOutput{InstanceRefreshId: aws.String("id")}, nil
		},
	}
	maxPct := int32(200)
	_, err := newTestRefresher(mock).StartRefresh(context.Background(), "asg", RefreshOptions{
		MinHealthyPercentage: 90,
		MaxHealthyPercentage: &maxPct,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got.Preferences.MaxHealthyPercentage == nil || *got.Preferences.MaxHealthyPercentage != 200 {
		t.Errorf("expected MaxHealthyPercentage=200, got %v", got.Preferences.MaxHealthyPercentage)
	}
}

func TestStartRefresh_Error(t *testing.T) {
	mock := &mockASClient{
		startFn: func(_ context.Context, _ *autoscaling.StartInstanceRefreshInput, _ ...func(*autoscaling.Options)) (*autoscaling.StartInstanceRefreshOutput, error) {
			return nil, fmt.Errorf("AWS error")
		},
	}
	_, err := newTestRefresher(mock).StartRefresh(context.Background(), "asg", RefreshOptions{})
	if err == nil {
		t.Fatal("expected error, got nil")
	}
}

// ── DescribeRefresh ───────────────────────────────────────────────────────────

func TestDescribeRefresh_Found(t *testing.T) {
	mock := &mockASClient{
		describeFn: func(_ context.Context, _ *autoscaling.DescribeInstanceRefreshesInput, _ ...func(*autoscaling.Options)) (*autoscaling.DescribeInstanceRefreshesOutput, error) {
			return &autoscaling.DescribeInstanceRefreshesOutput{
				InstanceRefreshes: []types.InstanceRefresh{
					{InstanceRefreshId: aws.String("id-123"), Status: types.InstanceRefreshStatusSuccessful},
				},
			}, nil
		},
	}
	result, err := newTestRefresher(mock).DescribeRefresh(context.Background(), "asg", "id-123")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result == nil {
		t.Fatal("expected non-nil result")
	}
	if aws.ToString(result.InstanceRefreshId) != "id-123" {
		t.Errorf("expected id-123, got %s", aws.ToString(result.InstanceRefreshId))
	}
}

func TestDescribeRefresh_NotFound(t *testing.T) {
	mock := &mockASClient{
		describeFn: func(_ context.Context, _ *autoscaling.DescribeInstanceRefreshesInput, _ ...func(*autoscaling.Options)) (*autoscaling.DescribeInstanceRefreshesOutput, error) {
			return &autoscaling.DescribeInstanceRefreshesOutput{}, nil
		},
	}
	result, err := newTestRefresher(mock).DescribeRefresh(context.Background(), "asg", "id-123")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result != nil {
		t.Errorf("expected nil result, got %v", result)
	}
}

func TestDescribeRefresh_Error(t *testing.T) {
	mock := &mockASClient{
		describeFn: func(_ context.Context, _ *autoscaling.DescribeInstanceRefreshesInput, _ ...func(*autoscaling.Options)) (*autoscaling.DescribeInstanceRefreshesOutput, error) {
			return nil, fmt.Errorf("AWS error")
		},
	}
	_, err := newTestRefresher(mock).DescribeRefresh(context.Background(), "asg", "id-123")
	if err == nil {
		t.Fatal("expected error, got nil")
	}
}

// ── WaitForRefresh ────────────────────────────────────────────────────────────

func TestWaitForRefresh_ImmediateSuccess(t *testing.T) {
	mock := &mockASClient{
		describeFn: func(_ context.Context, _ *autoscaling.DescribeInstanceRefreshesInput, _ ...func(*autoscaling.Options)) (*autoscaling.DescribeInstanceRefreshesOutput, error) {
			return &autoscaling.DescribeInstanceRefreshesOutput{
				InstanceRefreshes: []types.InstanceRefresh{
					{Status: types.InstanceRefreshStatusSuccessful, PercentageComplete: aws.Int32(100)},
				},
			}, nil
		},
	}
	result, err := newTestRefresher(mock).WaitForRefresh(context.Background(), "asg", "id", time.Second, time.Minute, nil)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result.Status != types.InstanceRefreshStatusSuccessful {
		t.Errorf("expected Successful, got %s", result.Status)
	}
}

func TestWaitForRefresh_PollsThenSucceeds(t *testing.T) {
	callCount := 0
	mock := &mockASClient{
		describeFn: func(_ context.Context, _ *autoscaling.DescribeInstanceRefreshesInput, _ ...func(*autoscaling.Options)) (*autoscaling.DescribeInstanceRefreshesOutput, error) {
			callCount++
			status := types.InstanceRefreshStatusInProgress
			if callCount >= 3 {
				status = types.InstanceRefreshStatusSuccessful
			}
			return &autoscaling.DescribeInstanceRefreshesOutput{
				InstanceRefreshes: []types.InstanceRefresh{{Status: status}},
			}, nil
		},
	}
	var callbackCount int
	result, err := newTestRefresher(mock).WaitForRefresh(context.Background(), "asg", "id", time.Millisecond, time.Minute, func(*types.InstanceRefresh) {
		callbackCount++
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result.Status != types.InstanceRefreshStatusSuccessful {
		t.Errorf("expected Successful, got %s", result.Status)
	}
	if callCount < 3 {
		t.Errorf("expected at least 3 describe calls, got %d", callCount)
	}
	if callbackCount < 3 {
		t.Errorf("expected at least 3 callback invocations, got %d", callbackCount)
	}
}

func TestWaitForRefresh_TerminalFailed(t *testing.T) {
	mock := &mockASClient{
		describeFn: func(_ context.Context, _ *autoscaling.DescribeInstanceRefreshesInput, _ ...func(*autoscaling.Options)) (*autoscaling.DescribeInstanceRefreshesOutput, error) {
			return &autoscaling.DescribeInstanceRefreshesOutput{
				InstanceRefreshes: []types.InstanceRefresh{{Status: types.InstanceRefreshStatusFailed}},
			}, nil
		},
	}
	result, err := newTestRefresher(mock).WaitForRefresh(context.Background(), "asg", "id", time.Millisecond, time.Minute, nil)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result.Status != types.InstanceRefreshStatusFailed {
		t.Errorf("expected Failed, got %s", result.Status)
	}
}

func TestWaitForRefresh_Timeout(t *testing.T) {
	mock := &mockASClient{
		describeFn: func(_ context.Context, _ *autoscaling.DescribeInstanceRefreshesInput, _ ...func(*autoscaling.Options)) (*autoscaling.DescribeInstanceRefreshesOutput, error) {
			return &autoscaling.DescribeInstanceRefreshesOutput{
				InstanceRefreshes: []types.InstanceRefresh{{Status: types.InstanceRefreshStatusInProgress}},
			}, nil
		},
	}
	// timeout=0 ensures the deadline is exceeded immediately after the first poll
	_, err := newTestRefresher(mock).WaitForRefresh(context.Background(), "asg", "id", time.Millisecond, 0, nil)
	if err == nil {
		t.Fatal("expected timeout error, got nil")
	}
}

func TestWaitForRefresh_DescribeError(t *testing.T) {
	mock := &mockASClient{
		describeFn: func(_ context.Context, _ *autoscaling.DescribeInstanceRefreshesInput, _ ...func(*autoscaling.Options)) (*autoscaling.DescribeInstanceRefreshesOutput, error) {
			return nil, fmt.Errorf("AWS error")
		},
	}
	_, err := newTestRefresher(mock).WaitForRefresh(context.Background(), "asg", "id", time.Millisecond, time.Minute, nil)
	if err == nil {
		t.Fatal("expected error, got nil")
	}
}

// ── start subcommand ──────────────────────────────────────────────────────────

func TestStartCommand_Success(t *testing.T) {
	mock := &mockASClient{
		startFn: func(_ context.Context, _ *autoscaling.StartInstanceRefreshInput, _ ...func(*autoscaling.Options)) (*autoscaling.StartInstanceRefreshOutput, error) {
			return &autoscaling.StartInstanceRefreshOutput{InstanceRefreshId: aws.String("id-456")}, nil
		},
	}
	var out bytes.Buffer
	root := newRootCmd(makeFactory(mock))
	root.SetOut(&out)
	root.SetArgs([]string{"start", "my-asg"})
	if err := root.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !bytes.Contains(out.Bytes(), []byte("id-456")) {
		t.Errorf("expected id-456 in output, got: %s", out.String())
	}
}

func TestStartCommand_DefaultSkipMatching(t *testing.T) {
	var got *autoscaling.StartInstanceRefreshInput
	mock := &mockASClient{
		startFn: func(_ context.Context, params *autoscaling.StartInstanceRefreshInput, _ ...func(*autoscaling.Options)) (*autoscaling.StartInstanceRefreshOutput, error) {
			got = params
			return &autoscaling.StartInstanceRefreshOutput{InstanceRefreshId: aws.String("id")}, nil
		},
	}
	root := newRootCmd(makeFactory(mock))
	root.SetArgs([]string{"start", "my-asg"})
	if err := root.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !*got.Preferences.SkipMatching {
		t.Error("expected SkipMatching=true by default")
	}
}

func TestStartCommand_WithOptions(t *testing.T) {
	var got *autoscaling.StartInstanceRefreshInput
	mock := &mockASClient{
		startFn: func(_ context.Context, params *autoscaling.StartInstanceRefreshInput, _ ...func(*autoscaling.Options)) (*autoscaling.StartInstanceRefreshOutput, error) {
			got = params
			return &autoscaling.StartInstanceRefreshOutput{InstanceRefreshId: aws.String("id")}, nil
		},
	}
	root := newRootCmd(makeFactory(mock))
	root.SetArgs([]string{"start", "my-asg", "--min-healthy-percentage", "80", "--instance-warmup", "300", "--skip-matching=false"})
	if err := root.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if *got.Preferences.MinHealthyPercentage != 80 {
		t.Errorf("expected 80, got %d", *got.Preferences.MinHealthyPercentage)
	}
	if got.Preferences.InstanceWarmup == nil || *got.Preferences.InstanceWarmup != 300 {
		t.Errorf("expected InstanceWarmup=300, got %v", got.Preferences.InstanceWarmup)
	}
	if *got.Preferences.SkipMatching {
		t.Error("expected SkipMatching=false when explicitly set")
	}
}

func TestStartCommand_MaxHealthyPercentage(t *testing.T) {
	var got *autoscaling.StartInstanceRefreshInput
	mock := &mockASClient{
		startFn: func(_ context.Context, params *autoscaling.StartInstanceRefreshInput, _ ...func(*autoscaling.Options)) (*autoscaling.StartInstanceRefreshOutput, error) {
			got = params
			return &autoscaling.StartInstanceRefreshOutput{InstanceRefreshId: aws.String("id")}, nil
		},
	}
	root := newRootCmd(makeFactory(mock))
	root.SetArgs([]string{"start", "my-asg", "--max-healthy-percentage", "110"})
	if err := root.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got.Preferences.MaxHealthyPercentage == nil || *got.Preferences.MaxHealthyPercentage != 110 {
		t.Errorf("expected MaxHealthyPercentage=110, got %v", got.Preferences.MaxHealthyPercentage)
	}
}

func TestStartCommand_MaxHealthyPercentageNotSetByDefault(t *testing.T) {
	var got *autoscaling.StartInstanceRefreshInput
	mock := &mockASClient{
		startFn: func(_ context.Context, params *autoscaling.StartInstanceRefreshInput, _ ...func(*autoscaling.Options)) (*autoscaling.StartInstanceRefreshOutput, error) {
			got = params
			return &autoscaling.StartInstanceRefreshOutput{InstanceRefreshId: aws.String("id")}, nil
		},
	}
	root := newRootCmd(makeFactory(mock))
	root.SetArgs([]string{"start", "my-asg"})
	if err := root.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got.Preferences.MaxHealthyPercentage != nil {
		t.Errorf("expected nil MaxHealthyPercentage by default, got %v", got.Preferences.MaxHealthyPercentage)
	}
}

func TestStartCommand_ASGNameFromEnv(t *testing.T) {
	t.Setenv("ASG_NAME", "env-asg")
	mock := &mockASClient{
		startFn: func(_ context.Context, params *autoscaling.StartInstanceRefreshInput, _ ...func(*autoscaling.Options)) (*autoscaling.StartInstanceRefreshOutput, error) {
			if aws.ToString(params.AutoScalingGroupName) != "env-asg" {
				return nil, fmt.Errorf("expected env-asg, got %s", aws.ToString(params.AutoScalingGroupName))
			}
			return &autoscaling.StartInstanceRefreshOutput{InstanceRefreshId: aws.String("id")}, nil
		},
	}
	root := newRootCmd(makeFactory(mock))
	root.SetArgs([]string{"start"})
	if err := root.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestStartCommand_MissingASGName(t *testing.T) {
	root := newRootCmd(makeFactory(&mockASClient{}))
	root.SetArgs([]string{"start"})
	if err := root.Execute(); err == nil {
		t.Fatal("expected error for missing ASG_NAME")
	}
}

func TestStartCommand_AWSError(t *testing.T) {
	mock := &mockASClient{
		startFn: func(_ context.Context, _ *autoscaling.StartInstanceRefreshInput, _ ...func(*autoscaling.Options)) (*autoscaling.StartInstanceRefreshOutput, error) {
			return nil, fmt.Errorf("access denied")
		},
	}
	root := newRootCmd(makeFactory(mock))
	root.SetArgs([]string{"start", "my-asg"})
	if err := root.Execute(); err == nil {
		t.Fatal("expected error from AWS")
	}
}

// ── check subcommand ──────────────────────────────────────────────────────────

func TestCheckCommand_Success(t *testing.T) {
	mock := &mockASClient{
		describeFn: func(_ context.Context, _ *autoscaling.DescribeInstanceRefreshesInput, _ ...func(*autoscaling.Options)) (*autoscaling.DescribeInstanceRefreshesOutput, error) {
			return &autoscaling.DescribeInstanceRefreshesOutput{
				InstanceRefreshes: []types.InstanceRefresh{
					{Status: types.InstanceRefreshStatusSuccessful, PercentageComplete: aws.Int32(100)},
				},
			}, nil
		},
	}
	var out bytes.Buffer
	root := newRootCmd(makeFactory(mock))
	root.SetOut(&out)
	root.SetArgs([]string{"check", "my-asg", "id-123"})
	if err := root.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !bytes.Contains(out.Bytes(), []byte("Successful")) {
		t.Errorf("expected Successful in output, got: %s", out.String())
	}
}

func TestCheckCommand_NonSuccessful(t *testing.T) {
	mock := &mockASClient{
		describeFn: func(_ context.Context, _ *autoscaling.DescribeInstanceRefreshesInput, _ ...func(*autoscaling.Options)) (*autoscaling.DescribeInstanceRefreshesOutput, error) {
			return &autoscaling.DescribeInstanceRefreshesOutput{
				InstanceRefreshes: []types.InstanceRefresh{{Status: types.InstanceRefreshStatusFailed}},
			}, nil
		},
	}
	root := newRootCmd(makeFactory(mock))
	root.SetArgs([]string{"check", "my-asg", "id-123"})
	err := root.Execute()
	if !errors.Is(err, errNonSuccessful) {
		t.Errorf("expected errNonSuccessful, got %v", err)
	}
}

func TestCheckCommand_FromEnv(t *testing.T) {
	t.Setenv("ASG_NAME", "env-asg")
	t.Setenv("INSTANCE_REFRESH_ID", "env-id")
	mock := &mockASClient{
		describeFn: func(_ context.Context, params *autoscaling.DescribeInstanceRefreshesInput, _ ...func(*autoscaling.Options)) (*autoscaling.DescribeInstanceRefreshesOutput, error) {
			if aws.ToString(params.AutoScalingGroupName) != "env-asg" {
				return nil, fmt.Errorf("expected env-asg, got %s", aws.ToString(params.AutoScalingGroupName))
			}
			return &autoscaling.DescribeInstanceRefreshesOutput{
				InstanceRefreshes: []types.InstanceRefresh{{Status: types.InstanceRefreshStatusSuccessful}},
			}, nil
		},
	}
	root := newRootCmd(makeFactory(mock))
	root.SetArgs([]string{"check"})
	if err := root.Execute(); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
}

func TestCheckCommand_MissingASGName(t *testing.T) {
	root := newRootCmd(makeFactory(&mockASClient{}))
	root.SetArgs([]string{"check"})
	if err := root.Execute(); err == nil {
		t.Fatal("expected error for missing ASG_NAME")
	}
}

func TestCheckCommand_MissingRefreshID(t *testing.T) {
	root := newRootCmd(makeFactory(&mockASClient{}))
	root.SetArgs([]string{"check", "my-asg"})
	if err := root.Execute(); err == nil {
		t.Fatal("expected error for missing REFRESH_ID")
	}
}

func TestCheckCommand_Timeout(t *testing.T) {
	mock := &mockASClient{
		describeFn: func(_ context.Context, _ *autoscaling.DescribeInstanceRefreshesInput, _ ...func(*autoscaling.Options)) (*autoscaling.DescribeInstanceRefreshesOutput, error) {
			return &autoscaling.DescribeInstanceRefreshesOutput{
				InstanceRefreshes: []types.InstanceRefresh{{Status: types.InstanceRefreshStatusInProgress}},
			}, nil
		},
	}
	root := newRootCmd(makeFactory(mock))
	root.SetArgs([]string{"check", "my-asg", "id-123", "--timeout", "0"})
	if err := root.Execute(); err == nil {
		t.Fatal("expected timeout error")
	}
}

// ── helper functions ──────────────────────────────────────────────────────────

func TestArgOrEnv_FromArg(t *testing.T) {
	if got := argOrEnv([]string{"from-arg"}, 0, "UNUSED_ENV"); got != "from-arg" {
		t.Errorf("expected from-arg, got %s", got)
	}
}

func TestArgOrEnv_FromEnv(t *testing.T) {
	t.Setenv("TEST_ENV_KEY", "from-env")
	if got := argOrEnv([]string{}, 0, "TEST_ENV_KEY"); got != "from-env" {
		t.Errorf("expected from-env, got %s", got)
	}
}

func TestEnvIntOrDefault_Set(t *testing.T) {
	t.Setenv("TEST_INT_KEY", "42")
	if v := envIntOrDefault("TEST_INT_KEY", 0); v != 42 {
		t.Errorf("expected 42, got %d", v)
	}
}

func TestEnvIntOrDefault_Default(t *testing.T) {
	os.Unsetenv("TEST_INT_KEY")
	if v := envIntOrDefault("TEST_INT_KEY", 99); v != 99 {
		t.Errorf("expected 99, got %d", v)
	}
}

func TestEnvIntOrDefault_Invalid(t *testing.T) {
	t.Setenv("TEST_INT_KEY", "not-a-number")
	if v := envIntOrDefault("TEST_INT_KEY", 5); v != 5 {
		t.Errorf("expected 5 (default), got %d", v)
	}
}
