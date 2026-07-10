#!/usr/bin/env node
/**
 * Starts the Firestore emulator via firebase-tools, runs the mocha rules
 * tests, then shuts the emulator down.  Run from the frontend/ directory:
 *   node tests/run-rules-test.js
 */
const { execSync, spawn } = require("child_process");
const path = require("path");

const FIREBASE_DIR = path.resolve(__dirname, "../../firebase");
const PROJECT_ID = "smartarena-test-rules";

async function main() {
  console.log("Starting Firestore emulator...");
  const emu = spawn(
    "firebase",
    ["emulators:start", "--project", PROJECT_ID, "--only", "firestore"],
    { cwd: FIREBASE_DIR, stdio: "pipe", shell: true }
  );

  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("Emulator startup timed out")), 45000);
    let output = "";
    let settled = false;
    emu.stdout.on("data", (d) => {
      const s = d.toString();
      output += s;
      process.stdout.write(s);
      if (!settled && (output.includes("All emulators ready") || /running on/i.test(output))) {
        settled = true;
        clearTimeout(timer);
        setTimeout(resolve, 2000);
      }
    });
    emu.stderr.on("data", (d) => { output += d.toString(); process.stderr.write(d); });
    emu.on("error", (e) => { if (!settled) { settled = true; clearTimeout(timer); reject(e); } });
    emu.on("exit", (code) => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        reject(new Error(`Emulator exited early with code ${code}: ${output.slice(-500)}`));
      }
    });
  });

  console.log("\nRunning Firestore rules tests...\n");
  let code = 0;
  try {
    execSync("npx mocha tests/firestore-rules.test.js --timeout 15000 --exit", {
      cwd: path.resolve(__dirname, ".."),
      stdio: "inherit",
    });
  } catch (e) {
    code = e.status || 1;
  }

  emu.kill("SIGTERM");
  await new Promise((r) => setTimeout(r, 2000));
  process.exit(code);
}

main().catch((e) => { console.error(e); process.exit(1); });
