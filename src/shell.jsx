import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "./auth";
import LanguageSwitcher from "./LanguageSwitcher";
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

export default function Shell({ children }) {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const nav = useNavigate();

  const links = [
    { to: "/", label: t("nav.dashboard"), icon: LayoutDashboard, testid: "nav-dashboard" },
    { to: "/dataset", label: t("nav.dataset"), icon: Database, testid: "nav-dataset" },
    { to: "/analytics", label: t("nav.analytics"), icon: BarChart3, testid: "nav-analytics" },
    { to: "/churn-analysis", label: t("nav.churnAnalysis"), icon: TrendingDown, testid: "nav-churn-analysis" },
    { to: "/predict", label: t("nav.prediction"), icon: Brain, testid: "nav-predict" },
    { to: "/risk", label: t("nav.risk"), icon: Search, testid: "nav-risk" },
    { to: "/reports", label: t("nav.reports"), icon: FileText, testid: "nav-reports" },
    { to: "/admin", label: t("nav.admin"), icon: Settings, testid: "nav-admin" },
  ];

  return (
    <div className="min-h-screen flex bg-[#050505] text-white">
      <aside className="w-64 border-r border-white/10 flex flex-col sticky top-0 h-screen">
        <div className="px-6 py-6 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-white text-black flex items-center justify-center font-black"><Cpu size={18} /></div>
            <div>
              <div className="text-sm font-black tracking-tighter uppercase">{t("app.title")}</div>
              <div className="text-[10px] uppercase tracking-[0.2em] text-[#555]">{t("app.subtitle")}</div>
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
        <div className="px-6 py-4 border-t border-white/10 space-y-2">
          <LanguageSwitcher />
          <div className="text-[10px] uppercase tracking-[0.2em] text-[#555]">{t("app.signedIn")}</div>
          <div className="text-sm font-mono truncate">{user?.email}</div>
          <button
            data-testid="logout-btn"
            onClick={() => { logout(); nav("/login"); }}
            className="mt-3 w-full flex items-center justify-center gap-2 border border-white/20 px-3 py-2 text-xs uppercase tracking-widest hover:border-white hover:bg-[#1A1A1A]"
          >
            <LogOut size={12} /> {t("app.logout")}
          </button>
        </div>
      </aside>
      <main className="flex-1 min-w-0">{children}</main>
    </div>
  );
}