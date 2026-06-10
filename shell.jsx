import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import {
  LayoutDashboard,
  Database,
  BarChart3,
  TrendingDown,
  Brain,
  Search,
  FileText,
  Settings,
  LogOut,
  Cpu
} from "lucide-react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { LayoutDashboard, Database, BarChart3, TrendingDown, Brain, Search, FileText, Settings, LogOut, Cpu } from "lucide-react";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, testid: "nav-dashboard" },
  { to: "/dataset", label: "Dataset", icon: Database, testid: "nav-dataset" },
  { to: "/analytics", label: "Customer Analytics", icon: BarChart3, testid: "nav-analytics" },
  { to: "/churn-analysis", label: "Churn Analysis", icon: TrendingDown, testid: "nav-churn-analysis" },
  { to: "/predict", label: "Churn Prediction", icon: Brain, testid: "nav-predict" },
  { to: "/risk", label: "Risk Monitoring", icon: Search, testid: "nav-risk" },
  { to: "/reports", label: "Reports", icon: FileText, testid: "nav-reports" },
  { to: "/admin", label: "Admin Panel", icon: Settings, testid: "nav-admin" },
];

export default function Shell({ children }) {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  return (
    <div className="min-h-screen flex bg-[#050505] text-white">
      <aside className="w-64 border-r border-white/10 flex flex-col sticky top-0 h-screen">
        <div className="px-6 py-6 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-white text-black flex items-center justify-center font-black"><Cpu size={18} /></div>
            <div>
              <div className="text-sm font-black tracking-tighter uppercase">RETAIN.AI</div>
              <div className="text-[10px] uppercase tracking-[0.2em] text-[#555]">Churn Control</div>
            </div>
          </div>
        </div>
        <nav className="flex-1 py-4">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === "/"}
              data-testid={l.testid}
              className={({ isActive }) =>
                `flex items-center gap-3 px-6 py-3 text-xs uppercase tracking-[0.18em] font-bold border-l-2 transition-colors ${
                  isActive ? "border-white bg-[#101010] text-white" : "border-transparent text-[#8F8F94] hover:bg-[#0a0a0a] hover:text-white"
                }`
              }
            >
              <l.icon size={14} />
              <span>{l.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="px-6 py-4 border-t border-white/10">
          <div className="text-[10px] uppercase tracking-[0.2em] text-[#555]">Signed in</div>
          <div className="text-sm font-mono truncate">{user?.email}</div>
          <button
            data-testid="logout-btn"
            onClick={() => { logout(); nav("/login"); }}
            className="mt-3 w-full flex items-center justify-center gap-2 border border-white/20 px-3 py-2 text-xs uppercase tracking-widest hover:border-white hover:bg-[#1A1A1A]"
          >
            <LogOut size={12} /> Logout
          </button>
        </div>
      </aside>
      <main className="flex-1 min-w-0">{children}</main>
    </div>
  );
}