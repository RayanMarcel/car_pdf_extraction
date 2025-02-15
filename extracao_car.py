import re
import sys
import json

import pdfplumber  # Certifique-se de instalar: pip install pdfplumber

def ler_pdf_plumber(caminho_pdf):

    texto = ""
    with pdfplumber.open(caminho_pdf) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
            texto += page_text + "\n"
    return texto

def identificar_modelo(texto):
    """
    Identifica o modelo a partir do cabeçalho do arquivo, usando:
      - Modelo 1: "RECIBO DE INSCRIÇÃO DO IMÓVEL RURAL NO CAR"
      - Modelo 2: "CADASTRO AMBIENTAL RURAL DO MATO GROSSO DO SUL"
      - Modelo 3: "Demonstrativo da Situação das Informações Declaradas no"
    """
    if "RECIBO DE INSCRIÇÃO DO IMÓVEL RURAL NO CAR" in texto:
        return "modelo1"
    elif "CADASTRO AMBIENTAL RURAL DO MATO GROSSO DO SUL" in texto:
        return "modelo2"
    elif "Demonstrativo da Situação das Informações Declaradas no" in texto:
        return "modelo3"
    else:
        return "desconhecido"

def extrair_informacoes_modelo1(texto):
    print(texto)

    patterns = {
        "registro_car": r"Registro no CAR:?\s+([^\r\n]+?)(?=\s*Data de Cadastro:)",
        "data_registro": r"Data de Cadastro:?\s+([^\r\n]+)",
        "nome_imovel": r"Nome do Im[oó]vel Rural:?\s+([^\r\n]+)",
        "municipio": r"Munic[ií]pio:?\s+([^\r\n]+)(?=\s*UF:)",
        "uf": r"UF:?\s+([^\r\n]+)",
        "latitude_longitude": r"Coordenadas Geogr[aá]ficas do Centroide.*?Latitude:?\s*([^\r\n]+).*?Longitude:?\s*([^\r\n]+)",
        "area_total": r"Área Total \(ha\) do Im[oó]vel Rural:?\s+(\d+(?:[.,]\d+)?)",
        "modulos_fiscais": r"M[oó]dulos Fiscais:?\s+(\d+(?:[.,]\d+)?)",
        "codigo_protocolo": r"C[oó]digo do Protocolo:?\s+([^\r\n]+)",
        "area_total_imovel": r"Área Total do Im[oó]vel\s*:?\s*(?:\r?\n)+\s*(\d+(?:[.,]\d+)?)",
        "area_serv_administrativa": r"Área de Servid[aã]o Administrativa\s*:?\s*(?:\r?\n)+\s*(\d+(?:[.,]\d+)?)",
        "area_liquida": r"Área L[ií]quida do Im[oó]vel\s*:?\s*(?:\r?\n)+\s*(\d+(?:[.,]\d+)?)",
        "area_preservacao": r"Área de Preservaç[aã]o Permanente\s*:?\s*(?:\r?\n)+\s*(\d+(?:[.,]\d+)?)",
        "area_uso_restrito": r"Área de Uso Restrito\s*:?\s*(?:\r?\n)+\s*(\d+(?:[.,]\d+)?)",
        "area_consolidada": r"Área Consolidada\s*:?\s*(?:\r?\n)+\s*(\d+(?:[.,]\d+)?)",
        "area_remanescente": r"Remanescente de Vegeta[cç][ãa]o Nativa\s*:?\s*(?:\r?\n)+\s*(\d+(?:[.,]\d+)?)",
        "area_reserva_legal": r"Área de Reserva Legal\s*:?\s*(?:\r?\n)+\s*(\d+(?:[.,]\d+)?)",
    }
    info = {}
    for field, pattern in patterns.items():
        match = re.search(pattern, texto, re.IGNORECASE | re.MULTILINE)
        print(match)
        if match:
            if field == "latitude_longitude":
                info["latitude"] = match.group(1).strip()
                info["longitude"] = match.group(2).strip()
            else:
                info[field] = match.group(1).strip()
    return info

