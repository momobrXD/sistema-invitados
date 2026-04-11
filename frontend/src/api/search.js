/**
 * Búsqueda fuzzy tolerante a:
 * - Tildes/acentos (jose = josé)
 * - Mayúsculas/minúsculas
 * - Errores de tipeo (hasta 2 caracteres de diferencia)
 * - Orden de palabras (pérez juan = juan pérez)
 * - Búsqueda parcial (jua = juan)
 */

// Quitar tildes y normalizar
function normalize(str) {
  return (str || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // quitar acentos
    .replace(/[^a-z0-9\s]/g, '')    // solo letras, números y espacios
    .trim()
}

// Distancia de Levenshtein (cuántos caracteres cambian entre 2 strings)
function levenshtein(a, b) {
  if (a.length === 0) return b.length
  if (b.length === 0) return a.length

  // Optimización: si la diferencia de longitud es > maxDist, no calcular
  if (Math.abs(a.length - b.length) > 3) return 99

  const matrix = []
  for (let i = 0; i <= b.length; i++) matrix[i] = [i]
  for (let j = 0; j <= a.length; j++) matrix[0][j] = j

  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b[i - 1] === a[j - 1]) {
        matrix[i][j] = matrix[i - 1][j - 1]
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1, // sustitución
          matrix[i][j - 1] + 1,     // inserción
          matrix[i - 1][j] + 1      // eliminación
        )
      }
    }
  }
  return matrix[b.length][a.length]
}

// Verifica si una palabra del query hace match fuzzy con alguna palabra del texto
function fuzzyWordMatch(queryWord, textWords) {
  for (const tw of textWords) {
    // Match exacto parcial (el query es inicio de la palabra)
    if (tw.startsWith(queryWord)) return { match: true, score: 0 }

    // Contiene el query
    if (tw.includes(queryWord) && queryWord.length >= 2) return { match: true, score: 0.5 }

    // Fuzzy: tolerar errores según longitud
    const maxDist = queryWord.length <= 3 ? 1 : 2
    const dist = levenshtein(queryWord, tw.substring(0, queryWord.length + 2))
    if (dist <= maxDist) return { match: true, score: dist }
  }
  return { match: false, score: 99 }
}

/**
 * Busca fuzzy en un objeto contra múltiples campos.
 * Retorna { match: boolean, score: number } (menor score = mejor match)
 *
 * @param {string} query - lo que escribió el usuario
 * @param {object} item - el objeto a buscar
 * @param {string[]} fields - campos del objeto donde buscar
 */
export function fuzzySearch(query, item, fields) {
  const q = normalize(query)
  if (!q) return { match: true, score: 0 }

  // Combinar todos los campos en un solo texto
  const fullText = fields.map(f => normalize(item[f])).join(' ')
  const textWords = fullText.split(/\s+/).filter(Boolean)

  // Separar query en palabras
  const queryWords = q.split(/\s+/).filter(Boolean)

  let totalScore = 0
  for (const qw of queryWords) {
    const result = fuzzyWordMatch(qw, textWords)
    if (!result.match) return { match: false, score: 99 }
    totalScore += result.score
  }

  return { match: true, score: totalScore }
}

/**
 * Filtra y ordena un array por relevancia de búsqueda.
 *
 * @param {string} query - lo que escribió el usuario
 * @param {array} items - array de objetos
 * @param {string[]} fields - campos donde buscar
 * @returns {array} items filtrados y ordenados por relevancia
 */
export function filterBySearch(query, items, fields) {
  if (!query || !query.trim()) return items

  return items
    .map(item => ({ item, ...fuzzySearch(query, item, fields) }))
    .filter(r => r.match)
    .sort((a, b) => a.score - b.score)
    .map(r => r.item)
}
