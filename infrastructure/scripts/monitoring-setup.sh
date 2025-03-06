#!/usr/bin/env bash
# monitoring-setup.sh
#
# This script automates the setup and configuration of monitoring infrastructure
# for the Freight Price Movement Agent, including metrics collection, log aggregation,
# distributed tracing, and alerting systems.
#
# The script sets up the following components:
# - Prometheus - for metrics collection
# - Grafana - for visualization dashboards
# - AlertManager - for alert handling and notifications
# - Elasticsearch - for log storage and analysis
# - Kibana - for log visualization
# - Filebeat - for log collection
# - Jaeger - for distributed tracing
# - Node Exporter - for host metrics collection
#
# Requirements:
# - Docker and Docker Compose
# - Root or sudo access
# - Internet connectivity to download container images

# Exit on error, undefined variable reference, or pipe failure
set -euo pipefail

# Script variables
SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
PROMETHEUS_VERSION="2.37.0"
GRAFANA_VERSION="9.1.0"
ALERTMANAGER_VERSION="0.24.0"
ELASTICSEARCH_VERSION="7.17.0"
KIBANA_VERSION="7.17.0"
FILEBEAT_VERSION="7.17.0"
JAEGER_VERSION="1.37.0"
NODE_EXPORTER_VERSION="1.3.1"
MONITORING_DIR="/opt/monitoring"
CONFIG_DIR="${SCRIPT_DIR}/../config/monitoring"
LOG_FILE="/var/log/monitoring-setup.log"

# Ensure log file exists and is writable
touch "$LOG_FILE" || { echo "Cannot create log file at $LOG_FILE. Exiting."; exit 1; }

# Function to log messages
log_message() {
    local timestamp
    timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] $1"
    echo "[$timestamp] $1" >> "$LOG_FILE"
}

# Function to check prerequisites
check_prerequisites() {
    log_message "Checking prerequisites..."
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        log_message "ERROR: This script must be run as root or with sudo privileges."
        return 1
    fi
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_message "ERROR: Docker is not installed. Please install Docker and try again."
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        log_message "ERROR: Docker daemon is not running. Please start Docker and try again."
        return 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_message "ERROR: Docker Compose is not installed. Please install Docker Compose and try again."
        return 1
    fi
    
    # Check if required ports are available
    local ports=(9090 9093 9100 3000 9200 5601 14268 16686)
    for port in "${ports[@]}"; do
        if netstat -tuln | grep -q ":$port "; then
            log_message "ERROR: Port $port is already in use. Please free up this port and try again."
            return 1
        fi
    done
    
    # Check if there's enough disk space (at least 10GB free)
    local free_space
    free_space=$(df -m "$MONITORING_DIR" 2>/dev/null | awk 'NR==2 {print $4}' || df -m / | awk 'NR==2 {print $4}')
    if [[ "$free_space" -lt 10240 ]]; then
        log_message "WARNING: Less than 10GB of free disk space available. This may not be sufficient for monitoring components."
    fi
    
    log_message "Prerequisites check passed."
    return 0
}

# Function to create necessary directories
create_directories() {
    log_message "Creating directories..."
    
    mkdir -p "$MONITORING_DIR"
    mkdir -p "$MONITORING_DIR/prometheus/data"
    mkdir -p "$MONITORING_DIR/grafana/data"
    mkdir -p "$MONITORING_DIR/alertmanager/data"
    mkdir -p "$MONITORING_DIR/elasticsearch/data"
    mkdir -p "$MONITORING_DIR/kibana/data"
    mkdir -p "$MONITORING_DIR/filebeat/data"
    mkdir -p "$MONITORING_DIR/jaeger/data"
    mkdir -p "$MONITORING_DIR/node_exporter"
    mkdir -p "$MONITORING_DIR/config"
    
    # Set appropriate permissions
    chmod -R 755 "$MONITORING_DIR"
    
    # Set Elasticsearch directory permissions (Elasticsearch needs these specific permissions)
    chown -R 1000:1000 "$MONITORING_DIR/elasticsearch/data"
    
    log_message "Directories created successfully."
    return 0
}

