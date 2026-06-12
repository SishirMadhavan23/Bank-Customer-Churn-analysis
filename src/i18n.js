import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

const resources = {
  en: {
    translation: {
      app: {
        title: "RETAIN.AI",
        subtitle: "Churn Control",
        signedIn: "Signed in",
        logout: "Logout",
      },
      nav: {
        dashboard: "Dashboard",
        dataset: "Dataset",
        analytics: "Customer Analytics",
        churnAnalysis: "Churn Analysis",
        prediction: "Churn Prediction",
        risk: "Risk Monitoring",
        reports: "Reports",
        admin: "Admin Panel",
      },
      chatbot: {
        ask: "Ask RetainAI",
        assistant: "Assistant",
        copilot: "RetainAI Co-pilot",
        placeholder: "Ask about churn…",
        thinking: "Thinking…",
        offline: "Sorry, the assistant is offline.",
        greeting: "Hello — I'm RetainAI. Ask me about churn patterns, retention strategies, or specific KPIs.",
      },
      auth: {
        login: "Login",
        register: "Register",
        email: "Email",
        password: "Password",
        invalidCredentials: "Invalid credentials",
      },
    },
  },
  hi: {
    translation: {
      app: {
        title: "RETAIN.AI",
        subtitle: "ग्राहक नियंत्रण",
        signedIn: "साइन इन किया",
        logout: "लॉग आउट",
      },
      nav: {
        dashboard: "डैशबोर्ड",
        dataset: "डेटासेट",
        analytics: "ग्राहक विश्लेषण",
        churnAnalysis: "चर्न विश्लेषण",
        prediction: "चर्न भविष्यवाणी",
        risk: "जोखिम निगरानी",
        reports: "रिपोर्ट",
        admin: "प्रशासन पैनल",
      },
      chatbot: {
        ask: "RetainAI से पूछें",
        assistant: "सहायक",
        copilot: "RetainAI सह-पायलट",
        placeholder: "चर्न के बारे में पूछें…",
        thinking: "सोच रहा है…",
        offline: "क्षमा करें, सहायक ऑफ़लाइन है।",
        greeting: "नमस्ते — मैं RetainAI हूँ। मुझसे चर्न पैटर्न, रिटेंशन रणनीतियों, या विशिष्ट KPI के बारे में पूछें।",
      },
      auth: {
        login: "लॉगिन",
        register: "पंजीकरण",
        email: "ईमेल",
        password: "पासवर्ड",
        invalidCredentials: "अमान्य क्रेडेंशियल",
      },
    },
  },
  es: {
    translation: {
      app: {
        title: "RETAIN.AI",
        subtitle: "Control de Abandono",
        signedIn: "Sesión iniciada",
        logout: "Cerrar sesión",
      },
      nav: {
        dashboard: "Panel",
        dataset: "Conjunto de Datos",
        analytics: "Analítica de Clientes",
        churnAnalysis: "Análisis de Abandono",
        prediction: "Predicción de Abandono",
        risk: "Monitoreo de Riesgo",
        reports: "Informes",
        admin: "Panel de Administración",
      },
      chatbot: {
        ask: "Preguntar a RetainAI",
        assistant: "Asistente",
        copilot: "RetainAI Copiloto",
        placeholder: "Pregunte sobre abandono…",
        thinking: "Pensando…",
        offline: "Lo siento, el asistente está desconectado.",
        greeting: "Hola — Soy RetainAI. Pregúntame sobre patrones de abandono, estrategias de retención o KPIs específicos.",
      },
      auth: {
        login: "Iniciar sesión",
        register: "Registrarse",
        email: "Correo electrónico",
        password: "Contraseña",
        invalidCredentials: "Credenciales inválidas",
      },
    },
  },
  fr: {
    translation: {
      app: {
        title: "RETAIN.AI",
        subtitle: "Contrôle du Churn",
        signedIn: "Connecté",
        logout: "Déconnexion",
      },
      nav: {
        dashboard: "Tableau de bord",
        dataset: "Ensemble de données",
        analytics: "Analytique Client",
        churnAnalysis: "Analyse du Churn",
        prediction: "Prédiction de Churn",
        risk: "Surveillance des Risques",
        reports: "Rapports",
        admin: "Panneau d'administration",
      },
      chatbot: {
        ask: "Demander à RetainAI",
        assistant: "Assistant",
        copilot: "RetainAI Copilote",
        placeholder: "Interrogez sur le churn…",
        thinking: "Réflexion…",
        offline: "Désolé, l'assistant est hors ligne.",
        greeting: "Bonjour — Je suis RetainAI. Interrogez-moi sur les modèles de churn, les stratégies de rétention ou des KPI spécifiques.",
      },
      auth: {
        login: "Connexion",
        register: "S'inscrire",
        email: "E-mail",
        password: "Mot de passe",
        invalidCredentials: "Identifiants invalides",
      },
    },
  },
  de: {
    translation: {
      app: {
        title: "RETAIN.AI",
        subtitle: "Abwanderungskontrolle",
        signedIn: "Angemeldet",
        logout: "Abmelden",
      },
      nav: {
        dashboard: "Dashboard",
        dataset: "Datensatz",
        analytics: "Kundenanalytik",
        churnAnalysis: "Abwanderungsanalyse",
        prediction: "Abwanderungsvorhersage",
        risk: "Risikoüberwachung",
        reports: "Berichte",
        admin: "Admin-Panel",
      },
      chatbot: {
        ask: "RetainAI fragen",
        assistant: "Assistent",
        copilot: "RetainAI Co-Pilot",
        placeholder: "Fragen Sie zur Abwanderung…",
        thinking: "Denkt nach…",
        offline: "Entschuldigung, der Assistent ist offline.",
        greeting: "Hallo — Ich bin RetainAI. Fragen Sie mich zu Abwanderungsmustern, Bindungsstrategien oder spezifischen KPIs.",
      },
      auth: {
        login: "Anmelden",
        register: "Registrieren",
        email: "E-Mail",
        password: "Passwort",
        invalidCredentials: "Ungültige Anmeldedaten",
      },
    },
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: "en",
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ["localStorage", "navigator", "htmlTag"],
      caches: ["localStorage"],
    },
  });

export default i18n;