def extrair_informacoes_modelo2(texto):
    print(texto)
   
    patterns = {
        "data_registro": r"Data de Inscri[cç][ãa]o\s*:?[\s]+(\d{2}/\d{2}/\d{4}(?:\s+\d{2}:\d{2}(?::\d{2})?)?)",
        "nome_imovel": r"Nome do Im[oó]vel\s*:?[\s]+([^\r\n]+)",
        "latitude_longitude": r"Centr[oó]ide do Im[oó]vel\s*:?[\s]+([^,]+),\s+([^\r\n]+)",
        "municipio": r"Munic[ií]pio\(s\) do Im[oó]vel\s*:?[\s]+([^\r\n]+)",
        "codigo_seguranca": r"C[oó]digo de Seguran[cç]a\s*:?[\s]+(\d+)",
        "area_total_documentada": r"Área Total Documentada do Im[oó]vel\s*\(ha\)\s*:?[\s]+(\d+(?:[.,]\d+)?)",
        "area_total_calculada": r"Área Total Calculada do Im[oó]vel\s*\(ha\)\s*:?[\s]+(\d+(?:[.,]\d+)?)",
        "area_remanescente": r"Remanescente de Vegeta[cç][ãa]o Nativa\s*\(ha\)\s*:?[\s]+(\d+(?:[.,]\d+)?)",
        "area_preservacao": r"Área de Preserva[çc][aã]o Permanente\s*\(ha\)\s*:?[\s]+(\d+(?:[.,]\d+)?)",
        "area_uso_restrito": r"Área de Uso Restrito\s*\(ha\)\s*:?[\s]+(\d+(?:[.,]\d+)?)",
        "area_reserva_legal_exigida": r"Área de Reserva Legal Exigida\s*\(ha\)\s*:?[\s]+(\d+(?:[.,]\d+)?)",
        "area_reserva_legal_existente": r"Área de Reserva Legal Existente\s*\(ha\)\s*:?[\s]*(\d+(?:[.,]\d+)?|\s?)",
        "area_reserva_legal_proposta": r"Área Proposta para Reserva Legal\s*\(ha\)\s*:?[\s]+(\d+(?:[.,]\d+)?)",
        "area_reserva_legal_em_condominio": r"Área de Reserva Legal em Condom[ií]nio\s*\(ha\)\s*:?[\s]*(\d+(?:[.,]\d+)?|\s?)",
        "certificado_inscricao": r"Certificado de Inscri[cç][ãa]o N[uú]mero:\s*([^\r\n]+)"
    }

    info = {}
    for field, pattern in patterns.items():
        m = re.search(pattern, texto, re.IGNORECASE)
        if m:
            if field == "latitude_longitude":
                info["latitude"] = m.group(1).strip()
                info["longitude"] = m.group(2).strip()
            else:
                valor = m.group(1).strip()
                info[field] = valor
    return info