# Function to set up Prometheus
setup_prometheus() {
    log_message "Setting up Prometheus..."
    
    # Create Prometheus configuration file
    cat > "$MONITORING_DIR/config/prometheus.yml" << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  scrape_timeout: 10s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

rule_files:
  - "/etc/prometheus/rules/*.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # Data Ingestion Service metrics
  - job_name: 'data-ingestion-service'
    metrics_path: '/metrics'
    scrape_interval: 15s
    static_configs:
      - targets: ['data-ingestion-service:8080']
        labels:
          service: 'data-ingestion'

  # Analysis Engine metrics
  - job_name: 'analysis-engine'
    metrics_path: '/metrics'
    scrape_interval: 15s
    static_configs:
      - targets: ['analysis-engine:8080']
        labels:
          service: 'analysis'

  # Presentation Service metrics
  - job_name: 'presentation-service'
    metrics_path: '/metrics'
    scrape_interval: 15s
    static_configs:
      - targets: ['presentation-service:8080']
        labels:
          service: 'presentation'

  # Integration Service metrics
  - job_name: 'integration-service'
    metrics_path: '/metrics'
    scrape_interval: 15s
    static_configs:
      - targets: ['integration-service:8080']
        labels:
          service: 'integration'

  # Database metrics
  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']
        labels:
          service: 'database'

  # Redis metrics
  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']
        labels:
          service: 'cache'

  # API Gateway metrics
  - job_name: 'api-gateway'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['api-gateway:8080']
        labels:
          service: 'api-gateway'
EOF

    # Create alerts configuration directory
    mkdir -p "$MONITORING_DIR/config/rules"
    
    # Create system alerts configuration
    cat > "$MONITORING_DIR/config/rules/system_alerts.yml" << EOF
groups:
- name: system_alerts
  rules:
  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 15m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage detected"
      description: "CPU usage is above 80% for more than 15 minutes on {{ \$labels.instance }}"

  - alert: HighMemoryUsage
    expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
    for: 15m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage detected"
      description: "Memory usage is above 85% for more than 15 minutes on {{ \$labels.instance }}"

  - alert: HighDiskUsage
    expr: 100 - ((node_filesystem_avail_bytes{mountpoint="/"} * 100) / node_filesystem_size_bytes{mountpoint="/"}) > 85
    for: 15m
    labels:
      severity: warning
    annotations:
      summary: "High disk usage detected"
      description: "Disk usage is above 85% for more than 15 minutes on {{ \$labels.instance }}"

  - alert: InstanceDown
    expr: up == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Instance {{ \$labels.instance }} down"
      description: "{{ \$labels.instance }} of job {{ \$labels.job }} has been down for more than 5 minutes."
EOF

    # Create application alerts configuration
    cat > "$MONITORING_DIR/config/rules/application_alerts.yml" << EOF
groups:
- name: application_alerts
  rules:
  - alert: HighErrorRate
    expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100 > 1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High HTTP error rate"
      description: "Error rate is above 1% for more than 5 minutes on service {{ \$labels.service }}"

  - alert: SlowResponseTime
    expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)) > 5
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Slow response time"
      description: "95th percentile of response time is above 5 seconds for more than 10 minutes on service {{ \$labels.service }}"

  - alert: HighDatabaseLatency
    expr: histogram_quantile(0.95, sum(rate(database_query_duration_seconds_bucket[5m])) by (le)) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High database latency"
      description: "95th percentile of database query duration is above 1 second for more than 5 minutes"

  - alert: LowCacheHitRatio
    expr: sum(rate(cache_hits_total[5m])) / (sum(rate(cache_hits_total[5m])) + sum(rate(cache_misses_total[5m]))) * 100 < 70
    for: 30m
    labels:
      severity: warning
    annotations:
      summary: "Low cache hit ratio"
      description: "Cache hit ratio is below 70% for more than 30 minutes"
EOF

    log_message "Prometheus configuration complete."
    return 0
}

