import { defineConfig } from "allure";

export default defineConfig({
  name: "Ness Automation Report",
  output: "./allure-report",
  historyPath: "./allure-history",
  results: ["./allure-results"],
  plugins: {
    awesome: {
      options: {
        singleFile: false,
        reportLanguage: "en",
      },
    },
  },
});
