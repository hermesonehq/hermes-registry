/**
 * Build an offline, minimal Iconify bundle from the icons actually referenced
 * in the registry index. Reads every `entry.iconify` id (e.g. "lucide:square-
 * kanban"), groups by prefix, subsets the matching `@iconify-json/<prefix>`
 * collection down to just the used icons, and writes them merged into
 * `src/generated/icons.json`.
 *
 * This keeps the client bundle tiny (only used glyphs ship) while staying fully
 * offline — no runtime calls to the Iconify CDN. Re-run on every build; it is
 * wired into the `build` script. Adding a new icon set only requires installing
 * its `@iconify-json/<prefix>` package — this script discovers prefixes from the
 * index automatically.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";
import { getIcons } from "@iconify/utils";

const require = createRequire(import.meta.url);
const here = path.dirname(fileURLToPath(import.meta.url));
const INDEX = path.resolve(here, "../../index.json");
const OUT = path.resolve(here, "../src/generated/icons.json");

function main() {
  if (!fs.existsSync(INDEX)) {
    console.warn(`[gen-icons] ${INDEX} not found; writing empty bundle`);
    write({});
    return;
  }

  const { entries = [] } = JSON.parse(fs.readFileSync(INDEX, "utf8"));

  // Collect used icon names grouped by Iconify prefix.
  const byPrefix = new Map(); // prefix -> Set(name)
  for (const e of entries) {
    const id = e.iconify;
    if (typeof id !== "string" || !id.includes(":")) continue;
    const [prefix, name] = id.split(":");
    if (!prefix || !name) continue;
    if (!byPrefix.has(prefix)) byPrefix.set(prefix, new Set());
    byPrefix.get(prefix).add(name);
  }

  const bundle = {};
  let total = 0;
  for (const [prefix, names] of byPrefix) {
    let collection;
    try {
      collection = require(`@iconify-json/${prefix}/icons.json`);
    } catch {
      console.warn(
        `[gen-icons] missing package @iconify-json/${prefix} for ${names.size} icon(s); ` +
          `run: npm i @iconify-json/${prefix}`
      );
      continue;
    }
    const subset = getIcons(collection, [...names]);
    if (!subset) continue;
    const found = Object.keys(subset.icons).length;
    const missing = [...names].filter(
      (n) => !subset.icons[n] && !(subset.aliases && subset.aliases[n])
    );
    if (missing.length) {
      console.warn(`[gen-icons] ${prefix}: unknown icon(s): ${missing.join(", ")}`);
    }
    bundle[prefix] = subset;
    total += found;
  }

  write(bundle);
  console.log(
    `[gen-icons] wrote ${total} icon(s) across ${Object.keys(bundle).length} set(s) -> ${path.relative(process.cwd(), OUT)}`
  );
}

function write(bundle) {
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify(bundle) + "\n");
}

main();
