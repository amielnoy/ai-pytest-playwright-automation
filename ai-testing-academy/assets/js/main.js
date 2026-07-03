/* Entry point. Inject the active language's regions, wire the interactive layers
   in order, then expose the handlers the inline onclick/onchange attributes call. */
import { $ } from './dom.js';
import { applyLocale } from './i18n.js';
import { initProviders, onProviderChange, testConnection, resetSettings } from './providers.js';
import { initResume, handleResumeFile, evaluateResume, showImprovedResume, downloadImprovedPdf } from './resume.js';
import { initInterview, startInterview, sendAnswer, requestVerdict } from './interview.js';
import { initQuestions } from './questions.js';
import { initUx } from './ux.js';
applyLocale(); // must be first — creates the DOM the rest queries
initProviders();
initResume();
initInterview();
initQuestions(); // adds the questions section + nav link before UX wires scroll-spy/chips
initUx();
// Inline handlers in the injected HTML resolve against the global scope.
Object.assign(window, {
    $,
    onProviderChange, testConnection, resetSettings,
    handleResumeFile, evaluateResume, showImprovedResume, downloadImprovedPdf,
    startInterview, sendAnswer, requestVerdict
});
