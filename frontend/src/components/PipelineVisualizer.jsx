import React from "react";

const stages = [
  {
    id: 1,
    name: "Data Ingestion",
    tool: "Airflow DAG",
    description: "Load raw CSV, validate schema, compute baseline stats",
    color: "#3b82f6",
    icon: "📥",
  },
  {
    id: 2,
    name: "Preprocessing",
    tool: "PySpark / Pandas",
    description: "Handle missing values, outlier capping, type casting",
    color: "#8b5cf6",
    icon: "🔧",
  },
  {
    id: 3,
    name: "Feature Engineering",
    tool: "Custom Pipeline",
    description: "Temporal, price, lag, rolling, Fourier features",
    color: "#ec4899",
    icon: "⚙️",
  },
  {
    id: 4,
    name: "Model Training",
    tool: "XGBoost + MLflow",
    description: "TimeSeriesSplit CV, hyperparameter tracking, model registry",
    color: "#f59e0b",
    icon: "🧠",
  },
  {
    id: 5,
    name: "Model Serving",
    tool: "FastAPI + MLflow",
    description: "REST API inference, /predict endpoint, health checks",
    color: "#10b981",
    icon: "🚀",
  },
  {
    id: 6,
    name: "Monitoring",
    tool: "Prometheus + Grafana",
    description: "Latency, drift detection, retraining triggers",
    color: "#ef4444",
    icon: "📊",
  },
];

const stageBoxStyle = (color) => ({
  background: "#0f1117",
  border: `1px solid ${color}44`,
  borderLeft: `4px solid ${color}`,
  borderRadius: "10px",
  padding: "1rem 1.2rem",
  flex: "1",
  minWidth: "160px",
  position: "relative",
  transition: "transform 0.2s",
});

const arrowStyle = {
  color: "#444",
  fontSize: "1.4rem",
  display: "flex",
  alignItems: "center",
  flexShrink: 0,
};

export default function PipelineVisualizer() {
  return (
    <div>
      {/* Horizontal pipeline flow */}
      <div style={{
        display: "flex",
        alignItems: "stretch",
        gap: "0.5rem",
        flexWrap: "wrap",
        marginBottom: "1.5rem",
      }}>
        {stages.map((stage, idx) => (
          <React.Fragment key={stage.id}>
            <div style={stageBoxStyle(stage.color)}>
              <div style={{ fontSize: "1.4rem", marginBottom: "0.4rem" }}>{stage.icon}</div>
              <div style={{ fontSize: "0.85rem", fontWeight: "700", color: "#e0e0e0", marginBottom: "0.2rem" }}>
                {stage.name}
              </div>
              <div style={{ fontSize: "0.72rem", color: stage.color, marginBottom: "0.4rem", fontWeight: "600" }}>
                {stage.tool}
              </div>
              <div style={{ fontSize: "0.72rem", color: "#666", lineHeight: "1.4" }}>
                {stage.description}
              </div>
            </div>
            {idx < stages.length - 1 && (
              <div style={arrowStyle}>→</div>
            )}
          </React.Fragment>
        ))}
      </div>

      {/* DVC Pipeline */}
      <div style={{
        background: "#0f1117",
        border: "1px solid #2d2f3e",
        borderRadius: "10px",
        padding: "1rem 1.2rem",
        marginBottom: "1rem",
      }}>
        <div style={{ fontSize: "0.78rem", color: "#888", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: "0.6rem" }}>
          DVC Pipeline DAG
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
          {["ingest", "preprocess", "featurize", "train"].map((stage, idx, arr) => (
            <React.Fragment key={stage}>
              <span style={{
                padding: "0.3rem 0.8rem",
                background: "#1a1d27",
                border: "1px solid #3b82f6",
                borderRadius: "20px",
                fontSize: "0.8rem",
                color: "#3b82f6",
                fontFamily: "monospace",
              }}>
                {stage}
              </span>
              {idx < arr.length - 1 && (
                <span style={{ color: "#3b82f6", fontSize: "0.9rem" }}>→</span>
              )}
            </React.Fragment>
          ))}
          <span style={{ marginLeft: "1rem", fontSize: "0.75rem", color: "#555" }}>
            Run: <code style={{ color: "#888" }}>dvc repro</code>
          </span>
        </div>
      </div>

      {/* Tool Stack */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
        gap: "0.6rem",
      }}>
        {[
          { name: "MLflow", desc: "Experiment tracking", color: "#3b82f6" },
          { name: "Airflow", desc: "DAG orchestration", color: "#f59e0b" },
          { name: "DVC", desc: "Data versioning", color: "#8b5cf6" },
          { name: "Prometheus", desc: "Metrics scraping", color: "#ef4444" },
          { name: "Grafana", desc: "NRT visualization", color: "#f97316" },
          { name: "Docker", desc: "Containerization", color: "#06b6d4" },
        ].map((tool) => (
          <div key={tool.name} style={{
            background: "#0f1117",
            border: `1px solid ${tool.color}33`,
            borderRadius: "8px",
            padding: "0.6rem 0.8rem",
            display: "flex",
            flexDirection: "column",
            gap: "0.2rem",
          }}>
            <div style={{ fontSize: "0.85rem", fontWeight: "600", color: tool.color }}>
              {tool.name}
            </div>
            <div style={{ fontSize: "0.72rem", color: "#666" }}>{tool.desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
}