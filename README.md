# NequiPay Monitor

Aplicación de escritorio para Windows que recibe por un módem USB **A7670G** (con SIM 4G) los SMS de
confirmación de pago de Nequi, los guarda y los anuncia por el altavoz del PC:

> "Recibiste un pago con valor 200 pesos de Rafael Sanchez"

El valor y el nombre se leen del propio SMS:
`notificacion Nequi: el negocio PORTAWARE recibio $200 de RAFAEL HERNANDO SANCHEZ CAMPO el 25/10/2026 a las 02:08 a.m a travez de  Bre-B.`

## 1. Compilar el .exe con GitHub Actions

1. Crea un repositorio nuevo en GitHub y sube **el contenido de esta carpeta** (que `.github/` quede en la raíz).
2. Entra a la pestaña **Actions**. El workflow *Build Windows EXE* corre solo con cada `push`
   (o ejecútalo a mano con **Run workflow**).
3. Al terminar, abre la ejecución y descarga el artefacto **NequiPayMonitor-windows** → contiene `NequiPayMonitor.exe`.
4. Opcional: crea un tag (`git tag v1.0.0 && git push --tags`) y el .exe se publica también en **Releases**.

> Windows SmartScreen puede avisar "editor desconocido" porque el .exe no está firmado digitalmente:
> *Más información → Ejecutar de todas formas*.

## 2. Preparar el módem

- Instala el **driver SimTech / SIMCom** del A7670G. Debe aparecer en el Administrador de dispositivos
  (Puertos COM) un puerto tipo *"SimTech HS-USB AT Port"*.
- La SIM debe tener **el PIN desactivado** y estar registrada en la red (la app muestra la señal 4G).
- En **Configuración → Dispositivo USB** deja *Detección automática* o elige el puerto; si no aparece,
  escríbelo en *Agregar manualmente* (ej. `COM5`).

## 3. Voz

Usa las voces de Windows (sin internet). Para que lea bien en español instala una voz en español:
*Configuración de Windows → Hora e idioma → Voz → Agregar voces* (Español). La app elige sola una voz en español.
El botón **Probar voz** en Configuración sirve para comprobar el altavoz.

## Cómo funciona

- Cada ~2 s consulta la SIM (`AT+CMGL`). Los SMS que coinciden con el formato de Nequi se guardan, se anuncian
  y se **borran de la SIM**. Los demás SMS no se tocan.
- Los SMS largos que lleguen en varias partes se unen automáticamente.
- Si el módem se desconecta, reintenta cada 4 s.
- Al cerrar la ventana la app queda en la **bandeja del sistema** (sigue anunciando pagos). Para salir: clic derecho → *Salir*.
- Los SMS de más de 12 h de antigüedad (los que estaban en la SIM antes de abrir la app) se guardan pero no se anuncian.
- Datos en `%APPDATA%\NequiPayMonitor\` (`payments.db`, `config.json`, `logo.png`, `nequipay.log`).
  Si un SMS de Nequi no se reconoce, queda registrado en `nequipay.log`.

## Ejecutar desde código (desarrollo)

```bash
pip install -r requirements.txt
python src/main.py
python -m pytest        # pruebas del lector de SMS
```
