resource "google_monitoring_alert_policy" "draft_policy" {
  project      = var.project_id
  display_name = "Draft Policy"
  combiner     = "OR"
  conditions {
    display_name = "Draft Condition"
    condition_prometheus_query_language {
      query = "sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count[5y])) / sum(rate(aiplatform_googleapis_com:reasoning_engine_request_count[5m]"
    }
  }
}
