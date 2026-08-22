import { HashRouter, NavLink, Navigate, Route, Routes } from "react-router-dom";
import { ComparisonPage } from "./pages/ComparisonPage";
import { FullSimulatorPage } from "./pages/FullSimulatorPage";
import { PlanPage } from "./pages/PlanPage";

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
            <NavLink to="/plan-g">Plan G</NavLink>
            <NavLink to="/plan-g-hd">Plan G HD</NavLink>
            <NavLink to="/plan-n">Plan N</NavLink>
            <NavLink to="/comparison">Compare plans</NavLink>
            <NavLink to="/full">Full simulator</NavLink>
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
          </nav>
        </header>
        <Routes>
          <Route path="/full" element={<FullSimulatorPage />} />
          <Route path="/plan-g" element={<PlanPage key="plan-g" planId="plan-g" />} />
          <Route path="/plan-g-hd" element={<PlanPage key="plan-hdg" planId="plan-hdg" />} />
          <Route path="/plan-n" element={<PlanPage key="plan-n" planId="plan-n" />} />
          <Route path="/single-plan" element={<Navigate to="/plan-g" replace />} />
          <Route path="/comparison" element={<ComparisonPage />} />
          <Route path="*" element={<Navigate to="/full" replace />} />
        </Routes>
        <footer className="site-footer">
          <a className="discord-button" href="https://discord.gg/F5ZWXpGb3" target="_blank" rel="noopener noreferrer">Questions / Comments / Suggestions? Let's talk on Discord</a>
          <div>This simulator is for educational and planning purposes only. This site uses Google Analytics to collect usage information. No other information is collected</div>
          <div className="copyright-statement">© {new Date().getFullYear()} VAST SCIENTIFIC.</div>
        </footer>
      </div>
    </HashRouter>
  );
}
