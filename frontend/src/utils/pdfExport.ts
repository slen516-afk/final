import html2pdf from 'html2pdf.js';

interface PdfExportOptions {
  filename: string;
  htmlContent: string;
  margin?: [number, number, number, number];
}

/**
 * Generate and download a PDF from an HTML string.
 * Uses html2pdf.js under the hood (html → canvas → PDF).
 */
export async function exportHtmlToPdf({
  filename,
  htmlContent,
  margin = [12, 12, 12, 12],
}: PdfExportOptions): Promise<void> {
  const wrapper = document.createElement('div');
  wrapper.innerHTML = htmlContent;
  wrapper.style.width = '700px';
  wrapper.style.fontFamily = "'Noto Sans TC', 'Microsoft JhengHei', sans-serif";
  wrapper.style.color = '#222';
  wrapper.style.lineHeight = '1.7';
  wrapper.style.fontSize = '13px';
  document.body.appendChild(wrapper);

  const opt = {
    margin,
    filename,
    image: { type: 'jpeg' as const, quality: 0.95 },
    html2canvas: { scale: 2, useCORS: true, logging: false },
    jsPDF: { unit: 'mm' as const, format: 'a4' as const, orientation: 'portrait' as const },
    pagebreak: { mode: ['avoid-all', 'css'] },
  };

  try {
    await html2pdf().set(opt).from(wrapper).save();
  } finally {
    document.body.removeChild(wrapper);
  }
}

/* ── Report HTML builders ── */

const h = (tag: string, style: string, content: string) =>
  `<${tag} style="${style}">${content}</${tag}>`;

const sectionTitle = (text: string) =>
  h('h2', 'font-size:16px;color:#1F3A5F;border-bottom:2px solid #1F3A5F;padding-bottom:6px;margin:20px 0 10px;', text);

const bulletList = (items: string[]) =>
  `<ul style="padding-left:18px;margin:0;">${items.map(i => `<li style="margin-bottom:4px;">${i}</li>`).join('')}</ul>`;

/** 履歷優化建議報告 */
export function buildSuggestionsReportHtml(suggestions: { section: string; original: string; optimized: string }[]): string {
  const rows = suggestions.map(s => `
    <div style="margin-bottom:16px;page-break-inside:avoid;">
      <h3 style="font-size:14px;color:#333;margin:0 0 6px;">【${s.section}】</h3>
      <p style="margin:0 0 4px;"><strong style="color:#888;">原始：</strong>${s.original}</p>
      <p style="margin:0;"><strong style="color:#1F3A5F;">優化建議：</strong>${s.optimized}</p>
    </div>
  `).join('');
  return `
    <div>
      ${h('h1', 'font-size:22px;text-align:center;color:#1F3A5F;margin-bottom:4px;', '履歷優化建議報告')}
      ${h('p', 'text-align:center;color:#888;font-size:12px;margin-bottom:24px;', `生成日期：${new Date().toLocaleDateString('zh-TW')}`)}
      ${rows}
    </div>
  `;
}

