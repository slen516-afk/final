/**
 * High-fidelity SVG wireframe thumbnails for resume templates.
 * Uses gray lines (greeking) to simulate text, showing layout structure clearly.
 */

const LINE_COLORS = {
  title: '#999',
  subtitle: '#bbb',
  body: '#d5d5d5',
  bodyLight: '#e5e5e5',
  divider: '#ccc',
  accent: '#c0c0c0',
  sidebar: '#f0f0f0',
  circle: '#e8e8e8',
};

/** Corporate Classic: centered header, horizontal sections stacked vertically */
export const CorporateThumbnail = () => (
  <svg viewBox="0 0 300 400" className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
    <rect width="300" height="400" fill="white" />

    {/* Header - centered name */}
    <rect x="100" y="24" width="100" height="10" rx="2" fill={LINE_COLORS.title} />
    {/* Contact row */}
    <rect x="70" y="42" width="40" height="5" rx="1" fill={LINE_COLORS.subtitle} />
    <rect x="118" y="42" width="3" height="5" rx="1" fill={LINE_COLORS.subtitle} />
    <rect x="130" y="42" width="35" height="5" rx="1" fill={LINE_COLORS.subtitle} />
    <rect x="173" y="42" width="3" height="5" rx="1" fill={LINE_COLORS.subtitle} />
    <rect x="185" y="42" width="45" height="5" rx="1" fill={LINE_COLORS.subtitle} />
    {/* Divider */}
    <rect x="24" y="56" width="252" height="2" rx="1" fill={LINE_COLORS.title} />

    {/* Section: 專業摘要 */}
    <rect x="24" y="70" width="60" height="7" rx="1.5" fill={LINE_COLORS.title} />
    <rect x="24" y="82" width="252" height="1" rx="0.5" fill={LINE_COLORS.divider} />
    <rect x="24" y="90" width="240" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="24" y="98" width="220" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="24" y="106" width="180" height="4" rx="1" fill={LINE_COLORS.bodyLight} />

    {/* Section: 學歷 */}
    <rect x="24" y="124" width="36" height="7" rx="1.5" fill={LINE_COLORS.title} />
    <rect x="24" y="136" width="252" height="1" rx="0.5" fill={LINE_COLORS.divider} />
    <rect x="24" y="144" width="200" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="24" y="152" width="160" height="4" rx="1" fill={LINE_COLORS.bodyLight} />

    {/* Section: 工作經驗 */}
    <rect x="24" y="172" width="56" height="7" rx="1.5" fill={LINE_COLORS.title} />
    <rect x="24" y="184" width="252" height="1" rx="0.5" fill={LINE_COLORS.divider} />
    <rect x="24" y="192" width="130" height="5" rx="1" fill={LINE_COLORS.subtitle} />
    <rect x="24" y="202" width="240" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="24" y="210" width="230" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="24" y="218" width="200" height="4" rx="1" fill={LINE_COLORS.bodyLight} />
    <rect x="24" y="230" width="120" height="5" rx="1" fill={LINE_COLORS.subtitle} />
    <rect x="24" y="240" width="245" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="24" y="248" width="210" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="24" y="256" width="190" height="4" rx="1" fill={LINE_COLORS.bodyLight} />

    {/* Section: 技能專長 */}
    <rect x="24" y="276" width="56" height="7" rx="1.5" fill={LINE_COLORS.title} />
    <rect x="24" y="288" width="252" height="1" rx="0.5" fill={LINE_COLORS.divider} />
    <rect x="24" y="296" width="240" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="24" y="304" width="200" height="4" rx="1" fill={LINE_COLORS.bodyLight} />

    {/* Section: 專案作品集 */}
    <rect x="24" y="322" width="64" height="7" rx="1.5" fill={LINE_COLORS.title} />
    <rect x="24" y="334" width="252" height="1" rx="0.5" fill={LINE_COLORS.divider} />
    <rect x="24" y="342" width="230" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="24" y="350" width="210" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="24" y="358" width="180" height="4" rx="1" fill={LINE_COLORS.bodyLight} />
    <rect x="24" y="366" width="220" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="24" y="374" width="160" height="4" rx="1" fill={LINE_COLORS.bodyLight} />
  </svg>
);

