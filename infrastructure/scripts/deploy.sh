# infrastructure/scripts/deploy.sh
``` bash
#!/bin/bash
#
# deploy.sh - Deployment script for the Freight Price Movement Agent
#
# This script automates the process of deploying the application to different
# environments (development, staging, production). It supports both Docker
# Compose and Kubernetes deployment methods, handles environment configuration,
# performs database migrations, and includes health checks to verify successful
# deployment.

set -euo pipefail

# --- Global Variables ---

# Script directory
SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")

# Project root directory
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)

# Docker directory
DOCKER_DIR="$PROJECT_ROOT/infrastructure/docker"

# Kubernetes directory
K8S_DIR="$PROJECT_ROOT/infrastructure/kubernetes"

# Log directory
LOG_DIR="$PROJECT_ROOT/logs"

# Log file
LOG_FILE="$LOG_DIR/deploy_$(date +"%Y%m%d_%H%M%S").log"

# Deployment environment (default: development)
ENVIRONMENT="${ENVIRONMENT:-development}"

# Deployment type (default: docker)
DEPLOYMENT_TYPE="${DEPLOYMENT_TYPE:-docker}"

# Docker registry (optional)
DOCKER_REGISTRY="${DOCKER_REGISTRY:-}"

# Docker image tag (default: latest)
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Kubernetes namespace (default: freight-price-agent)
NAMESPACE="${NAMESPACE:-freight-price-agent}"

# Kubernetes context (optional)
KUBE_CONTEXT="${KUBE_CONTEXT:-}"

# Database migration flag (default: true)
DB_MIGRATE="${DB_MIGRATE:-true}"

# Health check retries (default: 30)
HEALTH_CHECK_RETRIES="${HEALTH_CHECK_RETRIES:-30}"

# Health check delay in seconds (default: 10)
HEALTH_CHECK_DELAY="${HEALTH_CHECK_DELAY:-10}"

# Deployment timeout in seconds (default: 600)
DEPLOYMENT_TIMEOUT="${DEPLOYMENT_TIMEOUT:-600}"

# Rollback on failure flag (default: true)
ROLLBACK_ON_FAILURE="${ROLLBACK_ON_FAILURE:-true}"

# Canary deployment flag (default: false)
CANARY_DEPLOYMENT="${CANARY_DEPLOYMENT:-false}"

# Initial traffic percentage for canary deployment (default: 10)
CANARY_WEIGHT="${CANARY_WEIGHT:-10}"

# --- Helper Functions ---

# Function to log messages
log_message() {
  local level="$1"
  local message="$2"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$timestamp] [$level] $message"
  echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Function to display usage information
show_usage() {
  echo "Usage: $(basename "$0") [options]"
  echo
  echo "Deploys the Freight Price Movement Agent to different environments."
  echo
  echo "Options:"
  echo "  -h, --help              Show this help message and exit"
  echo "  -e, --environment <env> Deployment environment (development, staging, production)"
  echo "                          Default: $ENVIRONMENT"
  echo "  -t, --type <type>       Deployment type (docker, kubernetes)"
  echo "                          Default: $DEPLOYMENT_TYPE"
  echo "  -r, --registry <url>    Docker registry URL"
  echo "                          Default: $DOCKER_REGISTRY"
  echo "  -i, --image-tag <tag>   Docker image tag"
  echo "                          Default: $IMAGE_TAG"
  echo "  -n, --namespace <name>  Kubernetes namespace"
  echo "                          Default: $NAMESPACE"
  echo "  -c, --context <ctx>     Kubernetes context"
  echo "                          Default: $KUBE_CONTEXT"
  echo "  -m, --skip-migrations   Skip database migrations"
  echo "  -b, --build             Build Docker images before deployment"
  echo "  -f, --force             Force deployment even if health checks fail"
  echo "  -y, --canary            Use canary deployment strategy"
  echo
  echo "Environment Variables:"
  echo "  ENVIRONMENT         Deployment environment (development, staging, production)"
  echo "                      Default: development"
  echo "  DEPLOYMENT_TYPE     Deployment method (docker or kubernetes)"
  echo "                      Default: docker"
  echo "  DOCKER_REGISTRY     Docker registry URL for pushing images"
  echo "  IMAGE_TAG           Docker image tag"
  echo "                      Default: latest"
  echo "  NAMESPACE           Kubernetes namespace for deployment"
  echo "                      Default: freight-price-agent"
  echo "  KUBE_CONTEXT        Kubernetes context to use"
  echo "  DB_MIGRATE          Whether to run database migrations"
  echo "                      Default: true"
  echo "  HEALTH_CHECK_RETRIES Number of health check retry attempts"
  echo "                      Default: 30"
  echo "  HEALTH_CHECK_DELAY  Delay between health check attempts in seconds"
  echo "                      Default: 10"
  echo "  DEPLOYMENT_TIMEOUT  Timeout for deployment in seconds"
  echo "                      Default: 600"
  echo "  ROLLBACK_ON_FAILURE Whether to rollback on deployment failure"
  echo "                      Default: true"
  echo "  CANARY_DEPLOYMENT   Whether to use canary deployment strategy"
  echo "                      Default: false"
  echo "  CANARY_WEIGHT       Initial traffic percentage for canary deployment"
  echo "                      Default: 10"
  echo
  echo "Examples:"
  echo "  $(basename "$0") -e production -t kubernetes -i stable-1.0"
  echo "  ENVIRONMENT=staging DEPLOYMENT_TYPE=docker $(basename "$0") -b"
}

# Function to parse command line arguments
parse_arguments() {
  while [[ $# -gt 0 ]]; do
    local arg="$1"
    case "$arg" in
      -h|--help)
        show_usage
        exit 0
        ;;
      -e|--environment)
        ENVIRONMENT="$2"
        shift 2
        ;;
      -t|--type)
        DEPLOYMENT_TYPE="$2"
        shift 2
        ;;
      -r|--registry)
        DOCKER_REGISTRY="$2"
        shift 2
        ;;
      -i|--image-tag)
        IMAGE_TAG="$2"
        shift 2
        ;;
      -n|--namespace)
        NAMESPACE="$2"
        shift 2
        ;;
      -c|--context)
        KUBE_CONTEXT="$2"
        shift 2
        ;;
      -m|--skip-migrations)
        DB_MIGRATE="false"
        shift
        ;;
      -b|--build)
        BUILD_IMAGES="true"
        shift
        ;;
      -f|--force)
        ROLLBACK_ON_FAILURE="false"
        shift
        ;;
      -y|--canary)
        CANARY_DEPLOYMENT="true"
        shift
        ;;
      *)
        log_message "ERROR" "Unknown option: $arg"
        show_usage
        exit 1
        ;;
    esac
  done
}

# Function to check dependencies
check_dependencies() {
  log_message "INFO" "Checking dependencies..."

  # Check for common dependencies
  if ! command -v bash &> /dev/null; then
    log_message "ERROR" "bash command not found. Please install bash."
    exit 2
  fi

  if ! command -v curl &> /dev/null; then
    log_message "ERROR" "curl command not found. Please install curl."
    exit 2
  fi

  # Check for docker and docker-compose
  if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
    if ! command -v docker &> /dev/null; then
      log_message "ERROR" "docker command not found. Please install docker."
      exit 2
    fi
    if ! command -v docker-compose &> /dev/null; then
      log_message "ERROR" "docker-compose command not found. Please install docker-compose."
      exit 2
    fi
  fi

  # Check for kubectl
  if [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]]; then
    if ! command -v kubectl &> /dev/null; then
      log_message "ERROR" "kubectl command not found. Please install kubectl."
      exit 2
    fi
  fi

  # Check for aws-cli
  if [[ "$DOCKER_REGISTRY" == *"amazonaws.com"* ]]; then
    if ! command -v aws &> /dev/null; then
      log_message "ERROR" "aws-cli command not found. Please install aws-cli."
      exit 2
    fi
  fi

  log_message "INFO" "All dependencies are met."
}

# Function to load environment variables
load_environment_variables() {
  log_message "INFO" "Loading environment variables..."

  local env_file="$PROJECT_ROOT/.env.$ENVIRONMENT"

  if [[ ! -f "$env_file" ]]; then
    log_message "WARN" "Environment file not found: $env_file"
    return
  fi

  log_message "INFO" "Sourcing environment file: $env_file"
  source "$env_file"
}

# Function to build Docker images
build_docker_images() {
  log_message "INFO" "Building Docker images..."

  local compose_file="$DOCKER_DIR/docker-compose.$ENVIRONMENT.yml"

  if [[ ! -f "$compose_file" ]]; then
    log_message "ERROR" "Docker Compose file not found: $compose_file"
    exit 1
  fi

  docker-compose -f "$compose_file" build --parallel

  if [[ "$DOCKER_REGISTRY" != "" ]]; then
    log_message "INFO" "Tagging and pushing Docker images to registry: $DOCKER_REGISTRY"
    docker-compose -f "$compose_file" push
  fi
}

# Function to deploy using Docker Compose
deploy_docker_compose() {
  log_message "INFO" "Deploying using Docker Compose..."

  local compose_file="$DOCKER_DIR/docker-compose.$ENVIRONMENT.yml"

  if [[ ! -f "$compose_file" ]]; then
    log_message "ERROR" "Docker Compose file not found: $compose_file"
    exit 1
  fi

  docker-compose -f "$compose_file" up -d --remove-orphans --timeout "$DEPLOYMENT_TIMEOUT"

  if [[ "$ROLLBACK_ON_FAILURE" == "true" ]]; then
    log_message "WARN" "Rollback on failure is enabled, but Docker Compose does not support automated rollbacks."
    log_message "WARN" "Manual intervention may be required."
  fi
}

# Function to deploy to Kubernetes
deploy_kubernetes() {
  log_message "INFO" "Deploying to Kubernetes..."

  if [[ "$KUBE_CONTEXT" != "" ]]; then
    log_message "INFO" "Switching to Kubernetes context: $KUBE_CONTEXT"
    kubectl config use-context "$KUBE_CONTEXT"
  fi

  # Ensure namespace exists
  log_message "INFO" "Ensuring namespace exists: $NAMESPACE"
  kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

  # Apply ConfigMaps and Secrets
  log_message "INFO" "Applying ConfigMaps and Secrets..."
  kubectl apply -k "$K8S_DIR/base" -n "$NAMESPACE"

  # Deploy using kustomize
  log_message "INFO" "Applying kustomize configuration..."
  kubectl apply -k "$K8S_DIR/$ENVIRONMENT" -n "$NAMESPACE"

  # Wait for deployment to complete
  log_message "INFO" "Waiting for deployment to complete..."
  kubectl rollout status deployment/freight-price-agent -n "$NAMESPACE" --timeout="${DEPLOYMENT_TIMEOUT}s"
}

# Function to perform a canary deployment to Kubernetes
perform_canary_deployment() {
  log_message "INFO" "Performing canary deployment to Kubernetes..."
  # TODO: Implement canary deployment logic
  log_message "WARN" "Canary deployment is not yet implemented."
}

# Function to run database migrations
run_database_migrations() {
  log_message "INFO" "Running database migrations..."

  if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
    docker-compose -f "$DOCKER_DIR/docker-compose.$ENVIRONMENT.yml" exec -T api alembic upgrade head
  elif [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]]; then
    kubectl exec -n "$NAMESPACE" deployment/freight-price-agent -- alembic upgrade head
  else
    log_message "ERROR" "Unsupported deployment type: $DEPLOYMENT_TYPE"
    exit 1
  fi
}

# Function to perform a health check
perform_health_check() {
  log_message "INFO" "Performing health check..."

  local health_endpoint=""
  if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
    health_endpoint="http://localhost:8000/health"
  elif [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]]; then
    health_endpoint=$(kubectl get svc freight-price-agent -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    health_endpoint="http://$health_endpoint/health"
  else
    log_message "ERROR" "Unsupported deployment type: $DEPLOYMENT_TYPE"
    exit 1
  fi

  local i=0
  while [[ $i -lt $HEALTH_CHECK_RETRIES ]]; do
    log_message "INFO" "Health check attempt $((i+1)) of $HEALTH_CHECK_RETRIES..."
    if curl -s "$health_endpoint" | grep -q '"status": "ok"'; then
      log_message "INFO" "Health check passed."
      return 0
    else
      log_message "WARN" "Health check failed."
      i=$((i+1))
      sleep "$HEALTH_CHECK_DELAY"
    fi
  done

  log_message "ERROR" "Health check failed after $HEALTH_CHECK_RETRIES attempts."
  return 1
}

# Function to rollback deployment
rollback_deployment() {
  log_message "INFO" "Rolling back deployment..."

  if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
    log_message "WARN" "Rollback is not fully automated for Docker Compose. Manual intervention may be required."
    docker-compose -f "$DOCKER_DIR/docker-compose.$ENVIRONMENT.yml" down
  elif [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]]; then
    kubectl rollout undo deployment/freight-price-agent -n "$NAMESPACE"
  else
    log_message "ERROR" "Unsupported deployment type: $DEPLOYMENT_TYPE"
    exit 1
  fi
}

# Function to perform cleanup operations
cleanup() {
  log_message "INFO" "Performing cleanup operations..."

  # Remove temporary files
  log_message "INFO" "Removing temporary files..."
  # TODO: Add logic to remove temporary files

  # Prune old Docker images
  if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
    log_message "INFO" "Pruning old Docker images..."
    docker image prune -af
  fi

  log_message "INFO" "Cleanup completed."
}

# --- Main Script ---

# Parse command line arguments
parse_arguments "$@"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Log start of deployment process
log_message "INFO" "Starting deployment process for environment: $ENVIRONMENT, deployment type: $DEPLOYMENT_TYPE"

# Check dependencies
check_dependencies

# Load environment variables
load_environment_variables

# Build Docker images if requested
if [[ "$BUILD_IMAGES" == "true" ]]; then
  build_docker_images
fi

# Deploy based on deployment type
if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
  deploy_docker_compose
elif [[ "$DEPLOYMENT_TYPE" == "kubernetes" ]]; then
  deploy_kubernetes
else
  log_message "ERROR" "Unsupported deployment type: $DEPLOYMENT_TYPE"
  exit 1
fi

# Run database migrations if requested
if [[ "$DB_MIGRATE" == "true" ]]; then
  run_database_migrations
fi

# Perform health check
perform_health_check

# Rollback if health check fails and rollback is enabled
if [[ "$ROLLBACK_ON_FAILURE" == "true" ]] && [[ "$?" -ne "0" ]]; then
  log_message "ERROR" "Deployment failed. Rolling back..."
  rollback_deployment
  exit 1
fi

# Perform cleanup
cleanup

# Log completion of deployment process
log_message "INFO" "Deployment process completed successfully."

exit 0