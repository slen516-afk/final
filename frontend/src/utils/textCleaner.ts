/**
 * Text cleaner – strips dimension codes (D1–D6) and their bracketed labels
 * from recommendation text returned by the backend.
 */

const DIMENSION_MAP: Record<string, string> = {
    D1: '前端開發',
    D2: '後端開發',
    D3: '運維部署',
    D4: 'AI與數據',
    D5: '工程品質',
    D6: '軟實力',
};

/**
 * Clean dimension codes from text.
 *
 * Rule 1 – Code-first:  "D3 (DevOps)" or "D3（DevOps）" → "運維部署"
 * Rule 2 – Suffix-code: "後端開發能力（D2）" or "後端開發能力(D2)" → "後端開發能力"
 * Extra  – Replace "候選人" → "用戶"
 */
export function cleanDimensionText(raw: string | undefined | null): string {
    if (!raw) return '';

    let text = raw;

    // Rule 1: D1-D6 followed by optional parenthesised content → mapped name
    // e.g. "D3 (DevOps)" / "D3（Quality）" / bare "D3"
    text = text.replace(
        /D([1-6])\s*(?:[（(][^)）]*[)）])?/g,
        (_match, digit: string) => DIMENSION_MAP[`D${digit}`] ?? _match,
    );

    // Rule 2: suffix code in brackets after CJK text  e.g. "能力（D2）" → "能力"
    // After rule 1 the codes are already replaced, but handle any remaining patterns
    text = text.replace(/[（(]D[1-6][)）]/g, '');

    // Replace 候選人 → 用戶
    text = text.replace(/候選人/g, '用戶');

    return text.trim();
}

/**
 * Extract city (first 3 chars) from a full address string.
 * e.g. "台北市南港區園區街3之2號9樓" → "台北市"
 */
export function extractCity(fullAddress: string | undefined | null): string {
    if (!fullAddress) return '';
    return fullAddress.substring(0, 3);
}