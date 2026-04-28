import { defineConfig } from "allure";

export default defineConfig({
  name: "Ness Automation Report",
  output: "./allure-report",
  historyPath: "./allure-history/history.jsonl",
  plugins: {
    awesome: {
      options: {
        reportName: "Ness Automation Report",
        singleFile: false,
        reportLanguage: "en",
      },
    },
  },
});