# Function to set up Grafana
setup_grafana() {
    log_message "Setting up Grafana..."
    
    # Create Grafana configuration directory
    mkdir -p "$MONITORING_DIR/config/grafana/provisioning/datasources"
    mkdir -p "$MONITORING_DIR/config/grafana/provisioning/dashboards"
    
    # Create Grafana datasources configuration
    cat > "$MONITORING_DIR/config/grafana/provisioning/datasources/datasources.yml" << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false

  - name: Elasticsearch
    type: elasticsearch
    access: proxy
    url: http://elasticsearch:9200
    database: "filebeat-*"
    jsonData:
      timeField: "@timestamp"
      esVersion: 7.10.0
    editable: false

  - name: Jaeger
    type: jaeger
    access: proxy
    url: http://jaeger:16686
    editable: false
EOF

    # Create Grafana dashboards configuration
    cat > "$MONITORING_DIR/config/grafana/provisioning/dashboards/dashboards.yml" << EOF
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 60
    options:
      path: /var/lib/grafana/dashboards
EOF

    # Create Grafana initial admin password
    mkdir -p "$MONITORING_DIR/config/grafana/config"
    cat > "$MONITORING_DIR/config/grafana/config/grafana.ini" << EOF
[security]
admin_user = admin
admin_password = FreightPriceAgent2023
EOF

    # Create directory for dashboard JSON files
    mkdir -p "$MONITORING_DIR/config/grafana/dashboards"
    
    # Create System Overview dashboard
    cat > "$MONITORING_DIR/config/grafana/dashboards/system_overview.json" << EOF
{
  "annotations": {
    "list": []
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": 1,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 1,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "title": "CPU Usage",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "id": 2,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "title": "Memory Usage",
      "type": "timeseries"
    }
  ],
  "refresh": "5s",
  "schemaVersion": 37,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "System Overview",
  "uid": "system-overview",
  "version": 1,
  "weekStart": ""
}
EOF

    # Create Application Metrics dashboard
    cat > "$MONITORING_DIR/config/grafana/dashboards/application_metrics.json" << EOF
{
  "annotations": {
    "list": []
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": 2,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          },
          "unit": "reqps"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 1,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "title": "Request Rate",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "red",
                "value": 1
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "id": 2,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "title": "Error Rate",
      "type": "timeseries"
    }
  ],
  "refresh": "5s",
  "schemaVersion": 37,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "Application Metrics",
  "uid": "application-metrics",
  "version": 1,
  "weekStart": ""
}
EOF

    # Create SLA Monitoring dashboard
    cat > "$MONITORING_DIR/config/grafana/dashboards/sla_monitoring.json" << EOF
{
  "annotations": {
    "list": []
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": 3,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "red",
                "value": null
              },
              {
                "color": "yellow",
                "value": 99
              },
              {
                "color": "green",
                "value": 99.9
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 1,
      "options": {
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "showThresholdLabels": false,
        "showThresholdMarkers": true
      },
      "title": "System Availability",
      "type": "gauge"
    },
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              },
              {
                "color": "yellow",
                "value": 3
              },
              {
                "color": "red",
                "value": 5
              }
            ]
          },
          "unit": "s"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "id": 2,
      "options": {
        "orientation": "auto",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "showThresholdLabels": false,
        "showThresholdMarkers": true
      },
      "title": "Response Time (p95)",
      "type": "gauge"
    }
  ],
  "refresh": "5s",
  "schemaVersion": 37,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-6h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "SLA Monitoring",
  "uid": "sla-monitoring",
  "version": 1,
  "weekStart": ""
}
EOF

    log_message "Grafana configuration complete."
    return 0
}

# Function to set up AlertManager
setup_alertmanager() {
    log_message "Setting up AlertManager..."
    
    # Create AlertManager configuration file
    cat > "$MONITORING_DIR/config/alertmanager.yml" << EOF
global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.example.com:587'
  smtp_from: 'alerts@freightpriceagent.com'
  smtp_auth_username: 'alerts@freightpriceagent.com'
  smtp_auth_password: 'password'
  smtp_require_tls: true

route:
  group_by: ['alertname', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'team-email'
  routes:
  - match:
      severity: critical
    receiver: 'pagerduty'
    continue: true
  - match:
      severity: warning
    receiver: 'team-email'
    continue: true
  - match:
      severity: info
    receiver: 'slack'

receivers:
- name: 'team-email'
  email_configs:
  - to: 'team@freightpriceagent.com'
    send_resolved: true

- name: 'pagerduty'
  pagerduty_configs:
  - service_key: '<PAGERDUTY_SERVICE_KEY>'
    send_resolved: true

- name: 'slack'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
    channel: '#monitoring-alerts'
    send_resolved: true

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'service']
EOF

    log_message "AlertManager configuration complete."
    return 0
}

# Function to set up Elasticsearch
setup_elasticsearch() {
    log_message "Setting up Elasticsearch..."
    
    # Create Elasticsearch configuration file
    cat > "$MONITORING_DIR/config/elasticsearch.yml" << EOF
cluster.name: "freight-price-agent"
network.host: 0.0.0.0
discovery.type: single-node
bootstrap.memory_lock: true
xpack.security.enabled: false
EOF

    # Create JVM options file
    cat > "$MONITORING_DIR/config/elasticsearch-jvm.options" << EOF
-Xms512m
-Xmx512m
-XX:+UseG1GC
-XX:G1ReservePercent=25
-XX:InitiatingHeapOccupancyPercent=30
EOF

    log_message "Elasticsearch configuration complete."
    return 0
}

