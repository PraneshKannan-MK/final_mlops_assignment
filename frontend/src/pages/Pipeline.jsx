import React, { useEffect, useState } from "react";
import PipelineVisualizer from "../components/PipelineVisualizer";

const API = "http://127.0.0.1:8000";

const pageStyle = {
  padding: "2rem",
  maxWidth: "1200px",
  margin: "0 auto",
};

const cardStyle = {
  background: "#1a1d27",
  border: "1px solid #2d2f3e",
  borderRadius: "12px",
  padding: "1.5rem",
  marginBottom: "1.5rem",
};

const headingStyle = {
  fontSize: "1.1rem",
  fontWeight: "600",
  color: "#c0b8f8",
  marginBottom: "1.2rem",
  borderBottom: "1px solid #2d2f3e",
  paddingBottom: "0.6rem",
};

const badgeStyle = (status) => ({
  display: "inline-block",
  padding: "0.25rem 0.75rem",
  borderRadius: "20px",
  fontSize: "0.78rem",
  fontWeight: "600",
  background:
    status === "success" ? "#1a3a2a" :
    status === "failed" ? "#3a1a1a" :
    status === "running" ? "#1a2a3a" : "#2a2a2a",
  color:
    status === "success" ? "#4ade80" :
    status === "failed" ? "#f87171" :
    status === "running" ? "#60a5fa" : "#888",
  border: `1px solid ${
    status === "success" ? "#4ade80" :
    status === "failed" ? "#f87171" :
    status === "running" ? "#60a5fa" : "#444"
  }`,
});

export default function Pipeline() {
  const [status, setStatus] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStatus = async () => {
    try {
      const [pipeRes, healthRes] = await Promise.all([
        fetch(`${API}/api/v1/pipeline/status`),
        fetch(`${API}/health`),
      ]);
      const pipeData = await pipeRes.json();
      const healthData = await healthRes.json();
      setStatus(pipeData);
      setHealth(healthData);
    } catch (err) {
      console.error("Failed to fetch pipeline status:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={pageStyle}>
      <h1 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#fff", marginBottom: "1.5rem" }}>
        ML Pipeline Monitor
      </h1>

      {/* System Health */}
      <div style={cardStyle}>
        <div style={headingStyle}>System Health</div>
        {health ? (
          <div style={{ display: "flex", gap: "2rem", flexWrap: "wrap" }}>
            <div>
              <div style={{ fontSize: "0.75rem", color: "#888", marginBottom: "0.2rem" }}>API STATUS</div>
              <span style={badgeStyle("success")}>● {health.status?.toUpperCase()}</span>
            </div>
            <div>
              <div style={{ fontSize: "0.75rem", color: "#888", marginBottom: "0.2rem" }}>UPTIME</div>
              <div style={{ fontWeight: "600", color: "#4ade80" }}>
                {Math.floor(health.uptime_seconds / 3600)}h {Math.floor((health.uptime_seconds % 3600) / 60)}m
              </div>
            </div>
            <div>
              <div style={{ fontSize: "0.75rem", color: "#888", marginBottom: "0.2rem" }}>LAST CHECKED</div>
              <div style={{ fontWeight: "600" }}>{new Date().toLocaleTimeString()}</div>
            </div>
          </div>
        ) : (
          <div style={{ color: "#888" }}>Loading...</div>
        )}
      </div>

      {/* Pipeline Visualizer */}
      <div style={cardStyle}>
        <div style={headingStyle}>Pipeline Stages</div>
        <PipelineVisualizer />
      </div>

      {/* Pipeline Status Table */}
      {status && (
        <div style={cardStyle}>
          <div style={headingStyle}>Pipeline Run Status</div>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid #2d2f3e" }}>
                {["Pipeline", "Status", "Last Run", "Rows Processed"].map((h) => (
                  <th key={h} style={{
                    textAlign: "left", padding: "0.6rem 1rem",
                    fontSize: "0.75rem", color: "#888",
                    textTransform: "uppercase", letterSpacing: "0.5px"
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {status.pipelines.map((p, i) => (
                <tr key={i} style={{ borderBottom: "1px solid #1a1d27" }}>
                  <td style={{ padding: "0.8rem 1rem", fontWeight: "600" }}>
                    {p.pipeline_name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                  </td>
                  <td style={{ padding: "0.8rem 1rem" }}>
                    <span style={badgeStyle(p.last_run_status)}>
                      {p.last_run_status}
                    </span>
                  </td>
                  <td style={{ padding: "0.8rem 1rem", color: "#888", fontSize: "0.85rem" }}>
                    {p.last_run_time
                      ? new Date(p.last_run_time).toLocaleString()
                      : "Never"}
                  </td>
                  <td style={{ padding: "0.8rem 1rem", color: "#888" }}>
                    {p.rows_processed?.toLocaleString() || "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Drift Alert */}
          {status.drift_detected && (
            <div style={{
              marginTop: "1rem",
              padding: "0.8rem 1rem",
              background: "#3a2a1a",
              border: "1px solid #f59e0b",
              borderRadius: "8px",
              color: "#f59e0b",
              fontSize: "0.9rem",
            }}>
              ⚠️ Data drift detected in: {status.drift_features.join(", ")}
            </div>
          )}
        </div>
      )}
    </div>
  );
}