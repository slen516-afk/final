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

interface ResumeExportOptions {
  element: HTMLElement;
  filename: string;
}

/**
 * Generate and download a PDF from a DOM element (the resume).
 * Ensures consistency with UI by forcing width and font styles.
 */
export async function exportResumeToPdf({
  element,
  filename,
}: ResumeExportOptions): Promise<void> {
  // 1. Prepare sections for page breaks
  const sections = element.querySelectorAll('[data-pdf-section]');
  sections.forEach((section) => {
    (section as HTMLElement).style.pageBreakInside = 'avoid';
    (section as HTMLElement).style.breakInside = 'avoid';
  });

  // 2. Force consistency styles
  // We apply these to a clone or temporarily to the element to avoid flickering in UI
  // But since html2pdf is async, we'll apply them and then revert if needed.
  // Actually, html2pdf.from(element) takes the element as is.
  const originalStyle = element.getAttribute('style') || '';

  // A4 width at 96 DPI is approx 794px. We use 800px to match common desktop views.
  element.style.width = '800px';
  element.style.maxWidth = '800px';
  element.style.minWidth = '800px';
  element.style.padding = '40px'; // Add some padding for the PDF margin
  element.style.backgroundColor = '#ffffff';
  element.style.fontFamily = "'Noto Sans TC', 'Inter', system-ui, -apple-system, sans-serif";
  element.style.color = '#000000';

  const opt = {
    margin: [0, 0, 0, 0] as [number, number, number, number], // Padding is handled in style
    filename,
    image: { type: 'jpeg' as const, quality: 1.0 },
    html2canvas: {
      scale: 2,
      useCORS: true,
      letterRendering: true,
      logging: false,
      width: 800,
      windowWidth: 1200, // Simulate desktop window width
    },
    jsPDF: {
      unit: 'mm' as const,
      format: 'a4' as const,
      orientation: 'portrait' as const,
    },
    pagebreak: {
      mode: ['avoid-all', 'css', 'legacy'],
      before: '.page-break-before',
      after: '.page-break-after',
      avoid: ['[data-pdf-section]', '.avoid-break'],
    },
  };

  try {
    // Small delay to ensure any dynamic styles/fonts are settled
    await new Promise(resolve => setTimeout(resolve, 100));
    await html2pdf().set(opt).from(element).save();
  } catch (error) {
    console.error('PDF generation error:', error);
    throw error;
  } finally {
    // Revert styles
    element.setAttribute('style', originalStyle);
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
export function buildSuggestionsReportHtml(data: {
  candidate_positioning: string;
  target_role_gap_summary: string;
  overall_strengths: string[];
  overall_weaknesses: string[];
  critical_issues: { section: string; severity: string; original_text: string; issue_reason: string; improvement_direction: string }[];
  recommended_next_actions: string[];
}): string {
  const swBlock = (label: string, color: string, items: string[]) =>
    items.length > 0 ? `
      ${h('h3', `font-size:15px;color:${color};margin:0 0 10px;`, label)}
      ${items.map(s => `<div style="display:flex;gap:8px;align-items:flex-start;padding:10px 14px;border-radius:8px;background:${color}08;margin-bottom:8px;">
        <span style="color:${color};font-size:14px;margin-top:1px;">●</span>
        <p style="margin:0;font-size:13px;line-height:1.85;color:#333;">${s}</p>
      </div>`).join('')}
    ` : '';

  const issuesHtml = data.critical_issues.map(issue => `
    <div style="border:1px solid #e5e0db;border-radius:10px;overflow:hidden;margin-bottom:14px;page-break-inside:avoid;">
      <div style="display:flex;align-items:center;gap:8px;padding:10px 14px;background:#f5f0eb;border-bottom:1px solid #e5e0db;">
        <strong style="font-size:13px;">${issue.section}</strong>
        <span style="font-size:11px;padding:2px 8px;border-radius:10px;background:#fff;border:1px solid #ddd;color:#666;">${issue.severity}</span>
      </div>
      <div style="padding:14px;space-y:12px;">
        <div style="padding:10px 12px;border-radius:6px;background:#f9f9f7;border:1px solid #eee;margin-bottom:10px;">
          <p style="font-size:11px;color:#888;margin:0 0 4px;font-weight:600;">原文內容</p>
          <p style="font-size:13px;color:#555;line-height:1.85;margin:0;">${issue.original_text}</p>
        </div>
        <div style="margin-bottom:10px;">
          <p style="font-size:11px;color:#888;margin:0 0 4px;font-weight:600;">診斷分析</p>
          <p style="font-size:13px;line-height:1.85;margin:0;color:#333;">${issue.issue_reason}</p>
        </div>
        <div style="padding:10px 12px;border-radius:6px;background:#8d490308;border:1px solid #8d490320;">
          <p style="font-size:11px;color:#8d4903;margin:0 0 4px;font-weight:600;">優化方向</p>
          <p style="font-size:13px;line-height:1.85;margin:0;color:#502D03;font-weight:500;">${issue.improvement_direction}</p>
        </div>
      </div>
    </div>
  `).join('');

  const actionsHtml = data.recommended_next_actions.map((a, i) => `
    <div style="display:flex;align-items:flex-start;gap:10px;padding:10px 14px;border-radius:8px;background:#fff;border:1px solid #eee;margin-bottom:8px;">
      <span style="display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:50%;background:#8d490315;color:#8d4903;font-size:11px;font-weight:700;flex-shrink:0;">${i + 1}</span>
      <p style="margin:0;font-size:13px;line-height:1.85;color:#333;">${a}</p>
    </div>
  `).join('');

  return `
    <div>
      ${h('h1', 'font-size:22px;text-align:center;color:#1F3A5F;margin-bottom:4px;', '履歷優化建議報告')}
      ${h('p', 'text-align:center;color:#888;font-size:12px;margin-bottom:28px;', `生成日期：${new Date().toLocaleDateString('zh-TW')}`)}

      ${sectionTitle('一、核心定位分析')}
      <div style="padding:14px 18px;border-radius:8px;background:#8d490308;border:1px solid #8d490320;margin-bottom:14px;">
        <p style="font-size:12px;color:#8d4903;font-weight:600;margin:0 0 6px;">候選人定位</p>
        <p style="font-size:13px;line-height:1.85;margin:0;color:#333;">${data.candidate_positioning}</p>
      </div>
      <div style="padding:14px 18px;border-radius:8px;background:#f9f9f7;border:1px solid #eee;margin-bottom:20px;">
        <p style="font-size:12px;color:#666;font-weight:600;margin:0 0 6px;">目標職位落差摘要</p>
        <p style="font-size:13px;line-height:1.85;margin:0;color:#555;">${data.target_role_gap_summary}</p>
      </div>

      ${sectionTitle('二、優劣勢對比分析')}
      ${swBlock('整體優勢', '#059669', data.overall_strengths)}
      ${swBlock('待改善項目', '#8d4903', data.overall_weaknesses)}

      ${data.critical_issues.length > 0 ? `
        ${sectionTitle('三、關鍵問題診斷')}
        ${issuesHtml}
      ` : ''}

      ${data.recommended_next_actions.length > 0 ? `
        ${sectionTitle('四、後續行動計畫')}
        <div style="padding:14px 18px;border-radius:10px;background:#fbf1e810;border:1px solid #8d490315;">
          ${actionsHtml}
        </div>
      ` : ''}
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
  learningResources: { title: string; description: string; tags?: string[]; rating?: number; review_count?: number; level?: string; course_type?: string; duration?: string; priority?: number; strategy_reason?: string; link?: string }[];
  sideProjects: { name: string; name_en?: string; capability_gaps: string[]; technologies: string[]; phases: { phase_name: string; goal: string; tasks: string[]; resume_value: string }[]; overall_resume_impact: string; difficulty: number; difficulty_label?: string; estimated_duration?: string; difficulty_note?: string }[];
  overallStrategy?: string;
  milestones?: string[];
}): string {
  const swotBlock = (label: string, color: string, text: string) =>
    text ? `<div style="margin-bottom:12px;padding:12px 16px;border-left:4px solid ${color};background:${color}10;border-radius:6px;">
      <strong style="color:${color};letter-spacing:0.3px;">${label}</strong>
      <p style="margin:6px 0 0;font-size:13px;line-height:1.85;">${text}</p>
    </div>` : '';

  const starRating = (rating: number) => {
    const full = Math.floor(rating);
    const stars = '★'.repeat(full) + '☆'.repeat(5 - full);
    return `<span style="color:#d97706;letter-spacing:1px;">${stars}</span> <span style="font-size:12px;color:#888;">${rating}</span>`;
  };

  const difficultyDots = (level: number) => {
    return Array.from({ length: 5 }, (_, i) =>
      `<span style="display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:3px;background:${i < level ? '#8d4903' : '#ddd'};"></span>`
    ).join('');
  };

  const resourceCards = data.learningResources.map((r, i) => {
    const metaParts: string[] = [];
    if (r.rating != null) metaParts.push(starRating(r.rating));
    if (r.review_count != null) metaParts.push(`${r.review_count.toLocaleString()} 則評論`);
    if (r.course_type) metaParts.push(r.course_type);
    if (r.duration) metaParts.push(`⏱ ${r.duration}`);
    if (r.level) metaParts.push(r.level);

    return `<div style="border:1px solid #e5e0db;border-radius:8px;padding:16px;margin-bottom:12px;page-break-inside:avoid;background:#fff;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
        ${r.priority != null ? `<span style="background:#8d4903;color:#fff;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:600;">優先 ${r.priority}</span>` : '<span></span>'}
        ${r.level ? `<span style="border:1px solid #ccc;padding:2px 8px;border-radius:12px;font-size:11px;color:#666;">${r.level}</span>` : ''}
      </div>
      <h3 style="font-size:14px;margin:0 0 6px;color:#1F3A5F;">${r.title}</h3>
      <div style="font-size:11px;color:#888;margin-bottom:6px;">${metaParts.join(' · ')}</div>
      <p style="font-size:13px;margin:0 0 8px;color:#444;">${r.description}</p>
      ${r.strategy_reason ? `<div style="background:#fbf1e8;padding:8px 12px;border-radius:6px;margin-bottom:8px;">
        <p style="margin:0;font-size:12px;color:#502D03;"><strong>策略原因：</strong>${r.strategy_reason}</p>
      </div>` : ''}
      ${r.tags && r.tags.length > 0 ? `<div style="margin-top:4px;">${r.tags.map(t => `<span style="display:inline-block;background:#f0ebe5;color:#675143;padding:2px 8px;border-radius:10px;font-size:11px;margin-right:4px;">${t}</span>`).join('')}</div>` : ''}
    </div>`;
  }).join('');

  return `
    <div>
      ${h('h1', 'font-size:24px;text-align:center;color:#1F3A5F;margin-bottom:6px;letter-spacing:1px;', '職能分析報告')}
      ${h('p', 'text-align:center;color:#999;font-size:12px;margin-bottom:32px;', `生成日期：${new Date().toLocaleDateString('zh-TW')}`)}

      ${sectionTitle('一、核心洞察')}
      ${h('h3', 'font-size:14px;color:#675143;margin:0 0 6px;letter-spacing:0.3px;', '產業洞察')}
      <p style="margin-bottom:16px;line-height:1.85;">${data.industryInsight}</p>
      ${h('h3', 'font-size:15px;color:#502D03;margin:0 0 6px;font-weight:700;letter-spacing:0.3px;', '⭐ 個人總結')}
      <p style="font-weight:600;color:#502D03;margin-bottom:0;line-height:1.85;">${data.personalSummary}</p>

      ${sectionTitle('二、職能雷達圖')}
      <table style="width:100%;border-collapse:collapse;font-size:13px;margin-bottom:12px;">
        <tr style="background:#f5f0eb;"><th style="text-align:left;padding:8px 12px;">維度</th><th style="text-align:center;padding:8px 12px;">您的分數</th>${data.targetRadarDimensions ? '<th style="text-align:center;padding:8px 12px;">目標基準</th>' : ''}</tr>
        ${data.radarDimensions.map((d, i) => `<tr style="border-bottom:1px solid #eee;"><td style="padding:8px 12px;">${d.axis}</td><td style="text-align:center;padding:8px 12px;">${d.score} / 5</td>${data.targetRadarDimensions ? `<td style="text-align:center;padding:8px 12px;">${data.targetRadarDimensions[i]?.score ?? '-'} / 5</td>` : ''}</tr>`).join('')}
      </table>

      ${sectionTitle('三、領航員分析職類')}
      <div style="background:#fbf1e8;padding:16px 20px;border-radius:10px;margin-bottom:14px;">
        <p style="margin:0 0 6px;color:#675143;font-size:12px;letter-spacing:0.3px;">領航員分析您適合的職類</p>
        <p style="margin:0;font-size:20px;font-weight:700;color:#8d4903;letter-spacing:0.5px;">${data.targetRole} <span style="font-size:14px;margin-left:12px;">匹配度 ${data.matchScore}%</span></p>
      </div>
      <div style="display:flex;gap:16px;margin-bottom:14px;">
        <div style="flex:1;padding:12px 16px;border:1px solid #ddd;border-radius:8px;"><p style="margin:0 0 4px;color:#675143;font-size:12px;">自評等級</p><p style="margin:0;font-size:16px;font-weight:700;">${data.selfAssessment}</p></div>
        <div style="flex:1;padding:12px 16px;border:1px solid #ddd;border-radius:8px;"><p style="margin:0 0 4px;color:#675143;font-size:12px;">實際等級</p><p style="margin:0;font-size:16px;font-weight:700;color:#8d4903;">${data.actualLevel}</p></div>
      </div>
      <div style="background:#FFFBF5;padding:14px 18px;border-radius:8px;">
        <p style="margin:0 0 6px;font-weight:600;">認知偏差分析</p>
        <p style="margin:0;font-size:13px;color:#675143;line-height:1.85;">${data.cognitiveBias}</p>
      </div>

      ${sectionTitle('四、SWOT 分析')}
      ${swotBlock('優勢', '#059669', data.swot.strengths)}
      ${swotBlock('劣勢', '#d97706', data.swot.weaknesses)}
      ${swotBlock('機會', '#0284c7', data.swot.opportunities)}
      ${swotBlock('威脅', '#e11d48', data.swot.threats)}
      ${data.swot.gap ? `<div style="margin-top:16px;padding:14px 18px;border:2px solid #8d4903;border-radius:10px;background:linear-gradient(135deg,#fbf1e8,#fff);">
        <strong style="color:#8d4903;letter-spacing:0.3px;">核心落差</strong>
        <p style="margin:6px 0 0;color:#502D03;font-weight:500;line-height:1.85;">${data.swot.gap}</p>
      </div>` : ''}

      ${sectionTitle('五、職涯行動計畫')}
      <p style="margin-bottom:10px;line-height:1.85;"><strong>🔹 短期計畫：</strong>${data.actionPlan.short_term}</p>
      <p style="margin-bottom:10px;line-height:1.85;"><strong>🔸 中期計畫：</strong>${data.actionPlan.mid_term}</p>
      <p style="margin-bottom:10px;line-height:1.85;"><strong>🔹 長期計畫：</strong>${data.actionPlan.long_term}</p>
    </div>
  `;
}

/** 學習資源推薦報告 */
export function buildLearningResourcesReportHtml(data: {
  overallStrategy?: string;
  milestones?: string[];
  learningResources: { title: string; tags?: string[]; rating?: number; review_count?: number; level?: string; course_type?: string; duration?: string; priority?: number; strategy_reason?: string; link?: string }[];
}): string {
  const resourceCards = data.learningResources.map((r) => {
    const metaParts: string[] = [];
    if (r.rating != null) {
      const full = Math.floor(r.rating);
      const stars = '★'.repeat(full) + '☆'.repeat(5 - full);
      metaParts.push(`<span style="color:#d97706;letter-spacing:1px;">${stars}</span> <span style="font-size:12px;color:#888;">${r.rating}</span>`);
    }
    if (r.review_count != null) metaParts.push(`${r.review_count.toLocaleString()} 則評論`);
    if (r.course_type) metaParts.push(r.course_type);
    if (r.duration) metaParts.push(`⏱ ${r.duration}`);
    if (r.level) metaParts.push(r.level);

    return `<div style="border:1px solid #e5e0db;border-radius:10px;padding:18px;margin-bottom:14px;page-break-inside:avoid;background:#fff;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        ${r.priority != null ? `<span style="font-size:20px;font-weight:700;color:#8d4903;letter-spacing:0.5px;">${r.priority}</span>` : '<span></span>'}
        ${r.level ? `<span style="border:1px solid #ccc;padding:3px 10px;border-radius:12px;font-size:11px;color:#666;">${r.level}</span>` : ''}
      </div>
      <h3 style="font-size:15px;margin:0 0 8px;color:#1F3A5F;letter-spacing:0.3px;">${r.title}</h3>
      <div style="font-size:11px;color:#888;margin-bottom:8px;">${metaParts.join(' · ')}</div>
      ${r.strategy_reason ? `<p style="margin:0 0 10px;font-size:12px;color:#502D03;line-height:1.7;"><strong>策略原因：</strong>${r.strategy_reason}</p>` : ''}
      ${r.link && r.link !== '#' ? `<p style="margin:0 0 8px;font-size:12px;"><a href="${r.link}" style="color:#1F3A5F;word-break:break-all;">${r.link}</a></p>` : ''}
      ${r.tags && r.tags.length > 0 ? `<div style="margin-top:6px;">${r.tags.map(t => `<span style="display:inline-block;background:#f0ebe5;color:#675143;padding:3px 10px;border-radius:10px;font-size:11px;margin-right:5px;">${t}</span>`).join('')}</div>` : ''}
    </div>`;
  }).join('');

  return `
    <div>
      ${h('h1', 'font-size:24px;text-align:center;color:#1F3A5F;margin-bottom:6px;letter-spacing:1px;', '學習資源推薦報告')}
      ${h('p', 'text-align:center;color:#999;font-size:12px;margin-bottom:32px;', `生成日期：${new Date().toLocaleDateString('zh-TW')}`)}

      ${data.milestones && data.milestones.length > 0 ? `
        ${sectionTitle('關鍵里程碑')}
        <ol style="padding-left:20px;margin:0 0 24px;">
          ${data.milestones.map(m => `<li style="margin-bottom:8px;font-size:13px;color:#333;line-height:1.85;">${m}</li>`).join('')}
        </ol>
      ` : ''}

      ${sectionTitle('課程推薦')}
      ${resourceCards}
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

/** Side Project 推薦報告 */
export function buildSideProjectsReportHtml(projects: {
  name: string;
  name_en?: string;
  capability_gaps: string[];
  technologies: string[];
  phases: { phase_name: string; goal: string; tasks: string[]; resume_value: string }[];
  overall_resume_impact: string;
  difficulty: number;
  difficulty_label?: string;
  estimated_duration?: string;
  difficulty_note?: string;
}[]): string {
  const projectBlocks = projects.map((p) => {
    const phasesHtml = p.phases.map((ph) => `
      <div style="margin-bottom:18px;page-break-inside:avoid;padding-left:18px;border-left:3px solid #8d4903;">
        <strong style="font-size:14px;color:#1F3A5F;display:block;margin-bottom:6px;">${ph.phase_name}</strong>
        <p style="margin:0 0 6px;font-size:13px;line-height:1.85;color:#444;"><strong>目標：</strong>${ph.goal}</p>
        <ul style="padding-left:18px;margin:0 0 10px;">
          ${ph.tasks.map(t => `<li style="font-size:13px;color:#555;line-height:1.85;margin-bottom:5px;">${t}</li>`).join('')}
        </ul>
        <div style="background:#fbf1e8;padding:10px 14px;border-radius:6px;">
          <p style="margin:0;font-size:12px;color:#502D03;line-height:1.8;"><strong>履歷價值：</strong>${ph.resume_value}</p>
        </div>
      </div>
    `).join('');

    const gapTags = p.capability_gaps.map(g => `<span style="display:inline-block;background:#8d490310;border:1px solid #8d490330;color:#502D03;padding:4px 12px;border-radius:10px;font-size:12px;margin-right:6px;margin-bottom:5px;">${g}</span>`).join('');
    const techTags = p.technologies.map(t => `<span style="display:inline-block;border:1px solid #ccc;color:#555;padding:4px 12px;border-radius:10px;font-size:12px;margin-right:6px;margin-bottom:5px;">${t}</span>`).join('');

    return `
      <div style="margin-bottom:36px;page-break-inside:avoid;">
        <h2 style="font-size:18px;color:#1F3A5F;margin:0 0 8px;">${p.name}${p.name_en ? ` <span style="font-size:13px;color:#888;font-weight:400;">（${p.name_en}）</span>` : ''}</h2>
        <div style="font-size:13px;color:#888;margin-bottom:14px;">
          難度：<strong style="color:#333;">${p.difficulty_label ?? `${p.difficulty}/5`}</strong>
          ${p.estimated_duration ? ` · 預計開發週期：${p.estimated_duration}` : ''}
          ${p.difficulty_note ? ` · ${p.difficulty_note}` : ''}
        </div>

        <div style="margin-bottom:14px;">
          <p style="font-size:13px;color:#675143;font-weight:600;margin:0 0 8px;">能力缺口</p>
          ${gapTags}
        </div>
        <div style="margin-bottom:18px;">
          <p style="font-size:13px;color:#675143;font-weight:600;margin:0 0 8px;">技術棧</p>
          ${techTags}
        </div>

        ${h('h3', 'font-size:15px;color:#1F3A5F;margin:0 0 14px;', '項目階段')}
        ${phasesHtml}
      </div>
    `;
  }).join('');

  return `
    <div>
      ${h('h1', 'font-size:24px;text-align:center;color:#1F3A5F;margin-bottom:6px;letter-spacing:1px;', 'Side Project 推薦報告')}
      ${h('p', 'text-align:center;color:#999;font-size:12px;margin-bottom:32px;', `生成日期：${new Date().toLocaleDateString('zh-TW')}`)}
      ${projectBlocks}
    </div>
  `;
}