/* Shared types for the AI Testing Academy app. */

export interface Msg {
  role: string;
  content: string;
}

export interface BuiltRequest {
  url: string;
  headers: Record<string, string>;
  body: unknown;
}

/* A provider is a self-contained strategy (see providers.ts). */
export interface Provider {
  label: string;
  placeholder: string;
  models: string[];
  validateKey?(key: string): void;
  build(key: string, model: string, system: string, messages: Msg[], maxTokens: number): BuiltRequest;
  parse(data: any): string;
  keyHint?(key: string, status: number): string;
}

/* The 59 UI string keys. Because Locale.s is Record<StringKey, string>, a locale
   missing a key — or a typo — is a compile error, so en/he can never drift. */
export type StringKey =
  | 'keyLabelGemini' | 'keyLabelAnthropic' | 'keyLabelOpenai' | 'placeholderEnvKey'
  | 'labelSuffixLocal' | 'labelSuffixEnv' | 'errNoKey' | 'errKeyNotAnthropic'
  | 'errKeyNotOpenai' | 'errBlockedPrefix' | 'errBlockedMid' | 'errBlockedCauses'
  | 'errBlockedTry' | 'errBlockedOpenUrl' | 'errGeminiKeyHint' | 'errApiPrefix'
  | 'statusTesting' | 'pingSystem' | 'pingUser' | 'statusOkPrefix' | 'errNoJson'
  | 'errCdnFail' | 'uploadReading' | 'errFormatPrefix' | 'errFormatSuffix'
  | 'errExtractFail' | 'uploadLoadedMid' | 'uploadLoadedSuffix' | 'uploadPrompt'
  | 'errResumeEmpty' | 'btnEvaluating' | 'promptRolePrefix' | 'promptResumeLabel'
  | 'btnEvaluate' | 'errNoEval' | 'promptRolePrefixImprove' | 'promptJobDescLabel'
  | 'promptEvalResultsLabel' | 'promptOriginalResumeLabel' | 'btnImproving'
  | 'btnBuildResume' | 'btnPreparingPdf' | 'errPopupBlocked' | 'btnDownloadPdf'
  | 'statusInterviewerThinking' | 'errNoKeyInterview' | 'interviewOpener'
  | 'btnRestartInterview' | 'interviewOpenerMsg' | 'statusGeneratingVerdict'
  | 'videoMissingPrefix' | 'videoMissingSuffix' | 'videoLoading' | 'themeLabelLight'
  | 'themeLabelDark' | 'copyBtn' | 'copyBtnDone' | 'copyBtnReset' | 'copyBtnFail'
  | 'micTitle' | 'micListening' | 'voiceModeOn' | 'voiceModeOff';

export interface LocalePrompts {
  resume: string;
  improve: string;
  interview: string;
}

export interface LocaleUi {
  skip: string;
  navOpen: string;
  toTop: string;
}

/* One language's content: HTML region fragments + prompts + UI strings. */
export interface Locale {
  dir: 'ltr' | 'rtl';
  nav: string;
  hero: string;
  main: string;
  footer: string;
  prompts: LocalePrompts;
  s: Record<StringKey, string>;
  ui: LocaleUi;
}

/* Resume-evaluation result returned (as JSON) by the model. */
export interface EvalCategory {
  name: string;
  score: number;
}

export interface EvalResult {
  overall: number;
  summary?: string;
  categories?: EvalCategory[];
  strengths?: string[];
  gaps?: string[];
  recommendations?: string[];
}
