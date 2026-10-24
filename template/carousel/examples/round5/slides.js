// Round 5 layouts once each, for checking the template. Not a real post.
window.DECK = {
  id: "round5", series: "AI Decoded",
  slides: [
    { type: "cover", kicker: "Roadmap", title: "The order I'd learn ==AI engineering== if I started from zero", note: "save this one" },
    { type: "finding", kicker: "Check 1 of 6", title: "Count what's missing", body: "COUNTIF counts the empty cells in every column that matters.", code: "SELECT COUNT(*) AS total_rows,\n  COUNTIF(email IS NULL) AS missing_emails\nFROM signups", output: "total_rows 162 | missing_emails 6", found: "IS NULL found 9. **9 more were typed as 'null' and 'NA'.**" },
    { type: "finding", kicker: "Check 2 of 6", title: "One country, many spellings", rows: [["\"U.K.\"", "United Kingdom"], ["\"uk\"", "United Kingdom"], ["\"IE\"", "Ireland"]], found: "UPPER and TRIM first, so **one list catches every spelling**." },
    { type: "dodont", title: "Limited colour palette", body: "Fewer colours read as more confident.", bad: { text: "8 accent colours" }, good: { text: "1 accent + greys" } },
    { type: "roadmap", title: "Months 1–3", steps: [{ what: "Python, properly", resource: "CS50P · free" }, { what: "Git + GitHub", resource: "Pro Git book · free" }, { what: "One real project", resource: "build-your-own-x repo", hot: true }] },
    { type: "photo", image: "assets/desk.jpg", bubble: "What you need as a beginner?", items: ["One language, learned properly", "100–150 DSA problems done well", "Git, SQL, 1–2 real projects"] },
    { type: "cta", question: "Would you follow this roadmap?", share: "Send it to the friend starting out." }
  ]
};
