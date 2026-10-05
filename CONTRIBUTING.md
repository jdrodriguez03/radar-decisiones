# Cómo trabajamos

1. `git checkout main && git pull`
2. Rama propia: `git checkout -b <letra>/e<bloque>-<tema>` (ej. `a/e2-motor`)
3. Trabajar solo en tus carpetas (ver `.github/CODEOWNERS`).
4. `git add . && git commit -m "motor: filtro por minimos" && git push -u origin <rama>`
5. Abrir PR en GitHub antes de las 18:00 del cierre de bloque. Revisor: Aleja→Gaby, Gaby→Julian, Julian→Juanes, Juanes→Aleja.
6. Fusionar antes de las 20:00 y hacer `git pull` en `main`.

Reglas: no push directo a `main`; no cambiar la firma de funciones ajenas; no subir llaves ni el xlsx.
