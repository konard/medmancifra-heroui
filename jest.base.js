/** @type {import('jest').Config} */
module.exports = {
  collectCoverage: true,
  coverageProvider: "v8",
  coverageReporters: ["json"],
  coverageDirectory: "../",
  coveragePathIgnorePatterns: ["/node_modules/"],
};
