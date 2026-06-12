import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "./api";
import { MessageSquare, X, Send, Loader2 } from "lucide-react";

export default function Chatbot() {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState([
    { role: "assistant", text: t("chatbot.greeting") },
  ]);
  const [text, setText] = useState("");
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!text.trim()) return;
    const userMsg = text.trim();
    setMsgs((m) => [...m, { role: "user", text: userMsg }]);
    setText(""); setLoading(true);
    try {
      const { data } = await api.post("/ai/chat", { message: userMsg, session_id: session });
      setSession(data.session_id);
      setMsgs((m) => [...m, { role: "assistant", text: data.response }]);
    } catch (e) {
      setMsgs((m) => [...m, { role: "assistant", text: t("chatbot.offline") }]);
    } finally { setLoading(false); }
  };

  return (
    <>
      {!open && (
        <button
          data-testid="chatbot-open-btn"
          onClick={() => setOpen(true)}
          className="fixed bottom-6 right-6 z-40 bg-white text-black px-4 py-3 flex items-center gap-2 text-xs uppercase tracking-widest font-bold hover:bg-[#E5E5E5]"
        >
          <MessageSquare size={14} /> {t("chatbot.ask")}
        </button>
      )}
      {open && (
        <div className="fixed bottom-6 right-6 z-40 w-[380px] h-[520px] bg-[#0A0A0A] border border-white/15 flex flex-col">
          <div className="px-4 py-3 border-b border-white/10 flex items-center justify-between">
            <div>
              <div className="text-[10px] uppercase tracking-[0.25em] text-[#8F8F94]">{t("chatbot.assistant")}</div>
              <div className="text-sm font-bold tracking-tight">{t("chatbot.copilot")}</div>
            </div>
            <button data-testid="chatbot-close-btn" onClick={() => setOpen(false)} className="text-[#8F8F94] hover:text-white"><X size={16} /></button>
          </div>
          <div className="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-3">
            {msgs.map((m, i) => (
              <div key={i} className={m.role === "user" ? "text-right" : ""}>
                <div className={`inline-block max-w-[85%] text-xs leading-relaxed ${m.role === "user" ? "bg-white text-black px-3 py-2" : "border border-white/15 px-3 py-2 text-white"}`}>{m.text}</div>
              </div>
            ))}
            {loading && <div className="flex items-center gap-2 text-xs text-[#8F8F94]"><Loader2 size={14} className="animate-spin" /> {t("chatbot.thinking")}</div>}
          </div>
          <div className="border-t border-white/10 p-3 flex gap-2">
            <input
              data-testid="chatbot-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder={t("chatbot.placeholder")}
              className="flex-1 bg-[#050505] border border-white/15 px-3 py-2 text-xs focus:outline-none focus:border-white font-mono"
            />
            <button data-testid="chatbot-send-btn" onClick={send} className="bg-white text-black px-3 hover:bg-[#E5E5E5]"><Send size={14} /></button>
          </div>
        </div>
      )}
    </>
  );
}