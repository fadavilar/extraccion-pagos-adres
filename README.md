# 🔍 Extracción de Pagos ADRES - LupaAlGiro

## Descripción
Proyecto de automatización desarrollado en Python que permite extraer información de giros y pagos desde el portal público de ADRES (Administradora de los Recursos del Sistema General de Seguridad Social en Salud de Colombia).

## 🎯 Objetivo
Automatizar la consulta y consolidación de información de giros realizados por ADRES a múltiples entidades (EPS/IPS) en un período de tiempo determinado.

## 🛠️ Stack Tecnológico
| Componente | Tecnología |
|------------|------------|
| Lenguaje | Python 3.12 |
| Automatización Web | Selenium 4.25.0 |
| Navegador | Google Chrome (headless) |
| Parsing HTML | BeautifulSoup 4 |
| Procesamiento Datos | Pandas |
| Entorno Ejecución | Google Colab |

## 📁 Estructura del Proyecto
```
extraccion-pagos-adres/
├── README.md
├── docs/
│   └── Documentacion_LupaAlGiro_ADRES.docx
└── notebooks/
    └── LupaAlGiro_Clientes.ipynb
```

## 🚀 Uso Rápido
1. Abrir el notebook en Google Colab
2. Ejecutar los chunks en orden (0 → 4)
3. Esperar el mensaje "🏁 Proceso completado"
4. Descargar el archivo CSV generado

## 📊 Datos de Salida
El sistema genera un archivo `ConsolidadoADRES_YYYYMMDD.csv` con las siguientes columnas:
- `NIT_IPS` - NIT de la entidad beneficiaria
- `Nombre_IPS` - Nombre de la entidad
- `Fecha_Giro` - Fecha del giro realizado
- `Valor` - Monto del giro
- `Concepto` - Tipo de pago
- `Entidad` - Entidad origen del giro

## ⏱️ Tiempo de Ejecución
~63 minutos para 108 NITs (35 seg/consulta)

## 📖 Documentación
Consulta la documentación técnica completa en [`docs/Documentacion_LupaAlGiro_ADRES.docx`](docs/Documentacion_LupaAlGiro_ADRES.docx)

## 🔗 Fuente de Datos
- **Portal:** [ADRES - Lupa al Giro](https://www.adres.gov.co/lupa-al-giro/identifica-tu-giro)
- **Tipo de acceso:** Público (sin autenticación)

## 📝 Licencia
Uso interno

---
*Documentación generada: Enero 2026*
