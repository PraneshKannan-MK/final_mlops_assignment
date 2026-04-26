import React, { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

const statCardStyle = {
  background: "#0f1117",
  border: "1px solid #2d2f3e",
  borderRadius: "10px",
  padding: "1rem 1.2rem",
  minWidth: "160px",
  flex: "1",
};

const statLabelStyle = {
  fontSize: "0.72rem",
  color: "#666",
  textTransform: "uppercase",
  letterSpacing: "0.5px",
  marginBottom: "0.4rem",
};

const statValueStyle = {
  fontSize: "1.8rem",
  fontWeight: "700",
  color: "#7c6af7",
};

function parseMetric(raw, metricName) {
  const lines = raw.split("\n");
  for (const line of lines) {
    if (line.startsWith(metricName) && !line.startsWith("# ")) {
      const parts = line.split(" ");
      const val = parseFloat(parts[parts.length - 1]);
      return isNaN(val) ? null : val;
    }
  }
  return null;
}

function parseMetricWithLabel(raw, metricName, labelFilter) {
  const lines = raw.split("\n");
  for (const line of lines) {
    if (line.startsWith(metricName) && !line.startsWith("# ")) {
      if (labelFilter && !line.includes(labelFilter)) continue;
      const parts = line.split(" ");
      const val = parseFloat(parts[parts.length - 1]);
      return isNaN(val) ? null : val;
    }
  }
  return null;
}

export default function MetricsDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState(null);

  const fetchMetrics = async () => {
    try {
      const res = await fetch(`${API}/metrics`);
      const raw = await res.text();

      const success = parseMetricWithLabel(raw, "demand_forecast_requests_total", 'status="success"') || 0;
      const errors = parseMetricWithLabel(raw, "demand_forecast_requests_total", 'status="error"') || 0;
      const latencySum = parseMetricWithLabel(raw, "demand_forecast_request_latency_seconds_sum", null) || 0;
      const latencyCount = parseMetricWithLabel(raw, "demand_forecast_request_latency_seconds_count", null) || 1;
      const predValue = parseMetric(raw, "demand_forecast_prediction_value") || 0;
      const mae = parseMetric(raw, "demand_forecast_model_mae") || 0;

      setMetrics({
        success,
        errors,
        total: success + errors,
        avgLatencyMs: latencyCount > 0 ? ((latencySum / latencyCount) * 1000).toFixed(1) : "0.0",
        predValue: predValue.toFixed(1),
        errorRate: (success + errors) > 0
          ? ((errors / (success + errors)) * 100).toFixed(1)
          : "0.0",
        mae: mae.toFixed(2),
      });
      setLastUpdated(new Date().toLocaleTimeString());
      setError(null);
    } catch (err) {
      setError("Cannot reach /metrics endpoint");
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000);
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <div style={{ color: "#f87171", fontSize: "0.9rem" }}>⚠️ {error}</div>
    );
  }

  if (!metrics) {
    return <div style={{ color: "#888" }}>Loading metrics...</div>;
  }

  const stats = [
    { label: "Total Requests", value: metrics.total, color: "#7c6af7" },
    { label: "Successful", value: metrics.success, color: "#4ade80" },
    { label: "Errors", value: metrics.errors, color: "#f87171" },
    { label: "Error Rate", value: `${metrics.errorRate}%`, color: metrics.errorRate > 5 ? "#f87171" : "#4ade80" },
    { label: "Avg Latency", value: `${metrics.avgLatencyMs}ms`, color: "#60a5fa" },
    { label: "Last Prediction", value: `${metrics.predValue} units`, color: "#f59e0b" },
  ];

  return (
    <div>
      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "0.8rem" }}>
        {stats.map((s) => (
          <div key={s.label} style={statCardStyle}>
            <div style={statLabelStyle}>{s.label}</div>
            <div style={{ ...statValueStyle, color: s.color, fontSize: "1.5rem" }}>
              {s.value}
            </div>
          </div>
        ))}
      </div>
      <div style={{ fontSize: "0.75rem", color: "#555", marginTop: "0.4rem" }}>
        Auto-refreshes every 10s · Last updated: {lastUpdated}
      </div>
    </div>
  );
}