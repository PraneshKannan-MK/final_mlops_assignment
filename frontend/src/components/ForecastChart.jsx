import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

const tooltipStyle = {
  background: "#1a1d27",
  border: "1px solid #2d2f3e",
  borderRadius: "8px",
  color: "#e0e0e0",
  fontSize: "0.85rem",
};

export default function ForecastChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div style={{ color: "#888", textAlign: "center", padding: "2rem" }}>
        No forecast data yet. Make a prediction to see the chart.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2d2f3e" />
        <XAxis
          dataKey="date"
          stroke="#555"
          tick={{ fill: "#888", fontSize: 12 }}
        />
        <YAxis
          stroke="#555"
          tick={{ fill: "#888", fontSize: 12 }}
          label={{
            value: "Units",
            angle: -90,
            position: "insideLeft",
            fill: "#888",
            fontSize: 12,
          }}
        />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend
          wrapperStyle={{ color: "#888", fontSize: "0.85rem" }}
        />
        <Line
          type="monotone"
          dataKey="demand"
          stroke="#7c6af7"
          strokeWidth={2.5}
          dot={{ fill: "#7c6af7", r: 4 }}
          activeDot={{ r: 6 }}
          name="Predicted Demand"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}