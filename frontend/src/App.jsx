import React from "react";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Home from "./pages/Home";
import Pipeline from "./pages/Pipeline";

const navStyle = {
  display: "flex",
  gap: "2rem",
  padding: "1rem 2rem",
  background: "#1a1d27",
  borderBottom: "1px solid #2d2f3e",
  alignItems: "center",
};

const logoStyle = {
  fontSize: "1.2rem",
  fontWeight: "700",
  color: "#7c6af7",
  marginRight: "auto",
  letterSpacing: "0.5px",
};

const linkStyle = ({ isActive }) => ({
  color: isActive ? "#7c6af7" : "#a0a0b0",
  textDecoration: "none",
  fontWeight: isActive ? "600" : "400",
  fontSize: "0.95rem",
  padding: "0.4rem 1rem",
  borderRadius: "6px",
  background: isActive ? "#2d2843" : "transparent",
  transition: "all 0.2s",
});

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: "100vh", background: "#0f1117" }}>
        <nav style={navStyle}>
          <span style={logoStyle}>⚡ DemandAI</span>
          <NavLink to="/" style={linkStyle} end>
            Forecast
          </NavLink>
          <NavLink to="/pipeline" style={linkStyle}>
            Pipeline
          </NavLink>
        </nav>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/pipeline" element={<Pipeline />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}