/** 職能圖譜分析報告 */
export function buildSkillsReportHtml(data: {
  industryInsight: string;
  personalSummary: string;
  radarDimensions: { axis: string; score: number }[];
  targetRadarDimensions?: { axis: string; score: number }[];
  selfAssessment: string;
  actualLevel: string;
  cognitiveBias: string;
  targetRole: string;
  matchScore: number;
  swot: { strengths: string; weaknesses: string; opportunities: string; threats: string; gap: string };
  actionPlan: { short_term: string; mid_term: string; long_term: string };
  learningResources: { title: string; description: string }[];
  sideProjects: { name: string; technologies: string[] }[];
}): string {
  const swotBlock = (label: string, color: string, text: string) =>
    text ? `<div style="margin-bottom:10px;padding:10px 14px;border-left:4px solid ${color};background:${color}10;border-radius:4px;">
      <strong style="color:${color};">${label}</strong>
      <p style="margin:4px 0 0;font-size:13px;">${text}</p>
    </div>` : '';

  return `
    <div>
      ${h('h1', 'font-size:22px;text-align:center;color:#1F3A5F;margin-bottom:4px;', '職能分析報告')}
      ${h('p', 'text-align:center;color:#888;font-size:12px;margin-bottom:24px;', `生成日期：${new Date().toLocaleDateString('zh-TW')}`)}

      ${sectionTitle('一、核心洞察')}
      ${h('h3', 'font-size:14px;color:#675143;margin:0 0 4px;', '產業洞察')}
      <p style="margin-bottom:12px;">${data.industryInsight}</p>
      ${h('h3', 'font-size:15px;color:#502D03;margin:0 0 4px;font-weight:700;', '⭐ 個人總結')}
      <p style="font-weight:600;color:#502D03;margin-bottom:0;">${data.personalSummary}</p>

      ${sectionTitle('二、職能雷達圖')}
      <table style="width:100%;border-collapse:collapse;font-size:13px;margin-bottom:8px;">
        <tr style="background:#f5f0eb;"><th style="text-align:left;padding:6px 10px;">維度</th><th style="text-align:center;padding:6px 10px;">您的分數</th>${data.targetRadarDimensions ? '<th style="text-align:center;padding:6px 10px;">目標基準</th>' : ''}</tr>
        ${data.radarDimensions.map((d, i) => `<tr style="border-bottom:1px solid #eee;"><td style="padding:6px 10px;">${d.axis}</td><td style="text-align:center;padding:6px 10px;">${d.score} / 5</td>${data.targetRadarDimensions ? `<td style="text-align:center;padding:6px 10px;">${data.targetRadarDimensions[i]?.score ?? '-'} / 5</td>` : ''}</tr>`).join('')}
      </table>

      ${sectionTitle('三、領航員分析職類')}
      <div style="background:#fbf1e8;padding:14px 18px;border-radius:8px;margin-bottom:12px;">
        <p style="margin:0 0 4px;color:#675143;font-size:12px;">領航員分析您適合的職類</p>
        <p style="margin:0;font-size:20px;font-weight:700;color:#8d4903;">${data.targetRole} <span style="font-size:14px;margin-left:12px;">匹配度 ${data.matchScore}%</span></p>
      </div>
      <div style="display:flex;gap:16px;margin-bottom:12px;">
        <div style="flex:1;padding:10px 14px;border:1px solid #ddd;border-radius:8px;"><p style="margin:0 0 2px;color:#675143;font-size:12px;">自評等級</p><p style="margin:0;font-size:16px;font-weight:700;">${data.selfAssessment}</p></div>
        <div style="flex:1;padding:10px 14px;border:1px solid #ddd;border-radius:8px;"><p style="margin:0 0 2px;color:#675143;font-size:12px;">實際等級</p><p style="margin:0;font-size:16px;font-weight:700;color:#8d4903;">${data.actualLevel}</p></div>
      </div>
      <div style="background:#FFFBF5;padding:12px 16px;border-radius:8px;">
        <p style="margin:0 0 4px;font-weight:600;">認知偏差分析</p>
        <p style="margin:0;font-size:13px;color:#675143;">${data.cognitiveBias}</p>
      </div>

      ${sectionTitle('四、SWOT 分析')}
      ${swotBlock('優勢', '#059669', data.swot.strengths)}
      ${swotBlock('劣勢', '#d97706', data.swot.weaknesses)}
      ${swotBlock('機會', '#0284c7', data.swot.opportunities)}
      ${swotBlock('威脅', '#e11d48', data.swot.threats)}
      ${data.swot.gap ? `<div style="margin-top:12px;padding:12px 16px;border:2px solid #8d4903;border-radius:8px;background:linear-gradient(135deg,#fbf1e8,#fff);">
        <strong style="color:#8d4903;">核心落差</strong>
        <p style="margin:4px 0 0;color:#502D03;font-weight:500;">${data.swot.gap}</p>
      </div>` : ''}

      ${sectionTitle('五、職涯行動計畫')}
      <p><strong>🔹 短期計畫：</strong>${data.actionPlan.short_term}</p>
      <p><strong>🔸 中期計畫：</strong>${data.actionPlan.mid_term}</p>
      <p><strong>🔹 長期計畫：</strong>${data.actionPlan.long_term}</p>

      ${sectionTitle('六、推薦學習資源')}
      ${bulletList(data.learningResources.map(r => `${r.title}：${r.description}`))}

      ${sectionTitle('七、推薦 Side Project')}
      ${bulletList(data.sideProjects.map(p => `${p.name}（技術：${p.technologies.join('、')}）`))}
    </div>
  `;
}

/** 我的履歷 (plain text content → PDF) */
export function buildResumeContentHtml(name: string, content: string): string {
  return `
    <div>
      ${h('h1', 'font-size:22px;text-align:center;color:#1F3A5F;margin-bottom:24px;', name)}
      <pre style="white-space:pre-wrap;font-family:'Noto Sans TC',sans-serif;font-size:13px;line-height:1.8;">${content}</pre>
    </div>
  `;
}

/** 職涯分析結果報告 */
export function buildCareerAnalysisHtml(analysis: {
  title: string;
  date: string;
  summary: string;
  strengths: string[];
  improvements: string[];
  recommendations: string[];
}): string {
  return `
    <div>
      ${h('h1', 'font-size:22px;text-align:center;color:#1F3A5F;margin-bottom:4px;', analysis.title)}
      ${h('p', 'text-align:center;color:#888;font-size:12px;margin-bottom:24px;', `分析日期：${analysis.date}`)}

      ${sectionTitle('分析摘要')}
      <p>${analysis.summary}</p>

      ${sectionTitle('優勢亮點')}
      ${bulletList(analysis.strengths)}

      ${sectionTitle('待加強項目')}
      ${bulletList(analysis.improvements)}

      ${sectionTitle('發展建議')}
      ${bulletList(analysis.recommendations)}
    </div>
  `;
}