/** Modern Minimalist: left sidebar + right content, two-column */
export const ModernThumbnail = () => (
  <svg viewBox="0 0 300 400" className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
    <rect width="300" height="400" fill="white" />

    {/* Left sidebar background */}
    <rect x="0" y="0" width="95" height="400" fill={LINE_COLORS.sidebar} />

    {/* Avatar circle */}
    <circle cx="48" cy="40" r="22" fill={LINE_COLORS.circle} stroke={LINE_COLORS.accent} strokeWidth="1.5" />
    <text x="48" y="45" textAnchor="middle" fontSize="14" fill={LINE_COLORS.title} fontWeight="bold">A</text>

    {/* Contact info in sidebar */}
    <rect x="12" y="74" width="8" height="4" rx="1" fill={LINE_COLORS.accent} />
    <rect x="24" y="74" width="56" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="12" y="84" width="8" height="4" rx="1" fill={LINE_COLORS.accent} />
    <rect x="24" y="84" width="50" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="12" y="94" width="8" height="4" rx="1" fill={LINE_COLORS.accent} />
    <rect x="24" y="94" width="58" height="4" rx="1" fill={LINE_COLORS.body} />

    {/* Skills section in sidebar */}
    <rect x="12" y="116" width="44" height="6" rx="1" fill={LINE_COLORS.title} />
    <rect x="12" y="126" width="70" height="1" rx="0.5" fill={LINE_COLORS.divider} />
    {/* Skill bars */}
    {[0, 1, 2, 3, 4].map((i) => (
      <g key={i}>
        <rect x="12" y={136 + i * 18} width={35 + Math.random() * 20} height="4" rx="1" fill={LINE_COLORS.subtitle} />
        <rect x="12" y={144 + i * 18} width="70" height="5" rx="2.5" fill="#e8e8e8" />
        <rect x="12" y={144 + i * 18} width={55 - i * 7} height="5" rx="2.5" fill={LINE_COLORS.accent} />
      </g>
    ))}

    {/* Right content area */}
    {/* Name */}
    <rect x="108" y="24" width="120" height="12" rx="2" fill={LINE_COLORS.title} />
    {/* Summary */}
    <rect x="108" y="44" width="172" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="108" y="52" width="160" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="108" y="60" width="130" height="4" rx="1" fill={LINE_COLORS.bodyLight} />

    {/* Section: 工作經驗 */}
    <rect x="108" y="80" width="10" height="6" rx="1" fill={LINE_COLORS.accent} />
    <rect x="122" y="80" width="56" height="6" rx="1" fill={LINE_COLORS.title} />
    <rect x="108" y="90" width="172" height="1" rx="0.5" fill={LINE_COLORS.divider} />
    <rect x="108" y="98" width="100" height="5" rx="1" fill={LINE_COLORS.subtitle} />
    <rect x="108" y="108" width="170" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="108" y="116" width="160" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="108" y="124" width="140" height="4" rx="1" fill={LINE_COLORS.bodyLight} />
    <rect x="108" y="136" width="90" height="5" rx="1" fill={LINE_COLORS.subtitle} />
    <rect x="108" y="146" width="168" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="108" y="154" width="155" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="108" y="162" width="130" height="4" rx="1" fill={LINE_COLORS.bodyLight} />

    {/* Section: 學歷 */}
    <rect x="108" y="182" width="10" height="6" rx="1" fill={LINE_COLORS.accent} />
    <rect x="122" y="182" width="36" height="6" rx="1" fill={LINE_COLORS.title} />
    <rect x="108" y="192" width="172" height="1" rx="0.5" fill={LINE_COLORS.divider} />
    <rect x="108" y="200" width="150" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="108" y="208" width="130" height="4" rx="1" fill={LINE_COLORS.bodyLight} />

    {/* Section: 專案作品集 */}
    <rect x="108" y="228" width="10" height="6" rx="1" fill={LINE_COLORS.accent} />
    <rect x="122" y="228" width="56" height="6" rx="1" fill={LINE_COLORS.title} />
    <rect x="108" y="238" width="172" height="1" rx="0.5" fill={LINE_COLORS.divider} />
    <rect x="108" y="246" width="165" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="108" y="254" width="148" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="108" y="262" width="120" height="4" rx="1" fill={LINE_COLORS.bodyLight} />

    {/* Section: 自傳 */}
    <rect x="108" y="282" width="10" height="6" rx="1" fill={LINE_COLORS.accent} />
    <rect x="122" y="282" width="36" height="6" rx="1" fill={LINE_COLORS.title} />
    <rect x="108" y="292" width="172" height="1" rx="0.5" fill={LINE_COLORS.divider} />
    <rect x="108" y="300" width="170" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="108" y="308" width="160" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="108" y="316" width="155" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="108" y="324" width="140" height="4" rx="1" fill={LINE_COLORS.bodyLight} />
    <rect x="108" y="332" width="170" height="4" rx="1" fill={LINE_COLORS.body} />
    <rect x="108" y="340" width="130" height="4" rx="1" fill={LINE_COLORS.bodyLight} />
  </svg>
);

