"""
report_generator.py — генерация PDF-отчёта ESG и отправка его на email.

Зависимости (добавить в requirements.txt):
    weasyprint
    matplotlib

Использование во view (см. views_example.py):
    from report_generator import generate_pdf_report, send_report_email

    pdf_bytes = generate_pdf_report(result, roadmap, company_name, sector_name, sub_industry_name)
    send_report_email(pdf_bytes, recipient_email="user@example.com", company_name=company_name)
"""

import base64
from datetime import date
from io import BytesIO

import matplotlib
matplotlib.use("Agg")  # без GUI-бэкенда — обязательно для серверного окружения
import matplotlib.pyplot as plt

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from weasyprint import HTML

from esg_config import CATEGORY_NAMES, TIERS


# ============================================================
# ГРАФИКИ
# ============================================================

def generate_pillar_chart_base64(pillar_scores: dict) -> str:
    """Горизонтальный bar-chart по трём столпам E/S/G. Возвращает base64 PNG (без префикса data:image)."""
    fig, ax = plt.subplots(figsize=(6, 3))
    pillars = ["Environment", "Social", "Governance"]
    values = [pillar_scores["E"], pillar_scores["S"], pillar_scores["G"]]
    colors = ["#2e7d32", "#1565c0", "#6a1b9a"]

    ax.barh(pillars, values, color=colors)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Балл")
    for i, v in enumerate(values):
        ax.text(v + 1, i, f"{v:.1f}", va="center")

    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def generate_category_chart_base64(category_scores: dict, category_names: dict = None) -> str:
    """Горизонтальный bar-chart по всем 10 категориям, цвет зависит от балла (красный/жёлтый/зелёный)."""
    category_names = category_names or CATEGORY_NAMES
    cats = list(category_scores.keys())
    values = [category_scores[c] for c in cats]
    labels = [category_names.get(c, c) for c in cats]
    colors = ["#c62828" if v < 40 else "#f9a825" if v < 60 else "#2e7d32" for v in values]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    y_pos = range(len(cats))
    ax.barh(y_pos, values, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(0, 100)
    ax.invert_yaxis()
    ax.set_xlabel("Балл")
    for i, v in enumerate(values):
        ax.text(v + 1, i, f"{v:.0f}", va="center", fontsize=8)

    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ============================================================
# ТИР -> НОМЕР (для CSS-класса цвета в шаблоне: tier-1 ... tier-5)
# ============================================================

def _tier_number(tier_label: str) -> int:
    for i, tier in enumerate(TIERS):
        if tier["label"] == tier_label:
            return i + 1
    return 3  # дефолт на середину шкалы, если вдруг не нашли


# ============================================================
# СБОРКА PDF
# ============================================================

def generate_pdf_report(
    result: dict,
    roadmap: dict,
    company_name: str,
    sector_name: str,
    sub_industry_name: str = None,
    template_name: str = "reports/esg_report_template.html",
) -> bytes:
    """
    Собирает полный PDF-отчёт: скор, графики, controversy-предупреждения, роадмап.

    result:  вывод calculate_esg_score()
    roadmap: вывод generate_roadmap_from_answers()
    Возвращает PDF как bytes — можно отдать как HttpResponse, сохранить в media/, или сразу передать в send_report_email().

    ВАЖНО (i18n): result и roadmap должны быть уже посчитаны ПОСЛЕ активации нужного языка
    (translation.activate(lang)) — эта функция сама ничего не переводит, она просто рендерит
    уже готовые строки. Если result/roadmap посчитаны на одном языке, а рендер шаблона
    происходит после переключения на другой — получится смесь языков (статичные подписи
    шаблона переведутся через {% trans %}, а динамический текст (tier, рекомендации) — нет).
    """
    pillar_chart = generate_pillar_chart_base64(result["pillar_scores"])
    category_chart = generate_category_chart_base64(result["category_scores"])

    context = {
        "company_name": company_name,
        "sector_name": sector_name,
        "sub_industry_name": sub_industry_name,
        "generated_date": date.today().strftime("%d.%m.%Y"),
        "esg_final": result["esg_final"],
        "tier_label": result["tier"],
        "tier_number": _tier_number(result["tier"]),
        "conclusion": roadmap.get("summary", {}).get("conclusion"),
        "pillar_chart_base64": pillar_chart,
        "category_chart_base64": category_chart,
        "controversy_warnings": roadmap.get("controversy_warnings", []),
        "top_priority_actions": roadmap["top_priority_actions"],
        "recommendations_by_horizon": roadmap["recommendations_by_horizon"],
    }

    html_string = render_to_string(template_name, context)
    pdf_bytes = HTML(string=html_string).write_pdf()
    return pdf_bytes


# ============================================================
# ОТПРАВКА EMAIL (обычный SMTP через Django email backend)
# ============================================================

def send_report_email(
    pdf_bytes: bytes,
    recipient_email: str,
    company_name: str,
    tier_label: str = None,
    esg_final: float = None,
) -> None:
    """
    Отправляет PDF-отчёт вложением на email через SMTP-бэкенд, настроенный в settings.py
    (см. settings_email_snippet.py). Бросает исключение при ошибке отправки — оборачивай в try/except во view.
    """
    subject = f"ESG-отчёт для {company_name}"
    body_lines = [f"Здравствуйте!", "", "Во вложении — ваш ESG-отчёт по результатам самооценки."]
    if tier_label and esg_final is not None:
        body_lines.append(f"Итоговый балл: {esg_final} ({tier_label}).")
    body_lines.append("")
    body_lines.append("Это автоматическое письмо, отвечать на него не нужно.")
    body = "\n".join(body_lines)

    email = EmailMessage(
        subject=subject,
        body=body,
        to=[recipient_email],
    )
    filename = f"ESG_отчёт_{company_name.replace(' ', '_')}.pdf"
    email.attach(filename, pdf_bytes, "application/pdf")
    email.send(fail_silently=False)
