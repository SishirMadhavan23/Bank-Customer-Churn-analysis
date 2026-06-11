"""PDF and Excel report generation for churn analytics."""
import io

import pandas as pd

from ml_engine import ChurnEngine


def build_pdf_report(engine: ChurnEngine) -> io.BytesIO:
    """Generate a PDF report from engine data.
    Uses reportlab if available, otherwise creates a minimal report."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError:
        # Fallback: return a placeholder bytes buffer
        buf = io.BytesIO()
        buf.write(b"PDF report generation requires reportlab: pip install reportlab\n")
        buf.seek(0)
        return buf

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Churn Analytics Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    # KPIs
    if engine.df is not None:
        kpis = engine.kpis()
        elements.append(Paragraph(f"Total Customers: {kpis['total_customers']}", styles["Normal"]))
        elements.append(Paragraph(f"Churn Rate: {kpis['churn_rate']}%", styles["Normal"]))
        elements.append(Paragraph(f"Retention Rate: {kpis['retention_rate']}%", styles["Normal"]))
        elements.append(Spacer(1, 12))

        # Model metrics
        if engine.metrics:
            elements.append(Paragraph("Model Performance", styles["Heading2"]))
            metrics_data = [
                ["Metric", "Value"],
                ["Accuracy", f"{engine.metrics.get('accuracy', 0):.3f}"],
                ["Precision", f"{engine.metrics.get('precision', 0):.3f}"],
                ["Recall", f"{engine.metrics.get('recall', 0):.3f}"],
                ["F1 Score", f"{engine.metrics.get('f1', 0):.3f}"],
                ["ROC AUC", f"{engine.metrics.get('roc_auc', 0):.3f}"],
            ]
            t = Table(metrics_data)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 12))

        # Feature importance
        if engine.feature_importance:
            elements.append(Paragraph("Top Feature Importance", styles["Heading2"]))
            fi_data = [["Feature", "Importance"]]
            for fi in engine.feature_importance[:5]:
                fi_data.append([fi["feature"], f"{fi['importance']:.4f}"])
            t2 = Table(fi_data)
            t2.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(t2)

    doc.build(elements)
    buf.seek(0)
    return buf


def build_excel_export(engine: ChurnEngine) -> io.BytesIO:
    """Generate an Excel export from engine data."""
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        buf = io.BytesIO()
        buf.write(b"Excel export requires openpyxl: pip install openpyxl\n")
        buf.seek(0)
        return buf

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        if engine.df is not None:
            # Write raw data sheet
            engine.df.to_excel(writer, sheet_name="Customer Data", index=False)

            # KPI sheet
            kpis = engine.kpis()
            kpi_df = pd.DataFrame([kpis])
            kpi_df.to_excel(writer, sheet_name="KPIs", index=False)

            # Segmentation sheet
            try:
                segs = engine.segmentation()
                seg_df = pd.DataFrame(segs)
                seg_df.to_excel(writer, sheet_name="Segments", index=False)
            except Exception:
                pass

            # High risk sheet
            try:
                high_risk = engine.high_risk_customers(100)
                hr_df = pd.DataFrame(high_risk)
                hr_df.to_excel(writer, sheet_name="High Risk Customers", index=False)
            except Exception:
                pass

    buf.seek(0)
    return buf
