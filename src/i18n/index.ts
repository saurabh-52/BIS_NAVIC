import en from './en.json';
import hi from './hi.json';

const translations: Record<string, typeof en> = { en, hi };

type NestedKeys<T> = T extends object
  ? { [K in keyof T]: K extends string ? (T[K] extends object ? `${K}.${NestedKeys<T[K]>}` : K) : never }[keyof T]
  : never;

export type TranslationKey = NestedKeys<typeof en>;

export function getTranslation(lang: string, key: string): string {
  const dict = translations[lang] || translations['en'];
  const keys = key.split('.');
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let result: any = dict;
  for (const k of keys) {
    if (result && typeof result === 'object' && k in result) {
      result = result[k];
    } else {
      // Fallback to English
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      let fallback: any = translations['en'];
      for (const fk of keys) {
        if (fallback && typeof fallback === 'object' && fk in fallback) {
          fallback = fallback[fk];
        } else {
          return key; // Return key if not found
        }
      }
      return typeof fallback === 'string' ? fallback : key;
    }
  }
  return typeof result === 'string' ? result : key;
}

export function useTranslation(lang: string) {
  return {
    t: (key: string) => getTranslation(lang, key),
  };
}
