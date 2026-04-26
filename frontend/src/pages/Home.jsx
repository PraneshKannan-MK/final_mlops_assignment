import React, { useState } from "react";
import ForecastChart from "../components/ForecastChart";
import MetricsDashboard from "../components/MetricsDashboard";

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

const gridStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
  gap: "1rem",
  marginBottom: "1rem",
};

const labelStyle = {
  display: "block",
  fontSize: "0.78rem",
  color: "#888",
  marginBottom: "0.3rem",
  textTransform: "uppercase",
  letterSpacing: "0.5px",
};

const inputStyle = {
  width: "100%",
  padding: "0.6rem 0.8rem",
  background: "#0f1117",
  border: "1px solid #2d2f3e",
  borderRadius: "8px",
  color: "#e0e0e0",
  fontSize: "0.9rem",
  outline: "none",
};

const btnStyle = {
  padding: "0.7rem 2rem",
  background: "#7c6af7",
  color: "#fff",
  border: "none",
  borderRadius: "8px",
  fontSize: "0.95rem",
  fontWeight: "600",
  cursor: "pointer",
  marginTop: "0.5rem",
};

const resultBoxStyle = {
  background: "#0f1117",
  border: "1px solid #7c6af7",
  borderRadius: "10px",
  padding: "1.2rem 1.5rem",
  marginTop: "1rem",
  display: "flex",
  alignItems: "center",
  gap: "2rem",
  flexWrap: "wrap",
};

