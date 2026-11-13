"""Formatos regionales para Peru (es-PE).

Peru usa punto como separador decimal y coma para los miles (1,234.56),
a diferencia del locale `es` de Django (1.234,56).
"""
DECIMAL_SEPARATOR = "."
THOUSAND_SEPARATOR = ","
NUMBER_GROUPING = 3
USE_THOUSAND_SEPARATOR = True

DATE_INPUT_FORMATS = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
DATE_FORMAT = "d/m/Y"
SHORT_DATE_FORMAT = "d/m/Y"
DATETIME_FORMAT = "d/m/Y H:i"
SHORT_DATETIME_FORMAT = "d/m/Y H:i"
