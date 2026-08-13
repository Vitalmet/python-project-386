import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(here, "../..");
const dbPath = path.join(projectRoot, "e2e.sqlite");

const env = {
  ...process.env,
  DATABASE_URL: `sqlite:///${dbPath.replace(/\\/g, "/")}`,
};

fs.rmSync(dbPath, { force: true });

const options = { cwd: projectRoot, env, stdio: "inherit", shell: process.platform === "win32" };

const seed = spawnSync("poetry", ["run", "flask", "--app", "calendar_app", "seed"], options);
if (seed.status !== 0) {
  process.exit(seed.status ?? 1);
}

const server = spawn(
  "poetry",
  [
    "run",
    "flask",
    "--app",
    "calendar_app",
    "run",
    "--host",
    "127.0.0.1",
    "--port",
    "5000",
    "--no-reload",
    "--no-debugger",
  ],
  options,
);

const shutdown = () => server.kill();
process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
process.on("exit", shutdown);