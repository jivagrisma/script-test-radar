#!/bin/bash

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print with color
print_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_color $RED "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_color $RED "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Check AWS credentials
check_aws_credentials() {
    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        if [ ! -f ".env" ]; then
            print_color $YELLOW "AWS credentials not found in environment."
            print_color $YELLOW "Creating .env file from template..."
            cp .env.example .env
            print_color $YELLOW "Please update .env with your AWS credentials."
            exit 1
        fi
    fi
}

# Create necessary directories
create_directories() {
    print_color $GREEN "Creating necessary directories..."
    mkdir -p reports .cache
}

# Build Docker image
build_docker() {
    print_color $GREEN "Building Docker image..."
    docker-compose build
}

# Run tests
run_tests() {
    local test_path=$1
    print_color $GREEN "Running tests in ${test_path}..."

    # Export test path for docker-compose
    export TEST_PATH=$test_path

    # Run tests with docker-compose
    docker-compose run --rm test-radar run $test_path
}

# Main installation and setup
main() {
    print_color $GREEN "Starting Test Radar installation and setup..."

    # Check requirements
    check_docker
    check_aws_credentials

    # Setup
    create_directories
    build_docker

    # If test path is provided, run tests
    if [ ! -z "$1" ]; then
        run_tests "$1"
    else
        print_color $YELLOW "No test path provided. To run tests:"
        print_color $YELLOW "./install_and_run.sh /path/to/tests"
    fi
}

# Show help
show_help() {
    echo "Usage: $0 [test_path]"
    echo
    echo "Options:"
    echo "  test_path    Path to test directory or file"
    echo
    echo "Environment variables:"
    echo "  AWS_ACCESS_KEY_ID         AWS access key ID"
    echo "  AWS_SECRET_ACCESS_KEY     AWS secret access key"
    echo "  AWS_REGION               AWS region (default: us-east-1)"
    echo "  TEST_PARALLEL_JOBS       Number of parallel test jobs (default: 2)"
    echo "  TEST_TIMEOUT            Test timeout in seconds (default: 300)"
    echo "  TEST_COVERAGE_TARGET    Coverage target percentage (default: 95.0)"
    echo "  LOG_LEVEL              Logging level (default: INFO)"
}

# Parse command line arguments
case "$1" in
    -h|--help)
        show_help
        exit 0
        ;;
    "")
        main
        ;;
    *)
        main "$1"
        ;;
esac
