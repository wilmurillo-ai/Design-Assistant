---
name: crear-video-ia
version: "1.0.0"
displayName: "Crear Video IA — Crea Videos con Inteligencia Artificial en Español Gratis"
description: >
  Crea videos con inteligencia artificial en español — genera videos completos a partir de texto, guiones, descripciones o ideas usando IA. NemoVideo produce videos profesionales automáticamente: escribe tu idea en español, elige el estilo visual, y recibe un video terminado con voz en off en español, subtítulos, música de fondo, transiciones cinematográficas y efectos visuales. Ideal para YouTube, TikTok, Reels, presentaciones empresariales, contenido educativo y marketing digital. Editor de video con IA, generador de video automático, crear video sin programas, herramienta de video en español, video maker gratuito, editar videos fácil.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Crear Video IA — Videos Profesionales con Inteligencia Artificial en Español

Crear un video profesional solía requerir semanas de trabajo: escribir el guion, grabar con equipo costoso, editar en software complejo, añadir música y efectos, exportar y revisar. Cada paso exigía conocimiento técnico o un equipo de producción con presupuesto de miles de euros. Hoy, la inteligencia artificial cambia todo. NemoVideo transforma tu idea escrita en español en un video completo y listo para publicar. No necesitas cámara, no necesitas software de edición, no necesitas experiencia en producción audiovisual. Escribe lo que quieres comunicar — una explicación, una historia, un anuncio, un tutorial, una presentación — y la IA produce: selección de imágenes y clips que ilustran cada concepto, voz en off profesional en español con entonación natural, subtítulos sincronizados palabra por palabra, música de fondo que complementa el tono del contenido, transiciones suaves entre secciones, y formato optimizado para la plataforma que elijas (YouTube horizontal, TikTok vertical, Instagram cuadrado). El resultado es un video que parece producido por un equipo profesional, generado en minutos desde un texto en español.

## Casos de Uso

1. **YouTube — Video Educativo Completo (5-15 min)** — Tema: "Cómo funciona la bolsa de valores." NemoVideo genera: guion estructurado en español (introducción con gancho, 5 secciones temáticas, conclusión con llamada a la acción), imágenes y gráficos animados que ilustran cada concepto (gráficos de acciones, diagramas de oferta y demanda, comparaciones visuales), voz en off masculina profesional en español neutro, subtítulos sincronizados (texto blanco sobre fondo oscuro semitransparente), música corporativa sutil a -20dB, marcadores de capítulos para la navegación de YouTube, y miniatura sugerida con texto en español. Un video educativo completo desde una sola frase descriptiva.
2. **TikTok/Reels — Contenido Viral en Español (15-60s)** — Idea: "5 datos curiosos sobre el cerebro humano." NemoVideo produce: formato vertical 9:16, gancho en el primer segundo ("Tu cerebro consume el 20% de toda tu energía — y eso es solo el principio"), 5 datos presentados con ritmo rápido (cortes cada 3 segundos), texto animado que aparece con cada dato, voz en off dinámica y juvenil en español, música trending sincronizada con los cortes, y cierre que invita a seguir ("Sígueme para más datos que te van a volar la cabeza"). Contenido optimizado para el algoritmo de descubrimiento de TikTok en español.
3. **Presentación Empresarial — Video Corporativo (2-5 min)** — Una startup necesita un video de presentación para inversores. NemoVideo crea: apertura con el problema de mercado (animaciones de datos y estadísticas), presentación de la solución (mockups del producto con transiciones elegantes), tracción y métricas (gráficos animados de crecimiento), equipo (tarjetas animadas con fotos y títulos), y cierre con propuesta de valor y contacto. Voz en off profesional y autoritativa en español. Música: corporativa inspiradora. El pitch deck cobra vida como narrativa audiovisual.
4. **Marketing Digital — Anuncio de Producto (15-45s)** — Una tienda online lanza un producto nuevo. NemoVideo genera: gancho visual en el primer frame (producto en primer plano con texto "NUEVO"), beneficios principales como texto animado (3 frases, una por cada beneficio clave), demostración visual del producto en uso, precio y oferta con urgencia ("Solo esta semana — 30% de descuento"), y CTA claro ("Compra ahora en nuestra web"). Formatos: cuadrado para Facebook Feed, vertical para Stories e Instagram, horizontal para YouTube pre-roll. Tres versiones de un anuncio desde una descripción.
5. **Educación — Material Didáctico (3-10 min)** — Un profesor necesita videos para su curso online. NemoVideo produce: explicación paso a paso con diagramas animados, voz en off clara y pausada (ritmo pedagógico: 130 palabras/minuto), conceptos clave resaltados como tarjetas de texto, ejercicios prácticos presentados como pausas interactivas, y resumen visual al final de cada lección. Batch de 10 lecciones procesadas con estilo consistente — un curso completo en video desde apuntes escritos.

## Cómo Funciona

### Paso 1 — Escribe Tu Idea
Describe en español qué video quieres crear. Puede ser una idea simple ("explica cómo funciona la inflación"), un guion completo, o instrucciones detalladas con estructura y estilo.

