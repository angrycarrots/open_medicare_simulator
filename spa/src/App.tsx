import { HashRouter, NavLink, Navigate, Route, Routes } from "react-router-dom";
import { ComparisonPage } from "./pages/ComparisonPage";
import { FullSimulatorPage } from "./pages/FullSimulatorPage";
import { SinglePlanPage } from "./pages/SinglePlanPage";

export default function App() {
  return (
    <HashRouter>
      <div className="app-shell">
        <header className="site-header">
          <NavLink className="brand" to="/full" aria-label="Medicare Cost Simulator home">
            <span className="brand-mark" aria-hidden="true">M</span>
            <span>Medicare Cost Simulator</span>
          </NavLink>
          <nav aria-label="Primary navigation">
            <NavLink to="/full">Full simulator</NavLink>
            <NavLink to="/single-plan">Single plan</NavLink>
            <div className="nav-support">
              <NavLink to="/comparison">Compare plans</NavLink>
              <a
                className="coffee-link"
                href="https://ko-fi.com/A0A71KJNT6"
                target="_blank"
                rel="noopener noreferrer"
              >
                <img
                  height="36"
                  src="https://storage.ko-fi.com/cdn/kofi6.png?v=6"
                  alt="Buy Me a Coffee at ko-fi.com"
                />
              </a>
            </div>
          </nav>
        </header>
        <Routes>
          <Route path="/full" element={<FullSimulatorPage />} />
          <Route path="/single-plan" element={<SinglePlanPage />} />
          <Route path="/comparison" element={<ComparisonPage />} />
          <Route path="*" element={<Navigate to="/full" replace />} />
        </Routes>
        <footer className="site-footer">This simulator is for educational and planning purposes only. Actual Medicare costs vary by location, coverage, health status, and other factors.</footer>
      </div>
    </HashRouter>
  );
}
