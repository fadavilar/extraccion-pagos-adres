#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
LupaAlGiro - Extracción Automatizada de Pagos ADRES
================================================================================

Descripción:
    Este script automatiza la extracción de información de giros y pagos desde
    el portal público de ADRES (Administradora de los Recursos del Sistema 
    General de Seguridad Social en Salud de Colombia).

Fuente de datos:
    https://www.adres.gov.co/lupa-al-giro/identifica-tu-giro

Requisitos:
    - Python 3.12+
    - Google Chrome instalado
    - Selenium 4.25.0
    - BeautifulSoup4
    - Pandas

Instalación de dependencias:
    pip install selenium==4.25.0 beautifulsoup4 pandas

Uso:
    python LupaAlGiro_Clientes.py

Autor: Equipo de Automatización
Fecha: Enero 2026
Versión: 1.0
================================================================================
"""

import os
import time
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================

# Fechas de consulta (formato: DD/MM/YYYY)
FECHA_INICIO = "01/01/2025"
FECHA_FIN = "31/01/2026"

# Tiempo de espera para carga de resultados (segundos)
TIEMPO_ESPERA_RESULTADOS = 35

# Timeout para localizar elementos (segundos)
TIMEOUT_ELEMENTOS = 15

# URL del portal ADRES
URL_ADRES = "https://www.adres.gov.co/lupa-al-giro/identifica-tu-giro"

# Listado de NITs a procesar
NITS_PROCESAR = [
    '890303208', '816001182', '802010614', '890307200', '806007650', '807002424',
    '800194798', '890985122', '830011670', '860026123', '892099160', '811000620',
    '812005190', '800095628', '860514592', '800052534', '890941663', '890901475',
    '890501070', '800231604', '817004260', '800165262', '891409291', '800241602',
    '805007737', '890324177', '890901826', '860006560', '891408586', '890500893',
    '801000713', '890102768', '802020334', '17068260', '892300678', '806006237',
    '824000687', '802000608', '890107487', '890208788', '805027911', '24289833',
    '860037950', '811038014', '811045769', '900037353', '900047874', '16703018',
    '900098550', '830023202', '900112351', '900149596', '830110109', '900273686',
    '830512218', '900285194', '900330656', '900116494', '900335780', '900138858',
    '900368444', '900474727', '900236850', '900563107', '830500960', '830020599',
    '890300513', '66917463', '900580962', '900276658', '13487059', '900928616',
    '900699359', '900774610', '901196161', '901002107', '900099945', '890922113',
    '860007336', '860013570', '800149695', '890000381', '828002423', '901429936',
    '900067510', '900352592', '901300333', '900419563', '901212102', '901565478',
    '900073223', '830027158', '901308243', '900989962', '901731685', '891200235',
    '901256347', '900432887', '800130907', '900277244', '830129327', '890331949',
    '900293923', '811028445', '800005727', '900509068', '900413914', '830501223'
]


# ==============================================================================
# FUNCIONES
# ==============================================================================

def configurar_driver():
    """
    Configura e inicializa el driver de Chrome en modo headless.
    
    Returns:
        webdriver.Chrome: Instancia del driver configurado
    """
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=options)
    return driver


def extraer_datos_nit(driver, nit, fecha_inicio, fecha_fin):
    """
    Extrae los datos de giros para un NIT específico.
    
    Args:
        driver: Instancia del WebDriver
        nit: NIT de la entidad a consultar
        fecha_inicio: Fecha de inicio del período (DD/MM/YYYY)
        fecha_fin: Fecha de fin del período (DD/MM/YYYY)
    
    Returns:
        list: Lista de filas extraídas con los datos
    """
    try:
        driver.get(URL_ADRES)
        wait = WebDriverWait(driver, TIMEOUT_ELEMENTOS)
        
        # Esperar y cambiar al iframe del formulario
        iframe = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "iframe[id*='WebPartWPQ4']")
        ))
        driver.switch_to.frame(iframe)
        
        # Inyectar valores en el formulario mediante JavaScript
        driver.execute_script(f"""
            var inputs = document.querySelectorAll('input[type="text"]');
            if(inputs.length >= 3) {{
                inputs[0].value = '{fecha_inicio}';
                inputs[1].value = '{fecha_fin}';
                inputs[2].value = '{nit}';
                document.querySelectorAll('input[value="Ver informe"]')[0].click();
            }}
        """)
        
        # Esperar carga de resultados
        time.sleep(TIEMPO_ESPERA_RESULTADOS)
        
        # Extraer datos con BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        filas_extraidas = []
        
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) > 5:
                filas_extraidas.append([c.get_text(strip=True) for c in cells])
        
        return filas_extraidas
        
    except Exception as e:
        print(f"   ⚠️ Error en NIT {nit}: {str(e)[:50]}")
        return []
    
    finally:
        driver.switch_to.default_content()


def limpiar_datos(extraccion_bruta):
    """
    Limpia y estructura los datos extraídos.
    
    Args:
        extraccion_bruta: Lista de filas crudas extraídas
    
    Returns:
        pd.DataFrame: DataFrame con los datos limpios y estructurados
    """
    if not extraccion_bruta:
        return pd.DataFrame()
    
    df_raw = pd.DataFrame(extraccion_bruta)
    registros_finales = []
    
    for _, row in df_raw.iterrows():
        cols = [str(c).strip() for c in row if str(c).strip() != ""]
        
        for idx, cell in enumerate(cols):
            if "NIT-" in cell and (idx + 2) < len(cols):
                try:
                    posible_valor = cols[idx + 2]
                    if '$' not in posible_valor and not any(char.isdigit() for char in posible_valor):
                        continue
                    
                    partes = cell.split('-', 2)
                    if len(partes) >= 3:
                        registros_finales.append({
                            'NIT_IPS': partes[1],
                            'Nombre_IPS': partes[2],
                            'Fecha_Giro': cols[idx + 1],
                            'Valor': posible_valor,
                            'Concepto': cols[idx + 3] if idx + 3 < len(cols) else "N/A",
                            'Entidad': cols[idx + 4] if idx + 4 < len(cols) else "N/A"
                        })
                        break
                except:
                    continue
    
    df_final = pd.DataFrame(registros_finales)
    
    if not df_final.empty:
        # Limpiar y convertir valores monetarios
        df_final['Valor'] = (df_final['Valor']
                            .replace(r'[\$,\.]', '', regex=True)
                            .apply(pd.to_numeric, errors='coerce'))
        df_final = df_final.dropna(subset=['Valor'])
    
    return df_final


def main():
    """
    Función principal que ejecuta el proceso de extracción.
    """
    print("=" * 60)
    print("  LupaAlGiro - Extracción de Pagos ADRES")
    print("=" * 60)
    print(f"\n📅 Período: {FECHA_INICIO} - {FECHA_FIN}")
    print(f"📋 NITs a procesar: {len(NITS_PROCESAR)}")
    print(f"⏱️  Tiempo estimado: ~{len(NITS_PROCESAR) * TIEMPO_ESPERA_RESULTADOS // 60} minutos\n")
    
    # Crear directorio de backups si no existe
    if not os.path.exists('backups'):
        os.makedirs('backups')
    
    # Eliminar duplicados manteniendo orden
    nits_unicos = list(dict.fromkeys(NITS_PROCESAR))
    
    # Inicializar driver
    print("🔧 Configurando navegador...")
    driver = configurar_driver()
    
    # Test rápido del driver
    try:
        driver.get("https://www.google.com")
        print(f"✅ Driver funcionando correctamente\n")
    except Exception as e:
        print(f"❌ Error al inicializar driver: {e}")
        return
    
    # Extracción de datos
    EXTRACCION_BRUTA = []
    
    print(f"📡 Iniciando extracción para {len(nits_unicos)} NITs únicos...\n")
    
    for i, nit in enumerate(nits_unicos):
        try:
            print(f"[{i+1}/{len(nits_unicos)}] 📥 Capturando: {nit}")
            
            filas = extraer_datos_nit(driver, nit, FECHA_INICIO, FECHA_FIN)
            EXTRACCION_BRUTA.extend(filas)
            
        except Exception as e:
            print(f"   ❌ Error en NIT {nit}: {str(e)[:50]}")
    
    # Cerrar driver
    driver.quit()
    
    # Limpieza de datos
    print("\n🧹 Iniciando limpieza por anclaje de NIT...")
    df_final = limpiar_datos(EXTRACCION_BRUTA)
    
    # Exportar resultados
    if not df_final.empty:
        output_name = f"ConsolidadoADRES_{time.strftime('%Y%m%d')}.csv"
        df_final.to_csv(output_name, index=False, encoding='utf-8-sig')
        
        print(f"\n{'=' * 60}")
        print(f"🏁 Proceso completado exitosamente")
        print(f"{'=' * 60}")
        print(f"✅ Registros válidos: {len(df_final)}")
        print(f"📂 Archivo generado: {output_name}")
        print(f"{'=' * 60}\n")
    else:
        print("\n❌ No se encontraron datos que coincidan con el patrón de NIT y Valor.")


# ==============================================================================
# EJECUCIÓN
# ==============================================================================

if __name__ == "__main__":
    main()
