import React from "react";
import { useTranslation } from "react-i18next";
import { Languages } from "lucide-react";

const LANGUAGES = [
  { code: "en", label: "EN" },
  { code: "hi", label: "हि" },
  { code: "es", label: "ES" },
  { code: "fr", label: "FR" },
  { code: "de", label: "DE" },
];

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <div className="flex items-center gap-1 border border-white/10 px-2 py-1.5">
      <Languages size={12} className="text-[#8F8F94]" />
      {LANGUAGES.map((l) => (
        <button
          key={l.code}
          onClick={() => changeLanguage(l.code)}
          data-testid={`lang-${l.code}`}
          className={`text-[10px] uppercase tracking-wider font-bold px-1.5 py-0.5 transition-colors ${
            i18n.language === l.code
              ? "bg-white text-black"
              : "text-[#8F8F94] hover:text-white hover:bg-[#1A1A1A]"
          }`}
        >
          {l.label}
        </button>
      ))}
    </div>
  );
}