from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.shared import Cm

# ============================================
# CRIA DOCUMENTO
# ============================================

doc = Document()

# ============================================
# CONFIGURA MARGENS
# ============================================

section = doc.sections[0]
section.top_margin = Cm(2.5)
section.bottom_margin = Cm(2.5)
section.left_margin = Cm(2.5)
section.right_margin = Cm(2.5)

# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def add_title(text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(26)
    run.font.color.rgb = RGBColor(31, 78, 121)
    run.font.name = 'Arial'


def add_h1(text):
    p = doc.add_heading(level=1)

    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(20)
    run.font.color.rgb = RGBColor(31, 78, 121)
    run.font.name = 'Arial'


def add_h2(text):
    p = doc.add_heading(level=2)

    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(16)
    run.font.color.rgb = RGBColor(46, 117, 182)
    run.font.name = 'Arial'


def add_paragraph(text, bold=False):
    p = doc.add_paragraph()

    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(11)
    run.font.name = 'Arial'


def add_formula(text):
    p = doc.add_paragraph()

    run = p.add_run(text)
    run.font.name = 'Courier New'
    run.font.size = Pt(10)
    run.bold = True


def add_bullet(text):
    p = doc.add_paragraph(style='List Bullet')

    run = p.add_run(text)
    run.font.size = Pt(11)
    run.font.name = 'Arial'


# ============================================
# CAPA
# ============================================

doc.add_paragraph("\n\n\n")

add_title("RELATÓRIO TÉCNICO")

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

run = subtitle.add_run(
    "Validações Estatísticas do BeamNG como Digital Twin"
)
run.font.size = Pt(18)
run.font.color.rgb = RGBColor(46, 117, 182)
run.font.name = 'Arial'

doc.add_page_break()

# ============================================
# 1. VISÃO GERAL
# ============================================

add_h1("1. Visão Geral do Projeto")

add_paragraph(
    "Este notebook implementa um pipeline completo de validação "
    "estatística para avaliar o simulador BeamNG.drive como "
    "Digital Twin (DT) de veículos reais."
)

# ============================================
# 1.1 Estrutura da Comparação
# ============================================

add_h2("1.1 Estrutura da Comparação")

add_paragraph(
    "Cada arquivo simulado é comparado contra todos os arquivos "
    "reais disponíveis."
)

add_formula("simulado_1 x real_1 | simulado_1 x real_2")
add_formula("simulado_2 x real_1 | simulado_2 x real_2")

# ============================================
# VARIÁVEIS
# ============================================

add_h2("1.2 Variáveis Analisadas")

add_bullet("posX — posição longitudinal")
add_bullet("posY — posição lateral")
add_bullet("posZ — altitude")
add_bullet("vel — velocidade")

# ============================================
# MÉTRICAS
# ============================================

add_h1("2. Métricas de Validação")

# Pearson
add_h2("2.1 Correlação de Pearson")

add_paragraph(
    "Mede a correlação linear entre dois sinais."
)

add_formula(
    "r = sum((x_i - x̄)(y_i - ȳ)) / sqrt(...)"
)

# DTW
add_h2("2.2 Dynamic Time Warping (DTW)")

add_paragraph(
    "O DTW mede distância entre séries temporais permitindo "
    "alinhamento elástico."
)

add_formula(
    "D[i,j] = |x[i] - y[j]| + min(...)"
)

# RMSE
add_h2("2.3 RMSE")

add_formula(
    "RMSE = sqrt(mean((x_i - y_i)^2))"
)

# ============================================
# TABELA
# ============================================

add_h1("3. Tabela de Pesos")

table = doc.add_table(rows=1, cols=3)
table.style = 'Table Grid'

hdr = table.rows[0].cells
hdr[0].text = 'Métrica'
hdr[1].text = 'Peso'
hdr[2].text = 'Descrição'

dados = [
    ("Pearson", "30%", "Correlação global"),
    ("DTW", "20%", "Alinhamento temporal"),
    ("RMSE", "15%", "Erro quadrático"),
]

for metrica, peso, desc in dados:
    row = table.add_row().cells
    row[0].text = metrica
    row[1].text = peso
    row[2].text = desc

# ============================================
# CONSIDERAÇÕES FINAIS
# ============================================

add_h1("4. Considerações Finais")

add_paragraph(
    "O pipeline apresentado permite validar quantitativamente "
    "o simulador BeamNG como Digital Twin."
)

# ============================================
# SALVA
# ============================================

arquivo_saida = "relatorio_digital_twin_v8.docx"

doc.save(arquivo_saida)

print(f"OK: arquivo gerado -> {arquivo_saida}")