# Function to set up Kibana
setup_kibana() {
    log_message "Setting up Kibana..."
    
    # Create Kibana configuration file
    cat > "$MONITORING_DIR/config/kibana.yml" << EOF
server.name: kibana
server.host: "0.0.0.0"
elasticsearch.hosts: ["http://elasticsearch:9200"]
monitoring.ui.container.elasticsearch.enabled: true
EOF

    log_message "Kibana configuration complete."
    return 0
}

# Function to set up Filebeat
setup_filebeat() {
    log_message "Setting up Filebeat..."
    
    # Create Filebeat configuration file
    cat > "$MONITORING_DIR/config/filebeat.yml" << EOF
filebeat.inputs:
- type: container
  paths:
    - /var/lib/docker/containers/*/*.log
  json.keys_under_root: true
  json.add_error_key: true
  json.message_key: log

- type: log
  enabled: true
  paths:
    - /var/log/freight-price-agent/*.log
  fields:
    app: freight-price-agent
  fields_under_root: true

processors:
  - add_docker_metadata:
      host: "unix:///var/run/docker.sock"
  - add_host_metadata: ~
  - add_cloud_metadata: ~

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  indices:
    - index: "filebeat-%{[agent.version]}-%{+yyyy.MM.dd}"

setup.kibana:
  host: "kibana:5601"

setup.dashboards.enabled: true
setup.template.enabled: true
EOF

    log_message "Filebeat configuration complete."
    return 0
}

# Function to set up Jaeger
setup_jaeger() {
    log_message "Setting up Jaeger..."
    
    # Jaeger doesn't require a configuration file for basic setup
    # It will be configured via environment variables in the Docker Compose file
    
    log_message "Jaeger configuration complete."
    return 0
}

# Function to set up Node Exporter
setup_node_exporter() {
    log_message "Setting up Node Exporter..."
    
    # Node Exporter doesn't require a configuration file for basic setup
    
    log_message "Node Exporter configuration complete."
    return 0
}

# Function to generate Docker Compose file
generate_docker_compose() {
    log_message "Generating Docker Compose file..."
    
    cat > "$MONITORING_DIR/docker-compose.yml" << EOF
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v${PROMETHEUS_VERSION}
    container_name: prometheus
    volumes:
      - ${MONITORING_DIR}/config/prometheus.yml:/etc/prometheus/prometheus.yml
      - ${MONITORING_DIR}/config/rules:/etc/prometheus/rules
      - ${MONITORING_DIR}/prometheus/data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    restart: unless-stopped
    networks:
      - monitoring-network

  alertmanager:
    image: prom/alertmanager:v${ALERTMANAGER_VERSION}
    container_name: alertmanager
    volumes:
      - ${MONITORING_DIR}/config/alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - ${MONITORING_DIR}/alertmanager/data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    ports:
      - "9093:9093"
    restart: unless-stopped
    networks:
      - monitoring-network

  node-exporter:
    image: prom/node-exporter:v${NODE_EXPORTER_VERSION}
    container_name: node-exporter
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    restart: unless-stopped
    networks:
      - monitoring-network

  grafana:
    image: grafana/grafana:${GRAFANA_VERSION}
    container_name: grafana
    volumes:
      - ${MONITORING_DIR}/grafana/data:/var/lib/grafana
      - ${MONITORING_DIR}/config/grafana/provisioning:/etc/grafana/provisioning
      - ${MONITORING_DIR}/config/grafana/config/grafana.ini:/etc/grafana/grafana.ini
      - ${MONITORING_DIR}/config/grafana/dashboards:/var/lib/grafana/dashboards
    environment:
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-piechart-panel,grafana-worldmap-panel
    ports:
      - "3000:3000"
    restart: unless-stopped
    networks:
      - monitoring-network

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:${ELASTICSEARCH_VERSION}
    container_name: elasticsearch
    volumes:
      - ${MONITORING_DIR}/config/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml
      - ${MONITORING_DIR}/config/elasticsearch-jvm.options:/usr/share/elasticsearch/config/jvm.options.d/elasticsearch-jvm.options
      - ${MONITORING_DIR}/elasticsearch/data:/usr/share/elasticsearch/data
    environment:
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - "discovery.type=single-node"
    ports:
      - "9200:9200"
      - "9300:9300"
    restart: unless-stopped
    networks:
      - monitoring-network
    ulimits:
      memlock:
        soft: -1
        hard: -1

  kibana:
    image: docker.elastic.co/kibana/kibana:${KIBANA_VERSION}
    container_name: kibana
    volumes:
      - ${MONITORING_DIR}/config/kibana.yml:/usr/share/kibana/config/kibana.yml
    ports:
      - "5601:5601"
    restart: unless-stopped
    networks:
      - monitoring-network
    depends_on:
      - elasticsearch

  filebeat:
    image: docker.elastic.co/beats/filebeat:${FILEBEAT_VERSION}
    container_name: filebeat
    user: root
    volumes:
      - ${MONITORING_DIR}/config/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /var/log:/var/log:ro
    restart: unless-stopped
    networks:
      - monitoring-network
    depends_on:
      - elasticsearch
      - kibana

  jaeger:
    image: jaegertracing/all-in-one:${JAEGER_VERSION}
    container_name: jaeger
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
      - SPAN_STORAGE_TYPE=elasticsearch
      - ES_SERVER_URLS=http://elasticsearch:9200
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"
      - "14268:14268"
      - "14250:14250"
      - "9411:9411"
    restart: unless-stopped
    networks:
      - monitoring-network
    depends_on:
      - elasticsearch

networks:
  monitoring-network:
    driver: bridge
EOF

    log_message "Docker Compose file generated successfully."
    return 0
}

# Function to start the monitoring stack
start_monitoring_stack() {
    log_message "Starting monitoring stack..."
    
    cd "$MONITORING_DIR" || { log_message "ERROR: Could not change directory to $MONITORING_DIR"; return 1; }
    
    # Pull container images first to avoid timeout issues
    log_message "Pulling container images..."
    docker-compose pull
    
    # Start containers
    log_message "Starting containers..."
    docker-compose up -d
    
    # Check if all containers are running
    sleep 10
    if [[ $(docker-compose ps -q | wc -l) -lt 8 ]]; then
        log_message "ERROR: Not all containers are running. Please check the logs with 'docker-compose logs'."
        return 1
    fi
    
    log_message "Monitoring stack started successfully."
    return 0
}

# Function to configure application components for monitoring
configure_application_monitoring() {
    log_message "Configuring application components for monitoring..."
    
    # Create example Prometheus configuration for Python applications
    mkdir -p "$MONITORING_DIR/examples"
    cat > "$MONITORING_DIR/examples/prometheus_python_example.py" << EOF
# Example of how to set up Prometheus metrics in a Python application

from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Create metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['endpoint'])
ACTIVE_REQUESTS = Gauge('http_requests_active', 'Active HTTP requests', ['endpoint'])

# Example middleware or decorator for Flask/FastAPI
def track_request_metrics(endpoint):
    def decorator(func):
        def wrapper(*args, **kwargs):
            ACTIVE_REQUESTS.labels(endpoint=endpoint).inc()
            request_start = time.time()
            try:
                response = func(*args, **kwargs)
                status = response.status_code
            except Exception as e:
                status = 500
                raise e
            finally:
                REQUEST_COUNT.labels(method='GET', endpoint=endpoint, status=status).inc()
                REQUEST_LATENCY.labels(endpoint=endpoint).observe(time.time() - request_start)
                ACTIVE_REQUESTS.labels(endpoint=endpoint).dec()
            return response
        return wrapper
    return decorator

# Start metrics server
def start_metrics_server(port=8000):
    start_http_server(port)
    print(f"Prometheus metrics available on port {port}")
EOF

    # Create example OpenTelemetry configuration for Python applications
    cat > "$MONITORING_DIR/examples/opentelemetry_python_example.py" << EOF
# Example of how to set up OpenTelemetry tracing in a Python application

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure the tracer
def configure_tracer(service_name, jaeger_endpoint="http://jaeger:14268/api/traces"):
    resource = Resource(attributes={
        SERVICE_NAME: service_name
    })
    
    trace.set_tracer_provider(TracerProvider(resource=resource))
    
    # Create Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )
    
    # Create a BatchSpanProcessor and add the exporter to it
    span_processor = BatchSpanProcessor(jaeger_exporter)
    
    # Add to the tracer
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    return trace.get_tracer(service_name)

# Example usage
tracer = configure_tracer("data-ingestion-service")

@tracer.start_as_current_span("process_data")
def process_data(data):
    # Processing logic here
    with tracer.start_as_current_span("validate_data") as span:
        span.set_attribute("data.size", len(data))
        # Validation logic here
    
    with tracer.start_as_current_span("transform_data") as span:
        # Transformation logic here
        pass
    
    return processed_data
EOF

    # Create example logging configuration for Python applications
    cat > "$MONITORING_DIR/examples/logging_config_example.py" << EOF
# Example of how to configure logging in a Python application to work with ELK stack

import logging
import json
from datetime import datetime
import socket
import os

class JsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the log record.
    """
    def __init__(self, service_name):
        self.service_name = service_name
        self.hostname = socket.gethostname()
        
    def format(self, record):
        log_data = {
            "@timestamp": datetime.utcnow().isoformat() + "Z",
            "message": record.getMessage(),
            "level": record.levelname,
            "logger": record.name,
            "path": record.pathname,
            "line": record.lineno,
            "service": self.service_name,
            "host": self.hostname
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        if hasattr(record, "props"):
            log_data.update(record.props)
            
        return json.dumps(log_data)

def configure_logging(service_name, log_level=logging.INFO, log_file=None):
    """
    Configure logging to output JSON formatted logs that can be easily parsed by ELK stack.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JsonFormatter(service_name))
    root_logger.addHandler(console_handler)
    
    # Optionally create file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JsonFormatter(service_name))
        root_logger.addHandler(file_handler)
    
    return root_logger

# Example usage
logger = configure_logging("data-ingestion-service", log_file="/var/log/freight-price-agent/data-ingestion.log")

# Add custom fields to logs
def log_with_context(logger, level, message, **context):
    """
    Log with additional context information.
    """
    extra = {"props": context}
    logger.log(level, message, extra=extra)

# Usage example
log_with_context(logger, logging.INFO, "Processing batch data", 
                 batch_id="12345", 
                 records_count=100, 
                 operation="data_import")
EOF

    log_message "Application monitoring configuration examples created in $MONITORING_DIR/examples/"
    log_message "To enable monitoring in your application components, please implement these examples or similar patterns."
    
    return 0
}

# Function to verify the monitoring setup
verify_monitoring_setup() {
    log_message "Verifying monitoring setup..."
    
    # Check if Prometheus is running and accessible
    if ! curl -s "http://localhost:9090/-/healthy" | grep -q "Prometheus"; then
        log_message "ERROR: Prometheus is not running or accessible."
        return 1
    fi
    
    # Check if Grafana is running and accessible
    if ! curl -s "http://localhost:3000/api/health" | grep -q "ok"; then
        log_message "ERROR: Grafana is not running or accessible."
        return 1
    fi
    
    # Check if AlertManager is running and accessible
    if ! curl -s "http://localhost:9093/-/healthy" | grep -q "ok"; then
        log_message "ERROR: AlertManager is not running or accessible."
        return 1
    fi
    
    # Check if Elasticsearch is running and accessible
    if ! curl -s "http://localhost:9200/" | grep -q "version"; then
        log_message "ERROR: Elasticsearch is not running or accessible."
        return 1
    fi
    
    # Check if Kibana is running and accessible
    if ! curl -s "http://localhost:5601/api/status" | grep -q "kibana"; then
        log_message "ERROR: Kibana is not running or accessible."
        return 1
    fi
    
    # Check if Jaeger is running and accessible
    if ! curl -s "http://localhost:16686/"; then
        log_message "ERROR: Jaeger is not running or accessible."
        return 1
    fi
    
    log_message "All monitoring components are running and accessible."
    return 0
}

# Function to display access information
show_access_information() {
    local host_ip
    host_ip=$(hostname -I | awk '{print $1}')
    
    log_message "Access Information:"
    log_message "================================================================================="
    log_message "Prometheus UI:         http://${host_ip}:9090"
    log_message "Grafana UI:            http://${host_ip}:3000          (admin/FreightPriceAgent2023)"
    log_message "AlertManager UI:       http://${host_ip}:9093"
    log_message "Kibana UI:             http://${host_ip}:5601"
    log_message "Jaeger UI:             http://${host_ip}:16686"
    log_message "Elasticsearch API:     http://${host_ip}:9200"
    log_message "Node Exporter Metrics: http://${host_ip}:9100/metrics"
    log_message "================================================================================="
    log_message "To view logs: docker-compose logs -f [service_name]"
    log_message "To stop monitoring stack: cd ${MONITORING_DIR} && docker-compose down"
    log_message "To restart monitoring stack: cd ${MONITORING_DIR} && docker-compose restart"
    log_message "Example configurations for application monitoring: ${MONITORING_DIR}/examples/"
    log_message "================================================================================="
}

# Function to clean up resources in case of error
cleanup_on_error() {
    log_message "Error occurred. Cleaning up resources..."
    
    cd "$MONITORING_DIR" || { log_message "ERROR: Could not change directory to $MONITORING_DIR"; return; }
    
    # Stop and remove containers
    docker-compose down
    
    # Ask if the user wants to remove the created directories
    read -rp "Do you want to remove all created directories? [y/N] " remove_dirs
    if [[ "$remove_dirs" =~ ^[Yy]$ ]]; then
        log_message "Removing directories..."
        cd / || return
        rm -rf "$MONITORING_DIR"
        log_message "Directories removed."
    fi
    
    log_message "Cleanup complete."
}

# Main function
main() {
    log_message "Starting Freight Price Movement Agent Monitoring Setup"
    
    # Parse command line arguments
    local skip_prereq=false
    local skip_verify=false
    
    while (( "$#" )); do
        case "$1" in
            --skip-prereq)
                skip_prereq=true
                shift
                ;;
            --skip-verify)
                skip_verify=true
                shift
                ;;
            --help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --skip-prereq   Skip prerequisites check"
                echo "  --skip-verify   Skip verification step"
                echo "  --help          Show this help message"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use --help to see available options"
                exit 1
                ;;
        esac
    done
    
    # Check prerequisites
    if [[ "$skip_prereq" == "false" ]]; then
        if ! check_prerequisites; then
            log_message "Prerequisites check failed. Exiting."
            exit 1
        fi
    else
        log_message "Skipping prerequisites check as requested."
    fi
    
    # Create directories
    if ! create_directories; then
        log_message "Failed to create directories. Exiting."
        exit 1
    fi
    
    # Set up monitoring components
    if ! setup_prometheus; then
        log_message "Failed to set up Prometheus. Exiting."
        cleanup_on_error
        exit 1
    fi
    
    if ! setup_grafana; then
        log_message "Failed to set up Grafana. Exiting."
        cleanup_on_error
        exit 1
    fi
    
    if ! setup_alertmanager; then
        log_message "Failed to set up AlertManager. Exiting."
        cleanup_on_error
        exit 1
    fi
    
    if ! setup_elasticsearch; then
        log_message "Failed to set up Elasticsearch. Exiting."
        cleanup_on_error
        exit 1
    fi
    
    if ! setup_kibana; then
        log_message "Failed to set up Kibana. Exiting."
        cleanup_on_error
        exit 1
    fi
    
    if ! setup_filebeat; then
        log_message "Failed to set up Filebeat. Exiting."
        cleanup_on_error
        exit 1
    fi
    
    if ! setup_jaeger; then
        log_message "Failed to set up Jaeger. Exiting."
        cleanup_on_error
        exit 1
    fi
    
    if ! setup_node_exporter; then
        log_message "Failed to set up Node Exporter. Exiting."
        cleanup_on_error
        exit 1
    fi
    
    # Generate Docker Compose file
    if ! generate_docker_compose; then
        log_message "Failed to generate Docker Compose file. Exiting."
        cleanup_on_error
        exit 1
    fi
    
    # Start monitoring stack
    if ! start_monitoring_stack; then
        log_message "Failed to start monitoring stack. Exiting."
        cleanup_on_error
        exit 1
    fi
    
    # Configure application monitoring
    if ! configure_application_monitoring; then
        log_message "Warning: Failed to configure application monitoring."
        # Continue anyway, as this is not critical
    fi
    
    # Verify monitoring setup
    if [[ "$skip_verify" == "false" ]]; then
        if ! verify_monitoring_setup; then
            log_message "Monitoring setup verification failed. Please check the logs and try again."
            exit 1
        fi
    else
        log_message "Skipping verification step as requested."
    fi
    
    # Show access information
    show_access_information
    
    log_message "Freight Price Movement Agent Monitoring Setup completed successfully!"
    return 0
}

# Execute main function
main "$@"