/** Creative Portfolio: circle avatar + badge, header, 2-column content grid */
export const CreativeThumbnail = () => (
  <svg viewBox="0 0 300 400" className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
    <rect width="300" height="400" fill="white" />

    {/* Subtle background tint */}
    <rect width="300" height="400" fill={LINE_COLORS.sidebar} opacity="0.4" />

    {/* Header area */}
    <g>
      {/* Avatar circle */}
      <circle cx="56" cy="44" r="26" fill="white" stroke={LINE_COLORS.accent} strokeWidth="2.5" />
      <text x="56" y="50" textAnchor="middle" fontSize="16" fill={LINE_COLORS.title} fontWeight="bold">A</text>
      {/* Accent badge */}
      <circle cx="76" cy="64" r="7" fill={LINE_COLORS.accent} />
      <text x="76" y="67" textAnchor="middle" fontSize="7" fill="white">✦</text>

      {/* Name & summary */}
      <rect x="96" y="24" width="130" height="12" rx="2" fill={LINE_COLORS.title} />
      <rect x="96" y="44" width="180" height="4" rx="1" fill={LINE_COLORS.body} />
      <rect x="96" y="52" width="160" height="4" rx="1" fill={LINE_COLORS.body} />
      <rect x="96" y="60" width="120" height="4" rx="1" fill={LINE_COLORS.bodyLight} />

      {/* Contact row */}
      <rect x="96" y="74" width="8" height="4" rx="1" fill={LINE_COLORS.accent} />
      <rect x="108" y="74" width="50" height="4" rx="1" fill={LINE_COLORS.subtitle} />
      <rect x="166" y="74" width="8" height="4" rx="1" fill={LINE_COLORS.accent} />
      <rect x="178" y="74" width="42" height="4" rx="1" fill={LINE_COLORS.subtitle} />
    </g>

    {/* Divider */}
    <rect x="24" y="92" width="252" height="1.5" rx="0.5" fill={LINE_COLORS.divider} />

    {/* Two-column content grid */}
    {/* Left column */}
    <g>
      {/* 工作經驗 */}
      <rect x="24" y="106" width="8" height="8" rx="4" fill={LINE_COLORS.accent} />
      <rect x="38" y="107" width="56" height="6" rx="1" fill={LINE_COLORS.title} />
      <rect x="24" y="120" width="115" height="4" rx="1" fill={LINE_COLORS.body} />
      <rect x="24" y="128" width="108" height="4" rx="1" fill={LINE_COLORS.body} />
      <rect x="24" y="136" width="95" height="4" rx="1" fill={LINE_COLORS.bodyLight} />
      <rect x="24" y="148" width="100" height="5" rx="1" fill={LINE_COLORS.subtitle} />
      <rect x="24" y="158" width="115" height="4" rx="1" fill={LINE_COLORS.body} />
      <rect x="24" y="166" width="100" height="4" rx="1" fill={LINE_COLORS.body} />
      <rect x="24" y="174" width="85" height="4" rx="1" fill={LINE_COLORS.bodyLight} />

      {/* 技能 */}
      <rect x="24" y="196" width="8" height="8" rx="4" fill={LINE_COLORS.accent} />
      <rect x="38" y="197" width="48" height="6" rx="1" fill={LINE_COLORS.title} />
      {/* Skill tags */}
      <rect x="24" y="212" width="38" height="12" rx="6" fill={LINE_COLORS.circle} />
      <rect x="66" y="212" width="45" height="12" rx="6" fill={LINE_COLORS.circle} />
      <rect x="24" y="228" width="50" height="12" rx="6" fill={LINE_COLORS.circle} />
      <rect x="78" y="228" width="40" height="12" rx="6" fill={LINE_COLORS.circle} />
      <rect x="24" y="244" width="42" height="12" rx="6" fill={LINE_COLORS.circle} />
      <rect x="70" y="244" width="48" height="12" rx="6" fill={LINE_COLORS.circle} />
    </g>

    {/* Right column */}
    <g>
      {/* 學歷 */}
      <rect x="156" y="106" width="8" height="8" rx="4" fill={LINE_COLORS.accent} />
      <rect x="170" y="107" width="36" height="6" rx="1" fill={LINE_COLORS.title} />
      <rect x="156" y="120" width="115" height="4" rx="1" fill={LINE_COLORS.body} />
      <rect x="156" y="128" width="100" height="4" rx="1" fill={LINE_COLORS.body} />
      <rect x="156" y="136" width="80" height="4" rx="1" fill={LINE_COLORS.bodyLight} />

      {/* 專案作品集 */}
      <rect x="156" y="160" width="8" height="8" rx="4" fill={LINE_COLORS.accent} />
      <rect x="170" y="161" width="56" height="6" rx="1" fill={LINE_COLORS.title} />
      <rect x="156" y="174" width="115" height="4" rx="1" fill={LINE_COLORS.body} />
      <rect x="156" y="182" width="105" height="4" rx="1" fill={LINE_COLORS.body} />
      <rect x="156" y="190" width="90" height="4" rx="1" fill={LINE_COLORS.bodyLight} />
      <rect x="156" y="202" width="110" height="4" rx="1" fill={LINE_COLORS.body} />
      <rect x="156" y="210" width="95" height="4" rx="1" fill={LINE_COLORS.bodyLight} />

      {/* 自傳 */}
      <rect x="156" y="232" width="8" height="8" rx="4" fill={LINE_COLORS.accent} />
      <rect x="170" y="233" width="36" height="6" rx="1" fill={LINE_COLORS.title} />
      <rect x="156" y="246" width="115" height="4" rx="1" fill={LINE_COLORS.body} />
      <rect x="156" y="254" width="108" height="4" rx="1" fill={LINE_COLORS.body} />
      <rect x="156" y="262" width="100" height="4" rx="1" fill={LINE_COLORS.body} />
      <rect x="156" y="270" width="85" height="4" rx="1" fill={LINE_COLORS.bodyLight} />
      <rect x="156" y="278" width="110" height="4" rx="1" fill={LINE_COLORS.body} />
      <rect x="156" y="286" width="95" height="4" rx="1" fill={LINE_COLORS.bodyLight} />
    </g>
  </svg>
);

export const templateThumbnailComponents: Record<string, React.FC> = {
  corporate: CorporateThumbnail,
  modern: ModernThumbnail,
  creative: CreativeThumbnail,
};
