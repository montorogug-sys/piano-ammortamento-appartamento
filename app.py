import streamlit as st
import json
import os
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Configurazione pagina
st.set_page_config(
    page_title="Piano Ammortamento Appartamento",
    page_icon="🏠",
    layout="wide"
)

# Path file dati
DATA_FILE = "data/ammortamento_data.json"

# Inizializzazione dati
def init_data():
    """Inizializza o carica i dati"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "capitale_iniziale": 0.0,
            "durata_mesi": 0,
            "durata_originale": 0,
            "tasso_annuo": 2.0,
            "tipo_ammortamento": "italiano",
            "costi_manutenzione": [],
            "pagamenti": [],
            "versamenti_straordinari": [],
            "configurato": False,
            "email_guglielmo": "",
            "email_mattia": "",
            "iban_guglielmo": "",
            "iban_mattia": "",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_email": "",
            "smtp_password": ""
        }

def save_data(data):
    """Salva i dati su file"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def calcola_capitale_effettivo(data):
    """Calcola capitale effettivo dopo costi manutenzione"""
    capitale = data["capitale_iniziale"]
    for costo in data["costi_manutenzione"]:
        capitale -= costo["importo"]
    return capitale

def calcola_capitale_residuo(data):
    """Calcola capitale residuo dopo pagamenti"""
    capitale_effettivo = calcola_capitale_effettivo(data)
    totale_pagato = sum(p["importo"] for p in data["pagamenti"] if p.get("confermato", False))
    return capitale_effettivo - totale_pagato

def calcola_totale_versamenti_straordinari(data):
    """Calcola totale versamenti straordinari confermati"""
    return sum(v["importo"] for v in data.get("versamenti_straordinari", []) if v.get("confermato", False))

def calcola_nuova_durata_con_straordinari(capitale_residuo, tasso_annuo, rata_mensile, versamento_straordinario):
    """
    Calcola la nuova durata dopo un versamento straordinario.
    Il versamento riduce il capitale residuo, quindi servono meno rate.
    """
    nuovo_capitale = capitale_residuo - versamento_straordinario

    if nuovo_capitale <= 0:
        return 0  # Debito saldato

    # Calcola nuova durata necessaria
    piano_temp, nuova_durata = calcola_piano_con_rata_fissa(nuovo_capitale, tasso_annuo, rata_mensile)

    return nuova_durata if nuova_durata else 0

def calcola_durata_effettiva(data):
    """Calcola durata effettiva includendo rate saltate"""
    durata_base = data.get("durata_originale", data.get("durata_mesi", 0))
    rate_saltate = len(data.get("rate_saltate", []))
    return durata_base + rate_saltate

def get_numero_rata_corrente(data):
    """Calcola il numero della rata corrente (considerando rate saltate e pagate)"""
    rate_pagate = len([p for p in data["pagamenti"] if p.get("confermato", False)])
    rate_saltate = len([s for s in data.get("rate_saltate", []) if s.get("numero_rata", 0) <= rate_pagate + len(data.get("rate_saltate", []))])
    return rate_pagate + 1

def calcola_piano_ammortamento_italiano(capitale, tasso_annuo, durata_mesi, data_inizio=None):
    """
    Calcola piano ammortamento italiano (quota capitale costante)

    Args:
        capitale: Capitale da ammortizzare
        tasso_annuo: Tasso interesse annuo (es. 2.0 per 2%)
        durata_mesi: Durata in mesi
        data_inizio: Data di inizio (default: oggi)

    Returns:
        DataFrame con piano ammortamento
    """
    from dateutil.relativedelta import relativedelta

    if data_inizio is None:
        data_inizio = date.today()

    tasso_mensile = tasso_annuo / 100 / 12
    quota_capitale = capitale / durata_mesi

    piano = []
    debito_residuo = capitale

    for mese in range(1, durata_mesi + 1):
        interessi = debito_residuo * tasso_mensile
        rata = quota_capitale + interessi
        debito_residuo -= quota_capitale

        # Calcola data scadenza (aggiungi mese-1 perché il mese 1 è il primo pagamento)
        data_scadenza = data_inizio + relativedelta(months=mese-1)

        piano.append({
            "mese": mese,
            "data_scadenza": data_scadenza.strftime("%Y-%m-%d"),
            "quota_capitale": quota_capitale,
            "quota_interessi": interessi,
            "rata": rata,
            "debito_residuo": max(0, debito_residuo)  # evita negativi per arrotondamento
        })

    return pd.DataFrame(piano)

def calcola_rata_da_durata(capitale, tasso_annuo, durata_mesi):
    """Calcola rata mensile iniziale per ammortamento italiano"""
    tasso_mensile = tasso_annuo / 100 / 12
    quota_capitale = capitale / durata_mesi
    interessi_primo_mese = capitale * tasso_mensile
    return quota_capitale + interessi_primo_mese

def calcola_durata_da_rata(capitale, tasso_annuo, rata_desiderata):
    """
    Calcola durata necessaria data una rata fissa (ammortamento italiano).
    Usa ricerca binaria per trovare durata ottimale.
    """
    tasso_mensile = tasso_annuo / 100 / 12

    # Durata minima teorica (senza interessi)
    min_mesi = int(capitale / rata_desiderata)

    # Cerca durata ottimale
    for durata in range(min_mesi, min_mesi * 5):  # max 5x durata minima
        quota_capitale = capitale / durata
        interessi_primo_mese = capitale * tasso_mensile
        rata_prima = quota_capitale + interessi_primo_mese

        if rata_prima <= rata_desiderata:
            return durata

    return None  # Rata troppo bassa

def calcola_durata_effettiva_con_pagamenti_variabili(data):
    """
    Calcola la durata effettiva rimanente considerando i pagamenti variabili già effettuati.
    Ritorna la durata totale stimata (rate pagate + rate rimanenti stimate).
    """
    capitale_residuo_attuale = calcola_capitale_residuo(data)

    if capitale_residuo_attuale <= 0:
        # Debito saldato
        return len([p for p in data['pagamenti'] if p.get('confermato', False)])

    # Usa la rata target come riferimento per stimare le rate rimanenti
    rata_target = data.get('rata_target', 300.0)

    # Calcola durata rimanente necessaria
    durata_rimanente = calcola_durata_da_rata(capitale_residuo_attuale, data['tasso_annuo'], rata_target)

    if durata_rimanente is None:
        # Fallback: stima con quota capitale
        durata_rimanente = int(capitale_residuo_attuale / (rata_target * 0.8)) + 1

    # Rate già pagate
    rate_pagate = len([p for p in data['pagamenti'] if p.get('confermato', False)])

    # Durata totale = pagate + rimanenti
    durata_totale_stimata = rate_pagate + durata_rimanente

    return durata_totale_stimata


def calcola_piano_con_rata_fissa(capitale, tasso_annuo, rata_desiderata):
    """Calcola piano ammortamento italiano con rata target"""
    durata = calcola_durata_da_rata(capitale, tasso_annuo, rata_desiderata)

    if durata is None:
        return None, None

    piano = calcola_piano_ammortamento_italiano(capitale, tasso_annuo, durata)
    return piano, durata

def genera_pdf_ricevuta(pagamento, data, numero_rata):
    """Genera PDF ricevuta pagamento"""
    filename = f"cedolini/ricevuta_{pagamento['data']}_{numero_rata}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Stile titolo
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    # Titolo
    elements.append(Paragraph("RICEVUTA PAGAMENTO RATA", title_style))
    elements.append(Spacer(1, 20))

    # Informazioni generali
    info_data = [
        ["Data Pagamento:", pagamento['data']],
        ["Numero Rata:", str(numero_rata)],
        ["Importo Rata:", f"€ {pagamento['importo']:,.2f}"],
        ["", ""],
        ["Capitale Iniziale:", f"€ {data['capitale_iniziale']:,.2f}"],
        ["Costi Manutenzione:", f"€ {sum(c['importo'] for c in data['costi_manutenzione']):,.2f}"],
        ["Capitale Effettivo:", f"€ {calcola_capitale_effettivo(data):,.2f}"],
        ["", ""],
        ["Totale Pagato:", f"€ {sum(p['importo'] for p in data['pagamenti'] if p.get('confermato')):,.2f}"],
        ["Capitale Residuo:", f"€ {calcola_capitale_residuo(data):,.2f}"],
    ]

    table = Table(info_data, colWidths=[8*cm, 8*cm])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (1, -1), (1, -1), colors.HexColor('#d32f2f')),
        ('FONTSIZE', (1, -1), (1, -1), 14),
        ('FONTNAME', (1, -1), (1, -1), 'Helvetica-Bold'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 40))

    # Firme
    firma_data = [
        ["", ""],
        ["_________________________", "_________________________"],
        ["Firma Mattia (Debitore)", "Firma Guglielmo (Creditore)"],
    ]

    firma_table = Table(firma_data, colWidths=[8*cm, 8*cm])
    firma_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, -1), (-1, -1), 9),
    ]))

    elements.append(firma_table)

    # Genera PDF
    doc.build(elements)
    return filename


def crea_grafico_evoluzione_ammortamento(piano_df, rate_pagate=0):
    """Crea grafico ad area impilata con evoluzione capitale/interessi/residuo"""
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Backend non-interattivo per PDF

    fig, ax = plt.subplots(figsize=(7, 4))  # Ridotto da (10, 6)

    # Prepara dati
    mesi = piano_df['mese'].values

    # Calcola cumulativi
    capitale_cumulativo = piano_df['quota_capitale'].cumsum().values
    interessi_cumulativo = piano_df['quota_interessi'].cumsum().values
    debito_residuo = piano_df['debito_residuo'].values

    # Grafico ad area impilata - colori più eleganti
    ax.fill_between(mesi, 0, capitale_cumulativo, alpha=0.6, color='#2e7d32', label='Capitale Pagato')
    ax.fill_between(mesi, capitale_cumulativo, capitale_cumulativo + interessi_cumulativo,
                     alpha=0.6, color='#f57c00', label='Interessi Pagati')

    # Linea debito residuo - più sottile
    ax.plot(mesi, debito_residuo, color='#c62828', linewidth=1.8, label='Debito Residuo', linestyle='--')

    # Linea verticale per rate pagate
    if rate_pagate > 0:
        ax.axvline(x=rate_pagate, color='#1565c0', linewidth=1.5, linestyle=':', label=f'Rate Pagate ({rate_pagate})')

    # Formattazione - font più piccoli e minimalisti
    ax.set_xlabel('Mese', fontsize=9)
    ax.set_ylabel('Importo (€)', fontsize=9)
    ax.set_title('Evoluzione Piano Ammortamento', fontsize=10, fontweight='bold', pad=10)
    ax.legend(loc='best', frameon=True, shadow=False, fontsize=8, framealpha=0.9)
    ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)

    # Formato valori asse Y
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
    ax.tick_params(labelsize=8)

    plt.tight_layout()

    # Salva in file temporaneo con path assoluto - DPI ridotto per file più leggeri
    temp_filename = os.path.abspath('temp_grafico_evoluzione.png')
    plt.savefig(temp_filename, dpi=100, bbox_inches='tight')
    plt.close()

    return temp_filename


