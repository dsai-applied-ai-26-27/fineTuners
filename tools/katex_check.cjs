// Parses LaTeX fragments with the same KaTeX build the browser uses.
// Called by ingest/mathcheck.py:  stdin  [{"tex": "...", "display": true}, ...]
//                                 stdout [null | "error message", ...]
// No npm install needed: it loads the vendored file directly.
const path = require("path");
const katex = require(path.join(__dirname, "..", "static", "vendor", "katex", "katex.min.js"));

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => (input += chunk));
process.stdin.on("end", () => {
  const results = JSON.parse(input).map(({ tex, display }) => {
    try {
      katex.renderToString(tex, { displayMode: display, throwOnError: true, strict: "ignore" });
      return null;
    } catch (error) {
      return String(error.message || error);
    }
  });
  process.stdout.write(JSON.stringify(results));
});