def extrair_informacoes_modelo3(texto):
    print(texto)
    info = {}
    
    pattern_modelo3 = (
        r"Registro de Inscri[cç][ãa]o no CAR:.*?"
        r"Data da Inscri[cç][ãa]o:.*?"
        r"Data da Última Retifica[cç][ãa]o:\s*(?:\r?\n)+\s*"
        r"(\S+)\s+(\S+\s+\S+)\s+(\S+\s+\S+)"
    )
    match = re.search(pattern_modelo3, texto, re.IGNORECASE | re.DOTALL)
    if match:
        info["registro_car"] = match.group(1).strip()
        info["data_registro"] = match.group(2).strip()
        info["data_ultima_retificacao"] = match.group(3).strip()
    else:
        # Fallback: padrões individuais para cada field
        fallback_patterns = {
            "registro_car": r"Registro de Inscri[cç][ãa]o no CAR:?\s*(?:\r?\n)+\s*([^\r\n]+)",
            "data_registro": r"Data da Inscri[cç][ãa]o:?\s*(?:\r?\n)+\s*([^\r\n]+)",
            "data_ultima_retificacao": r"Data da Última Retifica[cç][ãa]o:?\s*(?:\r?\n)+\s*([^\r\n]+)",
        }
        for field, pattern in fallback_patterns.items():
            m = re.search(pattern, texto, re.IGNORECASE | re.MULTILINE)
            if m:
                info[field] = m.group(1).strip()
    other_patterns  = {
        "registro_car": r"Registro de Inscri[cç][ãa]o no CAR:?\s*(?:\r?\n)+\s*([^\r\n]+)",
        "data_registro": r"Data da Inscri[cç][ãa]o:?\s*(?:\r?\n)+\s*([^\r\n]+)",
        "data_ultima_retificacao": r"Data da Última Retifica[cç][ãa]o:?\s*(?:\r?\n)+\s*([^\r\n]+)",
        "area_total": r"Área do Im[oó]vel Rural:?\s+(\d+(?:[.,]\d+)?)",
        "modulos_fiscais": r"M[oó]dulos Fiscais:?\s+([^\r\n]+)",
        "latitude_longitude": r"Coordenadas Geogr[aá]ficas do Centr[oó]ide.*?Latitude:?\s*([^\r\n]+).*?Longitude:?\s*([^\r\n]+)",
        "municipio": r"Munic[ií]pio:?\s+([^\r\n]+)(?=\s* Unidade da Federação:)",
        "uf": r"Unidade da Federa[cç][ãa]o:?\s+([^\r\n]+)",
        "condicao_externa": r"Condi[cç][ãa]o Externa:?\s+([^\r\n]+)",
        "situacao_cadastro": r"Situa[cç][ãa]o do Cadastro:?\s+([^\r\n]+)",
        "condicao_pra": r"Condi[cç][ãa]o do PRA:?\s+([^\r\n]+)",
        "area_remanescente": r"Remanescente de Vegeta[cç][ãa]o Nativa:?\s+([^\r\n]+)",
        "area_rural_consolidada": r"Área Rural Consolidada:?\s+([^\r\n]+)",
        "area_serv_administrativa": r"Área de Servidão Administrativa:?\s+([^\r\n]+)",
        "area_reserva_legal_averbada_art30": r"Área de Reserva Legal Averbada, referente ao Art\.?\s*30 da Lei.*:?\s+([^\r\n]+)",
        "area_reserva_legal_averbada": r"Área de Reserva Legal Averbada:?\s+([^\r\n]+)",
        "area_reserva_legal_aprovada_nao_averbada": r"Área de Reserva Legal Aprovada n[aã]o Averbada:?\s+([^\r\n]+)",
        "area_reserva_legal_proposta": r"Área de Reserva Legal Proposta:?\s+([^\r\n]+)",
        "total_reserva_legal_declarada": r"Total de Reserva Legal Declarada pelo Propriet[aá]rio\/Possuidor:?\s+([^\r\n]+)",
        "app": r"\bAPP:?\s+([^\r\n]+)",
        "app_area_rural_consolidada": r"APP em Área Rural Consolidada:?\s+([^\r\n]+)",
        "app_area_remanescente": r"APP em Área de Remanescente de Vegeta[cç][ãa]o Nativa:?\s+([^\r\n]+)",
        "passivo_excedente_reserva_legal": r"Passivo\s*\/\s*Excedente de Reserva Legal:?\s+([^\r\n]+)",
        "area_reserva_legal_recompor": r"Área de Reserva Legal a recompor:?\s+([^\r\n]+)",
        "area_uso_restrito_recompor": r"Área de Uso Restrito a recompor:?\s+([^\r\n]+)",
    }
    for field, pattern in other_patterns.items():
        m = re.search(pattern, texto, re.IGNORECASE | re.MULTILINE)
        if m:
            if field == "latitude_longitude":
                info["latitude"] = m.group(1).strip()
                info["longitude"] = m.group(2).strip()
            else:
                info[field] = m.group(1).strip()
    return info

