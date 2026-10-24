// Every layout once, for checking the template. Not a real post.
window.DECK = {
  id: "sampler", series: "My Series",
  slides: [
    { type: "cover", kicker: "AI words, explained", title: "15 AI words everyone uses. ==Explained== like you're not an engineer.", note: "save this one", photo: "assets/avi-cutout.png" },
    { type: "statement", title: "You don't need to code to ==understand AI==.", body: "You need 15 words. I use them every day at work, and I'll explain each one like I would to my mom." },
    { type: "point", n: "1", title: "ChatGPT doesn't look things up.", body: "It guesses the next word, one at a time, from patterns it learned.", eg: "Your phone keyboard's autocomplete, after reading the internet.", note: "that's why it can be confidently wrong" },
    { type: "steps", kicker: "What happens when you hit Enter", title: "Your question takes 4 stops", steps: [{ label: "Step 1", text: "Your text is cut into tokens" }, { label: "Step 2", text: "Each token becomes numbers" }, { label: "Step 3", text: "The model scores every next word", hot: true }, { label: "Step 4", text: "It picks one and repeats" }] },
    { type: "compare", title: "Using AI in your job search", left: { head: "Gets you rejected", points: ["Generic AI cover letters", "Reading AI answers live"] }, right: { head: "Gets you hired", points: ["Mock interviews with AI", "Tailoring your resume, truthfully"] } },
    { type: "myth", n: "4", myth: "AI detectors can catch AI writing.", fact: "They ==can't==, reliably.", body: "OpenAI shut its own detector down. It caught only 26% of AI text." },
    { type: "checklist", title: "Change these tonight", items: [{ text: "Turn off training on your chats", small: "Settings → Data controls" }, { text: "Use temporary chat for private stuff" }, { text: "Clear saved memory you don't need" }] },
    { type: "glossary", kicker: "Words 3 & 4", terms: [{ term: "Token", def: "A piece of a word. AI reads tokens, not letters.", eg: "un · believ · able" }, { term: "Context window", def: "How much of your chat the AI can see at once." }] },
    { type: "story", stamp: "MIT · 1966", text: ["A chatbot that only repeated your words back made people pour their hearts out.", "Its creator's secretary asked them to ==leave the room==."] },
    { type: "stat", kicker: "Stanford, 2023", number: "61%", title: "of essays by non-native English writers were flagged as AI.", source: "Liang et al., Stanford (2023)" },
    { type: "timeline", title: "How a gaming chip took over AI", events: [{ when: "1999", text: "GeForce 256, sold for games" }, { when: "2012", text: "AlexNet trains on 2 gaming GPUs" }, { when: "2026", text: "1-million-GPU clusters", hot: true }] },
    { type: "template", title: "The brief I give ChatGPT", copy: "Context: I'm a [role] writing for [who].\nGoal: [what done looks like]\nRules: [length, tone, must / must not]\nExample: [one good output]\nFormat: [bullets / table / steps]" },
    { type: "recap", items: ["AI predicts words, it doesn't look up facts", "Tokens are pieces of words", "Context window = what it can see", "Detectors don't work reliably"] },
    { type: "cta", question: "Did you know ChatGPT doesn't look things up?", share: "Send this to the friend who trusts ChatGPT with everything." }
  ]
};
