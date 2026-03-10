/**
 * Split a raw text blob into paragraphs (hybrid mode).
 * 1. Prefer splitting by newlines (\n).
 * 2. Fallback: split on sentence-ending punctuation (。！？), one sentence per paragraph.
 */
export function splitIntoParagraphs(raw: string): string[] {
    if (!raw) return [];

    // 1. Try splitting by newlines
    const byNewline = raw
        .split(/\n{1,}/)
        .map((s) => s.trim())
        .filter(Boolean);

    if (byNewline.length > 1) return byNewline;

    // 2. Fallback: split after each sentence-ending punctuation
    let paragraphs = raw
        .split(/(?<=[。！？])\s*/)
        .map((s) => s.trim())
        .filter(Boolean);

    // 3. Fallback: split by common job description section headers preceded by space
    // e.g. "產業領域：... 工作內容：..." -> split at " 工作內容"
    paragraphs = paragraphs.flatMap(p => 
        p.split(/(?=\s+(?:工作內容|條件要求|員工福利|職務類別|上班地點|管理責任|出差外派|上班時段|休假制度|可上班日|需求人數|接受身份|工作經歷|學歷要求|科系要求|語文條件|擅長工具|工作技能|具備證照|其他條件|必備條件|加分)：?)/)
         .map((s) => s.trim())
         .filter(Boolean)
    );

    // 4. Fallback: split by list markers like "- " or "• " if they exist
    paragraphs = paragraphs.flatMap(p => 
        p.split(/(?=(?:^|\s)[-•]\s)/)
         .map((s) => s.trim())
         .filter(Boolean)
    );

    if (paragraphs.length > 1) return paragraphs;

    // 5. Final Fallback: split by spaces ONLY IF it's likely a delimiter (not surrounded by English letters/numbers like "Node.js" or "UI UX")
    // This regex looks for 2 or more spaces, or spaces between Chinese characters, but ignores single spaces between English text
    const bySpace = paragraphs[0]
        .split(/\s{2,}/) // First try 2+ spaces
        .map((s) => s.trim())
        .filter(Boolean);

    if (bySpace.length > 1) return bySpace;

    // If it's a mix of CJK and single spaces, try splitting by single space if it's not looking like an english sentence
    // Simplest heuristic: if it contains "- ", we already caught it. Otherwise, fallback to basic space split but ignore slashes
    const bySingleSpace = paragraphs[0]
        .split(/(?<![\/-])\s+(?![\/-])/)
        .map((s) => s.trim())
        .filter(Boolean);

    return bySingleSpace.length > 1 ? bySingleSpace : paragraphs;
}