export default function Home() {
  const [form, setForm] = useState({
    product_id: "P001",
    store_id: "S001",
    forecast_date: "2024-08-20",
    price: 90,
    price_lag_7: 92,
    sales_lag_1: 60,
    sales_lag_7: 58,
    sales_rolling_mean_7: 59,
    discount: 0.1,
    inventory_level: 1,
    competitor_price: 88,
    promotion: 1,
    weather: "sunny",
    seasonality: 2,
    epidemic: 0,
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const payload = {
        ...form,
        price: parseFloat(form.price),
        price_lag_7: parseFloat(form.price_lag_7),
        sales_lag_1: parseFloat(form.sales_lag_1),
        sales_lag_7: parseFloat(form.sales_lag_7),
        sales_rolling_mean_7: parseFloat(form.sales_rolling_mean_7),
        discount: parseFloat(form.discount),
        inventory_level: parseInt(form.inventory_level),
        competitor_price: parseFloat(form.competitor_price),
        promotion: parseInt(form.promotion),
        seasonality: parseInt(form.seasonality),
        epidemic: parseInt(form.epidemic),
      };
      const res = await fetch(`${API}/api/v1/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Prediction failed");
      setResult(data);
      setHistory((prev) => [
        ...prev.slice(-9),
        {
          date: data.forecast_date,
          demand: parseFloat(data.predicted_demand.toFixed(2)),
          product: data.product_id,
          store: data.store_id,
        },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fields1 = [
    { name: "product_id", label: "Product ID", type: "text" },
    { name: "store_id", label: "Store ID", type: "text" },
    { name: "forecast_date", label: "Forecast Date", type: "date" },
    { name: "price", label: "Price (₹)", type: "number" },
    { name: "competitor_price", label: "Competitor Price (₹)", type: "number" },
    { name: "discount", label: "Discount (0-1)", type: "number" },
  ];

  const fields2 = [
    { name: "price_lag_7", label: "Price 7 Days Ago", type: "number" },
    { name: "sales_lag_1", label: "Sales Yesterday", type: "number" },
    { name: "sales_lag_7", label: "Sales 7 Days Ago", type: "number" },
    { name: "sales_rolling_mean_7", label: "7-Day Avg Sales", type: "number" },
    { name: "inventory_level", label: "Inventory Level", type: "number" },
    { name: "promotion", label: "Promotion (0/1)", type: "number" },
  ];

  const fields3 = [
    { name: "seasonality", label: "Seasonality Index", type: "number" },
    { name: "epidemic", label: "Epidemic Flag (0/1)", type: "number" },
  ];

  return (
    <div style={pageStyle}>
      <h1 style={{ fontSize: "1.5rem", fontWeight: "700", color: "#fff", marginBottom: "1.5rem" }}>
        Demand Forecast
      </h1>

      {/* Input Form */}
      <div style={cardStyle}>
        <div style={headingStyle}>Product & Pricing</div>
        <div style={gridStyle}>
          {fields1.map((f) => (
            <div key={f.name}>
              <label style={labelStyle}>{f.label}</label>
              <input
                style={inputStyle}
                type={f.type}
                name={f.name}
                value={form[f.name]}
                onChange={handleChange}
              />
            </div>
          ))}
        </div>

        <div style={headingStyle}>Historical Context</div>
        <div style={gridStyle}>
          {fields2.map((f) => (
            <div key={f.name}>
              <label style={labelStyle}>{f.label}</label>
              <input
                style={inputStyle}
                type={f.type}
                name={f.name}
                value={form[f.name]}
                onChange={handleChange}
              />
            </div>
          ))}
        </div>

        <div style={headingStyle}>External Factors</div>
        <div style={gridStyle}>
          {fields3.map((f) => (
            <div key={f.name}>
              <label style={labelStyle}>{f.label}</label>
              <input
                style={inputStyle}
                type={f.type}
                name={f.name}
                value={form[f.name]}
                onChange={handleChange}
              />
            </div>
          ))}
          <div>
            <label style={labelStyle}>Weather</label>
            <select
              style={inputStyle}
              name="weather"
              value={form.weather}
              onChange={handleChange}
            >
              <option value="sunny">Sunny</option>
              <option value="rainy">Rainy</option>
              <option value="cloudy">Cloudy</option>
            </select>
          </div>
        </div>

        <button
          style={{ ...btnStyle, opacity: loading ? 0.7 : 1 }}
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Predicting..." : "Get Forecast"}
        </button>

        {error && (
          <div style={{ color: "#f87171", marginTop: "1rem", fontSize: "0.9rem" }}>
            ❌ {error}
          </div>
        )}

        {result && (
          <div style={resultBoxStyle}>
            <div>
              <div style={{ fontSize: "0.75rem", color: "#888", marginBottom: "0.2rem" }}>
                PREDICTED DEMAND
              </div>
              <div style={{ fontSize: "2.2rem", fontWeight: "700", color: "#7c6af7" }}>
                {result.predicted_demand.toFixed(0)}
                <span style={{ fontSize: "1rem", color: "#888", marginLeft: "0.4rem" }}>units</span>
              </div>
            </div>
            <div>
              <div style={{ fontSize: "0.75rem", color: "#888" }}>Product</div>
              <div style={{ fontWeight: "600" }}>{result.product_id}</div>
            </div>
            <div>
              <div style={{ fontSize: "0.75rem", color: "#888" }}>Store</div>
              <div style={{ fontWeight: "600" }}>{result.store_id}</div>
            </div>
            <div>
              <div style={{ fontSize: "0.75rem", color: "#888" }}>Date</div>
              <div style={{ fontWeight: "600" }}>{result.forecast_date}</div>
            </div>
            <div>
              <div style={{ fontSize: "0.75rem", color: "#888" }}>Model Version</div>
              <div style={{ fontWeight: "600" }}>v{result.model_version}</div>
            </div>
            <div>
              <div style={{ fontSize: "0.75rem", color: "#888" }}>Latency</div>
              <div style={{ fontWeight: "600" }}>{result.inference_latency_ms.toFixed(1)}ms</div>
            </div>
          </div>
        )}
      </div>

      {/* Forecast History Chart */}
      {history.length > 0 && (
        <div style={cardStyle}>
          <div style={headingStyle}>Forecast History</div>
          <ForecastChart data={history} />
        </div>
      )}

      {/* Live Metrics */}
      <div style={cardStyle}>
        <div style={headingStyle}>Live System Metrics</div>
        <MetricsDashboard />
      </div>
    </div>
  );
}