def crea_grafico_torta_composizione(piano_df):
    """Crea grafico a torta con composizione finale capitale/interessi"""
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')

    fig, ax = plt.subplots(figsize=(5, 5))  # Ridotto da (8, 8)

    # Calcola totali
    totale_capitale = piano_df['quota_capitale'].sum()
    totale_interessi = piano_df['quota_interessi'].sum()

    # Dati e colori - più eleganti
    sizes = [totale_capitale, totale_interessi]
    labels = [f'Capitale\n€{totale_capitale:,.0f}', f'Interessi\n€{totale_interessi:,.0f}']
    colors = ['#2e7d32', '#f57c00']  # Stessi colori del grafico evoluzione
    explode = (0.03, 0)  # Esplosione ridotta

    # Crea torta
    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                        autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})

    # Formattazione testi - più sobri
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)

    for text in texts:
        text.set_fontsize(9)
        text.set_fontweight('normal')

    ax.set_title('Composizione Pagamento', fontsize=10, fontweight='bold', pad=12)

    # Aggiungi totale - più discreto
    totale = totale_capitale + totale_interessi
    ax.text(0, -1.2, f'Totale: €{totale:,.0f}',
            ha='center', fontsize=9, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#f5f5f5', alpha=0.8, edgecolor='gray', linewidth=0.5))

    plt.tight_layout()

    # Salva con path assoluto - DPI ridotto
    temp_filename = os.path.abspath('temp_grafico_torta.png')
    plt.savefig(temp_filename, dpi=100, bbox_inches='tight')
    plt.close()

    return temp_filename


def genera_pdf_report_completo(data):
    """Genera PDF report completo con piano ammortamento e storico pagamenti"""
    from datetime import datetime

    filename = f"reports/report_ammortamento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()

    # Stili personalizzati
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=15,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )

    # Titolo principale
    elements.append(Paragraph("REPORT COMPLETO - PIANO AMMORTAMENTO", title_style))
    elements.append(Paragraph(f"Generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Sezione 1: Riepilogo Generale
    elements.append(Paragraph("1. RIEPILOGO GENERALE", subtitle_style))

    capitale_eff = calcola_capitale_effettivo(data)
    capitale_residuo = calcola_capitale_residuo(data)
    totale_pagato = sum(p['importo'] for p in data['pagamenti'] if p.get('confermato', False))
    rate_pagate = len([p for p in data['pagamenti'] if p.get('confermato', False)])
    progresso = (totale_pagato / capitale_eff * 100) if capitale_eff > 0 else 0

    riepilogo_data = [
        ["Capitale Iniziale:", f"€ {data['capitale_iniziale']:,.2f}"],
        ["Costi Manutenzione:", f"€ {sum(c['importo'] for c in data['costi_manutenzione']):,.2f}"],
        ["Capitale Effettivo:", f"€ {capitale_eff:,.2f}"],
        ["", ""],
        ["Rate Pagate:", f"{rate_pagate} di {data['durata_mesi']}"],
        ["Progresso:", f"{progresso:.1f}%"],
        ["Totale Pagato:", f"€ {totale_pagato:,.2f}"],
        ["Capitale Residuo:", f"€ {capitale_residuo:,.2f}"],
        ["", ""],
        ["Tasso Interesse Annuo:", f"{data['tasso_annuo']}%"],
        ["Tipo Ammortamento:", "Italiano (quota capitale costante)"],
    ]

    table = Table(riepilogo_data, colWidths=[9*cm, 7*cm])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # Sezione 2: Piano Ammortamento Completo
    elements.append(Paragraph("2. PIANO AMMORTAMENTO COMPLETO", subtitle_style))

    piano = calcola_piano_ammortamento_italiano(capitale_eff, data['tasso_annuo'], data['durata_mesi'])

    # Prepara mapping pagamenti confermati per numero rata
    pagamenti_map = {}
    rate_confermate = [p for p in data["pagamenti"] if p.get("confermato", False)]
    for idx, pag in enumerate(sorted(rate_confermate, key=lambda x: x['data']), 1):
        pagamenti_map[idx] = pag

    # Tabella piano ammortamento con marcatori pagamenti
    piano_data = [["#", "Scad.", "Pag.", "✓", "Q.Cap.", "Q.Int.", "Rata", "Deb.Res.", "Tot.Cap.", "Tot.Pag."]]

    # Calcola progressivi
    totale_capitale_pagato = 0
    totale_complessivo_pagato = 0

    for _, row in piano.iterrows():
        totale_capitale_pagato += row['quota_capitale']
        totale_complessivo_pagato += row['rata']

        mese_num = int(row['mese'])

        # Verifica se questa rata è stata pagata
        if mese_num in pagamenti_map:
            pag = pagamenti_map[mese_num]
            data_pagamento = pag['data']
            check = "✓"
        else:
            data_pagamento = "-"
            check = ""

        piano_data.append([
            str(mese_num),
            row['data_scadenza'],
            data_pagamento,
            check,
            f"€ {row['quota_capitale']:,.2f}",
            f"€ {row['quota_interessi']:,.2f}",
            f"€ {row['rata']:,.2f}",
            f"€ {row['debito_residuo']:,.2f}",
            f"€ {totale_capitale_pagato:,.2f}",
            f"€ {totale_complessivo_pagato:,.2f}"
        ])

    piano_table = Table(piano_data, colWidths=[0.8*cm, 1.7*cm, 1.7*cm, 0.7*cm, 1.6*cm, 1.6*cm, 1.6*cm, 1.9*cm, 1.9*cm, 1.9*cm])

    # Costruisci stili base
    table_styles = [
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 6.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        # Evidenzia le colonne progressive
        ('BACKGROUND', (8, 0), (9, 0), colors.HexColor('#2e7d32')),
        # Colonna check verde
        ('BACKGROUND', (3, 0), (3, 0), colors.HexColor('#4caf50')),
        ('FONTSIZE', (3, 1), (3, -1), 10),
        ('TEXTCOLOR', (3, 1), (3, -1), colors.HexColor('#4caf50')),
    ]

    # Evidenzia righe pagate con sfondo verde chiaro
    for mese_num in pagamenti_map.keys():
        table_styles.append(('BACKGROUND', (0, mese_num), (-1, mese_num), colors.HexColor('#e8f5e9')))

    piano_table.setStyle(TableStyle(table_styles))

    elements.append(piano_table)

    # Legenda
    legenda_style = ParagraphStyle(
        'Legenda',
        parent=styles['Normal'],
        fontSize=7,
        textColor=colors.grey,
        spaceAfter=10,
        spaceBefore=5
    )
    elements.append(Paragraph(
        "<i>#=Numero Rata | Scad.=Data Scadenza | Pag.=Data Pagamento | ✓=Verificato | Q.Cap.=Quota Capitale | "
        "Q.Int.=Quota Interessi | Deb.Res.=Debito Residuo | Tot.Cap.=Totale Capitale Pagato | "
        "Tot.Pag.=Totale Complessivo Pagato | <b>Sfondo Verde = Rata Pagata e Verificata</b></i>",
        legenda_style
    ))
    elements.append(Spacer(1, 20))

    # Sezione 3: Storico Pagamenti
    elements.append(Paragraph("3. STORICO PAGAMENTI EFFETTUATI", subtitle_style))

    rate_confermate = [p for p in data["pagamenti"] if p.get("confermato", False)]

    if rate_confermate:
        pagamenti_data = [["Data Pagamento", "Importo", "Note"]]

        for pag in sorted(rate_confermate, key=lambda x: x['data']):
            pagamenti_data.append([
                pag['data'],
                f"€ {pag['importo']:,.2f}",
                pag.get('note', '-')[:40]  # Limita lunghezza note
            ])

        # Aggiungi totale
        pagamenti_data.append(["", "", ""])
        pagamenti_data.append(["TOTALE PAGATO", f"€ {totale_pagato:,.2f}", ""])

        pag_table = Table(pagamenti_data, colWidths=[3.5*cm, 3.5*cm, 9*cm])
        pag_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('TEXTCOLOR', (1, -1), (1, -1), colors.HexColor('#2e7d32')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#2e7d32')),
        ]))

        elements.append(pag_table)
    else:
        elements.append(Paragraph("Nessun pagamento registrato", styles['Normal']))

    elements.append(Spacer(1, 20))

    # Sezione 4: Versamenti Straordinari (se presenti)
    versamenti_straord = [v for v in data.get("versamenti_straordinari", []) if v.get("confermato", False)]
    if versamenti_straord:
        elements.append(Paragraph("4. VERSAMENTI STRAORDINARI", subtitle_style))

        straord_data = [["Data", "Importo", "Note"]]
        totale_straord = 0

        for vers in versamenti_straord:
            straord_data.append([
                vers['data'],
                f"€ {vers['importo']:,.2f}",
                vers.get('note', '-')[:40]
            ])
            totale_straord += vers['importo']

        straord_data.append(["", "", ""])
        straord_data.append(["TOTALE STRAORDINARI", f"€ {totale_straord:,.2f}", ""])

        straord_table = Table(straord_data, colWidths=[3.5*cm, 3.5*cm, 9*cm])
        straord_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.grey),
        ]))

        elements.append(straord_table)
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("I versamenti straordinari riducono la durata del finanziamento.", styles['Italic']))

    # Sezione 5: Grafici Riassuntivi
    elements.append(Paragraph("4. GRAFICI RIASSUNTIVI", subtitle_style))
    elements.append(Spacer(1, 10))

    # Genera grafici
    grafico_evoluzione_path = None
    grafico_torta_path = None

    try:
        import os

        # Grafico evoluzione
        rate_pagate_count = len([p for p in data['pagamenti'] if p.get('confermato', False)])
        grafico_evoluzione_path = crea_grafico_evoluzione_ammortamento(piano, rate_pagate_count)

        # Aggiungi grafico evoluzione al PDF - dimensioni ridotte per eleganza
        from reportlab.platypus import Image
        img_evoluzione = Image(grafico_evoluzione_path, width=12*cm, height=7*cm)
        elements.append(img_evoluzione)
        elements.append(Spacer(1, 12))

        # Grafico torta
        grafico_torta_path = crea_grafico_torta_composizione(piano)

        # Aggiungi grafico torta al PDF - dimensioni ridotte
        img_torta = Image(grafico_torta_path, width=9*cm, height=9*cm)
        elements.append(img_torta)

    except Exception as e:
        elements.append(Paragraph(f"<i>Errore nella generazione dei grafici: {str(e)}</i>", styles['Italic']))

    # Genera PDF
    doc.build(elements)

    # Rimuovi file temporanei DOPO la generazione del PDF
    try:
        if grafico_evoluzione_path and os.path.exists(grafico_evoluzione_path):
            os.remove(grafico_evoluzione_path)
        if grafico_torta_path and os.path.exists(grafico_torta_path):
            os.remove(grafico_torta_path)
    except:
        pass  # Ignora errori nella pulizia

    return filename