### Paso 2 — Elige Estilo y Formato
Selecciona: estilo visual (cinematográfico, corporativo, educativo, dinámico), formato (horizontal, vertical, cuadrado), voz (masculina/femenina, tono), y plataforma destino.

### Paso 3 — Genera
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "crear-video-ia",
    "prompt": "Crea un video de 3 minutos sobre los 5 mejores hábitos financieros para jóvenes. Estilo: dinámico y accesible, como un creador de contenido popular. Gancho fuerte en los primeros 3 segundos. Cada hábito con ejemplo práctico y visual. Voz en off: masculina, joven, energética, español latinoamericano. Subtítulos: palabra por palabra con highlight amarillo. Música: lo-fi relajante a -18dB. Formato: 16:9 para YouTube + versión 9:16 para TikTok.",
    "language": "es",
    "voice": "masculina-joven-energetica",
    "accent": "latinoamericano",
    "style": "dinamico-accesible",
    "subtitles": {"style": "word-highlight", "text": "#FFFFFF", "highlight": "#FFD700"},
    "music": "lo-fi",
    "music_volume": "-18dB",
    "formats": ["16:9", "9:16"],
    "duration": "3 min"
  }'
```

### Paso 4 — Revisa y Publica
Previsualiza el video generado. Ajusta: ritmo de la voz, estilo de subtítulos, selección de música. Exporta y publica directamente en la plataforma elegida.

## Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|:---------:|-------------|
| `prompt` | string | ✅ | Descripción del video en español |
| `language` | string | | "es" (español), "es-MX" (México), "es-AR" (Argentina) |
| `voice` | string | | "masculina-profesional", "femenina-cálida", "joven-energética" |
| `accent` | string | | "neutro", "latinoamericano", "español", "mexicano", "argentino" |
| `style` | string | | "cinematográfico", "corporativo", "educativo", "dinámico" |
| `subtitles` | object | | {style, text, highlight, bg} |
| `music` | string | | "lo-fi", "corporativa", "dramática", "trending", "ninguna" |
| `music_volume` | string | | "-14dB" a "-22dB" |
| `formats` | array | | ["16:9", "9:16", "1:1"] |
| `duration` | string | | "30 sec", "1 min", "3 min", "5 min", "10 min" |
| `batch_prompts` | array | | Múltiples videos en lote |

## Ejemplo de Salida

```json
{
  "job_id": "cvi-20260328-001",
  "status": "completed",
  "language": "es",
  "duration_seconds": 184,
  "outputs": {
    "youtube_16x9": {
      "file": "habitos-financieros-16x9.mp4",
      "resolution": "1920x1080",
      "duration": "3:04",
      "voice": "masculina-joven-energetica (es-LATAM)",
      "subtitles": "word-highlight (218 palabras)",
      "music": "lo-fi at -18dB"
    },
    "tiktok_9x16": {
      "file": "habitos-financieros-9x16.mp4",
      "resolution": "1080x1920",
      "duration": "3:04"
    }
  },
  "sections": [
    {"title": "Gancho — Tu futuro financiero", "timestamp": "0:00"},
    {"title": "Hábito 1 — Págate a ti primero", "timestamp": "0:18"},
    {"title": "Hábito 2 — El fondo de emergencia", "timestamp": "0:48"},
    {"title": "Hábito 3 — Invierte desde joven", "timestamp": "1:22"},
    {"title": "Hábito 4 — Elimina deudas malas", "timestamp": "1:55"},
    {"title": "Hábito 5 — Educación financiera continua", "timestamp": "2:28"},
    {"title": "Cierre y llamada a la acción", "timestamp": "2:52"}
  ]
}
```

## Consejos

1. **Escribe el gancho primero** — Los primeros 3 segundos deciden si el espectador se queda o pasa al siguiente video. "El 78% de los jóvenes no ahorra nada" es un gancho. "Hola, hoy vamos a hablar de finanzas" no lo es.
2. **Español neutro llega a más audiencia** — A menos que tu público sea específicamente de un país, usa español neutro para maximizar el alcance en toda Latinoamérica y España.
3. **Subtítulos palabra por palabra para plataformas móviles** — El 80% del contenido en TikTok y Reels se consume sin sonido inicialmente. Los subtítulos con highlight no solo son accesibles, son obligatorios para retención.
4. **Un video en español tiene 10x menos competencia que en inglés** — El contenido de calidad en español está subrepresentado en todas las plataformas. Un video bien producido en español tiene mucho más espacio para destacar.
5. **Batch de lecciones para cursos completos** — Genera 10-20 lecciones con estilo consistente en una sola sesión. La consistencia visual entre lecciones transmite profesionalismo y calidad de producción.

## Formatos de Salida

| Formato | Resolución | Uso |
|---------|-----------|-----|
| MP4 16:9 | 1080p / 4K | YouTube / presentaciones |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | Instagram / Facebook Feed |
| SRT | — | Subtítulos cerrados |

## Skills Relacionados

- [facebook-video-editor](/skills/facebook-video-editor) — Edición de video para Facebook
- [linkedin-video-creator](/skills/linkedin-video-creator) — Videos para LinkedIn
