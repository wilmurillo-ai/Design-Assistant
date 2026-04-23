const fs = require("fs");
const path = require("path");

const skillPath = path.join(__dirname, "SKILL.md");
const referencesDir = path.join(__dirname, "references");

module.exports = {
  skillPath,
  referencesDir,
  get content() {
    return fs.readFileSync(skillPath, "utf8");
  },
};