def genera_cedolino_rata(pagamento, data, numero_rata, piano_completo):
    """Genera cedolino PDF individuale per una singola rata pagata"""
    from datetime import datetime

    filename = f"cedolino_rata_{numero_rata}_{pagamento['data'].replace('-', '')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()

    # Stili personalizzati
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=15,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    # Header
    elements.append(Paragraph("CEDOLINO PAGAMENTO RATA", title_style))
    elements.append(Paragraph("Piano Ammortamento Appartamento", subtitle_style))
    elements.append(Spacer(1, 10))

    # Box con numero rata evidenziato
    rata_box_data = [[f"RATA N. {numero_rata}"]]
    rata_box = Table(rata_box_data, colWidths=[16*cm])
    rata_box.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 24),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1f4788')),
    ]))
    elements.append(rata_box)
    elements.append(Spacer(1, 20))

    # Informazioni rata dal piano
    rata_info = piano_completo.iloc[numero_rata - 1]
    capitale_residuo_dopo = calcola_capitale_residuo(data)

    # Sezione 1: Dati Pagamento
    elements.append(Paragraph("DATI PAGAMENTO", styles['Heading3']))
    elements.append(Spacer(1, 10))

    pagamento_data = [
        ["Data Scadenza:", rata_info['data_scadenza']],
        ["Data Pagamento Effettivo:", pagamento['data']],
        ["Importo Pagato:", f"€ {pagamento['importo']:,.2f}"],
        ["Causale:", f"Pagamento Rata {numero_rata} - Piano Ammortamento Appartamento"],
    ]

    if pagamento.get('note'):
        pagamento_data.append(["Note:", pagamento['note'][:60]])

    pag_table = Table(pagamento_data, colWidths=[7*cm, 9*cm])
    pag_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
    ]))

    elements.append(pag_table)
    elements.append(Spacer(1, 20))

    # Sezione 2: Dettaglio Rata
    elements.append(Paragraph("DETTAGLIO COMPOSIZIONE RATA", styles['Heading3']))
    elements.append(Spacer(1, 10))

    dettaglio_data = [
        ["Quota Capitale:", f"€ {rata_info['quota_capitale']:,.2f}"],
        ["Quota Interessi (2% annuo):", f"€ {rata_info['quota_interessi']:,.2f}"],
        ["", ""],
        ["TOTALE RATA:", f"€ {rata_info['rata']:,.2f}"],
    ]

    det_table = Table(dettaglio_data, colWidths=[10*cm, 6*cm])
    det_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#1f4788')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('TEXTCOLOR', (1, -1), (1, -1), colors.HexColor('#1f4788')),
    ]))

    elements.append(det_table)
    elements.append(Spacer(1, 20))

    # Sezione 3: Situazione Finanziaria
    elements.append(Paragraph("SITUAZIONE FINANZIARIA", styles['Heading3']))
    elements.append(Spacer(1, 10))

    capitale_eff = calcola_capitale_effettivo(data)
    rate_pagate = len([p for p in data['pagamenti'] if p.get('confermato', False)])
    totale_pagato = sum(p['importo'] for p in data['pagamenti'] if p.get('confermato', False))

    situazione_data = [
        ["Capitale Iniziale:", f"€ {data['capitale_iniziale']:,.2f}"],
        ["Spese Ripristino:", f"€ {sum(c['importo'] for c in data['costi_manutenzione']):,.2f}"],
        ["Capitale Effettivo:", f"€ {capitale_eff:,.2f}"],
        ["", ""],
        ["Rate Pagate (inclusa questa):", f"{rate_pagate} di {data['durata_mesi']}"],
        ["Totale Versato:", f"€ {totale_pagato:,.2f}"],
        ["", ""],
        ["CAPITALE RESIDUO:", f"€ {capitale_residuo_dopo:,.2f}"],
    ]

    sit_table = Table(situazione_data, colWidths=[10*cm, 6*cm])
    sit_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#d32f2f')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('TEXTCOLOR', (1, -1), (1, -1), colors.HexColor('#d32f2f')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ffebee')),
    ]))

    elements.append(sit_table)
    elements.append(Spacer(1, 30))

    # Box Verificato
    verificato_data = [["✓ PAGAMENTO VERIFICATO E CONFERMATO"]]
    verif_box = Table(verificato_data, colWidths=[16*cm])
    verif_box.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#4caf50')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#2e7d32')),
    ]))
    elements.append(verif_box)
    elements.append(Spacer(1, 30))

    # Firme
    elements.append(Spacer(1, 20))
    firma_data = [
        ["", ""],
        ["_____________________________", "_____________________________"],
        ["Firma Mattia (Debitore)", "Firma Guglielmo (Creditore)"],
        ["", ""],
        [f"Data: {pagamento['data']}", f"Data: {pagamento['data']}"],
    ]

    firma_table = Table(firma_data, colWidths=[8*cm, 8*cm])
    firma_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, 1), 30),
    ]))

    elements.append(firma_table)
    elements.append(Spacer(1, 20))

    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        f"<i>Cedolino generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')} - "
        f"Piano Ammortamento Italiano - Tasso Fisso 2% Annuo</i>",
        footer_style
    ))
    elements.append(Paragraph(
        "<i>Conservare per documentazione fiscale e garanzia</i>",
        footer_style
    ))

    # Genera PDF
    doc.build(elements)
    return filename


def genera_cedolino_bonifico(pagamento, data, numero_rata, stato="eseguito"):
    """
    Genera cedolino PDF per bonifico bancario
    stato: 'eseguito' o 'verificato'
    """
    from datetime import datetime

    stato_upper = stato.upper()
    filename = f"cedolini/cedolino_bonifico_{stato}_{pagamento['data'].replace('-', '')}_{numero_rata}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()

    # Stili
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1f4788') if stato == "eseguito" else colors.HexColor('#2e7d32'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    # Titolo
    elements.append(Paragraph(f"CEDOLINO BONIFICO BANCARIO - {stato_upper}", title_style))
    elements.append(Spacer(1, 20))

    # Info bonifico
    info_bonifico = [
        ["DATI BONIFICO", ""],
        ["Data Pagamento:", pagamento.get('data', '')],
        ["Importo:", f"€ {pagamento.get('importo', 0):,.2f}"],
        ["Causale:", pagamento.get('causale', '')],
        ["", ""],
        ["IBAN Mittente (Mattia):", pagamento.get('iban_mittente', '')],
        ["IBAN Beneficiario (Guglielmo):", pagamento.get('iban_beneficiario', '')],
        ["", ""],
        ["Numero Rata:", str(numero_rata)],
        ["Stato:", stato_upper],
    ]

    if stato == "verificato":
        info_bonifico.append(["Data Verifica:", pagamento.get('data_verifica', '')])
        info_bonifico.append(["Verificato da:", "Guglielmo (Creditore)"])

    table = Table(info_bonifico, colWidths=[9*cm, 9*cm])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    # Riepilogo finanziamento
    capitale_residuo = calcola_capitale_residuo(data)
    totale_pagato = sum(p['importo'] for p in data['pagamenti'] if p.get('confermato', False))

    riepilogo = [
        ["RIEPILOGO FINANZIAMENTO", ""],
        ["Capitale Effettivo:", f"€ {calcola_capitale_effettivo(data):,.2f}"],
        ["Totale Pagato:", f"€ {totale_pagato:,.2f}"],
        ["Capitale Residuo:", f"€ {capitale_residuo:,.2f}"],
        ["Progresso:", f"{(totale_pagato/calcola_capitale_effettivo(data)*100):.1f}%"],
    ]

    table2 = Table(riepilogo, colWidths=[9*cm, 9*cm])
    table2.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fff3e0')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))

    elements.append(table2)
    elements.append(Spacer(1, 40))

    # Footer
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph(
        f"<i>Cedolino generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}</i>",
        footer_style
    ))

    doc.build(elements)
    return filename


def invia_email_con_allegato(destinatari, oggetto, corpo, allegato_path, data):
    """
    Invia email con allegato PDF
    destinatari: lista di email
    allegato_path: percorso al file PDF
    """
    try:
        smtp_server = data.get('smtp_server', 'smtp.gmail.com')
        smtp_port = data.get('smtp_port', 587)
        smtp_email = data.get('smtp_email', '')
        smtp_password = data.get('smtp_password', '')

        if not smtp_email or not smtp_password:
            raise Exception("Configurazione SMTP non completa. Verifica email e password SMTP nelle impostazioni.")

        # Crea messaggio
        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = ', '.join(destinatari)
        msg['Subject'] = oggetto

        # Corpo email
        msg.attach(MIMEText(corpo, 'html'))

        # Allega PDF se esiste
        if allegato_path and os.path.exists(allegato_path):
            with open(allegato_path, 'rb') as f:
                pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                pdf_attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(allegato_path))
                msg.attach(pdf_attachment)

        # Invia email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.send_message(msg)
        server.quit()

        return True, "Email inviata con successo"

    except Exception as e:
        return False, f"Errore invio email: {str(e)}"


