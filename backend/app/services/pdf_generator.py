import os
from datetime import datetime
from html import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PDFReportGenerator:
    @staticmethod
    def generate_compliance_report(
        output_path: str,
        product_name: str,
        fiber_composition: str,
        intended_market: str,
        label_text: str,
        analysis_result: str,
        status: str,
        analyst_name: str,
        confidence: float | None = None,
        references: list[str] | None = None,
    ) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1.6 * cm,
            leftMargin=1.6 * cm,
            topMargin=1.6 * cm,
            bottomMargin=1.6 * cm,
            title=f"Rapport TextileBot - {product_name}",
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=8,
        )
        subtitle_style = ParagraphStyle(
            name="Subtitle",
            parent=styles["BodyText"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=18,
        )
        heading_style = ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=12,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            name="ReportBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
        )

        status_meta = {
            "compliant": ("CONFORME", "#15803d"),
            "non_compliant": ("NON CONFORME", "#b91c1c"),
            "conditional": ("CONFORME AVEC RESERVE", "#b45309"),
            "warning": ("CONFORME AVEC RESERVE", "#b45309"),
        }
        status_text, status_color = status_meta.get(status, ("A VERIFIER", "#475569"))
        status_style = ParagraphStyle(
            name="Status",
            parent=body_style,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor(status_color),
        )

        story = [
            Paragraph("Rapport d'analyse de conformite textile", title_style),
            Paragraph("TextileBot Pro - Controle documentaire, RAG et verification reglementaire", subtitle_style),
        ]

        metadata = [
            [Paragraph("<b>Produit</b>", body_style), Paragraph(escape(product_name), body_style)],
            [Paragraph("<b>Composition</b>", body_style), Paragraph(escape(fiber_composition), body_style)],
            [Paragraph("<b>Marche cible</b>", body_style), Paragraph(escape(intended_market), body_style)],
            [Paragraph("<b>Statut</b>", body_style), Paragraph(status_text, status_style)],
            [
                Paragraph("<b>Confiance</b>", body_style),
                Paragraph(f"{confidence:.0%}" if confidence is not None else "Non calculee", body_style),
            ],
            [Paragraph("<b>Date</b>", body_style), Paragraph(datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), body_style)],
        ]
        table = Table(metadata, colWidths=[4.2 * cm, 12.2 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dbe3ef")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )
        story.extend([table, Spacer(1, 0.35 * cm)])

        if label_text:
            story.append(Paragraph("Etiquette soumise", heading_style))
            story.append(Paragraph(escape(label_text), body_style))

        story.append(Paragraph("Evaluation detaillee", heading_style))
        for block in PDFReportGenerator._markdown_blocks(analysis_result):
            story.append(Paragraph(block, body_style))
            story.append(Spacer(1, 0.12 * cm))

        if references:
            story.append(Paragraph("References consolidees", heading_style))
            for ref in references:
                story.append(Paragraph(f"- {escape(ref)}", body_style))

        story.extend(
            [
                Spacer(1, 0.4 * cm),
                Paragraph(f"Analyste: <b>{escape(analyst_name)}</b>", body_style),
                Paragraph("Note: ce rapport assiste la decision et ne remplace pas une validation juridique finale.", subtitle_style),
            ]
        )

        doc.build(story)
        return output_path

    @staticmethod
    def _markdown_blocks(text: str) -> list[str]:
        blocks = []
        for raw in (text or "").splitlines():
            line = raw.strip()
            if not line:
                continue
            line = escape(line)
            line = line.replace("**", "<b>", 1).replace("**", "</b>", 1)
            if line.startswith("### "):
                blocks.append(f"<b>{line[4:]}</b>")
            elif line.startswith("## "):
                blocks.append(f"<b>{line[3:]}</b>")
            else:
                blocks.append(line)
        return blocks