def unificar_campos(extracted, modelo):
    final = {
        "registro_car": "",
        "data_registro": "",
        "nome_imovel": "",
        "municipio": "",
        "uf": "",
        "latitude": "",
        "longitude": "",
        "area_total_imovel": "",
        "area_total_calculada": "",
        "modulos_fiscais": "",
        "codigo_protocolo": "",
        "codigo_seguranca": "",
        "area_preservacao": "",
        "area_uso_restrito": "",
        "area_consolidada": "",
        "area_remanescente": "",
        "area_reserva_legal": "",
        "area_reserva_legal_exigida": "",
        "area_reserva_legal_existente": "",
        "area_reserva_legal_proposta": "",
        "area_reserva_legal_em_condominio": "",
        "area_rural_consolidada": "",
        "area_serv_administrativa": "",
        "area_reserva_legal_averbada_art30": "",
        "area_reserva_legal_averbada": "",
        "area_reserva_legal_aprovada_nao_averbada": "",
        "total_reserva_legal_declarada": "",
        "passivo_excedente_reserva_legal": "",
        "area_reserva_legal_recompor": "",
        "area_uso_restrito_recompor": "",
        "app_area_rural_consolidada": "",
        "app_area_remanescente": "",
        "certificado_inscricao": ""
    }

    final["registro_car"] = extracted.get("registro_car", "")
    final["data_registro"] = extracted.get("data_registro", "")
    final["nome_imovel"] = extracted.get("nome_imovel", "")
    final["municipio"] = extracted.get("municipio", "")
    final["uf"] = extracted.get("uf", "")
    final["latitude"] = extracted.get("latitude", "")
    final["longitude"] = extracted.get("longitude", "")
    final["modulos_fiscais"] = extracted.get("modulos_fiscais", "")
    final["codigo_protocolo"] = extracted.get("codigo_protocolo", "")
    final["codigo_seguranca"] = extracted.get("codigo_seguranca", "")
    final["certificado_inscricao"] = extracted.get("certificado_inscricao", "")

    final["area_total_imovel"] = (
        extracted.get("area_total_imovel", "") or
        extracted.get("area_total_documentada", "") or
        extracted.get("area_total", "")
    )

    final["area_total_calculada"] = extracted.get("area_total_calculada", "")

    final["area_preservacao"] = (
        extracted.get("area_preservacao", "") or
        extracted.get("app", "")  # do modelo 3
    )

    final["area_uso_restrito"] = extracted.get("area_uso_restrito", "")
    final["area_consolidada"] = extracted.get("area_consolidada", "")
    final["area_remanescente"] = extracted.get("area_remanescente", "")
    final["area_reserva_legal"] = extracted.get("area_reserva_legal", "")
    final["area_reserva_legal_exigida"] = extracted.get("area_reserva_legal_exigida", "")
    final["area_reserva_legal_existente"] = extracted.get("area_reserva_legal_existente", "")
    final["area_reserva_legal_proposta"] = extracted.get("area_reserva_legal_proposta", "")
    final["area_reserva_legal_em_condominio"] = extracted.get("area_reserva_legal_em_condominio", "")
    final["area_rural_consolidada"] = extracted.get("area_rural_consolidada", "")
    final["area_serv_administrativa"] = extracted.get("area_serv_administrativa", "")
    final["area_reserva_legal_averbada_art30"] = extracted.get("area_reserva_legal_averbada_art30", "")
    final["area_reserva_legal_averbada"] = extracted.get("area_reserva_legal_averbada", "")
    final["area_reserva_legal_aprovada_nao_averbada"] = extracted.get("area_reserva_legal_aprovada_nao_averbada", "")
    final["total_reserva_legal_declarada"] = extracted.get("total_reserva_legal_declarada", "")
    final["passivo_excedente_reserva_legal"] = extracted.get("passivo_excedente_reserva_legal", "")
    final["area_reserva_legal_recompor"] = extracted.get("area_reserva_legal_recompor", "")
    final["area_uso_restrito_recompor"] = extracted.get("area_uso_restrito_recompor", "")
    final["app_area_rural_consolidada"] = extracted.get("app_area_rural_consolidada", "")
    final["app_area_remanescente"] = extracted.get("app_area_remanescente", "")

    return final

def extrair_dados_car(caminho_pdf):
    """
    - Lê o PDF com pdfplumber
    - Identifica o modelo (1, 2 ou 3)
    - Extrai campos específicos
    - Unifica no dicionário final
    """
    texto = ler_pdf_plumber(caminho_pdf)
    modelo = identificar_modelo(texto)

    if modelo == "modelo1":
        extracted = extrair_informacoes_modelo1(texto)
    elif modelo == "modelo2":
        extracted = extrair_informacoes_modelo2(texto)
    elif modelo == "modelo3":
        extracted = extrair_informacoes_modelo3(texto)
    else:
        return {"erro": "Modelo não identificado"}

    final = unificar_campos(extracted, modelo)
    return final

# --------------------------------------------------------
#   Execução via CLI
# --------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python extracao_car.py caminho/para/o/arquivo.pdf")
        sys.exit(1)

    caminho_arquivo = sys.argv[1]
    dados_unificados = extrair_dados_car(caminho_arquivo)

    print("IC Debug Output:")
    print(json.dumps(dados_unificados, indent=4, ensure_ascii=False))
