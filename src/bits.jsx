import React from "react";

export const PageHeader = ({ eyebrow, title, subtitle, right }) => (
  <div className="px-10 py-8 border-b border-white/10 flex items-end justify-between gap-6">
    <div>
      <div className="text-[10px] uppercase tracking-[0.3em] text-[#555]">{eyebrow}</div>
      <h1 className="mt-2 text-4xl sm:text-5xl font-black tracking-tighter uppercase">{title}</h1>
      {subtitle && <p className="mt-3 text-sm text-[#8F8F94] max-w-2xl">{subtitle}</p>}
    </div>
    {right}
  </div>
);

export const Cell = ({ children, className = "", testid }) => (
  <div data-testid={testid} className={`border border-white/10 bg-[#0A0A0A] p-6 ${className}`}>{children}</div>
);

export const Stat = ({ label, value, accent = "text-white", sub, testid }) => (
  <div data-testid={testid} className="border border-white/10 bg-[#0A0A0A] p-6">
    <div className="text-[10px] uppercase tracking-[0.25em] text-[#8F8F94]">{label}</div>
    <div className={`mt-4 font-mono font-light text-4xl tracking-tighter ${accent}`}>{value}</div>
    {sub && <div className="mt-2 text-xs text-[#555] font-mono">{sub}</div>}
  </div>
);

export const SectionTitle = ({ children, right }) => (
  <div className="flex items-center justify-between mb-3">
    <div className="text-[10px] uppercase tracking-[0.25em] text-[#8F8F94] font-bold">{children}</div>
    {right}
  </div>
);

export const Btn = ({ children, variant = "primary", className = "", ...props }) => {
  const base = "px-5 py-3 text-xs uppercase tracking-widest font-bold transition-colors disabled:opacity-50";
  const styles = {
    primary: "bg-white text-black hover:bg-[#E5E5E5]",
    secondary: "bg-transparent border border-white/30 text-white hover:border-white hover:bg-[#1A1A1A]",
    danger: "bg-[#FF3333] text-white hover:bg-[#CC0000]",
  };
  return <button className={`${base} ${styles[variant]} ${className}`} {...props}>{children}</button>;
};

export const Input = ({ label, testid, ...props }) => (
  <label className="block">
    {label && <span className="text-[10px] uppercase tracking-[0.2em] font-bold text-[#8F8F94] mb-2 block">{label}</span>}
    <input
      data-testid={testid}
      {...props}
      className="w-full bg-[#050505] border-b-2 border-white/20 text-white px-0 py-2 focus:outline-none focus:border-white font-mono text-sm"
    />
  </label>
);

export const Select = ({ label, testid, children, ...props }) => (
  <label className="block">
    {label && <span className="text-[10px] uppercase tracking-[0.2em] font-bold text-[#8F8F94] mb-2 block">{label}</span>}
    <select
      data-testid={testid}
      {...props}
      className="w-full bg-[#050505] border-b-2 border-white/20 text-white px-0 py-2 focus:outline-none focus:border-white font-mono text-sm"
    >
      {children}
    </select>
  </label>
);
