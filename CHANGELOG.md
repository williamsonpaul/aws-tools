## [2.0.0](https://github.com/williamsonpaul/aws-tools/compare/v1.0.1...v2.0.0) (2026-02-23)

### ⚠ BREAKING CHANGES

* CLI now requires subcommand - use `asg-refresh start`
instead of `asg-refresh` to start a refresh.

Co-authored-by: paulwilliamson <jenratech@gmail.com>
Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

### Features

* add check subcommand to poll instance refresh completion ([f8721aa](https://github.com/williamsonpaul/aws-tools/commit/f8721aa4919c5816f3325c939cc2c7f6a0e833c1))

### Bug Fixes

* resolve flake8 unused import and line length violations ([#6](https://github.com/williamsonpaul/aws-tools/issues/6)) ([c446aa1](https://github.com/williamsonpaul/aws-tools/commit/c446aa15f8851dd2cfd5b5e701d3213dc632e674))

## [1.0.1](https://github.com/williamsonpaul/aws-tools/compare/v1.0.0...v1.0.1) (2026-02-23)

### Bug Fixes

* bump dev dependency floor versions to resolve pip-audit CVEs ([#3](https://github.com/williamsonpaul/aws-tools/issues/3)) ([be9f497](https://github.com/williamsonpaul/aws-tools/commit/be9f497275edca8ebfc54ae0ba5e2185ad4aaa89))

## 1.0.0 (2026-02-23)

### Features

* replace acronym creator with AWS ASG instance refresh tool ([#1](https://github.com/williamsonpaul/aws-tools/issues/1)) ([a6a5abd](https://github.com/williamsonpaul/aws-tools/commit/a6a5abd0a600453db94350d8fd47eeb58f3cbe6a))

## [1.9.1](https://github.com/reaandrew/acronymcreator/compare/v1.9.0...v1.9.1) (2025-10-06)

### Bug Fixes

* **ci:** increase max-turns for Claude Code action from 20 to 50 ([5a59a38](https://github.com/reaandrew/acronymcreator/commit/5a59a38b7c29d69efa775aa3eb51aa5a66417521))

## [1.9.0](https://github.com/reaandrew/acronymcreator/compare/v1.8.1...v1.9.0) (2025-10-06)

### Features

* add YAML export format ([#8](https://github.com/reaandrew/acronymcreator/issues/8)) ([35ef9fb](https://github.com/reaandrew/acronymcreator/commit/35ef9fb4734208131f2033313bbc44271d9b483c))

## [1.8.1](https://github.com/reaandrew/acronymcreator/compare/v1.8.0...v1.8.1) (2025-10-06)

### Bug Fixes

* **ci:** add CI environment guidance to auto-fix workflow ([66b8c74](https://github.com/reaandrew/acronymcreator/commit/66b8c74dac0a096003b3eda35aec2744ccaa27aa))

## [1.8.0](https://github.com/reaandrew/acronymcreator/compare/v1.7.0...v1.8.0) (2025-10-06)

### Features

* optimize auto-fix workflow for efficiency ([421dbcc](https://github.com/reaandrew/acronymcreator/commit/421dbcc0cb4ab5d2e27bfd80a461c5eeddbbd281))

## [1.7.0](https://github.com/reaandrew/acronymcreator/compare/v1.6.0...v1.7.0) (2025-10-06)

### Features

* enhance auto-fix workflow to update documentation ([e112ea3](https://github.com/reaandrew/acronymcreator/commit/e112ea37c5d27e0890eb60c291a2d42dc64b56c1))

### Bug Fixes

* increase auto-fix max-turns from 20 to 50 ([d2d47ea](https://github.com/reaandrew/acronymcreator/commit/d2d47eadfae26148b5b9ff77c744594f0774cf07))

## [1.6.0](https://github.com/reaandrew/acronymcreator/compare/v1.5.4...v1.6.0) (2025-10-06)

### Features

* add concurrency control to cancel previous CI runs ([8f91647](https://github.com/reaandrew/acronymcreator/commit/8f916473ce7232639b7281bc6eb7a6ba48a3c3f8))
* add JSON export functionality ([#4](https://github.com/reaandrew/acronymcreator/issues/4)) ([4a1a0cc](https://github.com/reaandrew/acronymcreator/commit/4a1a0ccc00a29783d48114b16e5bef0e1ec66880))

### Bug Fixes

* add actions:write permission and clarify CI trigger timing ([7891ce2](https://github.com/reaandrew/acronymcreator/commit/7891ce22590559d9a8b061c8c032ff3c0f03c302))
* add allowed_files to auto-fix workflow for file edit permissions ([1fa5095](https://github.com/reaandrew/acronymcreator/commit/1fa5095bdaef4ed419875d99d49867371151e47f))
* add checkout step for gh pr comment ([9ad29f0](https://github.com/reaandrew/acronymcreator/commit/9ad29f05cea9d540ac0590213269468dcfe4400c))
* add timeouts to SonarCloud quality gate check to prevent hanging ([0eb4311](https://github.com/reaandrew/acronymcreator/commit/0eb4311b31f69ebe62c52fbbb26aedd4f24809c5))
* auto-fix workflow should trigger on workflow_dispatch events too ([f750146](https://github.com/reaandrew/acronymcreator/commit/f75014655c79bc804d4e1700b8b4d863b7a19bc4))
* checkout PR branch in auto-fix workflow ([6241421](https://github.com/reaandrew/acronymcreator/commit/6241421194c76b3ca7b394502d70afcea8abdbd4))
* **ci:** amend Claude's commit instead of creating empty trigger commit ([ca6ac8a](https://github.com/reaandrew/acronymcreator/commit/ca6ac8abfa62458f989c1e5043f3c07b67c4b500))
* **ci:** complete v1 migration and remove test error ([522aea2](https://github.com/reaandrew/acronymcreator/commit/522aea293b273a36ec98010bc290a225afcc7d57))
* **ci:** complete v1 migration with PATH, loop guard, and git author config ([77c04fe](https://github.com/reaandrew/acronymcreator/commit/77c04fe491f0d25bf56796db7f26f46d085d5178))
* **ci:** remove invalid allowed_files parameter blocking file edits ([eb0a9d7](https://github.com/reaandrew/acronymcreator/commit/eb0a9d7d2e2f0a8fe3bb8e20208cc4aa631b584f))
* **ci:** remove invalid allowed_files parameter blocking file edits ([69e00d9](https://github.com/reaandrew/acronymcreator/commit/69e00d9159dbc2ab318e04f673dd43b134f8a939))
* **ci:** remove redundant trigger step, Claude's commit already triggers CI ([caa9a0f](https://github.com/reaandrew/acronymcreator/commit/caa9a0f522c89ad7c16ee821a84b22d6c30ca3f1))
* **ci:** remove token usage tracking step causing failures ([2795051](https://github.com/reaandrew/acronymcreator/commit/27950512950339eb9f1b17bec1bd8d817e1313c2))
* **ci:** set permissionMode to always-allow to enable file edits ([fb57892](https://github.com/reaandrew/acronymcreator/commit/fb57892df3596b8b4c97c1056ba663066d8d8394))
* **ci:** set permissionMode to always-allow to enable file edits ([cc227fc](https://github.com/reaandrew/acronymcreator/commit/cc227fc2a5a0ce7e4d24309b7538a87e256e22e8))
* **ci:** use acceptEdits permission mode with allowed tools ([4ce76fa](https://github.com/reaandrew/acronymcreator/commit/4ce76fa7f9c4aa40025fb4fdc0b609f35286de07))
* **ci:** use acceptEdits permission mode with allowed tools ([c847875](https://github.com/reaandrew/acronymcreator/commit/c847875de0117ca6fe8240e0eccdc93bb44ebcd1))
* correct allowedTools syntax - use simple comma-separated list ([ace8d0f](https://github.com/reaandrew/acronymcreator/commit/ace8d0f3ae435f5446ebbbd6452671db7dd6c0a3))
* disable Go cache for lefthook installation ([f227940](https://github.com/reaandrew/acronymcreator/commit/f22794070755f494665adfa75f68f8752d3ce300))
* fallback to PR lookup by branch name for workflow_dispatch events ([6c5d484](https://github.com/reaandrew/acronymcreator/commit/6c5d4846883b1bebf2e4a93f388d1b1f00b09a2d))
* get PR number from workflow run object correctly ([f8bf96f](https://github.com/reaandrew/acronymcreator/commit/f8bf96f7a5f0faedb3980d959423565805f0e1cb))
* grant Claude additional permissions for Bash, WebFetch, Edit tools ([8ed81d0](https://github.com/reaandrew/acronymcreator/commit/8ed81d0c2d7a93cd93854abfa99156cb2d3d2590))
* improve lefthook configuration for GitGuardian and pytest hooks ([d6b696a](https://github.com/reaandrew/acronymcreator/commit/d6b696acbfaa8f3ef3ac3633ebf50824728023c4))
* improve PR number lookup error handling ([0f6bf3f](https://github.com/reaandrew/acronymcreator/commit/0f6bf3f26ea061eddd52a0615f14d852cd66ad76))
* instruct Claude to trigger CI after pushing fixes ([2b3239f](https://github.com/reaandrew/acronymcreator/commit/2b3239f9e97dfd3d30475a444e599b47efc59cf4))
* invoke Claude Code Action directly instead of posting comment ([0cb3e46](https://github.com/reaandrew/acronymcreator/commit/0cb3e463e80ec59a138938ddb2101d3513abd9a9))
* properly quote multiline comment body ([cbb5f78](https://github.com/reaandrew/acronymcreator/commit/cbb5f784be6607225ae4612ffabc1712194c0211))
* remove broken branch-ci workflow and add manual CI trigger ([d32bafc](https://github.com/reaandrew/acronymcreator/commit/d32bafc976e78168aa80b40404c21433e7c52ffa))
* remove markdown bold syntax causing YAML error ([249df9a](https://github.com/reaandrew/acronymcreator/commit/249df9a4f9e1bed78cd821d41f226cebfec20d5f))
* resolve SonarCloud MAJOR issues ([378a3e6](https://github.com/reaandrew/acronymcreator/commit/378a3e6f3d915e323038bcc7c01bd505128b1e95))
* revert to valid v1 additional_permissions parameter ([845a087](https://github.com/reaandrew/acronymcreator/commit/845a087d10394e545fbad511dab8f50b898236d4))
* update auto-fix workflow to properly get PR number ([915a009](https://github.com/reaandrew/acronymcreator/commit/915a009099e495598a75cce7c3afd4b47a440ec0))
* update CI workflow to properly install lefthook and fix GitGuardian secret name ([a1989b8](https://github.com/reaandrew/acronymcreator/commit/a1989b888b2ef48d3b77e4aa7ca4caab28ddc627))
* use claude_args --allowedTools for v1 tool permissions ([3fabda7](https://github.com/reaandrew/acronymcreator/commit/3fabda7a433e01f8b95d19573e3e64a0f1b37983))
* use correct allowed_tools parameter for Claude Code Action ([c41f0af](https://github.com/reaandrew/acronymcreator/commit/c41f0afc18e5724fb1312d7db00d5e660b56db4d))
* use full path to lefthook in CI to avoid PATH timing issues ([3fe2e9a](https://github.com/reaandrew/acronymcreator/commit/3fe2e9aca2947d95093777f456ff1a555c348b1c))
* use Go to install lefthook instead of curl script ([174104e](https://github.com/reaandrew/acronymcreator/commit/174104e93dc3e4f84c30df741e9ff7b474f85367))
* use proper variable expansion in comment body ([880b8b4](https://github.com/reaandrew/acronymcreator/commit/880b8b4bd495fea59c781bce338c8eb822e37883))

## [1.5.4](https://github.com/reaandrew/acronymcreator/compare/v1.5.3...v1.5.4) (2025-06-15)

### Bug Fixes

* exclude docs/scripts from SonarCloud coverage analysis ([2574c58](https://github.com/reaandrew/acronymcreator/commit/2574c58df0838b74abbb977fcfc08d34f2f5bb7c))
* standardize GitGuardian API key environment variable name ([37458ec](https://github.com/reaandrew/acronymcreator/commit/37458ec007751287383ec21279319d3cc6c53653))
* use non-interactive matplotlib backend in graph script ([6d071b4](https://github.com/reaandrew/acronymcreator/commit/6d071b40940068225da2ef96ea5275bb2fdd1035))

## [1.5.3](https://github.com/reaandrew/acronymcreator/compare/v1.5.2...v1.5.3) (2025-06-13)

### Bug Fixes

* explicitly exclude tests and setup.py from SonarCloud source analysis ([5d9d9b2](https://github.com/reaandrew/acronymcreator/commit/5d9d9b2d16478479e8ee3a6d20116c4e4f9340df))

## [1.5.2](https://github.com/reaandrew/acronymcreator/compare/v1.5.1...v1.5.2) (2025-06-13)

### Bug Fixes

* align SonarCloud source analysis with local coverage scope ([46bfe88](https://github.com/reaandrew/acronymcreator/commit/46bfe8891d52bef7253238497698feeb16b391d3))

## [1.5.1](https://github.com/reaandrew/acronymcreator/compare/v1.5.0...v1.5.1) (2025-06-13)

### Bug Fixes

* improve SonarCloud quality gate handling and debugging ([4d2f8ab](https://github.com/reaandrew/acronymcreator/commit/4d2f8ab2f4c0400ab9787a6f878bb93e8ea0decf))

## [1.5.0](https://github.com/reaandrew/acronymcreator/compare/v1.4.0...v1.5.0) (2025-06-13)

### Features

* implement multiple acronym options generation ([b68301b](https://github.com/reaandrew/acronymcreator/commit/b68301b4e4464d7d82281cf4c1a7004915a92e40))
* implement syllable-based acronym generation ([7f11c2f](https://github.com/reaandrew/acronymcreator/commit/7f11c2f93cb160b5c029a44aa842aacff14db968))

## [1.4.0](https://github.com/reaandrew/acronymcreator/compare/v1.3.0...v1.4.0) (2025-06-13)

### Features

* implement word extraction and filtering functionality ([1794e8a](https://github.com/reaandrew/acronymcreator/commit/1794e8afe1a722b44c8005a3b31680195a828a9b))

## [1.3.0](https://github.com/reaandrew/acronymcreator/compare/v1.2.2...v1.3.0) (2025-06-13)

### Features

* integrate Semgrep security analysis into CI pipeline ([8cfb990](https://github.com/reaandrew/acronymcreator/commit/8cfb990d3ef0e8c21bbf2bd8f215d57f62f1cf5d))

## [1.2.2](https://github.com/reaandrew/acronymcreator/compare/v1.2.1...v1.2.2) (2025-06-12)

### Bug Fixes

* configure Flake8 line length to match Black (88 chars) ([3d07c41](https://github.com/reaandrew/acronymcreator/commit/3d07c41234b2ceb00fca86c063e978547a770f6d))

## [1.2.1](https://github.com/reaandrew/acronymcreator/compare/v1.2.0...v1.2.1) (2025-06-12)

### Bug Fixes

* correct pytest config section header and remove test code ([85c0a2c](https://github.com/reaandrew/acronymcreator/commit/85c0a2c1c9df3f265e5a462838753cc7b8eb940d))
* prevent pytest coverage from creating files in pre-commit ([ac033cc](https://github.com/reaandrew/acronymcreator/commit/ac033cc555529c3f2a03fd8a1f263ee40d73351f))
* prevent pytest from creating cache files during pre-commit ([40f148d](https://github.com/reaandrew/acronymcreator/commit/40f148d651d8960094236e6a51c5309914f54965))
* use .coveragerc to properly redirect coverage data file ([e0bbfbc](https://github.com/reaandrew/acronymcreator/commit/e0bbfbc08b373b3bbae22efb642e2dfd6a814ad4))

## [1.2.0](https://github.com/reaandrew/acronymcreator/compare/v1.1.0...v1.2.0) (2025-06-12)

### Features

* add complete Python package structure and CLI ([d7c4cd4](https://github.com/reaandrew/acronymcreator/commit/d7c4cd4e888c1466c09c1c377c9fc90801d04386))
* add detailed SonarCloud quality gate status reporting ([add571c](https://github.com/reaandrew/acronymcreator/commit/add571c920b28ba3a72fe943a79c8872582a7cf5))
* implement article filtering for acronym generation ([2f96c4f](https://github.com/reaandrew/acronymcreator/commit/2f96c4fd5de000148e14e4252812896ee734e490))

### Bug Fixes

* configure pytest pre-commit hook for CI compatibility ([58f9331](https://github.com/reaandrew/acronymcreator/commit/58f9331d5095a3e3cc932217b08b38ce4ab48d55))
* configure pytest pre-commit hook to show Passed when coverage is good ([d8e33d3](https://github.com/reaandrew/acronymcreator/commit/d8e33d345aece8962c291567a5ddc49a83ca10b5))
* install project dependencies including click in CI ([ba87333](https://github.com/reaandrew/acronymcreator/commit/ba873333da38f8d08652c993f75dd1a366e7f7e6))
* update repository URL in semantic-release config ([6ea0983](https://github.com/reaandrew/acronymcreator/commit/6ea0983e33462a10ed3ca0c1c139040062d3301b))

## [1.1.0](https://github.com/reaandrew/git-guardian-ci-examples/compare/v1.0.1...v1.1.0) (2025-06-12)

### Features

* add initial acronym creator with basic functionality ([c68b2e0](https://github.com/reaandrew/git-guardian-ci-examples/commit/c68b2e08a675e563dcdc89394f2b177ee4ccad37))
* add SonarCloud analysis with improved CI stage naming ([b0fbb39](https://github.com/reaandrew/git-guardian-ci-examples/commit/b0fbb397d1aa46422981d4fadedc209dacffb986))

### Bug Fixes

* remove trailing whitespace from README ([9e49825](https://github.com/reaandrew/git-guardian-ci-examples/commit/9e49825a0043412bbede68a13a2080c55640597c))

## [1.0.1](https://github.com/reaandrew/git-guardian-ci-examples/compare/v1.0.0...v1.0.1) (2025-06-12)

### Bug Fixes

* update pre-commit hooks to resolve deprecation warnings ([a5c9773](https://github.com/reaandrew/git-guardian-ci-examples/commit/a5c9773daddcbfa6108d2f9a09fc8accca70ec9a))

## 1.0.0 (2025-06-12)

### Features

* add basic GitHub Actions CI workflow ([5db32ca](https://github.com/reaandrew/git-guardian-ci-examples/commit/5db32ca5217326700d043c9c943dc991aab930fe))
* add conventional commit enforcement with pre-commit ([a1cbbf1](https://github.com/reaandrew/git-guardian-ci-examples/commit/a1cbbf1270981369f3b3659f0baaa79c3c91a5fc))
* add semantic-release for automated versioning and tagging ([828c9b9](https://github.com/reaandrew/git-guardian-ci-examples/commit/828c9b994c10e55e7462e1aee402abd6b8d54602))
* add test file for demonstrating pre-commit validation ([ab30896](https://github.com/reaandrew/git-guardian-ci-examples/commit/ab308966ec3a45b63e28c604624d2b3bb0775709))

### Bug Fixes

* add missing conventional-changelog dependency and fix semantic-release config ([de1c5c7](https://github.com/reaandrew/git-guardian-ci-examples/commit/de1c5c7dc79871f5443fedcdb2aaa22f542e20d4))
