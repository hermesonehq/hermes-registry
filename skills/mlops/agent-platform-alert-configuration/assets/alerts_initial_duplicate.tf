resource "google_monitoring_alert_policy" "agent_error_rate_fast_burn" {
  project      = var.project_id
  display_name = "Agent Error Rate Fast Burn"
  combiner     = "OR"
  conditions {
    display_name = "Error Rate Fast Burn"
    condition_prometheus_query_language {
      query    = <<-EOT
        (
          sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count{response_code!~"2..", reasoning_engine_id="12345"}[5m]))
          /
          sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count{reasoning_engine_id="12345"}[5m]))
          > (1 - var.slo_target) * 3
        )
      EOT
      duration = "300s"
    }
  }
}
