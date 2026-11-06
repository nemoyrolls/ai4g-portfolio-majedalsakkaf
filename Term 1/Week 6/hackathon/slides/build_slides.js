const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const { applyTheme } = require("/Users/majed/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/220b44dd-5560-4fe7-a034-2b751278d108/943f8499-22f2-4e8e-8f05-5040a90af458/skills/pptx/scripts/apply_theme.js");

const OUT = process.argv[2] || "Hackathon6_Green_Transition_Pulse.pptx";

const THEME = {
  name: "Green Transition",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2B24", lt1: "FFFFFF", dk2: "1F4D3A", lt2: "EEF3EF",
    accent1: "1F4D3A", accent2: "F2B705", accent3: "5B6C7D",
    accent4: "D1495B", accent5: "00798C", accent6: "6A4C93",
    hlink: "00798C", folHlink: "6A4C93",
  },
};
const HEX = THEME.colors;

async function icon(Comp, color, size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: String(size) }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
  pres.author = "Majed Al-Sakkaf";
  pres.title = "Green Transition Pulse – Hackathon 6";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  const C = pres.SchemeColor;

  // ---------- Layouts ----------
  pres.defineSlideMaster({
    title: "DARK",
    background: { color: C.text2 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.3, w: 11.7, h: 1.4, fontSize: 48, bold: true, color: C.background1, valign: "bottom" }, text: "" } },
      { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.85, w: 11.7, h: 1.2, fontSize: 22, color: C.background2, valign: "top" }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "CONTENT",
    background: { color: C.background1 },
    margin: [0.5, 0.6, 0.6, 0.6],
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.9, fontSize: 34, bold: true, color: C.text2, valign: "middle" }, text: "" } },
      { text: { text: "Green Transition Pulse · Hackathon 6 · SDG 9", options: { x: 0.6, y: 7.0, w: 8, h: 0.3, fontSize: 10, color: C.accent3 } } },
    ],
    slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: HEX.accent3, align: "right" },
  });

  const add = (master, section) => pres.addSlide({ masterName: master, sectionTitle: section });
  const card = (s, x, y, w, h, name, fill = C.background2) =>
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.12, objectName: name });
  const circleIcon = async (s, Comp, x, y, d, bg, fg, name) => {
    s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: bg }, line: { color: bg }, objectName: name + " circle" });
    s.addImage({ data: await icon(Comp, fg), x: x + d * 0.24, y: y + d * 0.24, w: d * 0.52, h: d * 0.52, altText: name, objectName: name + " icon" });
  };
  const txt = (s, text, opts) => s.addText(text, { isTextBox: true, margin: 0, fontSize: 16, color: C.text1, valign: "top", ...opts });

  // ---------- 1. Title ----------
  pres.addSection({ title: "Opening" });
  let s = add("DARK", "Opening");
  s.addText("Green Transition Pulse", { placeholder: "title" });
  s.addText("Reading the mood of the Dutch energy transition, every hour", { placeholder: "body" });
  await circleIcon(s, fa.FaSolarPanel, 0.8, 0.9, 1.1, HEX.accent2, HEX.dk2, "solar");
  await circleIcon(s, fa.FaPlug, 2.1, 0.9, 1.1, HEX.lt2, HEX.dk2, "grid");
  txt(s, "Hackathon 6 – Live Pulse  ·  SDG 9  ·  Majed Al-Sakkaf  ·  resubmission", { x: 0.8, y: 6.4, w: 11.7, h: 0.4, fontSize: 14, color: C.background2 });
  s.addNotes("Green Transition Pulse reads Dutch news and Bluesky every hour about going green at home and about the electricity grid, and shows a municipality how the mood moves.");

  // ---------- 2. Problem ----------
  pres.addSection({ title: "Problem and user" });
  s = add("CONTENT", "Problem and user");
  s.addText("Households must go green while the grid is full", { placeholder: "title" });
  const stats = [
    ["15,498", "requests to take power from the grid waiting on 30 June 2026", fa.FaPlug, HEX.accent3],
    ["1 Jan 2027", "net metering for solar panels ends: feed-in no longer offsets use", fa.FaSolarPanel, HEX.accent2],
    ["2029", "at least a hybrid heat pump when a boiler is replaced (planned)", fa.FaFire, HEX.accent4],
  ];
  for (let i = 0; i < stats.length; i++) {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.6, 3.8, 4.1, "stat card " + (i + 1));
    await circleIcon(s, stats[i][2], x + 0.35, 1.9, 0.9, stats[i][3], HEX.lt1, "stat icon " + (i + 1));
    txt(s, stats[i][0], { x: x + 0.35, y: 3.0, w: 3.2, h: 1.0, fontSize: 44, bold: true, color: C.text2, fontFace: "Cambria" });
    txt(s, stats[i][1], { x: x + 0.35, y: 4.1, w: 3.2, h: 1.4, fontSize: 16 });
  }
  txt(s, "Sources: Netbeheer Nederland half-year figures via TPO (5 Oct 2026) · Rijksoverheid, salderingsregeling · Solar Magazine / Consumentenbond on the 2029 norm",
    { x: 0.6, y: 6.0, w: 12.1, h: 0.4, fontSize: 11, color: C.accent3, italic: true });
  s.addNotes("Three pressures at once: a full grid, the end of net metering, and a heat-pump norm. Residents hear all of this at the same time, and a municipality usually notices the frustration late, through complaints or the news.");

  // ---------- 3. User ----------
  s = add("CONTENT", "Problem and user");
  s.addText("Noor decides where the green budget goes", { placeholder: "title" });
  card(s, 0.6, 1.6, 4.4, 4.9, "persona card", C.text2);
  await circleIcon(s, fa.FaUserTie, 0.95, 1.95, 1.0, HEX.accent2, HEX.dk2, "persona");
  txt(s, "Noor Bakker", { x: 0.95, y: 3.15, w: 3.8, h: 0.5, fontSize: 24, bold: true, color: C.background1, fontFace: "Cambria" });
  txt(s, "Energy-transition advisor, sustainability team, Municipality of The Hague (persona)", { x: 0.95, y: 3.7, w: 3.7, h: 0.9, fontSize: 14, color: C.background2 });
  txt(s, "Every week: which green measure do we promote next, and where does the subsidy and campaign budget go?",
    { x: 0.95, y: 4.75, w: 3.7, h: 1.5, fontSize: 16, italic: true, color: C.background1 });
  const acts = [
    ["Solar frustration rises as net metering ends", "Shift budget to insulation: saves now, no extra grid load"],
    ["Heat pumps liked, but grid mood falls", "Promote \"insulate first, then a heat pump\""],
    ["Negative peak about one measure", "Open the items, add the objection to the FAQ and info evening"],
  ];
  txt(s, "The pulse shows…", { x: 5.5, y: 1.6, w: 3.5, h: 0.4, fontSize: 14, bold: true, color: C.accent3 });
  txt(s, "…Noor acts", { x: 9.3, y: 1.6, w: 3.4, h: 0.4, fontSize: 14, bold: true, color: C.accent3 });
  for (let i = 0; i < acts.length; i++) {
    const y = 2.1 + i * 1.5;
    card(s, 5.5, y, 3.5, 1.25, "signal " + (i + 1));
    txt(s, acts[i][0], { x: 5.7, y: y + 0.18, w: 3.1, h: 0.9, fontSize: 15, valign: "middle" });
    await circleIcon(s, fa.FaArrowRight, 9.0, y + 0.37, 0.5, HEX.lt1, HEX.dk2, "arrow " + (i + 1));
    card(s, 9.5, y, 3.2, 1.25, "action " + (i + 1), C.accent2);
    txt(s, acts[i][1], { x: 9.7, y: y + 0.18, w: 2.85, h: 0.9, fontSize: 15, bold: true, color: C.text2, valign: "middle" });
  }
  s.addNotes("Noor is a persona; the role is real. The decision is weekly, during the heating season. Surveys come a few times a year; prices and grid news change week by week.");

  // ---------- 4. Pipeline ----------
  pres.addSection({ title: "Tool" });
  s = add("CONTENT", "Tool");
  s.addText("Every hour: fetch, filter, score, store, show", { placeholder: "title" });
  const steps = [
    [fa.FaRss, "Fetch", "Google News NL, Bluesky (Dutch), 4 RSS feeds"],
    [fa.FaFilter, "Filter", "Keep items about solar, heat pumps, insulation, EV charging, grid"],
    [fa.FaBrain, "Score", "XLM-RoBERTa (main) and RobBERT (comparison) on every item"],
    [fa.FaDatabase, "Store", "CSV with time written + time collected; no names"],
    [fa.FaChartLine, "Show", "Streamlit: % negative per line, and the items behind it"],
  ];
  for (let i = 0; i < steps.length; i++) {
    const x = 0.6 + i * 2.5;
    await circleIcon(s, steps[i][0], x + 0.6, 1.7, 1.0, HEX.dk2, HEX.lt1, "step " + steps[i][1]);
    txt(s, steps[i][1], { x, y: 2.9, w: 2.2, h: 0.45, fontSize: 20, bold: true, color: C.text2, align: "center", fontFace: "Cambria" });
    txt(s, steps[i][2], { x, y: 3.4, w: 2.2, h: 1.3, fontSize: 14, align: "center" });
  }
  card(s, 0.6, 5.0, 12.1, 1.5, "data card");
  const nums = [["2,360", "items so far"], ["1,758", "Bluesky posts"], ["602", "news items"], ["5", "lines"]];
  for (let i = 0; i < nums.length; i++) {
    txt(s, nums[i][0], { x: 0.9 + i * 3.0, y: 5.15, w: 2.6, h: 0.75, fontSize: 36, bold: true, color: C.text2, fontFace: "Cambria" });
    txt(s, nums[i][1], { x: 0.9 + i * 3.0, y: 5.9, w: 2.6, h: 0.4, fontSize: 14, color: C.accent3 });
  }
  s.addNotes("Runs every hour on GitHub Actions. Main model: cardiffnlp/twitter-xlm-roberta-base-sentiment, trained on tweets, 3 classes including neutral. Comparison: DTAI-KULeuven/robbert-v2-dutch-sentiment, Dutch, trained on book reviews, positive/negative only. Honest note: the collector was not running between 13 Oct and 6 Nov.");

  // ---------- 5. Media vs public ----------
  s = add("CONTENT", "Tool");
  s.addText("The public is far more negative than the news", { placeholder: "title" });
  const lines = ["Zonnepanelen", "Warmtepomp", "Isolatie", "Laadpalen", "Stroomnet"];
  s.addChart(pres.charts.BAR, [
    { name: "News", labels: lines, values: [14, 10, 8, 17, 23] },
    { name: "Bluesky", labels: lines, values: [35, 34, 38, 34, 37] },
  ], {
    x: 0.6, y: 1.5, w: 7.6, h: 5.1, barDir: "col", barGrouping: "clustered",
    chartColors: [HEX.accent3, HEX.dk2],
    showTitle: true, title: "% of items labelled negative by XLM-RoBERTa, since 1 Oct", titleFontSize: 14, titleColor: HEX.dk1, titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 12, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt", dataLabelFormatCode: "0\"%\"",
    showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
    catAxisLabelColor: HEX.dk1, catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt",
    valAxisLabelColor: HEX.accent3, valAxisLabelFontSize: 11, valAxisLabelFontFace: "+mn-lt", valAxisMaxVal: 50, valAxisMinVal: 0,
    valGridLine: { color: "D9E2DC", size: 0.5 }, catGridLine: { style: "none" },
    objectName: "media vs public chart",
  });
  card(s, 8.6, 1.6, 4.1, 4.9, "insight card");
  txt(s, "What Noor learns", { x: 8.9, y: 1.85, w: 3.5, h: 0.45, fontSize: 20, bold: true, color: C.text2, fontFace: "Cambria" });
  s.addText([
    { text: "Headlines stay factual; residents on Bluesky are 2–4× more negative on every line", options: { bullet: true, breakLine: true } },
    { text: "Insulation news is calm (8%), posts are not (38%)", options: { bullet: true, breakLine: true } },
    { text: "Reading only the news would make the transition look smooth", options: { bullet: true } },
  ], { isTextBox: true, x: 8.9, y: 2.45, w: 3.5, h: 3.8, fontSize: 16, color: C.text1, paraSpaceAfter: 10, valign: "top", margin: 0 });
  s.addNotes("Live demo: open the dashboard, Media vs public. Remember the model under-reads negatives (honest test), so these are lower bounds.");

  // ---------- 6. Behind a peak ----------
  s = add("CONTENT", "Tool");
  s.addText("Behind a peak: heat pumps on 10 October", { placeholder: "title" });
  card(s, 0.6, 1.6, 3.6, 4.9, "peak card", C.text2);
  txt(s, "50%", { x: 0.95, y: 1.9, w: 3.0, h: 1.2, fontSize: 66, bold: true, color: C.accent2, fontFace: "Cambria" });
  txt(s, "of 28 heat-pump items labelled negative, the highest day for this line", { x: 0.95, y: 3.15, w: 3.0, h: 1.1, fontSize: 16, color: C.background1 });
  txt(s, "Same day in the news: \"Hybride warmtepomp straks de norm? 'Een verplicht systeem past niet bij ieder huishouden'\"",
    { x: 0.95, y: 4.4, w: 3.0, h: 1.9, fontSize: 13, italic: true, color: C.background2 });
  const quotes = [
    ["\"En wie betaalt die warmtepomp dan? Dat is dus niet voor iedereen 'gewoon'\"", "Who pays for it? Not 'normal' for everyone"],
    ["\"En een warmtepomp, zonnepanelen en een batterij zijn ook duur.\"", "Heat pump, panels and battery are expensive too"],
    ["\"Als je alles ineens perfect wil hebben voor een warmtepomp, dan duurt het te lang…\"", "Debate: insulate first, or heat pump first?"],
  ];
  for (let i = 0; i < quotes.length; i++) {
    const y = 1.6 + i * 1.25;
    card(s, 4.6, y, 8.1, 1.05, "quote " + (i + 1));
    txt(s, quotes[i][0], { x: 4.85, y: y + 0.12, w: 7.6, h: 0.5, fontSize: 15, italic: true });
    txt(s, quotes[i][1], { x: 4.85, y: y + 0.6, w: 7.6, h: 0.35, fontSize: 13, color: C.accent3 });
  }
  card(s, 4.6, 5.45, 8.1, 1.05, "takeaway", C.accent2);
  txt(s, "Takeaway for Noor: the objection is cost, not the technology → add cost and subsidy answers for lower incomes to the FAQ and the next info evening",
    { x: 4.85, y: 5.55, w: 7.6, h: 0.85, fontSize: 15, bold: true, color: C.text2, valign: "middle" });
  s.addNotes("Live demo: dashboard, 'What's behind a peak or dip?', line Warmtepomp, day 10 Oct. Quotes are public Bluesky posts; no names are stored or shown.");

  // ---------- 7. Honest test table ----------
  pres.addSection({ title: "Honest test" });
  s = add("CONTENT", "Honest test");
  s.addText("Honest test: 50 labelled items, three readers", { placeholder: "title" });
  const hdr = (t) => ({ text: t, options: { bold: true, color: HEX.lt1, fill: { color: HEX.dk2 }, fontSize: 15 } });
  const cell = (t, bold = false) => ({ text: t, options: { bold, fontSize: 15, color: HEX.dk1 } });
  s.addTable([
    [hdr("Model"), hdr("All 50"), hdr("30 non-neutral"), hdr("News (25)"), hdr("Bluesky (25)")],
    [cell("XLM-RoBERTa (main)", true), cell("64%", true), cell("43%"), cell("76%"), cell("52%")],
    [cell("RobBERT Dutch (comparison)"), cell("38%"), cell("63%", true), cell("24%"), cell("52%")],
    [cell("Word list (no AI)"), cell("62%"), cell("40%"), cell("84%", true), cell("40%")],
  ], { x: 0.6, y: 1.6, w: 12.1, colW: [3.9, 1.9, 2.3, 2.0, 2.0], rowH: 0.6, border: { type: "solid", pt: 0.5, color: "D9E2DC" }, fill: { color: HEX.lt1 }, valign: "middle", objectName: "results table" });
  const findings = [
    [fa.FaBalanceScale, "Labels", "10 per line, half news, half Bluesky. Drafted by Claude, checked by me one by one"],
    [fa.FaBook, "RobBERT", "Knows Dutch, but trained on book reviews: 17 of 20 neutral items became \"positive\""],
    [fa.FaNewspaper, "Word list", "Good on headlines (duurder, stop), lost on sarcasm and slang on Bluesky"],
  ];
  for (let i = 0; i < findings.length; i++) {
    const x = 0.6 + i * 4.1;
    await circleIcon(s, findings[i][0], x, 4.45, 0.75, HEX.lt2, HEX.dk2, "finding " + findings[i][1]);
    txt(s, findings[i][1], { x: x + 0.95, y: 4.45, w: 2.8, h: 0.4, fontSize: 17, bold: true, color: C.text2 });
    txt(s, findings[i][2], { x: x + 0.95, y: 4.9, w: 2.85, h: 1.6, fontSize: 14 });
  }
  s.addNotes("Agreement with my labels. RobBERT can't say neutral, so the non-neutral column is its fair score. The word list only contains general Dutch sentiment words; an earlier version with words copied from the test items was removed because it inflated the score.");

  // ---------- 8. Failure that taught most ----------
  s = add("CONTENT", "Honest test");
  s.addText("The failure that taught me most: the model is too calm", { placeholder: "title" });
  s.addChart(pres.charts.BAR, [
    { name: "My labels (average)", labels: lines, values: [-0.3, -0.3, 0.0, -0.1, -0.5] },
    { name: "XLM-RoBERTa (average mood)", labels: lines, values: [0.0, 0.01, -0.08, 0.06, -0.06] },
  ], {
    x: 0.6, y: 1.5, w: 7.0, h: 5.1, barDir: "col", barGrouping: "clustered",
    chartColors: [HEX.accent4, HEX.accent3],
    showTitle: true, title: "Average tone per line on the 50 test items (−1 … +1)", titleFontSize: 14, titleColor: HEX.dk1, titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 11, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt", dataLabelFormatCode: "+0.00;-0.00;0",
    showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
    catAxisLabelColor: HEX.dk1, catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt", catAxisLabelPos: "low",
    valAxisLabelColor: HEX.accent3, valAxisLabelFontSize: 11, valAxisLabelFontFace: "+mn-lt", valAxisMaxVal: 0.2, valAxisMinVal: -0.6, valAxisMajorUnit: 0.2,
    valGridLine: { color: "D9E2DC", size: 0.5 }, catGridLine: { style: "none" },
    objectName: "human vs model chart",
  });
  card(s, 8.0, 1.6, 4.7, 2.2, "example card");
  txt(s, "\"Deel van Gelderland krijgt aansluitstop op stroomnet\"", { x: 8.3, y: 1.8, w: 4.1, h: 0.9, fontSize: 16, italic: true });
  txt(s, "Bad news for residents, but no emotional word in it → model says neutral. Grid items: only 30% right.", { x: 8.3, y: 2.7, w: 4.1, h: 1.0, fontSize: 14, color: C.accent3 });
  card(s, 8.0, 4.05, 4.7, 2.45, "design change card", C.text2);
  txt(s, "When it says \"negative\", it was right 9 of 9", { x: 8.3, y: 4.25, w: 4.1, h: 0.8, fontSize: 18, bold: true, color: C.accent2, fontFace: "Cambria" });
  txt(s, "So the dashboard now shows % negative items by default, a trustworthy lower bound, instead of an average that hides frustration.",
    { x: 8.3, y: 5.05, w: 4.1, h: 1.3, fontSize: 14, color: C.background1 });
  s.addNotes("The grid: my labels average −0.50, the model −0.06. It misses half of the negatives (10 of 21 called neutral) but never invents one. That changed the product: % negative as default measure, and read direction, not level.");

  // ---------- 9. Ethics ----------
  pres.addSection({ title: "Ethics and conclusion" });
  s = add("CONTENT", "Ethics and conclusion");
  s.addText("Who is missing, and what I did about it", { placeholder: "title" });
  const missing = [
    [fa.FaHome, "Renters and low-income households", "often can't install solar or a heat pump, and post less"],
    [fa.FaUserClock, "Older residents and people offline", "many decide about their own boiler"],
    [fa.FaLanguage, "Non-Dutch speakers", "we only fetch Dutch posts and news"],
    [fa.FaUsers, "Most of the public", "Bluesky is small; X, Facebook, WhatsApp groups not included"],
  ];
  txt(s, "Not in the stream", { x: 0.6, y: 1.5, w: 6, h: 0.45, fontSize: 18, bold: true, color: C.accent4 });
  for (let i = 0; i < missing.length; i++) {
    const y = 2.05 + i * 1.12;
    await circleIcon(s, missing[i][0], 0.6, y, 0.8, HEX.lt2, HEX.accent4, "missing " + (i + 1));
    txt(s, missing[i][1], { x: 1.6, y: y + 0.02, w: 4.9, h: 0.4, fontSize: 16, bold: true });
    txt(s, missing[i][2], { x: 1.6, y: y + 0.42, w: 4.9, h: 0.5, fontSize: 14, color: C.accent3 });
  }
  card(s, 7.0, 1.5, 5.7, 5.0, "measures card");
  txt(s, "What I did", { x: 7.3, y: 1.7, w: 5.1, h: 0.45, fontSize: 18, bold: true, color: C.text2 });
  s.addText([
    { text: "No names, handles or post links stored; mentions become @user", options: { bullet: true, breakLine: true } },
    { text: "Number of items next to every point; points under 5 items hidden", options: { bullet: true, breakLine: true } },
    { text: "Warning banner: written mood ≠ what residents think", options: { bullet: true, breakLine: true } },
    { text: "% negative by default, because the test showed it is trustworthy", options: { bullet: true, breakLine: true } },
    { text: "Notice for collection gaps, so missing data isn't read as a trend", options: { bullet: true } },
  ], { isTextBox: true, x: 7.3, y: 2.3, w: 5.1, h: 4.0, fontSize: 16, color: C.text1, paraSpaceAfter: 10, valign: "top", margin: 0 });
  s.addNotes("The biggest risk: Noor moves budget away from a measure because 'the mood is fine', leaving behind exactly the households without a voice in this data. The model also makes things look calmer than they are. Not for: judging people or neighbourhoods, or reading silence as satisfaction.");

  // ---------- 10. Conclusion ----------
  s = add("DARK", "Ethics and conclusion");
  s.addText("I'd hand Noor XLM-RoBERTa: read direction, not level", { placeholder: "title" });
  s.addText("A rising share of negative items is worth opening; one number on its own is not a fact about residents", { placeholder: "body" });
  const next = [["Fine-tune", "on a few hundred labelled items, starting with grid news"], ["Talk to a real team", "check the decision with a municipal sustainability team"], ["Widen the voices", "add sources that reach renters and older residents"]];
  for (let i = 0; i < next.length; i++) {
    const x = 0.8 + i * 3.95;
    txt(s, next[i][0], { x, y: 5.35, w: 3.6, h: 0.45, fontSize: 18, bold: true, color: C.accent2 });
    txt(s, next[i][1], { x, y: 5.8, w: 3.6, h: 0.8, fontSize: 14, color: C.background2 });
  }
  s.addNotes("Next steps: fine-tuning is allowed by the brief and would target the biggest failure, grid news. Then validate the persona's decision with a real sustainability team.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