# Login semplice
def login():
    """Sistema di login semplice"""
    st.sidebar.title("Login")

    utente = st.sidebar.radio("Seleziona utente:", ["Mattia (Debitore)", "Guglielmo (Creditore)"])
    password = st.sidebar.text_input("Password:", type="password")

    if st.sidebar.button("Accedi"):
        # Password semplici (in produzione usare hash e secrets)
        if utente == "Mattia (Debitore)" and password == "mattia2025":
            st.session_state['logged_in'] = True
            st.session_state['user'] = "Mattia"
            st.session_state['role'] = "debitore"
            st.rerun()
        elif utente == "Guglielmo (Creditore)" and password == "guglielmo2025":
            st.session_state['logged_in'] = True
            st.session_state['user'] = "Guglielmo"
            st.session_state['role'] = "creditore"
            st.rerun()
        else:
            st.sidebar.error("Password errata!")

    return False

# Main App
def main():
    # Inizializza session state
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Carica dati
    data = init_data()

    # Login
    if not st.session_state['logged_in']:
        st.title("🏠 Piano Ammortamento Appartamento")
        st.info("**Password di default:**\n- Mattia: `mattia2025`\n- Guglielmo: `guglielmo2025`")
        login()
        st.stop()

    # Header
    st.title("🏠 Piano Ammortamento Appartamento")
    st.write(f"**Utente:** {st.session_state['user']} ({st.session_state['role'].capitalize()})")

    if st.sidebar.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    # Tabs principali
    if not data["configurato"]:
        tab1, tab2 = st.tabs(["⚙️ Configurazione Iniziale", "📊 Dashboard"])
    else:
        if st.session_state['role'] == "creditore":
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "💰 Gestione Rate", "🔧 Spese Ripristino", "⚙️ Configurazione", "📈 Storico"])
        else:
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "💳 Registra Pagamento", "🔧 Spese Ripristino", "⚙️ Impostazioni", "📈 Storico"])

    # TAB 1: Configurazione Iniziale (solo creditore)
    if not data["configurato"]:
        with tab1:
            if st.session_state['role'] != "creditore":
                st.warning("Solo Guglielmo può configurare il piano iniziale.")
                st.stop()

            st.header("Configurazione Piano Ammortamento")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Parametri Ammortamento")

                capitale = st.number_input(
                    "Capitale Iniziale (€)",
                    min_value=0.0,
                    value=80000.0,
                    step=1000.0,
                    format="%.2f"
                )

                tasso = st.number_input(
                    "Tasso Interesse Annuo (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=2.0,
                    step=0.1,
                    format="%.2f"
                )

                rata_target = st.number_input(
                    "Rata Mensile Target (€)",
                    min_value=0.0,
                    value=300.0,
                    step=50.0,
                    format="%.2f"
                )

                st.info(f"**Ammortamento Italiano** (quota capitale costante)")

                # Calcola durata necessaria
                if capitale > 0 and rata_target > 0:
                    piano_temp, durata_calcolata = calcola_piano_con_rata_fissa(capitale, tasso, rata_target)

                    if durata_calcolata:
                        durata_anni = durata_calcolata / 12
                        st.success(f"**Durata necessaria:** {durata_anni:.1f} anni ({durata_calcolata} mesi)")
                        st.metric("Rata 1° mese", f"€ {piano_temp.iloc[0]['rata']:,.2f}")
                        st.metric("Rata ultima", f"€ {piano_temp.iloc[-1]['rata']:,.2f}")
                        st.caption("Le rate diminuiranno progressivamente")

                        # Salva durata calcolata in variabile per uso successivo
                        durata_mesi = durata_calcolata
                    else:
                        st.error("⚠️ Rata troppo bassa! Aumenta l'importo della rata.")
                        durata_mesi = 0
                else:
                    st.caption("Inserisci capitale e rata per calcolare la durata")
                    durata_mesi = 0

            with col2:
                st.subheader("Costi Manutenzione")

                descrizione_costo = st.text_input("Descrizione costo:")
                importo_costo = st.number_input("Importo (€):", min_value=0.0, step=100.0, format="%.2f")

                if st.button("Aggiungi Costo"):
                    if descrizione_costo and importo_costo > 0:
                        data["costi_manutenzione"].append({
                            "descrizione": descrizione_costo,
                            "importo": importo_costo,
                            "data": datetime.now().strftime("%Y-%m-%d")
                        })
                        save_data(data)
                        st.success(f"Costo aggiunto: {descrizione_costo} - € {importo_costo:,.2f}")
                        st.rerun()

            # Mostra costi
            if data["costi_manutenzione"]:
                st.subheader("Costi Registrati")
                df_costi = pd.DataFrame(data["costi_manutenzione"])
                st.dataframe(df_costi, use_container_width=True)

                # Opzione rimozione
                idx_remove = st.selectbox("Rimuovi costo:", range(len(data["costi_manutenzione"])), format_func=lambda x: data["costi_manutenzione"][x]["descrizione"])
                if st.button("Rimuovi Costo Selezionato"):
                    data["costi_manutenzione"].pop(idx_remove)
                    save_data(data)
                    st.rerun()

            st.divider()

            # Riepilogo
            capitale_effettivo = capitale - sum(c["importo"] for c in data["costi_manutenzione"])

            col1, col2, col3 = st.columns(3)
            col1.metric("Capitale Iniziale", f"€ {capitale:,.2f}")
            col2.metric("Totale Costi", f"€ {sum(c['importo'] for c in data['costi_manutenzione']):,.2f}")
            col3.metric("Capitale Effettivo", f"€ {capitale_effettivo:,.2f}", delta=f"{-sum(c['importo'] for c in data['costi_manutenzione']):,.2f}")

            # Mostra piano ammortamento
            if capitale_effettivo > 0 and durata_mesi > 0:
                st.subheader("Piano Ammortamento (prime 12 rate)")
                piano = calcola_piano_ammortamento_italiano(capitale_effettivo, tasso, durata_mesi)

                # Mostra solo prime 12 rate
                piano_preview = piano.head(12).copy()
                piano_preview.columns = ['Mese', 'Data Scadenza', 'Quota Capitale', 'Quota Interessi', 'Rata', 'Debito Residuo']

                # Formatta valori
                for col in ['Quota Capitale', 'Quota Interessi', 'Rata', 'Debito Residuo']:
                    piano_preview[col] = piano_preview[col].apply(lambda x: f"€ {x:,.2f}")

                st.dataframe(piano_preview, use_container_width=True, hide_index=True)

                # Statistiche
                totale_interessi = piano['quota_interessi'].sum()
                totale_da_pagare = capitale_effettivo + totale_interessi
                durata_anni_display = durata_mesi / 12

                col1, col2, col3 = st.columns(3)
                col1.metric("Totale Interessi", f"€ {totale_interessi:,.2f}")
                col2.metric("Totale da Pagare", f"€ {totale_da_pagare:,.2f}")
                col3.metric("Durata", f"{durata_anni_display:.1f} anni ({durata_mesi} mesi)")

            if st.button("✅ Conferma Configurazione", type="primary"):
                if durata_mesi > 0:
                    data["capitale_iniziale"] = capitale
                    data["durata_mesi"] = durata_mesi
                    data["durata_originale"] = durata_mesi  # Salva durata originale
                    data["tasso_annuo"] = tasso
                    data["tipo_ammortamento"] = "italiano"
                    data["rata_target"] = rata_target
                    data["configurato"] = True
                    data["rate_saltate"] = []  # Inizializza lista rate saltate
                    save_data(data)
                    st.success("Configurazione completata!")
                    st.rerun()
                else:
                    st.error("Configura correttamente i parametri prima di confermare!")

    else:
        # Dashboard
        with tab1 if st.session_state['role'] == "creditore" else tab1:
            st.header("Dashboard Riepilogativa")

            capitale_effettivo = calcola_capitale_effettivo(data)
            capitale_residuo = calcola_capitale_residuo(data)
            totale_pagato = sum(p["importo"] for p in data["pagamenti"] if p.get("confermato", False))
            rate_pagate = len([p for p in data["pagamenti"] if p.get("confermato", False)])

            # Calcola piano ammortamento
            piano_completo = calcola_piano_ammortamento_italiano(
                capitale_effettivo,
                data["tasso_annuo"],
                data["durata_mesi"]
            )

            # Calcola durata effettiva e rate saltate
            durata_effettiva = calcola_durata_effettiva(data)
            num_rate_saltate = len(data.get("rate_saltate", []))

            # Calcola durata dinamica con pagamenti variabili
            durata_stimata_variabile = calcola_durata_effettiva_con_pagamenti_variabili(data)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Capitale Effettivo", f"€ {capitale_effettivo:,.2f}")
            col2.metric("Totale Pagato", f"€ {totale_pagato:,.2f}")
            col3.metric("Capitale Residuo", f"€ {capitale_residuo:,.2f}")

            # Mostra durata dinamica
            if rate_pagate > 0:
                durata_originale = data.get("durata_originale", data["durata_mesi"])
                delta_durata = durata_stimata_variabile - durata_originale

                if delta_durata != 0:
                    col4.metric(
                        "Durata Stimata",
                        f"{durata_stimata_variabile} mesi",
                        delta=f"{delta_durata:+d} mesi",
                        delta_color="inverse"  # Verde se negativo (meno mesi), rosso se positivo (più mesi)
                    )

                    # Info box con spiegazione
                    if delta_durata > 0:
                        st.info(f"📊 **Rate Variabili Attive:** La durata stimata è aumentata di {delta_durata} mesi rispetto al piano originale ({durata_originale} mesi) a causa di pagamenti inferiori alla rata target di €{data.get('rata_target', 300):,.2f}")
                    elif delta_durata < 0:
                        st.success(f"🎉 **Rate Variabili Attive:** La durata stimata è diminuita di {abs(delta_durata)} mesi rispetto al piano originale ({durata_originale} mesi) grazie a pagamenti superiori alla rata target di €{data.get('rata_target', 300):,.2f}!")
                else:
                    col4.metric("Durata", f"{data['durata_mesi']} mesi")
            else:
                col4.metric("Durata", f"{data['durata_mesi']} mesi")

            if num_rate_saltate > 0:
                col4.metric(
                    "Rate Pagate / Totali",
                    f"{rate_pagate} / {durata_effettiva}",
                    delta=f"+{num_rate_saltate} rate saltate",
                    delta_color="inverse"
                )
            else:
                col4.metric("Rate Pagate / Totali", f"{rate_pagate} / {data['durata_mesi']}")

            # Versamenti straordinari
            totale_straordinari = calcola_totale_versamenti_straordinari(data)
            if totale_straordinari > 0:
                st.info(f"💰 **Versamenti straordinari:** € {totale_straordinari:,.2f} (riduce la durata del piano)")

            # Grafico progresso
            st.subheader("Progresso Pagamento")
            progresso = (totale_pagato / capitale_effettivo * 100) if capitale_effettivo > 0 else 0
            st.progress(progresso / 100)
            st.write(f"**{progresso:.1f}%** completato")

            # Prossima rata
            if rate_pagate < data["durata_mesi"]:
                prossima_rata = piano_completo.iloc[rate_pagate]
                st.info(f"**Prossima Rata ({rate_pagate + 1}):** € {prossima_rata['rata']:,.2f}\n\n"
                       f"Scadenza: {prossima_rata['data_scadenza']} (Capitale: € {prossima_rata['quota_capitale']:,.2f} + Interessi: € {prossima_rata['quota_interessi']:,.2f})")

            # Rate in attesa conferma
            rate_pending = [p for p in data["pagamenti"] if not p.get("confermato", False)]
            if rate_pending and st.session_state['role'] == "creditore":
                st.warning(f"⚠️ {len(rate_pending)} rata/e in attesa di conferma")

            # Mostra piano ammortamento (prime rate e ultime)
            st.subheader("Piano Ammortamento")
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Prime 6 rate:**")
                piano_prime = piano_completo.head(6).copy()
                piano_prime.columns = ['Mese', 'Data Scadenza', 'Quota Capitale', 'Quota Interessi', 'Rata', 'Debito Residuo']
                for col in ['Quota Capitale', 'Quota Interessi', 'Rata', 'Debito Residuo']:
                    piano_prime[col] = piano_prime[col].apply(lambda x: f"€ {x:,.2f}")
                st.dataframe(piano_prime, use_container_width=True, hide_index=True)

            with col2:
                st.write("**Ultime 6 rate:**")
                piano_ultime = piano_completo.tail(6).copy()
                piano_ultime.columns = ['Mese', 'Data Scadenza', 'Quota Capitale', 'Quota Interessi', 'Rata', 'Debito Residuo']
                for col in ['Quota Capitale', 'Quota Interessi', 'Rata', 'Debito Residuo']:
                    piano_ultime[col] = piano_ultime[col].apply(lambda x: f"€ {x:,.2f}")
                st.dataframe(piano_ultime, use_container_width=True, hide_index=True)

            # Grafici riassuntivi
            st.subheader("📊 Grafici Riassuntivi")

            # Crea grafici matplotlib
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')

            # Grafico 1: Evoluzione ammortamento
            fig1, ax1 = plt.subplots(figsize=(12, 6))

            mesi = piano_completo['mese'].values
            capitale_cumulativo = piano_completo['quota_capitale'].cumsum().values
            interessi_cumulativo = piano_completo['quota_interessi'].cumsum().values
            debito_residuo = piano_completo['debito_residuo'].values

            ax1.fill_between(mesi, 0, capitale_cumulativo, alpha=0.7, color='#4caf50', label='Capitale Pagato')
            ax1.fill_between(mesi, capitale_cumulativo, capitale_cumulativo + interessi_cumulativo,
                             alpha=0.7, color='#ff9800', label='Interessi Pagati')
            ax1.plot(mesi, debito_residuo, color='#d32f2f', linewidth=2.5, label='Debito Residuo', linestyle='--')

            if rate_pagate > 0:
                ax1.axvline(x=rate_pagate, color='#1f4788', linewidth=2, linestyle=':', label=f'Rate Pagate ({rate_pagate})')

            ax1.set_xlabel('Mese', fontsize=11, fontweight='bold')
            ax1.set_ylabel('Importo (€)', fontsize=11, fontweight='bold')
            ax1.set_title('Evoluzione Piano Ammortamento nel Tempo', fontsize=13, fontweight='bold', pad=15)
            ax1.legend(loc='best', frameon=True, shadow=True)
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))

            st.pyplot(fig1)
            plt.close(fig1)

            # Grafico 2: Torta composizione
            col1, col2, col3 = st.columns([1, 2, 1])

            with col2:
                fig2, ax2 = plt.subplots(figsize=(8, 8))

                totale_capitale = piano_completo['quota_capitale'].sum()
                totale_interessi = piano_completo['quota_interessi'].sum()

                sizes = [totale_capitale, totale_interessi]
                labels = [f'Capitale\n€{totale_capitale:,.2f}', f'Interessi\n€{totale_interessi:,.2f}']
                colors = ['#4caf50', '#ff9800']
                explode = (0.05, 0)

                wedges, texts, autotexts = ax2.pie(sizes, explode=explode, labels=labels, colors=colors,
                                                    autopct='%1.1f%%', startangle=90, textprops={'fontsize': 11})

                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(12)

                for text in texts:
                    text.set_fontsize(12)
                    text.set_fontweight('bold')

                ax2.set_title('Composizione Totale Pagamento', fontsize=14, fontweight='bold', pad=20)

                totale = totale_capitale + totale_interessi
                ax2.text(0, -1.3, f'Totale da Pagare: €{totale:,.2f}',
                        ha='center', fontsize=13, fontweight='bold',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

                st.pyplot(fig2)
                plt.close(fig2)

        # TAB 2: Registra Pagamento (Mattia) o Gestione Rate (Guglielmo)
        if st.session_state['role'] == "debitore":
            with tab2:
                st.header("Registra Pagamento Rata")

                # Calcola prossima rata
                rate_pagate = len([p for p in data["pagamenti"] if p.get("confermato", False)])
                capitale_effettivo = calcola_capitale_effettivo(data)
                piano = calcola_piano_ammortamento_italiano(capitale_effettivo, data["tasso_annuo"], data["durata_mesi"])

                if rate_pagate < data["durata_mesi"]:
                    prossima_rata_info = piano.iloc[rate_pagate]
                    durata_effettiva = calcola_durata_effettiva(data)
                    num_rate_saltate = len(data.get("rate_saltate", []))

                    st.info(f"**Rata {rate_pagate + 1} di {data['durata_mesi']}**" +
                           (f" (Durata totale: {durata_effettiva} mesi - {num_rate_saltate} saltate)" if num_rate_saltate > 0 else "") +
                           f"\n\n**Data Scadenza:** {prossima_rata_info['data_scadenza']}\n\n"
                           f"Importo suggerito: € {prossima_rata_info['rata']:,.2f}\n\n"
                           f"- Quota Capitale: € {prossima_rata_info['quota_capitale']:,.2f}\n"
                           f"- Quota Interessi: € {prossima_rata_info['quota_interessi']:,.2f}")

                    # Info su pagamenti variabili
                    st.success("💡 **Pagamenti Flessibili:** Puoi pagare un importo diverso ogni mese (meno o più di €300). Il sistema ricalcolerà automaticamente la durata rimanente.")

                    col1, col2 = st.columns(2)

                    with col1:
                        data_pagamento = st.date_input("Data Pagamento:", value=date.today())
                        importo = st.number_input(
                            "Importo (€) - Modifica liberamente:",
                            min_value=0.01,
                            value=float(prossima_rata_info['rata']),
                            step=10.0,
                            format="%.2f",
                            help="Puoi inserire qualsiasi importo. Pagamenti maggiori riducono la durata, pagamenti minori la allungano."
                        )

                    with col2:
                        causale_bonifico = st.text_input(
                            "Causale Bonifico:",
                            value=f"Rata {rate_pagate + 1} - Piano Ammortamento Appartamento",
                            help="Causale del bonifico bancario"
                        )
                        note = st.text_area("Note aggiuntive (opzionale):", height=100)

                    st.subheader("🏦 Dati Bonifico Bancario")
                    col3, col4 = st.columns(2)

                    with col3:
                        iban_mittente = st.text_input(
                            "IBAN Mittente (tuo IBAN):",
                            value=data.get("iban_mattia", ""),
                            help="Il tuo IBAN da cui hai effettuato il bonifico"
                        )

                    with col4:
                        iban_beneficiario = st.text_input(
                            "IBAN Beneficiario (IBAN Guglielmo):",
                            value=data.get("iban_guglielmo", ""),
                            help="IBAN di Guglielmo a cui hai inviato il bonifico"
                        )

                    # Anteprima impatto pagamento variabile
                    if importo != float(prossima_rata_info['rata']):
                        capitale_residuo = calcola_capitale_residuo(data)
                        # Simula il pagamento
                        capitale_dopo_pagamento = capitale_residuo - importo

                        if capitale_dopo_pagamento <= 0:
                            st.success("🎉 **Con questo pagamento salderai completamente il debito!**")
                        else:
                            # Calcola durata rimanente con la rata target
                            rata_target = data.get("rata_target", 300.0)
                            durata_rimanente = calcola_durata_da_rata(capitale_dopo_pagamento, data['tasso_annuo'], rata_target)

                            if durata_rimanente:
                                durata_attuale = calcola_durata_effettiva_con_pagamenti_variabili(data)
                                durata_nuova_stimata = rate_pagate + 1 + durata_rimanente
                                delta_mesi = durata_nuova_stimata - durata_attuale

                                if abs(importo - float(prossima_rata_info['rata'])) > 1.0:  # Solo se differenza > €1
                                    if delta_mesi < 0:
                                        st.success(f"📉 **Impatto:** Pagando €{importo:,.2f} (invece di €{prossima_rata_info['rata']:,.2f}), la durata stimata si riduce di circa **{abs(delta_mesi):.0f} mesi**")
                                    elif delta_mesi > 0:
                                        st.warning(f"📈 **Impatto:** Pagando €{importo:,.2f} (invece di €{prossima_rata_info['rata']:,.2f}), la durata stimata aumenta di circa **{delta_mesi:.0f} mesi**")

                    st.divider()

                    # Sezione Versamento Straordinario
                    with st.expander("💰 Versamento Straordinario (Una Tantum)", expanded=False):
                        st.write("**Effettua un versamento extra per ridurre la durata del finanziamento**")

                        capitale_residuo = calcola_capitale_residuo(data)
                        st.info(f"Capitale residuo attuale: € {capitale_residuo:,.2f}")

                        importo_straordinario = st.number_input(
                            "Importo versamento straordinario (€):",
                            min_value=0.0,
                            max_value=float(capitale_residuo),
                            value=0.0,
                            step=100.0,
                            format="%.2f",
                            key="importo_straord"
                        )

                        if importo_straordinario > 0:
                            # Calcola impatto
                            rata_mensile = data.get("rata_target", 300.0)
                            nuova_durata = calcola_nuova_durata_con_straordinari(
                                capitale_residuo,
                                data["tasso_annuo"],
                                rata_mensile,
                                importo_straordinario
                            )

                            if nuova_durata == 0:
                                st.success("🎉 Con questo versamento saldi completamente il debito!")
                            else:
                                rate_rimanenti_originali = data["durata_mesi"] - rate_pagate
                                mesi_risparmiati = rate_rimanenti_originali - nuova_durata

                                col1, col2 = st.columns(2)
                                col1.metric("Nuova durata", f"{nuova_durata} mesi", delta=f"-{mesi_risparmiati} mesi")
                                col2.metric("Nuova fine prevista", f"{(date.today().year + nuova_durata//12)}")

                        note_straord = st.text_area("Note versamento straordinario:", key="note_straord")

                        if st.button("💸 Registra Versamento Straordinario", type="secondary", use_container_width=True):
                            if importo_straordinario > 0:
                                nuovo_versamento = {
                                    "data": date.today().strftime("%Y-%m-%d"),
                                    "importo": importo_straordinario,
                                    "note": note_straord,
                                    "confermato": False,
                                    "registrato_da": "Mattia",
                                    "timestamp": datetime.now().isoformat()
                                }
                                if "versamenti_straordinari" not in data:
                                    data["versamenti_straordinari"] = []
                                data["versamenti_straordinari"].append(nuovo_versamento)
                                save_data(data)
                                st.success(f"✅ Versamento straordinario di € {importo_straordinario:,.2f} registrato! In attesa di conferma da Guglielmo.")
                                st.rerun()
                            else:
                                st.error("Inserisci un importo maggiore di 0!")

                    st.divider()

                    col_btn1, col_btn2 = st.columns(2)

                    with col_btn1:
                        if st.button("📤 Registra Pagamento Rata", type="primary", use_container_width=True):
                            # Validazione IBAN
                            if not iban_mittente or not iban_beneficiario:
                                st.error("⚠️ Inserisci entrambi gli IBAN prima di procedere!")
                            elif not causale_bonifico:
                                st.error("⚠️ Inserisci la causale del bonifico!")
                            else:
                                nuovo_pagamento = {
                                    "data": data_pagamento.strftime("%Y-%m-%d"),
                                    "importo": importo,
                                    "numero_rata": rate_pagate + 1,
                                    "note": note,
                                    "causale": causale_bonifico,
                                    "iban_mittente": iban_mittente,
                                    "iban_beneficiario": iban_beneficiario,
                                    "confermato": False,
                                    "registrato_da": "Mattia",
                                    "timestamp": datetime.now().isoformat()
                                }
                                data["pagamenti"].append(nuovo_pagamento)
                                save_data(data)

                                # Genera cedolino "eseguito" e invia email
                                try:
                                    pdf_cedolino = genera_cedolino_bonifico(nuovo_pagamento, data, rate_pagate + 1, stato="eseguito")

                                    # Prepara email
                                    destinatari = [data.get("email_guglielmo", ""), data.get("email_mattia", "")]
                                    destinatari = [e for e in destinatari if e]  # Rimuovi email vuote

                                    if destinatari and data.get("smtp_email"):
                                        oggetto = f"🏦 Bonifico Eseguito - Rata {rate_pagate + 1}"
                                        corpo = f"""
                                        <html>
                                        <body style="font-family: Arial, sans-serif;">
                                            <h2 style="color: #1f4788;">Bonifico Eseguito - Rata {rate_pagate + 1}</h2>
                                            <p>Ciao,</p>
                                            <p><strong>Mattia</strong> ha registrato un nuovo pagamento:</p>
                                            <ul>
                                                <li><strong>Data:</strong> {data_pagamento.strftime("%d/%m/%Y")}</li>
                                                <li><strong>Importo:</strong> €{importo:,.2f}</li>
                                                <li><strong>Causale:</strong> {causale_bonifico}</li>
                                                <li><strong>IBAN Mittente:</strong> {iban_mittente}</li>
                                                <li><strong>IBAN Beneficiario:</strong> {iban_beneficiario}</li>
                                            </ul>
                                            <p><strong>Stato:</strong> ⏳ In attesa di verifica da Guglielmo</p>
                                            <p>Il cedolino è allegato a questa email.</p>
                                            <hr>
                                            <p style="font-size: 12px; color: #666;">Piano Ammortamento Appartamento - Notifica Automatica</p>
                                        </body>
                                        </html>
                                        """

                                        success, message = invia_email_con_allegato(destinatari, oggetto, corpo, pdf_cedolino, data)

                                        if success:
                                            st.success(f"✅ Pagamento registrato e email inviate a {', '.join(destinatari)}!")
                                        else:
                                            st.success("✅ Pagamento registrato!")
                                            st.warning(f"⚠️ Email non inviate: {message}")
                                    else:
                                        st.success("✅ Pagamento registrato! In attesa di conferma da Guglielmo.")
                                        if not data.get("smtp_email"):
                                            st.info("ℹ️ Configura SMTP per abilitare l'invio automatico email.")

                                except Exception as e:
                                    st.success("✅ Pagamento registrato!")
                                    st.warning(f"⚠️ Errore invio email: {str(e)}")

                                st.rerun()

                    with col_btn2:
                        if st.button("⏭️ Salta Questa Rata", type="secondary", use_container_width=True):
                            # Registra rata saltata
                            rata_saltata = {
                                "numero_rata": rate_pagate + 1,
                                "data": datetime.now().strftime("%Y-%m-%d"),
                                "motivo": note if note else "Rata saltata",
                                "registrato_da": "Mattia",
                                "timestamp": datetime.now().isoformat()
                            }
                            if "rate_saltate" not in data:
                                data["rate_saltate"] = []
                            data["rate_saltate"].append(rata_saltata)

                            # Estendi durata di 1 mese
                            data["durata_mesi"] += 1

                            save_data(data)
                            st.warning(f"⏭️ Rata {rate_pagate + 1} saltata! Scadenza finale posticipata di 1 mese.")
                            st.info(f"Nuova durata totale: {data['durata_mesi']} mesi ({data['durata_mesi']/12:.1f} anni)")
                            st.rerun()

                    st.divider()
                    st.caption("**Nota:** Saltando una rata, la scadenza finale viene automaticamente posticipata di 1 mese. "
                              "La rata non viene persa, ma spostata alla fine del piano.")

                else:
                    st.success("🎉 Tutte le rate sono state pagate! Appartamento completamente saldato!")

        else:  # creditore
            with tab2:
                st.header("Gestione Rate")

                # Rate in attesa
                rate_pending = [p for p in data["pagamenti"] if not p.get("confermato", False)]

                if rate_pending:
                    st.subheader("Rate in Attesa di Conferma")

                    for idx, pagamento in enumerate(rate_pending):
                        with st.expander(f"Rata {pagamento.get('numero_rata', idx+1)} del {pagamento['data']} - € {pagamento['importo']:,.2f}"):
                            col_info1, col_info2 = st.columns(2)

                            with col_info1:
                                st.write(f"**Data:** {pagamento['data']}")
                                st.write(f"**Importo:** € {pagamento['importo']:,.2f}")
                                st.write(f"**Causale:** {pagamento.get('causale', 'N/A')}")
                                st.write(f"**Note:** {pagamento.get('note', 'N/A')}")

                            with col_info2:
                                st.write(f"**IBAN Mittente:** {pagamento.get('iban_mittente', 'N/A')}")
                                st.write(f"**IBAN Beneficiario:** {pagamento.get('iban_beneficiario', 'N/A')}")
                                st.write(f"**Registrato da:** {pagamento['registrato_da']}")
                                st.write(f"**Timestamp:** {pagamento.get('timestamp', 'N/A')}")

                            st.divider()
                            col1, col2 = st.columns(2)

                            with col1:
                                if st.button(f"✅ Verifica e Conferma Bonifico", key=f"confirm_{idx}"):
                                    # Trova indice originale
                                    orig_idx = data["pagamenti"].index(pagamento)
                                    data["pagamenti"][orig_idx]["confermato"] = True
                                    data["pagamenti"][orig_idx]["confermato_da"] = "Guglielmo"
                                    data["pagamenti"][orig_idx]["data_conferma"] = datetime.now().isoformat()
                                    data["pagamenti"][orig_idx]["data_verifica"] = datetime.now().strftime("%Y-%m-%d")
                                    save_data(data)

                                    # Genera cedolino verificato e report completo
                                    try:
                                        numero_rata = pagamento.get('numero_rata', len([p for p in data["pagamenti"] if p.get("confermato", False)]))
                                        pdf_cedolino_verificato = genera_cedolino_bonifico(data["pagamenti"][orig_idx], data, numero_rata, stato="verificato")
                                        pdf_report = genera_pdf_report_completo(data)

                                        # Invia email con cedolino verificato + link report
                                        destinatari = [data.get("email_guglielmo", ""), data.get("email_mattia", "")]
                                        destinatari = [e for e in destinatari if e]

                                        if destinatari and data.get("smtp_email"):
                                            oggetto = f"✅ Bonifico Verificato - Rata {numero_rata}"
                                            corpo = f"""
                                            <html>
                                            <body style="font-family: Arial, sans-serif;">
                                                <h2 style="color: #2e7d32;">✅ Bonifico Verificato e Confermato</h2>
                                                <p>Ciao,</p>
                                                <p><strong>Guglielmo</strong> ha verificato e confermato il bonifico:</p>
                                                <ul>
                                                    <li><strong>Rata:</strong> {numero_rata}</li>
                                                    <li><strong>Data Pagamento:</strong> {pagamento['data']}</li>
                                                    <li><strong>Importo:</strong> €{pagamento['importo']:,.2f}</li>
                                                    <li><strong>Causale:</strong> {pagamento.get('causale', 'N/A')}</li>
                                                    <li><strong>Data Verifica:</strong> {datetime.now().strftime("%d/%m/%Y")}</li>
                                                </ul>
                                                <p><strong>Stato:</strong> ✅ Pagamento Confermato</p>
                                                <p>📄 Il cedolino aggiornato è allegato a questa email.</p>
                                                <p>📊 <strong>Report Completo Piano Ammortamento:</strong> {pdf_report}</p>
                                                <hr>
                                                <p style="font-size: 12px; color: #666;">Piano Ammortamento Appartamento - Notifica Automatica</p>
                                            </body>
                                            </html>
                                            """

                                            success, message = invia_email_con_allegato(destinatari, oggetto, corpo, pdf_cedolino_verificato, data)

                                            if success:
                                                st.success(f"✅ Bonifico verificato! Email inviate a {', '.join(destinatari)}")
                                            else:
                                                st.success(f"✅ Bonifico verificato! PDF: {pdf_cedolino_verificato}")
                                                st.warning(f"⚠️ Email non inviate: {message}")
                                        else:
                                            st.success(f"✅ Bonifico verificato! PDF: {pdf_cedolino_verificato}")
                                            if not data.get("smtp_email"):
                                                st.info("ℹ️ Configura SMTP per abilitare email automatiche.")

                                    except Exception as e:
                                        st.success("✅ Bonifico verificato!")
                                        st.warning(f"⚠️ Errore generazione PDF/email: {str(e)}")

                                    st.rerun()

                            with col2:
                                if st.button(f"❌ Rifiuta", key=f"reject_{idx}"):
                                    orig_idx = data["pagamenti"].index(pagamento)
                                    data["pagamenti"].pop(orig_idx)
                                    save_data(data)
                                    st.warning("Pagamento rifiutato e rimosso.")
                                    st.rerun()
                else:
                    st.info("Nessuna rata in attesa di conferma.")

                st.divider()

                # Versamenti Straordinari in attesa
                versamenti_pending = [v for v in data.get("versamenti_straordinari", []) if not v.get("confermato", False)]

                if versamenti_pending:
                    st.subheader("💰 Versamenti Straordinari in Attesa")

                    for idx, versamento in enumerate(versamenti_pending):
                        with st.expander(f"Versamento del {versamento['data']} - € {versamento['importo']:,.2f}"):
                            st.write(f"**Data:** {versamento['data']}")
                            st.write(f"**Importo:** € {versamento['importo']:,.2f}")
                            st.write(f"**Note:** {versamento.get('note', 'N/A')}")
                            st.write(f"**Registrato da:** {versamento['registrato_da']}")

                            # Calcola impatto
                            capitale_residuo = calcola_capitale_residuo(data)
                            rata_mensile = data.get("rata_target", 300.0)
                            rate_pagate = len([p for p in data["pagamenti"] if p.get("confermato", False)])

                            nuova_durata = calcola_nuova_durata_con_straordinari(
                                capitale_residuo,
                                data["tasso_annuo"],
                                rata_mensile,
                                versamento['importo']
                            )

                            if nuova_durata == 0:
                                st.success("🎉 Questo versamento salda completamente il debito!")
                            else:
                                rate_rimanenti = data["durata_mesi"] - rate_pagate
                                mesi_risparmiati = rate_rimanenti - nuova_durata
                                st.info(f"**Impatto:** Riduzione durata di {mesi_risparmiati} mesi (da {rate_rimanenti} a {nuova_durata} mesi)")

                            col1, col2 = st.columns(2)

                            with col1:
                                if st.button(f"✅ Conferma Versamento", key=f"confirm_straord_{idx}"):
                                    # Trova indice originale
                                    orig_idx = data["versamenti_straordinari"].index(versamento)
                                    data["versamenti_straordinari"][orig_idx]["confermato"] = True
                                    data["versamenti_straordinari"][orig_idx]["confermato_da"] = "Guglielmo"
                                    data["versamenti_straordinari"][orig_idx]["data_conferma"] = datetime.now().isoformat()

                                    # Aggiorna durata
                                    if nuova_durata == 0:
                                        data["durata_mesi"] = rate_pagate  # Tutto saldato
                                    else:
                                        data["durata_mesi"] = rate_pagate + nuova_durata

                                    save_data(data)
                                    st.success(f"✅ Versamento straordinario confermato! Durata aggiornata.")
                                    st.rerun()

                            with col2:
                                if st.button(f"❌ Rifiuta", key=f"reject_straord_{idx}"):
                                    orig_idx = data["versamenti_straordinari"].index(versamento)
                                    data["versamenti_straordinari"].pop(orig_idx)
                                    save_data(data)
                                    st.warning("Versamento rifiutato e rimosso.")
                                    st.rerun()

        # TAB 3: Spese Ripristino (tutti possono vedere)
        with tab3:
            st.header("🔧 Spese di Ripristino Appartamento")

            st.write("Questa sezione contiene tutte le spese sostenute per il ripristino dell'appartamento.")
            st.write("**Queste spese vengono detratte dal capitale iniziale** per calcolare il capitale effettivo da pagare.")

            # Solo creditore può aggiungere/modificare
            if st.session_state['role'] == "creditore":
                st.subheader("Aggiungi Nuova Spesa")

                col1, col2, col3 = st.columns(3)

                with col1:
                    categoria = st.selectbox(
                        "Categoria:",
                        ["Imbiancatura", "Idraulica", "Elettricità", "Pavimenti", "Serramenti",
                         "Riscaldamento", "Mobili", "Elettrodomestici", "Altro"]
                    )

                with col2:
                    descrizione = st.text_input("Descrizione dettagliata:")

                with col3:
                    importo_spesa = st.number_input("Importo (€):", min_value=0.0, step=50.0, format="%.2f")

                col_data, col_fornitore = st.columns(2)

                with col_data:
                    data_spesa = st.date_input("Data spesa:", value=date.today())

                with col_fornitore:
                    fornitore = st.text_input("Fornitore/Note:")

                if st.button("➕ Aggiungi Spesa", type="primary"):
                    if descrizione and importo_spesa > 0:
                        nuova_spesa = {
                            "categoria": categoria,
                            "descrizione": descrizione,
                            "importo": importo_spesa,
                            "data": data_spesa.strftime("%Y-%m-%d"),
                            "fornitore": fornitore,
                            "timestamp": datetime.now().isoformat()
                        }
                        data["costi_manutenzione"].append(nuova_spesa)
                        save_data(data)
                        st.success(f"✅ Spesa aggiunta: {descrizione} - € {importo_spesa:,.2f}")
                        st.rerun()
                    else:
                        st.error("Inserisci descrizione e importo validi!")

                st.divider()

            # Mostra riepilogo spese (tutti)
            if data["costi_manutenzione"]:
                st.subheader("Riepilogo Spese")

                # Totale per categoria
                df_costi = pd.DataFrame(data["costi_manutenzione"])

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Totale Spese Ripristino", f"€ {df_costi['importo'].sum():,.2f}")

                with col2:
                    st.metric("Numero Voci", f"{len(df_costi)}")

                # Grafico per categoria
                if 'categoria' in df_costi.columns:
                    st.subheader("Spese per Categoria")
                    spese_categoria = df_costi.groupby('categoria')['importo'].sum().sort_values(ascending=False)

                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.bar_chart(spese_categoria)

                    with col2:
                        st.write("**Dettaglio:**")
                        for cat, importo in spese_categoria.items():
                            st.write(f"**{cat}:** € {importo:,.2f}")

                st.divider()

                # Tabella dettagliata
                st.subheader("Dettaglio Completo Spese")

                # Ordina per data
                df_costi_sorted = df_costi.sort_values('data', ascending=False)

                # Formatta per visualizzazione
                df_display = df_costi_sorted.copy()

                # Rimuovi timestamp se presente
                if 'timestamp' in df_display.columns:
                    df_display = df_display.drop('timestamp', axis=1)

                # Formatta importo
                df_display['importo'] = df_display['importo'].apply(lambda x: f"€ {x:,.2f}")

                # Seleziona e rinomina solo le colonne necessarie
                if 'categoria' in df_display.columns:
                    df_display = df_display[['categoria', 'descrizione', 'importo', 'data', 'fornitore']]
                    df_display.columns = ['Categoria', 'Descrizione', 'Importo', 'Data', 'Fornitore/Note']
                else:
                    df_display = df_display[['descrizione', 'importo', 'data']]
                    df_display.columns = ['Descrizione', 'Importo', 'Data']

                st.dataframe(df_display, use_container_width=True, hide_index=True)

                # Opzione rimozione (solo creditore)
                if st.session_state['role'] == "creditore" and len(data["costi_manutenzione"]) > 0:
                    st.divider()
                    st.subheader("Gestione Spese")

                    col1, col2 = st.columns([3, 1])

                    with col1:
                        idx_remove = st.selectbox(
                            "Seleziona spesa da rimuovere:",
                            range(len(data["costi_manutenzione"])),
                            format_func=lambda x: f"{data['costi_manutenzione'][x].get('categoria', 'N/A')} - {data['costi_manutenzione'][x]['descrizione']} - € {data['costi_manutenzione'][x]['importo']:,.2f}"
                        )

                    with col2:
                        if st.button("🗑️ Rimuovi Spesa", type="secondary"):
                            spesa_rimossa = data["costi_manutenzione"].pop(idx_remove)
                            save_data(data)
                            st.warning(f"Spesa rimossa: {spesa_rimossa['descrizione']}")
                            st.rerun()

            else:
                st.info("📋 Nessuna spesa registrata. " +
                       ("Usa il modulo sopra per aggiungere spese." if st.session_state['role'] == "creditore" else ""))

            # Impatto sul capitale
            st.divider()
            st.subheader("Impatto sul Capitale")

            capitale_iniziale = data.get("capitale_iniziale", 0)
            totale_costi = sum(c["importo"] for c in data["costi_manutenzione"])
            capitale_effettivo = capitale_iniziale - totale_costi

            col1, col2, col3 = st.columns(3)
            col1.metric("Capitale Iniziale", f"€ {capitale_iniziale:,.2f}")
            col2.metric("Totale Spese Ripristino", f"€ {totale_costi:,.2f}", delta=f"-{totale_costi:,.2f}")
            col3.metric("Capitale Effettivo da Pagare", f"€ {capitale_effettivo:,.2f}")

        # TAB 4: Configurazione (solo creditore)
        if st.session_state['role'] == "creditore":
            with tab4:
                st.header("Modifica Configurazione")
                st.warning("⚠️ Modificare questi valori influenzerà i calcoli!")

                nuovo_capitale = st.number_input(
                    "Capitale Iniziale (€)",
                    value=data["capitale_iniziale"],
                    step=1000.0
                )

                nuovo_tasso = st.number_input(
                    "Tasso Interesse Annuo (%)",
                    value=data.get("tasso_annuo", 2.0),
                    step=0.1,
                    format="%.2f"
                )

                nuova_durata_anni = st.number_input(
                    "Durata (anni)",
                    value=data.get("durata_mesi", 120) // 12,
                    step=1
                )

                st.divider()
                st.subheader("📧 Configurazione Email e IBAN")

                col1, col2 = st.columns(2)
                with col1:
                    email_guglielmo = st.text_input(
                        "Email Guglielmo (Creditore)",
                        value=data.get("email_guglielmo", ""),
                        help="Email per ricevere notifiche pagamenti"
                    )
                    iban_guglielmo = st.text_input(
                        "IBAN Guglielmo (Beneficiario)",
                        value=data.get("iban_guglielmo", ""),
                        help="IBAN del conto corrente di Guglielmo"
                    )

                with col2:
                    email_mattia = st.text_input(
                        "Email Mattia (Debitore)",
                        value=data.get("email_mattia", ""),
                        help="Email per ricevere conferme pagamenti"
                    )
                    iban_mattia = st.text_input(
                        "IBAN Mattia (Mittente)",
                        value=data.get("iban_mattia", ""),
                        help="IBAN del conto corrente di Mattia"
                    )

                st.divider()
                st.subheader("📮 Configurazione Server SMTP")
                st.info("💡 Per Gmail: usa la tua email Gmail e genera una 'App Password' da https://myaccount.google.com/apppasswords")

                smtp_email = st.text_input(
                    "Email SMTP (per invio notifiche)",
                    value=data.get("smtp_email", ""),
                    help="Email usata per inviare le notifiche (es. tua email Gmail)"
                )

                smtp_password = st.text_input(
                    "Password SMTP / App Password",
                    value=data.get("smtp_password", ""),
                    type="password",
                    help="App Password generata da Gmail (non la password normale!)"
                )

                col3, col4 = st.columns(2)
                with col3:
                    smtp_server = st.text_input(
                        "Server SMTP",
                        value=data.get("smtp_server", "smtp.gmail.com"),
                        help="Default: smtp.gmail.com"
                    )
                with col4:
                    smtp_port = st.number_input(
                        "Porta SMTP",
                        value=data.get("smtp_port", 587),
                        step=1,
                        help="Default: 587 (TLS)"
                    )

                if st.button("Aggiorna Configurazione"):
                    data["capitale_iniziale"] = nuovo_capitale
                    data["tasso_annuo"] = nuovo_tasso
                    data["durata_mesi"] = nuova_durata_anni * 12
                    data["email_guglielmo"] = email_guglielmo
                    data["email_mattia"] = email_mattia
                    data["iban_guglielmo"] = iban_guglielmo
                    data["iban_mattia"] = iban_mattia
                    data["smtp_email"] = smtp_email
                    data["smtp_password"] = smtp_password
                    data["smtp_server"] = smtp_server
                    data["smtp_port"] = smtp_port
                    save_data(data)
                    st.success("Configurazione aggiornata!")
                    st.rerun()

        # TAB 4: Impostazioni (solo debitore)
        if st.session_state['role'] == "debitore":
            with tab4:
                st.header("⚙️ Impostazioni Personali")
                st.info("Configura qui i tuoi dati personali per i bonifici e le notifiche email.")

                st.subheader("📧 Dati Personali")

                col1, col2 = st.columns(2)

                with col1:
                    email_mattia_personale = st.text_input(
                        "La Tua Email",
                        value=data.get("email_mattia", ""),
                        help="Email dove riceverai le conferme dei pagamenti",
                        key="email_mattia_settings"
                    )

                with col2:
                    iban_mattia_personale = st.text_input(
                        "Il Tuo IBAN",
                        value=data.get("iban_mattia", ""),
                        help="IBAN del tuo conto corrente (precompilato nei bonifici)",
                        key="iban_mattia_settings"
                    )

                st.divider()

                st.subheader("ℹ️ Informazioni")

                col_info1, col_info2 = st.columns(2)

                with col_info1:
                    st.metric("Email Guglielmo (Creditore)", data.get("email_guglielmo", "Non configurato"))
                    st.caption("Destinatario delle notifiche di pagamento")

                with col_info2:
                    st.metric("IBAN Guglielmo (Beneficiario)", data.get("iban_guglielmo", "Non configurato"))
                    st.caption("IBAN dove inviare i bonifici")

                st.divider()

                if st.button("💾 Salva Impostazioni", type="primary", use_container_width=True):
                    data["email_mattia"] = email_mattia_personale
                    data["iban_mattia"] = iban_mattia_personale
                    save_data(data)
                    st.success("✅ Impostazioni salvate con successo!")
                    st.rerun()

                st.divider()
                st.caption("💡 **Nota:** Solo Guglielmo può modificare la configurazione SMTP per l'invio email automatiche.")

        # TAB 5 (creditore) o TAB 5 (debitore): Storico
        with tab5:
            st.header("Storico Pagamenti")

            # Pulsante per generare PDF report completo
            if st.button("📄 Genera Report PDF Completo", type="primary", use_container_width=True):
                try:
                    pdf_filename = genera_pdf_report_completo(data)
                    st.success(f"✅ Report PDF generato con successo: **{pdf_filename}**")
                    st.info("Il file è stato salvato nella cartella 'reports' dell'applicazione. Puoi scaricarlo e conservarlo.")
                except Exception as e:
                    st.error(f"❌ Errore durante la generazione del PDF: {str(e)}")

            st.divider()

            rate_confermate = [p for p in data["pagamenti"] if p.get("confermato", False)]

            # Sezione Generazione Cedolini Individuali
            if rate_confermate:
                st.subheader("📋 Genera Cedolini Individuali")
                st.write("Genera e stampa cedolini per singole rate pagate (per garanzia e documentazione fiscale)")

                # Calcola piano completo per i cedolini
                capitale_eff = calcola_capitale_effettivo(data)
                piano_completo = calcola_piano_ammortamento_italiano(capitale_eff, data['tasso_annuo'], data['durata_mesi'])

                # Crea mapping pagamenti per numero rata
                pagamenti_map = {}
                for idx, pag in enumerate(sorted(rate_confermate, key=lambda x: x['data']), 1):
                    pagamenti_map[idx] = pag

                # Opzioni per selezionare le rate
                col1, col2 = st.columns([3, 1])

                with col1:
                    rate_disponibili = list(pagamenti_map.keys())
                    rate_disponibili_str = [f"Rata {n} - {pagamenti_map[n]['data']}" for n in rate_disponibili]

                    rate_selezionate = st.multiselect(
                        "Seleziona le rate per cui generare i cedolini:",
                        options=rate_disponibili,
                        format_func=lambda x: f"Rata {x} - {pagamenti_map[x]['data']} (€ {pagamenti_map[x]['importo']:,.2f})",
                        default=[]
                    )

                with col2:
                    st.write("")
                    st.write("")
                    if st.checkbox("Seleziona tutte"):
                        rate_selezionate = rate_disponibili

                if rate_selezionate:
                    if st.button(f"🖨️ Genera {len(rate_selezionate)} Cedolino/i", type="secondary", use_container_width=True):
                        cedolini_generati = []
                        errori = []

                        with st.spinner(f"Generazione di {len(rate_selezionate)} cedolino/i in corso..."):
                            for num_rata in rate_selezionate:
                                try:
                                    pag = pagamenti_map[num_rata]
                                    filename = genera_cedolino_rata(pag, data, num_rata, piano_completo)
                                    cedolini_generati.append(f"✓ Rata {num_rata}: {filename}")
                                except Exception as e:
                                    errori.append(f"✗ Rata {num_rata}: {str(e)}")

                        if cedolini_generati:
                            st.success(f"✅ Generati {len(cedolini_generati)} cedolini con successo!")
                            for msg in cedolini_generati:
                                st.text(msg)

                        if errori:
                            st.error("❌ Errori durante la generazione:")
                            for err in errori:
                                st.text(err)

                        if cedolini_generati:
                            st.info("💾 I cedolini sono stati salvati nella cartella dell'applicazione. Conservali per documentazione fiscale e garanzia.")

                st.divider()

            if rate_confermate:
                df_pagamenti = pd.DataFrame(rate_confermate)
                df_pagamenti['data'] = pd.to_datetime(df_pagamenti['data'])
                df_pagamenti = df_pagamenti.sort_values('data', ascending=False)

                # Calcola capitale residuo progressivo
                capitale_eff = calcola_capitale_effettivo(data)
                df_pagamenti['capitale_residuo'] = capitale_eff - df_pagamenti['importo'].cumsum()

                st.dataframe(
                    df_pagamenti[['data', 'importo', 'capitale_residuo', 'note']],
                    use_container_width=True
                )

                # Saldo anticipato
                st.subheader("Calcolo Saldo Anticipato")
                if capitale_residuo > 0:
                    st.info(f"**Per saldare completamente:** € {capitale_residuo:,.2f}")
                else:
                    st.success("🎉 Appartamento completamente pagato!")
            else:
                st.info("Nessun pagamento confermato ancora.")

            # Mostra versamenti straordinari
            st.divider()
            versamenti_confermati = [v for v in data.get("versamenti_straordinari", []) if v.get("confermato", False)]

            if versamenti_confermati:
                st.subheader("💰 Versamenti Straordinari")

                totale_straord = sum(v["importo"] for v in versamenti_confermati)
                st.success(f"**Totale versamenti straordinari:** € {totale_straord:,.2f} - **Riduce la durata del finanziamento**")

                df_straord = pd.DataFrame(versamenti_confermati)
                df_straord['data'] = pd.to_datetime(df_straord['data'])
                df_straord = df_straord.sort_values('data', ascending=False)

                st.dataframe(
                    df_straord[['data', 'importo', 'note']],
                    use_container_width=True
                )

            # Mostra rate saltate
            st.divider()
            rate_saltate = data.get("rate_saltate", [])

            if rate_saltate:
                st.subheader("⏭️ Rate Saltate")

                st.info(f"**Totale rate saltate:** {len(rate_saltate)} - **Scadenza posticipata di:** {len(rate_saltate)} mesi")

                df_saltate = pd.DataFrame(rate_saltate)
                df_saltate['data'] = pd.to_datetime(df_saltate['data'])
                df_saltate = df_saltate.sort_values('data', ascending=False)

                df_display_saltate = df_saltate[['numero_rata', 'data', 'motivo']].copy()
                df_display_saltate.columns = ['Numero Rata', 'Data', 'Motivo']

                st.dataframe(df_display_saltate, use_container_width=True, hide_index=True)

                # Info durata
                durata_originale = data.get("durata_originale", data.get("durata_mesi", 0))
                durata_effettiva = calcola_durata_effettiva(data)

                col1, col2, col3 = st.columns(3)
                col1.metric("Durata Originale", f"{durata_originale} mesi ({durata_originale/12:.1f} anni)")
                col2.metric("Rate Saltate", f"{len(rate_saltate)}")
                col3.metric("Durata Effettiva", f"{durata_effettiva} mesi ({durata_effettiva/12:.1f} anni)", delta=f"+{len(rate_saltate)} mesi")
            else:
                st.info("📋 Nessuna rata saltata")

if __name__ == "__main__":
    main()
