#!/bin/bash
# This script outputs environment variables for Claude Code
# Replace the placeholder values with your actual token retrieval method

# Example methods to retrieve tokens:
# 1. From environment variables already set:
#    echo "SONAR_TOKEN=${SONAR_TOKEN}"
# 2. From a password manager like pass:
#    echo "SONAR_TOKEN=$(pass sonarcloud/token)"
# 3. From a .env file (not committed):
#    source .env.local && echo "SONAR_TOKEN=${SONAR_TOKEN}"

# For now, using environment variables (set these in your shell):
echo "SONAR_TOKEN=${SONAR_TOKEN}"
echo "GITGUARDIAN_API_KEY=${GITGUARDIAN_API_KEY}"
