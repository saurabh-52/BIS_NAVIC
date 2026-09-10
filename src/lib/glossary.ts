export type GlossaryTerm = 
  | "ISI" 
  | "CRS" 
  | "CML" 
  | "R_NUMBER" 
  | "HUID" 
  | "ECOMARK" 
  | "FMCS" 
  | "MSME";

type GlossaryDictionary = Record<GlossaryTerm, {
  title: { en: string; hi: string };
  desc: { en: string; hi: string };
}>;

export const GLOSSARY: GlossaryDictionary = {
  ISI: {
    title: { en: "ISI Mark", hi: "ISI मार्क" },
    desc: { 
      en: "A certification mark for industrial products in India. It ensures the product conforms to Indian Standards (IS) developed by BIS, guaranteeing safety and quality.",
      hi: "भारत में औद्योगिक उत्पादों के लिए एक प्रमाणीकरण चिह्न। यह सुनिश्चित करता है कि उत्पाद BIS द्वारा विकसित भारतीय मानकों (IS) के अनुरूप है, जिससे सुरक्षा और गुणवत्ता की गारंटी मिलती है।"
    }
  },
  CRS: {
    title: { en: "CRS (Compulsory Registration Scheme)", hi: "CRS (अनिवार्य पंजीकरण योजना)" },
    desc: {
      en: "A scheme primarily for electronics and IT goods. Manufacturers must get their products tested at BIS-recognized labs and register them before selling in India.",
      hi: "मुख्य रूप से इलेक्ट्रॉनिक्स और आईटी सामानों के लिए एक योजना। निर्माताओं को भारत में बेचने से पहले BIS-मान्यता प्राप्त प्रयोगशालाओं में अपने उत्पादों का परीक्षण कराना और पंजीकृत करना आवश्यक है।"
    }
  },
  CML: {
    title: { en: "CM/L Number", hi: "CM/L नंबर" },
    desc: {
      en: "Certification Mark Licence number. A unique 7 or 8 digit number granted by BIS to a manufacturer, printed alongside the ISI mark on products.",
      hi: "प्रमाणीकरण चिह्न लाइसेंस नंबर। BIS द्वारा निर्माता को प्रदान किया गया एक विशिष्ट 7 या 8 अंकों का नंबर, जो उत्पादों पर ISI मार्क के साथ मुद्रित होता है।"
    }
  },
  R_NUMBER: {
    title: { en: "R-Number", hi: "R-नंबर" },
    desc: {
      en: "Registration Number assigned under CRS. Usually an 8-digit number printed with the standard mark on electronics to verify authenticity.",
      hi: "CRS के तहत दिया गया पंजीकरण नंबर। प्रामाणिकता सत्यापित करने के लिए आमतौर पर इलेक्ट्रॉनिक्स पर मानक चिह्न के साथ मुद्रित 8 अंकों का नंबर।"
    }
  },
  HUID: {
    title: { en: "HUID (Hallmark Unique Identification)", hi: "HUID (हॉलमार्क विशिष्ट पहचान)" },
    desc: {
      en: "A 6-digit alphanumeric code laser-engraved on gold jewellery. It ensures traceability and verifies the purity of the precious metal.",
      hi: "सोने के आभूषणों पर लेजर द्वारा उकेरा गया 6 अंकों का अल्फ़ान्यूमेरिक कोड। यह ट्रेसबिलिटी सुनिश्चित करता है और कीमती धातु की शुद्धता की पुष्टि करता है।"
    }
  },
  ECOMARK: {
    title: { en: "Eco Mark", hi: "इको मार्क" },
    desc: {
      en: "A voluntary certification mark issued by BIS for products that are environmentally friendly and meet prescribed quality standards.",
      hi: "BIS द्वारा जारी पर्यावरण के अनुकूल और निर्धारित गुणवत्ता मानकों को पूरा करने वाले उत्पादों के लिए एक स्वैच्छिक प्रमाणीकरण चिह्न।"
    }
  },
  FMCS: {
    title: { en: "FMCS (Foreign Manufacturers Certification Scheme)", hi: "FMCS (विदेशी निर्माता प्रमाणीकरण योजना)" },
    desc: {
      en: "A scheme enabling overseas manufacturers to use the standard ISI mark on their products, ensuring they meet Indian standards.",
      hi: "एक योजना जो विदेशी निर्माताओं को अपने उत्पादों पर मानक ISI मार्क का उपयोग करने में सक्षम बनाती है, यह सुनिश्चित करते हुए कि वे भारतीय मानकों को पूरा करते हैं।"
    }
  },
  MSME: {
    title: { en: "MSME", hi: "MSME" },
    desc: {
      en: "Micro, Small & Medium Enterprises. BIS offers massive fee concessions (up to 80%) for recognized MSMEs and Startups to ease compliance burdens.",
      hi: "सूक्ष्म, लघु और मध्यम उद्यम। BIS अनुपालन के बोझ को कम करने के लिए मान्यता प्राप्त MSME और स्टार्टअप्स को भारी शुल्क रियायतें (80% तक) प्रदान करता है।"
    }
  }
};

export function getGlossaryDef(term: GlossaryTerm, language: "en" | "hi" | "mr" | "ta" | "te" = "en") {
  const entry = GLOSSARY[term];
  // Fallback to hindi if regional languages are selected but not supported yet, or english
  const langKey = language === "hi" ? "hi" : "en";
  return {
    title: entry.title[langKey],
    desc: entry.desc[langKey],
  };
}
