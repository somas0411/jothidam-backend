"""
i18n.py — names and labels for reports.

Languages: en, ta, hi, te, kn, ml, mr, bn, plus 'bi' (English + Tamil).
Planet and rasi names exist in all eight languages. Report labels are fully
translated for English, Tamil and Hindi (Marathi reuses the Hindi labels);
the remaining languages fall back to English labels.
"""

LANGS = ['en', 'ta', 'hi', 'te', 'kn', 'ml', 'mr', 'bn', 'bi']

RASIS = {
    'en': ['Mesha', 'Rishabha', 'Mithuna', 'Kataka', 'Simha', 'Kanya', 'Thula', 'Vrischika', 'Dhanu', 'Makara', 'Kumbha', 'Meena'],
    'ta': ['மேஷம்', 'ரிஷபம்', 'மிதுனம்', 'கடகம்', 'சிம்மம்', 'கன்னி', 'துலாம்', 'விருச்சிகம்', 'தனுசு', 'மகரம்', 'கும்பம்', 'மீனம்'],
    'hi': ['मेष', 'वृष', 'मिथुन', 'कर्क', 'सिंह', 'कन्या', 'तुला', 'वृश्चिक', 'धनु', 'मकर', 'कुम्भ', 'मीन'],
    'te': ['మేషము', 'వృషభము', 'మిథునము', 'కర్కాటకము', 'సింహము', 'కన్య', 'తుల', 'వృశ్చికము', 'ధనుస్సు', 'మకరము', 'కుంభము', 'మీనము'],
    'kn': ['ಮೇಷ', 'ವೃಷಭ', 'ಮಿಥುನ', 'ಕರ್ಕಾಟಕ', 'ಸಿಂಹ', 'ಕನ್ಯಾ', 'ತುಲಾ', 'ವೃಶ್ಚಿಕ', 'ಧನು', 'ಮಕರ', 'ಕುಂಭ', 'ಮೀನ'],
    'ml': ['മേടം', 'ഇടവം', 'മിഥുനം', 'കർക്കടകം', 'ചിങ്ങം', 'കന്നി', 'തുലാം', 'വൃശ്ചികം', 'ധനു', 'മകരം', 'കുംഭം', 'മീനം'],
    'mr': ['मेष', 'वृषभ', 'मिथुन', 'कर्क', 'सिंह', 'कन्या', 'तूळ', 'वृश्चिक', 'धनु', 'मकर', 'कुंभ', 'मीन'],
    'bn': ['মেষ', 'বৃষ', 'মিথুন', 'কর্কট', 'সিংহ', 'কন্যা', 'তুলা', 'বৃশ্চিক', 'ধনু', 'মকর', 'কুম্ভ', 'মীন'],
}

RASIS_SHORT = {
    'en': ['Mes', 'Ris', 'Mit', 'Kat', 'Sim', 'Kan', 'Thu', 'Vri', 'Dha', 'Mak', 'Kum', 'Mee'],
    'ta': ['மேஷ', 'ரிஷ', 'மிது', 'கட', 'சிம்', 'கன்', 'துலா', 'விரு', 'தனு', 'மக', 'கும்', 'மீன'],
    'hi': ['मेष', 'वृष', 'मिथु', 'कर्क', 'सिंह', 'कन्या', 'तुला', 'वृश्चि', 'धनु', 'मकर', 'कुंभ', 'मीन'],
    'te': ['మేష', 'వృష', 'మిథు', 'కర్క', 'సింహ', 'కన్య', 'తుల', 'వృశ్చి', 'ధను', 'మకర', 'కుంభ', 'మీన'],
    'kn': ['ಮೇಷ', 'ವೃಷ', 'ಮಿಥು', 'ಕರ್ಕ', 'ಸಿಂಹ', 'ಕನ್ಯಾ', 'ತುಲಾ', 'ವೃಶ್ಚಿ', 'ಧನು', 'ಮಕರ', 'ಕುಂಭ', 'ಮೀನ'],
    'ml': ['മേടം', 'ഇടവം', 'മിഥു', 'കർക്ക', 'ചിങ്ങം', 'കന്നി', 'തുലാം', 'വൃശ്ചി', 'ധനു', 'മകരം', 'കുംഭം', 'മീനം'],
    'mr': ['मेष', 'वृषभ', 'मिथु', 'कर्क', 'सिंह', 'कन्या', 'तूळ', 'वृश्चि', 'धनु', 'मकर', 'कुंभ', 'मीन'],
    'bn': ['মেষ', 'বৃষ', 'মিথু', 'কর্কট', 'সিংহ', 'কন্যা', 'তুলা', 'বৃশ্চি', 'ধনু', 'মকর', 'কুম্ভ', 'মীন'],
}

NAKS = {
    'en': ['Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra', 'Punarvasu', 'Pushya', 'Ashlesha',
           'Magha', 'Purva Phalguni', 'Uttara Phalguni', 'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
           'Moola', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishtha', 'Shatabhisha',
           'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'],
    'ta': ['அஸ்வினி', 'பரணி', 'கிருத்திகை', 'ரோகிணி', 'மிருகசீரிடம்', 'திருவாதிரை', 'புனர்பூசம்', 'பூசம்', 'ஆயில்யம்',
           'மகம்', 'பூரம்', 'உத்திரம்', 'அஸ்தம்', 'சித்திரை', 'சுவாதி', 'விசாகம்', 'அனுஷம்', 'கேட்டை',
           'மூலம்', 'பூராடம்', 'உத்திராடம்', 'திருவோணம்', 'அவிட்டம்', 'சதயம்',
           'பூரட்டாதி', 'உத்திரட்டாதி', 'ரேவதி'],
    'hi': ['अश्विनी', 'भरणी', 'कृत्तिका', 'रोहिणी', 'मृगशिरा', 'आर्द्रा', 'पुनर्वसु', 'पुष्य', 'आश्लेषा',
           'मघा', 'पूर्वा फाल्गुनी', 'उत्तरा फाल्गुनी', 'हस्त', 'चित्रा', 'स्वाति', 'विशाखा', 'अनुराधा', 'ज्येष्ठा',
           'मूल', 'पूर्वाषाढ़ा', 'उत्तराषाढ़ा', 'श्रवण', 'धनिष्ठा', 'शतभिषा',
           'पूर्वा भाद्रपद', 'उत्तरा भाद्रपद', 'रेवती'],
}
NAKS['mr'] = NAKS['hi']

PLANETS = {
    'en': {'Lagna': 'Lagna', 'Sun': 'Sun', 'Moon': 'Moon', 'Mars': 'Mars', 'Mercury': 'Mercury', 'Jupiter': 'Jupiter', 'Venus': 'Venus', 'Saturn': 'Saturn', 'Rahu': 'Rahu', 'Ketu': 'Ketu', 'Mandi': 'Mandi'},
    'ta': {'Lagna': 'லக்னம்', 'Sun': 'சூரியன்', 'Moon': 'சந்திரன்', 'Mars': 'செவ்வாய்', 'Mercury': 'புதன்', 'Jupiter': 'குரு', 'Venus': 'சுக்கிரன்', 'Saturn': 'சனி', 'Rahu': 'ராகு', 'Ketu': 'கேது', 'Mandi': 'மாந்தி'},
    'hi': {'Lagna': 'लग्न', 'Sun': 'सूर्य', 'Moon': 'चंद्र', 'Mars': 'मंगल', 'Mercury': 'बुध', 'Jupiter': 'गुरु', 'Venus': 'शुक्र', 'Saturn': 'शनि', 'Rahu': 'राहु', 'Ketu': 'केतु', 'Mandi': 'मांदि'},
    'te': {'Lagna': 'లగ్నం', 'Sun': 'సూర్యుడు', 'Moon': 'చంద్రుడు', 'Mars': 'కుజుడు', 'Mercury': 'బుధుడు', 'Jupiter': 'గురువు', 'Venus': 'శుక్రుడు', 'Saturn': 'శని', 'Rahu': 'రాహువు', 'Ketu': 'కేతువు', 'Mandi': 'మాంది'},
    'kn': {'Lagna': 'ಲಗ್ನ', 'Sun': 'ಸೂರ್ಯ', 'Moon': 'ಚಂದ್ರ', 'Mars': 'ಕುಜ', 'Mercury': 'ಬುಧ', 'Jupiter': 'ಗುರು', 'Venus': 'ಶುಕ್ರ', 'Saturn': 'ಶನಿ', 'Rahu': 'ರಾಹು', 'Ketu': 'ಕೇತು', 'Mandi': 'ಮಾಂದಿ'},
    'ml': {'Lagna': 'ലഗ്നം', 'Sun': 'സൂര്യൻ', 'Moon': 'ചന്ദ്രൻ', 'Mars': 'ചൊവ്വ', 'Mercury': 'ബുധൻ', 'Jupiter': 'വ്യാഴം', 'Venus': 'ശുക്രൻ', 'Saturn': 'ശനി', 'Rahu': 'രാഹു', 'Ketu': 'കേതു', 'Mandi': 'മാന്ദി'},
    'mr': {'Lagna': 'लग्न', 'Sun': 'रवि', 'Moon': 'चंद्र', 'Mars': 'मंगळ', 'Mercury': 'बुध', 'Jupiter': 'गुरु', 'Venus': 'शुक्र', 'Saturn': 'शनि', 'Rahu': 'राहू', 'Ketu': 'केतू', 'Mandi': 'मांदी'},
    'bn': {'Lagna': 'লগ্ন', 'Sun': 'সূর্য', 'Moon': 'চন্দ্র', 'Mars': 'মঙ্গল', 'Mercury': 'বুধ', 'Jupiter': 'বৃহস্পতি', 'Venus': 'শুক্র', 'Saturn': 'শনি', 'Rahu': 'রাহু', 'Ketu': 'কেতু', 'Mandi': 'মান্দি'},
}

ABBR = {
    'en': {'Lagna': 'La', 'Sun': 'Su', 'Moon': 'Mo', 'Mars': 'Ma', 'Mercury': 'Me', 'Jupiter': 'Ju', 'Venus': 'Ve', 'Saturn': 'Sa', 'Rahu': 'Ra', 'Ketu': 'Ke', 'ALP': 'AL', 'Mandi': 'Md'},
    'ta': {'Lagna': 'லக்', 'Sun': 'சூ', 'Moon': 'சந்', 'Mars': 'செ', 'Mercury': 'பு', 'Jupiter': 'குரு', 'Venus': 'சுக்', 'Saturn': 'சனி', 'Rahu': 'ரா', 'Ketu': 'கே', 'ALP': 'அல', 'Mandi': 'மா'},
    'hi': {'Lagna': 'ल', 'Sun': 'सू', 'Moon': 'चं', 'Mars': 'मं', 'Mercury': 'बु', 'Jupiter': 'गु', 'Venus': 'शु', 'Saturn': 'श', 'Rahu': 'रा', 'Ketu': 'के', 'ALP': 'अल', 'Mandi': 'मा'},
    'te': {'Lagna': 'ల', 'Sun': 'సూ', 'Moon': 'చం', 'Mars': 'కు', 'Mercury': 'బు', 'Jupiter': 'గు', 'Venus': 'శు', 'Saturn': 'శ', 'Rahu': 'రా', 'Ketu': 'కే', 'ALP': 'AL', 'Mandi': 'మా'},
    'kn': {'Lagna': 'ಲ', 'Sun': 'ಸೂ', 'Moon': 'ಚಂ', 'Mars': 'ಕು', 'Mercury': 'ಬು', 'Jupiter': 'ಗು', 'Venus': 'ಶು', 'Saturn': 'ಶ', 'Rahu': 'ರಾ', 'Ketu': 'ಕೇ', 'ALP': 'AL', 'Mandi': 'ಮಾ'},
    'ml': {'Lagna': 'ല', 'Sun': 'സൂ', 'Moon': 'ച', 'Mars': 'ചൊ', 'Mercury': 'ബു', 'Jupiter': 'വ്യാ', 'Venus': 'ശു', 'Saturn': 'ശനി', 'Rahu': 'രാ', 'Ketu': 'കേ', 'ALP': 'AL', 'Mandi': 'മാ'},
    'mr': {'Lagna': 'ल', 'Sun': 'र', 'Moon': 'चं', 'Mars': 'मं', 'Mercury': 'बु', 'Jupiter': 'गु', 'Venus': 'शु', 'Saturn': 'श', 'Rahu': 'रा', 'Ketu': 'के', 'ALP': 'अल', 'Mandi': 'मा'},
    'bn': {'Lagna': 'ল', 'Sun': 'সূ', 'Moon': 'চ', 'Mars': 'ম', 'Mercury': 'বু', 'Jupiter': 'বৃ', 'Venus': 'শু', 'Saturn': 'শ', 'Rahu': 'রা', 'Ketu': 'কে', 'ALP': 'AL', 'Mandi': 'মা'},
}
RETRO_MARK = {'en': '(R)', 'ta': '(வ)', 'hi': '(व)', 'mr': '(व)'}

WEEKDAYS = {
    'en': {'Monday': 'Monday', 'Tuesday': 'Tuesday', 'Wednesday': 'Wednesday', 'Thursday': 'Thursday', 'Friday': 'Friday', 'Saturday': 'Saturday', 'Sunday': 'Sunday'},
    'ta': {'Monday': 'திங்கள்', 'Tuesday': 'செவ்வாய்', 'Wednesday': 'புதன்', 'Thursday': 'வியாழன்', 'Friday': 'வெள்ளி', 'Saturday': 'சனி', 'Sunday': 'ஞாயிறு'},
    'hi': {'Monday': 'सोमवार', 'Tuesday': 'मंगलवार', 'Wednesday': 'बुधवार', 'Thursday': 'गुरुवार', 'Friday': 'शुक्रवार', 'Saturday': 'शनिवार', 'Sunday': 'रविवार'},
}

TITHIS = {
    'ta': {'Prathama': 'பிரதமை', 'Dwitiya': 'துவிதியை', 'Tritiya': 'திருதியை', 'Chaturthi': 'சதுர்த்தி', 'Panchami': 'பஞ்சமி',
           'Shashthi': 'சஷ்டி', 'Saptami': 'சப்தமி', 'Ashtami': 'அஷ்டமி', 'Navami': 'நவமி', 'Dashami': 'தசமி',
           'Ekadashi': 'ஏகாதசி', 'Dwadashi': 'துவாதசி', 'Trayodashi': 'திரயோதசி', 'Chaturdashi': 'சதுர்த்தசி',
           'Purnima': 'பௌர்ணமி', 'Amavasya': 'அமாவாசை'},
    'hi': {'Prathama': 'प्रतिपदा', 'Dwitiya': 'द्वितीया', 'Tritiya': 'तृतीया', 'Chaturthi': 'चतुर्थी', 'Panchami': 'पंचमी',
           'Shashthi': 'षष्ठी', 'Saptami': 'सप्तमी', 'Ashtami': 'अष्टमी', 'Navami': 'नवमी', 'Dashami': 'दशमी',
           'Ekadashi': 'एकादशी', 'Dwadashi': 'द्वादशी', 'Trayodashi': 'त्रयोदशी', 'Chaturdashi': 'चतुर्दशी',
           'Purnima': 'पूर्णिमा', 'Amavasya': 'अमावस्या'},
}
TITHIS['mr'] = TITHIS['hi']

WORDS = {   # short value words
    'ta': {'Shukla': 'வளர்பிறை', 'Krishna': 'தேய்பிறை', 'Exalted': 'உச்சம்', 'Debilitated': 'நீசம்', 'Own sign': 'ஆட்சி',
           'Yes': 'ஆம்', 'Mean': 'சராசரி', 'True': 'உண்மை', 'Male': 'ஆண்', 'Female': 'பெண்',
           'Placidus': 'பிளாசிடஸ்', 'Porphyry': 'போர்ஃபிரி'},
    'hi': {'Shukla': 'शुक्ल', 'Krishna': 'कृष्ण', 'Exalted': 'उच्च', 'Debilitated': 'नीच', 'Own sign': 'स्वराशि',
           'Yes': 'हाँ', 'Mean': 'मध्यम', 'True': 'स्पष्ट', 'Male': 'पुरुष', 'Female': 'स्त्री'},
}

# Divisional charts: name and one-line purpose, by chart key.
VARGA_NAMES = {
    'en': {'D1': 'Rasi', 'D2': 'Hora', 'D3': 'Drekkana', 'D4': 'Chaturthamsa', 'D7': 'Saptamsa', 'D9': 'Navamsa',
           'D10': 'Dasamsa', 'D12': 'Dwadasamsa', 'D16': 'Shodasamsa', 'D20': 'Vimsamsa', 'D24': 'Chaturvimsamsa',
           'D27': 'Bhamsa', 'D30': 'Trimsamsa', 'D40': 'Khavedamsa', 'D45': 'Akshavedamsa', 'D60': 'Shashtiamsa'},
    'ta': {'D1': 'ராசி', 'D2': 'ஹோரை', 'D3': 'திரேக்காணம்', 'D4': 'சதுர்த்தாம்சம்', 'D7': 'சப்தாம்சம்', 'D9': 'நவாம்சம்',
           'D10': 'தசாம்சம்', 'D12': 'துவாதசாம்சம்', 'D16': 'ஷோடசாம்சம்', 'D20': 'விம்சாம்சம்', 'D24': 'சதுர்விம்சாம்சம்',
           'D27': 'பாம்சம்', 'D30': 'திரிம்சாம்சம்', 'D40': 'கவேதாம்சம்', 'D45': 'அட்சவேதாம்சம்', 'D60': 'சஷ்டியாம்சம்'},
    'hi': {'D1': 'राशि', 'D2': 'होरा', 'D3': 'द्रेष्काण', 'D4': 'चतुर्थांश', 'D7': 'सप्तमांश', 'D9': 'नवांश',
           'D10': 'दशमांश', 'D12': 'द्वादशांश', 'D16': 'षोडशांश', 'D20': 'विंशांश', 'D24': 'चतुर्विंशांश',
           'D27': 'भांश', 'D30': 'त्रिंशांश', 'D40': 'खवेदांश', 'D45': 'अक्षवेदांश', 'D60': 'षष्ट्यंश'},
}
VARGA_NAMES['mr'] = VARGA_NAMES['hi']

VARGA_PURPOSE = {
    'en': {'D1': 'Body, health and life as a whole', 'D2': 'Wealth and resources',
           'D3': 'Siblings, courage and effort', 'D4': 'Home, property and fortune',
           'D7': 'Children and progeny', 'D9': 'Marriage, spouse and the inner strength of planets',
           'D10': 'Career, status and achievements', 'D12': 'Parents and ancestry',
           'D16': 'Vehicles, comforts and happiness', 'D20': 'Worship and spiritual progress',
           'D24': 'Education and learning', 'D27': 'Strengths and weaknesses',
           'D30': 'Misfortunes and difficulties',
           'D40': 'Auspicious and inauspicious effects (maternal line)',
           'D45': 'Character and general indications (paternal line)',
           'D60': 'All matters; the fine detail of the chart'},
    'ta': {'D1': 'உடல், ஆரோக்கியம், வாழ்க்கை முழுவதும்', 'D2': 'செல்வம், பொருளாதாரம்',
           'D3': 'சகோதரர்கள், தைரியம், முயற்சி', 'D4': 'வீடு, சொத்து, பாக்கியம்',
           'D7': 'குழந்தைகள், சந்ததி', 'D9': 'திருமணம், வாழ்க்கைத் துணை, கிரகங்களின் உள் பலம்',
           'D10': 'தொழில், அந்தஸ்து, சாதனைகள்', 'D12': 'பெற்றோர், முன்னோர்',
           'D16': 'வாகனம், சுகம், மகிழ்ச்சி', 'D20': 'வழிபாடு, ஆன்மிக முன்னேற்றம்',
           'D24': 'கல்வி, அறிவு', 'D27': 'பலம், பலவீனம்',
           'D30': 'துன்பங்கள், இடையூறுகள்',
           'D40': 'சுப, அசுப பலன்கள் (தாய் வழி)',
           'D45': 'குணம், பொதுப் பலன்கள் (தந்தை வழி)',
           'D60': 'அனைத்து விஷயங்கள்; ஜாதகத்தின் நுணுக்கமான விவரம்'},
    'hi': {'D1': 'शरीर, स्वास्थ्य और संपूर्ण जीवन', 'D2': 'धन और संसाधन',
           'D3': 'भाई-बहन, साहस और प्रयास', 'D4': 'घर, संपत्ति और भाग्य',
           'D7': 'संतान', 'D9': 'विवाह, जीवनसाथी और ग्रहों का आंतरिक बल',
           'D10': 'करियर, प्रतिष्ठा और उपलब्धियां', 'D12': 'माता-पिता और वंश',
           'D16': 'वाहन, सुख और प्रसन्नता', 'D20': 'उपासना और आध्यात्मिक प्रगति',
           'D24': 'शिक्षा और ज्ञान', 'D27': 'बल और दुर्बलता',
           'D30': 'कष्ट और कठिनाइयां',
           'D40': 'शुभ और अशुभ फल (मातृ पक्ष)',
           'D45': 'चरित्र और सामान्य संकेत (पितृ पक्ष)',
           'D60': 'सभी विषय; कुंडली का सूक्ष्म विवरण'},
}

LABELS = {
    'en': {
        'brand': 'HoroscopeGen', 'report_title': 'Horoscope Report',
        'subtitle': 'Vedic · KP · ALP',
        'summary': 'Summary', 'vedic': 'Vedic', 'kp': 'KP', 'alp': 'ALP', 'dasa_sheet': 'Dasa', 'notes': 'Notes',
        'birth_details': 'Birth Details', 'name': 'Name', 'gender': 'Gender', 'dob': 'Date of Birth',
        'tob': 'Time of Birth', 'pob': 'Place of Birth', 'lat': 'Latitude', 'lon': 'Longitude',
        'tz': 'Time Zone', 'ayanamsha': 'Ayanamsha', 'kp_ayanamsha': 'KP Ayanamsha', 'nodes': 'Rahu / Ketu',
        'core': 'Key Details', 'lagna': 'Lagna', 'janma_rasi': 'Rasi (Moon Sign)', 'nakshatra': 'Nakshatra',
        'pada': 'Pada', 'nak_lord': 'Nakshatra Lord', 'tithi': 'Tithi', 'vara': 'Weekday', 'yoga': 'Yoga',
        'karana': 'Karana', 'sunrise': 'Sunrise', 'sunset': 'Sunset', 'panchangam': 'Panchangam at Birth',
        'mandi_rise': 'Mandi Rise Time',
        'divisional': 'Divisional Charts', 'varga_table': 'Sign of Each Point in the 16 Charts',
        'vargottama': 'Vargottama', 'vargottama_note': 'Vargottama: same sign in the Rasi (D1) and Navamsa (D9) charts.',
        'varga_time_note': 'The higher charts depend on an accurate birth time: the D60 lagna changes about every two minutes.',
        'dasa_balance': 'Dasa Balance at Birth', 'current_period': 'Current Period',
        'dasa': 'Dasa', 'bhukti': 'Bhukti', 'antaram': 'Antaram', 'ends': 'ends', 'until': 'until',
        'planet': 'Planet', 'rasi': 'Rasi', 'degree': 'Degree', 'rasi_lord': 'Rasi Lord', 'star_lord': 'Star Lord',
        'sub_lord': 'Sub Lord', 'subsub_lord': 'Sub-Sub Lord', 'house': 'House', 'bhava': 'Bhava',
        'navamsa': 'Navamsa', 'retro': 'Retro', 'combust': 'Combust', 'dignity': 'Dignity',
        'planet_positions': 'Planet Positions', 'bhava_table': 'Bhava (Sripati)', 'bhava_start': 'Bhava Start',
        'bhava_mid': 'Bhava Middle',
        'rasi_chart': 'Rasi Chart (D1)', 'navamsa_chart': 'Navamsa Chart (D9)', 'bhava_chart': 'Bhava Chart',
        'kp_chart': 'KP Cusp Chart', 'alp_chart': 'ALP Chart',
        'cusp': 'Cusp', 'cusps': 'House Cusps (Placidus)', 'kp_planets': 'KP Planet Positions',
        'planet_sig': 'Planet Significators', 'house_sig': 'House Significators',
        'level1': 'Level 1: star lord occupies', 'level2': 'Level 2: occupies',
        'level3': 'Level 3: star lord owns', 'level4': 'Level 4: owns',
        'sig_a': 'A: in star of occupants', 'sig_b': 'B: occupants', 'sig_c': 'C: in star of owner', 'sig_d': 'D: owner',
        'ruling_planets': 'Ruling Planets at Birth', 'day_lord': 'Day Lord',
        'moon_sign_lord': 'Moon Sign Lord', 'moon_star_lord': 'Moon Star Lord', 'moon_sub_lord': 'Moon Sub Lord',
        'lagna_sign_lord': 'Lagna Sign Lord', 'lagna_star_lord': 'Lagna Star Lord', 'lagna_sub_lord': 'Lagna Sub Lord',
        'node_agents': 'Rahu / Ketu as Agents', 'node': 'Node', 'conjoined': 'Planets in Same Sign',
        'kp_dasa': 'Vimshottari Dasa (KP Ayanamsha)', 'vim_dasa': 'Vimshottari Dasa',
        'house_system': 'House System',
        'alp_title': 'Akshaya Lagna Paddhati', 'alp_birth_lagna': 'Birth Lagna', 'alp_lagna_now': 'ALP Lagna Today',
        'alp_rule': 'Rule', 'alp_sign_periods': 'ALP Lagna by Rasi (10 years each)',
        'alp_pada_periods': 'ALP Lagna by Nakshatra Pada', 'age': 'Age', 'age_from': 'Age From', 'age_to': 'Age To',
        'from': 'From', 'to': 'To', 'start': 'Start', 'end': 'End', 'status': 'Status',
        'completed': 'Completed', 'current': 'Current', 'upcoming': 'Upcoming', 'years': 'years',
        'y': 'y', 'm': 'm', 'd': 'd', 'as_of': 'As of', 'generated': 'Generated',
        'abbreviations': 'Abbreviations', 'how_calculated': 'How This Report Was Calculated',
        'disclaimer': 'This report presents astrological calculations for guidance only.',
        'page': 'Page',
    },
    'ta': {
        'brand': 'HoroscopeGen', 'report_title': 'ஜாதக அறிக்கை',
        'subtitle': 'வேத ஜோதிடம் · கே.பி. · அட்சய லக்னம்',
        'summary': 'சுருக்கம்', 'vedic': 'வேத ஜோதிடம்', 'kp': 'கே.பி.', 'alp': 'அட்சய லக்னம்', 'dasa_sheet': 'தசை', 'notes': 'குறிப்புகள்',
        'birth_details': 'பிறப்பு விவரங்கள்', 'name': 'பெயர்', 'gender': 'பாலினம்', 'dob': 'பிறந்த தேதி',
        'tob': 'பிறந்த நேரம்', 'pob': 'பிறந்த இடம்', 'lat': 'அட்சரேகை', 'lon': 'தீர்க்கரேகை',
        'tz': 'நேர மண்டலம்', 'ayanamsha': 'அயனாம்சம்', 'kp_ayanamsha': 'கே.பி. அயனாம்சம்', 'nodes': 'ராகு / கேது',
        'core': 'முக்கிய விவரங்கள்', 'lagna': 'லக்னம்', 'janma_rasi': 'ராசி', 'nakshatra': 'நட்சத்திரம்',
        'pada': 'பாதம்', 'nak_lord': 'நட்சத்திர அதிபதி', 'tithi': 'திதி', 'vara': 'கிழமை', 'yoga': 'யோகம்',
        'karana': 'கரணம்', 'sunrise': 'சூரிய உதயம்', 'sunset': 'சூரிய அஸ்தமனம்', 'panchangam': 'பிறப்பு பஞ்சாங்கம்',
        'mandi_rise': 'மாந்தி உதய நேரம்',
        'divisional': 'வர்க்க சக்கரங்கள்', 'varga_table': '16 வர்க்க சக்கரங்களில் ஒவ்வொரு கிரகத்தின் ராசி',
        'vargottama': 'வர்கோத்தமம்', 'vargottama_note': 'வர்கோத்தமம்: ராசி (D1), நவாம்சம் (D9) இரண்டிலும் ஒரே ராசி.',
        'varga_time_note': 'உயர் வர்க்க சக்கரங்களுக்கு துல்லியமான பிறந்த நேரம் அவசியம்: D60 லக்னம் சுமார் இரண்டு நிமிடங்களுக்கு ஒருமுறை மாறும்.',
        'dasa_balance': 'பிறப்பு தசை இருப்பு', 'current_period': 'நடப்பு காலம்',
        'dasa': 'தசை', 'bhukti': 'புக்தி', 'antaram': 'அந்தரம்', 'ends': 'முடிவு', 'until': 'வரை',
        'planet': 'கிரகம்', 'rasi': 'ராசி', 'degree': 'பாகை', 'rasi_lord': 'ராசி அதிபதி', 'star_lord': 'நட்சத்திர அதிபதி',
        'sub_lord': 'உப அதிபதி', 'subsub_lord': 'உப-உப அதிபதி', 'house': 'வீடு', 'bhava': 'பாவம்',
        'navamsa': 'நவாம்சம்', 'retro': 'வக்ரம்', 'combust': 'அஸ்தங்கம்', 'dignity': 'பலம்',
        'planet_positions': 'கிரக நிலைகள்', 'bhava_table': 'பாவங்கள் (ஸ்ரீபதி)', 'bhava_start': 'பாவ ஆரம்பம்',
        'bhava_mid': 'பாவ மத்தியம்',
        'rasi_chart': 'ராசி சக்கரம் (D1)', 'navamsa_chart': 'நவாம்ச சக்கரம் (D9)', 'bhava_chart': 'பாவ சக்கரம்',
        'kp_chart': 'கே.பி. பாவ சக்கரம்', 'alp_chart': 'அட்சய லக்ன சக்கரம்',
        'cusp': 'பாவ முனை', 'cusps': 'பாவ முனைகள் (பிளாசிடஸ்)', 'kp_planets': 'கே.பி. கிரக நிலைகள்',
        'planet_sig': 'கிரக காரகத்துவம்', 'house_sig': 'பாவ காரகர்கள்',
        'level1': 'நிலை 1: நட்சத்திர அதிபதி நின்ற பாவம்', 'level2': 'நிலை 2: நின்ற பாவம்',
        'level3': 'நிலை 3: நட்சத்திர அதிபதியின் பாவங்கள்', 'level4': 'நிலை 4: சொந்த பாவங்கள்',
        'sig_a': 'A: நின்றவர் நட்சத்திரத்தில்', 'sig_b': 'B: நின்றவர்கள்', 'sig_c': 'C: அதிபதி நட்சத்திரத்தில்', 'sig_d': 'D: அதிபதி',
        'ruling_planets': 'பிறப்பு நேர ஆளும் கிரகங்கள்', 'day_lord': 'கிழமை அதிபதி',
        'moon_sign_lord': 'சந்திர ராசி அதிபதி', 'moon_star_lord': 'சந்திர நட்சத்திர அதிபதி', 'moon_sub_lord': 'சந்திர உப அதிபதி',
        'lagna_sign_lord': 'லக்ன ராசி அதிபதி', 'lagna_star_lord': 'லக்ன நட்சத்திர அதிபதி', 'lagna_sub_lord': 'லக்ன உப அதிபதி',
        'node_agents': 'ராகு / கேது பிரதிநிதித்துவம்', 'node': 'சாயா கிரகம்', 'conjoined': 'அதே ராசியில் உள்ள கிரகங்கள்',
        'kp_dasa': 'விம்சோத்தரி தசை (கே.பி. அயனாம்சம்)', 'vim_dasa': 'விம்சோத்தரி தசை',
        'house_system': 'பாவ முறை',
        'alp_title': 'அட்சய லக்ன பத்ததி', 'alp_birth_lagna': 'பிறப்பு லக்னம்', 'alp_lagna_now': 'இன்றைய அட்சய லக்னம்',
        'alp_rule': 'விதி', 'alp_sign_periods': 'ராசி வாரியாக அட்சய லக்னம் (தலா 10 ஆண்டுகள்)',
        'alp_pada_periods': 'நட்சத்திர பாதம் வாரியாக அட்சய லக்னம்', 'age': 'வயது', 'age_from': 'வயது முதல்', 'age_to': 'வயது வரை',
        'from': 'முதல்', 'to': 'வரை', 'start': 'தொடக்கம்', 'end': 'முடிவு', 'status': 'நிலை',
        'completed': 'முடிந்தது', 'current': 'நடப்பு', 'upcoming': 'வரவிருப்பது', 'years': 'ஆண்டுகள்',
        'y': 'வ', 'm': 'மா', 'd': 'நா', 'as_of': 'கணித்த நாள்', 'generated': 'உருவாக்கிய நாள்',
        'abbreviations': 'சுருக்கக் குறியீடுகள்', 'how_calculated': 'இந்த அறிக்கை கணிக்கப்பட்ட முறை',
        'disclaimer': 'இந்த அறிக்கை ஜோதிடக் கணிதங்களை வழிகாட்டுதலுக்காக மட்டுமே வழங்குகிறது.',
        'page': 'பக்கம்',
    },
    'hi': {
        'brand': 'HoroscopeGen', 'report_title': 'कुंडली रिपोर्ट',
        'subtitle': 'वैदिक · केपी · एएलपी',
        'summary': 'सारांश', 'vedic': 'वैदिक', 'kp': 'केपी', 'alp': 'एएलपी', 'dasa_sheet': 'दशा', 'notes': 'टिप्पणियां',
        'birth_details': 'जन्म विवरण', 'name': 'नाम', 'gender': 'लिंग', 'dob': 'जन्म तिथि',
        'tob': 'जन्म समय', 'pob': 'जन्म स्थान', 'lat': 'अक्षांश', 'lon': 'देशांतर',
        'tz': 'समय क्षेत्र', 'ayanamsha': 'अयनांश', 'kp_ayanamsha': 'केपी अयनांश', 'nodes': 'राहु / केतु',
        'core': 'मुख्य विवरण', 'lagna': 'लग्न', 'janma_rasi': 'राशि (चंद्र राशि)', 'nakshatra': 'नक्षत्र',
        'pada': 'चरण', 'nak_lord': 'नक्षत्र स्वामी', 'tithi': 'तिथि', 'vara': 'वार', 'yoga': 'योग',
        'karana': 'करण', 'sunrise': 'सूर्योदय', 'sunset': 'सूर्यास्त', 'panchangam': 'जन्म पंचांग',
        'mandi_rise': 'मांदि उदय समय',
        'divisional': 'वर्ग कुंडलियां', 'varga_table': '16 वर्ग कुंडलियों में प्रत्येक ग्रह की राशि',
        'vargottama': 'वर्गोत्तम', 'vargottama_note': 'वर्गोत्तम: राशि (D1) और नवांश (D9) दोनों में एक ही राशि।',
        'varga_time_note': 'उच्च वर्ग कुंडलियां सटीक जन्म समय पर निर्भर हैं: D60 लग्न लगभग हर दो मिनट में बदलता है।',
        'dasa_balance': 'जन्म के समय दशा शेष', 'current_period': 'वर्तमान काल',
        'dasa': 'दशा', 'bhukti': 'अंतर्दशा', 'antaram': 'प्रत्यंतर', 'ends': 'समाप्ति', 'until': 'तक',
        'planet': 'ग्रह', 'rasi': 'राशि', 'degree': 'अंश', 'rasi_lord': 'राशि स्वामी', 'star_lord': 'नक्षत्र स्वामी',
        'sub_lord': 'उप स्वामी', 'subsub_lord': 'उप-उप स्वामी', 'house': 'भाव', 'bhava': 'चलित भाव',
        'navamsa': 'नवांश', 'retro': 'वक्री', 'combust': 'अस्त', 'dignity': 'स्थिति',
        'planet_positions': 'ग्रह स्थिति', 'bhava_table': 'भाव (श्रीपति)', 'bhava_start': 'भाव आरंभ',
        'bhava_mid': 'भाव मध्य',
        'rasi_chart': 'लग्न कुंडली (D1)', 'navamsa_chart': 'नवांश कुंडली (D9)', 'bhava_chart': 'भाव चलित कुंडली',
        'kp_chart': 'केपी भाव कुंडली', 'alp_chart': 'एएलपी कुंडली',
        'cusp': 'भाव आरंभ', 'cusps': 'भाव आरंभ बिंदु (प्लेसिडस)', 'kp_planets': 'केपी ग्रह स्थिति',
        'planet_sig': 'ग्रह कारकत्व', 'house_sig': 'भाव कारक',
        'level1': 'स्तर 1: नक्षत्र स्वामी जिस भाव में', 'level2': 'स्तर 2: स्वयं जिस भाव में',
        'level3': 'स्तर 3: नक्षत्र स्वामी के भाव', 'level4': 'स्तर 4: स्वयं के भाव',
        'sig_a': 'A: भावस्थ ग्रह के नक्षत्र में', 'sig_b': 'B: भावस्थ ग्रह', 'sig_c': 'C: भावेश के नक्षत्र में', 'sig_d': 'D: भावेश',
        'ruling_planets': 'जन्म के समय शासक ग्रह', 'day_lord': 'वार स्वामी',
        'moon_sign_lord': 'चंद्र राशि स्वामी', 'moon_star_lord': 'चंद्र नक्षत्र स्वामी', 'moon_sub_lord': 'चंद्र उप स्वामी',
        'lagna_sign_lord': 'लग्न राशि स्वामी', 'lagna_star_lord': 'लग्न नक्षत्र स्वामी', 'lagna_sub_lord': 'लग्न उप स्वामी',
        'node_agents': 'राहु / केतु प्रतिनिधित्व', 'node': 'छाया ग्रह', 'conjoined': 'उसी राशि के ग्रह',
        'kp_dasa': 'विंशोत्तरी दशा (केपी अयनांश)', 'vim_dasa': 'विंशोत्तरी दशा',
        'house_system': 'भाव पद्धति',
        'alp_title': 'अक्षय लग्न पद्धति', 'alp_birth_lagna': 'जन्म लग्न', 'alp_lagna_now': 'आज का अक्षय लग्न',
        'alp_rule': 'नियम', 'alp_sign_periods': 'राशि अनुसार अक्षय लग्न (प्रत्येक 10 वर्ष)',
        'alp_pada_periods': 'नक्षत्र चरण अनुसार अक्षय लग्न', 'age': 'आयु', 'age_from': 'आयु से', 'age_to': 'आयु तक',
        'from': 'से', 'to': 'तक', 'start': 'प्रारंभ', 'end': 'समाप्ति', 'status': 'स्थिति',
        'completed': 'पूर्ण', 'current': 'वर्तमान', 'upcoming': 'आगामी', 'years': 'वर्ष',
        'y': 'व', 'm': 'मा', 'd': 'दि', 'as_of': 'गणना तिथि', 'generated': 'निर्माण तिथि',
        'abbreviations': 'संक्षिप्त रूप', 'how_calculated': 'इस रिपोर्ट की गणना विधि',
        'disclaimer': 'यह रिपोर्ट ज्योतिषीय गणनाएं केवल मार्गदर्शन के लिए प्रस्तुत करती है।',
        'page': 'पृष्ठ',
    },
}

# ── te, kn, ml, bn and Marathi's own tables ──────────────────────────────────
NAKS['te'] = ['అశ్విని', 'భరణి', 'కృత్తిక', 'రోహిణి', 'మృగశిర', 'ఆర్ద్ర', 'పునర్వసు', 'పుష్యమి', 'ఆశ్లేష',
              'మఖ', 'పుబ్బ', 'ఉత్తర', 'హస్త', 'చిత్త', 'స్వాతి', 'విశాఖ', 'అనూరాధ', 'జ్యేష్ఠ',
              'మూల', 'పూర్వాషాఢ', 'ఉత్తరాషాఢ', 'శ్రవణం', 'ధనిష్ఠ', 'శతభిషం',
              'పూర్వాభాద్ర', 'ఉత్తరాభాద్ర', 'రేవతి']
NAKS['kn'] = ['ಅಶ್ವಿನಿ', 'ಭರಣಿ', 'ಕೃತ್ತಿಕಾ', 'ರೋಹಿಣಿ', 'ಮೃಗಶಿರ', 'ಆರ್ದ್ರಾ', 'ಪುನರ್ವಸು', 'ಪುಷ್ಯ', 'ಆಶ್ಲೇಷಾ',
              'ಮಘಾ', 'ಪೂರ್ವಾ ಫಲ್ಗುಣಿ', 'ಉತ್ತರಾ ಫಲ್ಗುಣಿ', 'ಹಸ್ತ', 'ಚಿತ್ರಾ', 'ಸ್ವಾತಿ', 'ವಿಶಾಖಾ', 'ಅನುರಾಧಾ', 'ಜ್ಯೇಷ್ಠಾ',
              'ಮೂಲಾ', 'ಪೂರ್ವಾಷಾಢಾ', 'ಉತ್ತರಾಷಾಢಾ', 'ಶ್ರವಣ', 'ಧನಿಷ್ಠಾ', 'ಶತಭಿಷಾ',
              'ಪೂರ್ವಾಭಾದ್ರಪದ', 'ಉತ್ತರಾಭಾದ್ರಪದ', 'ರೇವತಿ']
NAKS['ml'] = ['അശ്വതി', 'ഭരണി', 'കാർത്തിക', 'രോഹിണി', 'മകയിരം', 'തിരുവാതിര', 'പുണർതം', 'പൂയം', 'ആയില്യം',
              'മകം', 'പൂരം', 'ഉത്രം', 'അത്തം', 'ചിത്തിര', 'ചോതി', 'വിശാഖം', 'അനിഴം', 'തൃക്കേട്ട',
              'മൂലം', 'പൂരാടം', 'ഉത്രാടം', 'തിരുവോണം', 'അവിട്ടം', 'ചതയം',
              'പൂരുരുട്ടാതി', 'ഉത്രട്ടാതി', 'രേവതി']
NAKS['bn'] = ['অশ্বিনী', 'ভরণী', 'কৃত্তিকা', 'রোহিণী', 'মৃগশিরা', 'আর্দ্রা', 'পুনর্বসু', 'পুষ্যা', 'অশ্লেষা',
              'মঘা', 'পূর্বফাল্গুনী', 'উত্তরফাল্গুনী', 'হস্তা', 'চিত্রা', 'স্বাতী', 'বিশাখা', 'অনুরাধা', 'জ্যেষ্ঠা',
              'মূলা', 'পূর্বাষাঢ়া', 'উত্তরাষাঢ়া', 'শ্রবণা', 'ধনিষ্ঠা', 'শতভিষা',
              'পূর্বভাদ্রপদ', 'উত্তরভাদ্রপদ', 'রেবতী']

RETRO_MARK.update({'te': '(వ)', 'kn': '(ವ)', 'ml': '(വ)', 'bn': '(ব)'})

WEEKDAYS['te'] = {'Monday': 'సోమవారం', 'Tuesday': 'మంగళవారం', 'Wednesday': 'బుధవారం', 'Thursday': 'గురువారం',
                  'Friday': 'శుక్రవారం', 'Saturday': 'శనివారం', 'Sunday': 'ఆదివారం'}
WEEKDAYS['kn'] = {'Monday': 'ಸೋಮವಾರ', 'Tuesday': 'ಮಂಗಳವಾರ', 'Wednesday': 'ಬುಧವಾರ', 'Thursday': 'ಗುರುವಾರ',
                  'Friday': 'ಶುಕ್ರವಾರ', 'Saturday': 'ಶನಿವಾರ', 'Sunday': 'ಭಾನುವಾರ'}
WEEKDAYS['ml'] = {'Monday': 'തിങ്കൾ', 'Tuesday': 'ചൊവ്വ', 'Wednesday': 'ബുധൻ', 'Thursday': 'വ്യാഴം',
                  'Friday': 'വെള്ളി', 'Saturday': 'ശനി', 'Sunday': 'ഞായർ'}
WEEKDAYS['bn'] = {'Monday': 'সোমবার', 'Tuesday': 'মঙ্গলবার', 'Wednesday': 'বুধবার', 'Thursday': 'বৃহস্পতিবার',
                  'Friday': 'শুক্রবার', 'Saturday': 'শনিবার', 'Sunday': 'রবিবার'}
WEEKDAYS['mr'] = {'Monday': 'सोमवार', 'Tuesday': 'मंगळवार', 'Wednesday': 'बुधवार', 'Thursday': 'गुरुवार',
                  'Friday': 'शुक्रवार', 'Saturday': 'शनिवार', 'Sunday': 'रविवार'}

TITHIS['te'] = {'Prathama': 'పాడ్యమి', 'Dwitiya': 'విదియ', 'Tritiya': 'తదియ', 'Chaturthi': 'చవితి', 'Panchami': 'పంచమి',
                'Shashthi': 'షష్ఠి', 'Saptami': 'సప్తమి', 'Ashtami': 'అష్టమి', 'Navami': 'నవమి', 'Dashami': 'దశమి',
                'Ekadashi': 'ఏకాదశి', 'Dwadashi': 'ద్వాదశి', 'Trayodashi': 'త్రయోదశి', 'Chaturdashi': 'చతుర్దశి',
                'Purnima': 'పౌర్ణమి', 'Amavasya': 'అమావాస్య'}
TITHIS['kn'] = {'Prathama': 'ಪ್ರತಿಪದ', 'Dwitiya': 'ದ್ವಿತೀಯ', 'Tritiya': 'ತೃತೀಯ', 'Chaturthi': 'ಚತುರ್ಥಿ', 'Panchami': 'ಪಂಚಮಿ',
                'Shashthi': 'ಷಷ್ಠಿ', 'Saptami': 'ಸಪ್ತಮಿ', 'Ashtami': 'ಅಷ್ಟಮಿ', 'Navami': 'ನವಮಿ', 'Dashami': 'ದಶಮಿ',
                'Ekadashi': 'ಏಕಾದಶಿ', 'Dwadashi': 'ದ್ವಾದಶಿ', 'Trayodashi': 'ತ್ರಯೋದಶಿ', 'Chaturdashi': 'ಚತುರ್ದಶಿ',
                'Purnima': 'ಹುಣ್ಣಿಮೆ', 'Amavasya': 'ಅಮಾವಾಸ್ಯೆ'}
TITHIS['ml'] = {'Prathama': 'പ്രഥമ', 'Dwitiya': 'ദ്വിതീയ', 'Tritiya': 'തൃതീയ', 'Chaturthi': 'ചതുർത്ഥി', 'Panchami': 'പഞ്ചമി',
                'Shashthi': 'ഷഷ്ഠി', 'Saptami': 'സപ്തമി', 'Ashtami': 'അഷ്ടമി', 'Navami': 'നവമി', 'Dashami': 'ദശമി',
                'Ekadashi': 'ഏകാദശി', 'Dwadashi': 'ദ്വാദശി', 'Trayodashi': 'ത്രയോദശി', 'Chaturdashi': 'ചതുർദ്ദശി',
                'Purnima': 'പൗർണ്ണമി', 'Amavasya': 'അമാവാസി'}
TITHIS['bn'] = {'Prathama': 'প্রতিপদ', 'Dwitiya': 'দ্বিতীয়া', 'Tritiya': 'তৃতীয়া', 'Chaturthi': 'চতুর্থী', 'Panchami': 'পঞ্চমী',
                'Shashthi': 'ষষ্ঠী', 'Saptami': 'সপ্তমী', 'Ashtami': 'অষ্টমী', 'Navami': 'নবমী', 'Dashami': 'দশমী',
                'Ekadashi': 'একাদশী', 'Dwadashi': 'দ্বাদশী', 'Trayodashi': 'ত্রয়োদশী', 'Chaturdashi': 'চতুর্দশী',
                'Purnima': 'পূর্ণিমা', 'Amavasya': 'অমাবস্যা'}

WORDS['te'] = {'Shukla': 'శుక్ల', 'Krishna': 'కృష్ణ', 'Exalted': 'ఉచ్చ', 'Debilitated': 'నీచ', 'Own sign': 'స్వక్షేత్రం',
               'Yes': 'అవును', 'Mean': 'సగటు', 'True': 'స్పష్ట', 'Male': 'పురుషుడు', 'Female': 'స్త్రీ'}
WORDS['kn'] = {'Shukla': 'ಶುಕ್ಲ', 'Krishna': 'ಕೃಷ್ಣ', 'Exalted': 'ಉಚ್ಚ', 'Debilitated': 'ನೀಚ', 'Own sign': 'ಸ್ವಕ್ಷೇತ್ರ',
               'Yes': 'ಹೌದು', 'Mean': 'ಸರಾಸರಿ', 'True': 'ಸ್ಪಷ್ಟ', 'Male': 'ಪುರುಷ', 'Female': 'ಸ್ತ್ರೀ'}
WORDS['ml'] = {'Shukla': 'ശുക്ല', 'Krishna': 'കൃഷ്ണ', 'Exalted': 'ഉച്ചം', 'Debilitated': 'നീചം', 'Own sign': 'സ്വക്ഷേത്രം',
               'Yes': 'അതെ', 'Mean': 'ശരാശരി', 'True': 'സ്ഫുടം', 'Male': 'പുരുഷൻ', 'Female': 'സ്ത്രീ'}
WORDS['bn'] = {'Shukla': 'শুক্ল', 'Krishna': 'কৃষ্ণ', 'Exalted': 'উচ্চ', 'Debilitated': 'নীচ', 'Own sign': 'স্বক্ষেত্র',
               'Yes': 'হ্যাঁ', 'Mean': 'গড়', 'True': 'স্পষ্ট', 'Male': 'পুরুষ', 'Female': 'নারী'}
WORDS['mr'] = {'Shukla': 'शुक्ल', 'Krishna': 'कृष्ण', 'Exalted': 'उच्च', 'Debilitated': 'नीच', 'Own sign': 'स्वराशी',
               'Yes': 'होय', 'Mean': 'मध्यम', 'True': 'स्पष्ट', 'Male': 'पुरुष', 'Female': 'स्त्री'}

VARGA_NAMES['te'] = {'D1': 'రాశి', 'D2': 'హోర', 'D3': 'ద్రేక్కాణం', 'D4': 'చతుర్థాంశ', 'D7': 'సప్తాంశ', 'D9': 'నవాంశ',
                     'D10': 'దశాంశ', 'D12': 'ద్వాదశాంశ', 'D16': 'షోడశాంశ', 'D20': 'వింశాంశ', 'D24': 'చతుర్వింశాంశ',
                     'D27': 'భాంశ', 'D30': 'త్రింశాంశ', 'D40': 'ఖవేదాంశ', 'D45': 'అక్షవేదాంశ', 'D60': 'షష్ట్యంశ'}
VARGA_NAMES['kn'] = {'D1': 'ರಾಶಿ', 'D2': 'ಹೋರಾ', 'D3': 'ದ್ರೇಕ್ಕಾಣ', 'D4': 'ಚತುರ್ಥಾಂಶ', 'D7': 'ಸಪ್ತಾಂಶ', 'D9': 'ನವಾಂಶ',
                     'D10': 'ದಶಾಂಶ', 'D12': 'ದ್ವಾದಶಾಂಶ', 'D16': 'ಷೋಡಶಾಂಶ', 'D20': 'ವಿಂಶಾಂಶ', 'D24': 'ಚತುರ್ವಿಂಶಾಂಶ',
                     'D27': 'ಭಾಂಶ', 'D30': 'ತ್ರಿಂಶಾಂಶ', 'D40': 'ಖವೇದಾಂಶ', 'D45': 'ಅಕ್ಷವೇದಾಂಶ', 'D60': 'ಷಷ್ಟ್ಯಂಶ'}
VARGA_NAMES['ml'] = {'D1': 'രാശി', 'D2': 'ഹോര', 'D3': 'ദ്രേക്കാണം', 'D4': 'ചതുർത്ഥാംശം', 'D7': 'സപ്താംശം', 'D9': 'നവാംശം',
                     'D10': 'ദശാംശം', 'D12': 'ദ്വാദശാംശം', 'D16': 'ഷോഡശാംശം', 'D20': 'വിംശാംശം', 'D24': 'ചതുർവിംശാംശം',
                     'D27': 'ഭാംശം', 'D30': 'ത്രിംശാംശം', 'D40': 'ഖവേദാംശം', 'D45': 'അക്ഷവേദാംശം', 'D60': 'ഷഷ്ട്യംശം'}
VARGA_NAMES['bn'] = {'D1': 'রাশি', 'D2': 'হোরা', 'D3': 'দ্রেক্কাণ', 'D4': 'চতুর্থাংশ', 'D7': 'সপ্তাংশ', 'D9': 'নবাংশ',
                     'D10': 'দশাংশ', 'D12': 'দ্বাদশাংশ', 'D16': 'ষোড়শাংশ', 'D20': 'বিংশাংশ', 'D24': 'চতুর্বিংশাংশ',
                     'D27': 'ভাংশ', 'D30': 'ত্রিংশাংশ', 'D40': 'খবেদাংশ', 'D45': 'অক্ষবেদাংশ', 'D60': 'ষষ্ট্যংশ'}

VARGA_PURPOSE['te'] = {'D1': 'శరీరం, ఆరోగ్యం మరియు సంపూర్ణ జీవితం', 'D2': 'సంపద మరియు వనరులు',
    'D3': 'తోబుట్టువులు, ధైర్యం మరియు ప్రయత్నం', 'D4': 'ఇల్లు, ఆస్తి మరియు అదృష్టం',
    'D7': 'సంతానం', 'D9': 'వివాహం, జీవిత భాగస్వామి మరియు గ్రహాల అంతర్బలం',
    'D10': 'వృత్తి, హోదా మరియు విజయాలు', 'D12': 'తల్లిదండ్రులు మరియు వంశం',
    'D16': 'వాహనాలు, సుఖాలు మరియు ఆనందం', 'D20': 'ఉపాసన మరియు ఆధ్యాత్మిక పురోగతి',
    'D24': 'విద్య మరియు జ్ఞానం', 'D27': 'బలాలు మరియు బలహీనతలు', 'D30': 'కష్టాలు మరియు ఆటంకాలు',
    'D40': 'శుభ, అశుభ ఫలితాలు (తల్లి వైపు)', 'D45': 'స్వభావం మరియు సాధారణ సూచనలు (తండ్రి వైపు)',
    'D60': 'అన్ని విషయాలు; జాతకంలోని సూక్ష్మ వివరాలు'}
VARGA_PURPOSE['kn'] = {'D1': 'ದೇಹ, ಆರೋಗ್ಯ ಮತ್ತು ಸಮಗ್ರ ಜೀವನ', 'D2': 'ಸಂಪತ್ತು ಮತ್ತು ಸಂಪನ್ಮೂಲ',
    'D3': 'ಒಡಹುಟ್ಟಿದವರು, ಧೈರ್ಯ ಮತ್ತು ಪ್ರಯತ್ನ', 'D4': 'ಮನೆ, ಆಸ್ತಿ ಮತ್ತು ಅದೃಷ್ಟ',
    'D7': 'ಸಂತಾನ', 'D9': 'ಮದುವೆ, ಸಂಗಾತಿ ಮತ್ತು ಗ್ರಹಗಳ ಆಂತರಿಕ ಬಲ',
    'D10': 'ವೃತ್ತಿ, ಸ್ಥಾನಮಾನ ಮತ್ತು ಸಾಧನೆ', 'D12': 'ಪೋಷಕರು ಮತ್ತು ವಂಶ',
    'D16': 'ವಾಹನ, ಸುಖ ಮತ್ತು ಸಂತೋಷ', 'D20': 'ಉಪಾಸನೆ ಮತ್ತು ಆಧ್ಯಾತ್ಮಿಕ ಪ್ರಗತಿ',
    'D24': 'ವಿದ್ಯೆ ಮತ್ತು ಜ್ಞಾನ', 'D27': 'ಬಲ ಮತ್ತು ದೌರ್ಬಲ್ಯ', 'D30': 'ಕಷ್ಟ ಮತ್ತು ತೊಂದರೆಗಳು',
    'D40': 'ಶುಭ, ಅಶುಭ ಫಲಗಳು (ತಾಯಿಯ ಕಡೆ)', 'D45': 'ಸ್ವಭಾವ ಮತ್ತು ಸಾಮಾನ್ಯ ಸೂಚನೆಗಳು (ತಂದೆಯ ಕಡೆ)',
    'D60': 'ಎಲ್ಲ ವಿಷಯಗಳು; ಜಾತಕದ ಸೂಕ್ಷ್ಮ ವಿವರ'}
VARGA_PURPOSE['ml'] = {'D1': 'ശരീരം, ആരോഗ്യം, ജീവിതം മൊത്തത്തിൽ', 'D2': 'സമ്പത്തും വിഭവങ്ങളും',
    'D3': 'സഹോദരങ്ങൾ, ധൈര്യം, പരിശ്രമം', 'D4': 'വീട്, വസ്തു, ഭാഗ്യം',
    'D7': 'സന്താനങ്ങൾ', 'D9': 'വിവാഹം, പങ്കാളി, ഗ്രഹങ്ങളുടെ ആന്തരിക ബലം',
    'D10': 'തൊഴിൽ, പദവി, നേട്ടങ്ങൾ', 'D12': 'മാതാപിതാക്കളും പരമ്പരയും',
    'D16': 'വാഹനങ്ങൾ, സുഖം, സന്തോഷം', 'D20': 'ഉപാസനയും ആത്മീയ പുരോഗതിയും',
    'D24': 'വിദ്യാഭ്യാസവും അറിവും', 'D27': 'ബലവും ദൗർബല്യവും', 'D30': 'കഷ്ടതകളും പ്രയാസങ്ങളും',
    'D40': 'ശുഭ, അശുഭ ഫലങ്ങൾ (മാതൃപക്ഷം)', 'D45': 'സ്വഭാവവും പൊതു സൂചനകളും (പിതൃപക്ഷം)',
    'D60': 'എല്ലാ കാര്യങ്ങളും; ജാതകത്തിന്റെ സൂക്ഷ്മ വിവരം'}
VARGA_PURPOSE['bn'] = {'D1': 'শরীর, স্বাস্থ্য ও সামগ্রিক জীবন', 'D2': 'সম্পদ ও সংস্থান',
    'D3': 'ভাইবোন, সাহস ও প্রচেষ্টা', 'D4': 'বাড়ি, সম্পত্তি ও ভাগ্য',
    'D7': 'সন্তান', 'D9': 'বিবাহ, জীবনসঙ্গী ও গ্রহের অন্তর্নিহিত বল',
    'D10': 'কর্মজীবন, মর্যাদা ও সাফল্য', 'D12': 'পিতামাতা ও বংশ',
    'D16': 'যানবাহন, সুখস্বাচ্ছন্দ্য ও আনন্দ', 'D20': 'উপাসনা ও আধ্যাত্মিক অগ্রগতি',
    'D24': 'শিক্ষা ও জ্ঞান', 'D27': 'শক্তি ও দুর্বলতা', 'D30': 'দুর্ভোগ ও বাধা',
    'D40': 'শুভ ও অশুভ ফল (মাতৃকুল)', 'D45': 'চরিত্র ও সাধারণ ইঙ্গিত (পিতৃকুল)',
    'D60': 'সব বিষয়; কুণ্ডলীর সূক্ষ্ম বিবরণ'}
VARGA_PURPOSE['mr'] = {'D1': 'शरीर, आरोग्य आणि संपूर्ण जीवन', 'D2': 'धन आणि साधनसंपत्ती',
    'D3': 'भावंडे, धैर्य आणि प्रयत्न', 'D4': 'घर, मालमत्ता आणि भाग्य',
    'D7': 'संतती', 'D9': 'विवाह, जोडीदार आणि ग्रहांचे आंतरिक बळ',
    'D10': 'करिअर, प्रतिष्ठा आणि यश', 'D12': 'आई-वडील आणि वंश',
    'D16': 'वाहने, सुख आणि आनंद', 'D20': 'उपासना आणि आध्यात्मिक प्रगती',
    'D24': 'शिक्षण आणि ज्ञान', 'D27': 'बळ आणि दुर्बलता', 'D30': 'कष्ट आणि अडचणी',
    'D40': 'शुभ आणि अशुभ फळे (मातृपक्ष)', 'D45': 'स्वभाव आणि सामान्य संकेत (पितृपक्ष)',
    'D60': 'सर्व विषय; कुंडलीचा सूक्ष्म तपशील'}

LABELS['te'] = {
    'brand': 'HoroscopeGen', 'report_title': 'జాతక నివేదిక', 'subtitle': 'వైదిక · కేపీ · అక్షయ లగ్నం',
    'summary': 'సారాంశం', 'vedic': 'వైదిక', 'kp': 'కేపీ', 'alp': 'అక్షయ లగ్నం', 'dasa_sheet': 'దశ', 'notes': 'గమనికలు',
    'birth_details': 'జనన వివరాలు', 'name': 'పేరు', 'gender': 'లింగం', 'dob': 'జనన తేదీ',
    'tob': 'జనన సమయం', 'pob': 'జనన స్థలం', 'lat': 'అక్షాంశం', 'lon': 'రేఖాంశం',
    'tz': 'సమయ మండలం', 'ayanamsha': 'అయనాంశ', 'kp_ayanamsha': 'కేపీ అయనాంశ', 'nodes': 'రాహువు / కేతువు',
    'core': 'ముఖ్య వివరాలు', 'lagna': 'లగ్నం', 'janma_rasi': 'రాశి (చంద్ర రాశి)', 'nakshatra': 'నక్షత్రం',
    'pada': 'పాదం', 'nak_lord': 'నక్షత్ర అధిపతి', 'tithi': 'తిథి', 'vara': 'వారం', 'yoga': 'యోగం',
    'karana': 'కరణం', 'sunrise': 'సూర్యోదయం', 'sunset': 'సూర్యాస్తమయం', 'panchangam': 'జనన పంచాంగం',
    'mandi_rise': 'మాంది ఉదయ సమయం',
    'divisional': 'వర్గ చక్రాలు', 'varga_table': '16 వర్గ చక్రాలలో ప్రతి గ్రహం రాశి',
    'vargottama': 'వర్గోత్తమం', 'vargottama_note': 'వర్గోత్తమం: రాశి (D1) మరియు నవాంశ (D9) రెండింటిలో ఒకే రాశి.',
    'varga_time_note': 'ఉన్నత వర్గ చక్రాలకు ఖచ్చితమైన జనన సమయం అవసరం: D60 లగ్నం సుమారు ప్రతి రెండు నిమిషాలకు మారుతుంది.',
    'dasa_balance': 'జనన సమయ దశ శేషం', 'current_period': 'ప్రస్తుత కాలం',
    'dasa': 'దశ', 'bhukti': 'అంతర్దశ', 'antaram': 'ప్రత్యంతర్దశ', 'ends': 'ముగింపు', 'until': 'వరకు',
    'planet': 'గ్రహం', 'rasi': 'రాశి', 'degree': 'భాగలు', 'rasi_lord': 'రాశి అధిపతి', 'star_lord': 'నక్షత్ర అధిపతి',
    'sub_lord': 'ఉప అధిపతి', 'subsub_lord': 'ఉప-ఉప అధిపతి', 'house': 'భావం', 'bhava': 'భావ చలితం',
    'navamsa': 'నవాంశ', 'retro': 'వక్రం', 'combust': 'అస్తంగతం', 'dignity': 'స్థితి',
    'planet_positions': 'గ్రహ స్థితులు', 'bhava_table': 'భావాలు (శ్రీపతి)', 'bhava_start': 'భావ ఆరంభం',
    'bhava_mid': 'భావ మధ్యం',
    'rasi_chart': 'రాశి చక్రం (D1)', 'navamsa_chart': 'నవాంశ చక్రం (D9)', 'bhava_chart': 'భావ చక్రం',
    'kp_chart': 'కేపీ భావ చక్రం', 'alp_chart': 'అక్షయ లగ్న చక్రం',
    'cusp': 'భావ సంధి', 'cusps': 'భావ సంధులు (ప్లాసిడస్)', 'kp_planets': 'కేపీ గ్రహ స్థితులు',
    'planet_sig': 'గ్రహ కారకత్వం', 'house_sig': 'భావ కారకులు',
    'level1': 'స్థాయి 1: నక్షత్ర అధిపతి ఉన్న భావం', 'level2': 'స్థాయి 2: ఉన్న భావం',
    'level3': 'స్థాయి 3: నక్షత్ర అధిపతి భావాలు', 'level4': 'స్థాయి 4: స్వంత భావాలు',
    'sig_a': 'A: భావస్థుల నక్షత్రంలో', 'sig_b': 'B: భావస్థులు', 'sig_c': 'C: భావాధిపతి నక్షత్రంలో', 'sig_d': 'D: భావాధిపతి',
    'ruling_planets': 'జనన సమయ పాలక గ్రహాలు', 'day_lord': 'వార అధిపతి',
    'moon_sign_lord': 'చంద్ర రాశి అధిపతి', 'moon_star_lord': 'చంద్ర నక్షత్ర అధిపతి', 'moon_sub_lord': 'చంద్ర ఉప అధిపతి',
    'lagna_sign_lord': 'లగ్న రాశి అధిపతి', 'lagna_star_lord': 'లగ్న నక్షత్ర అధిపతి', 'lagna_sub_lord': 'లగ్న ఉప అధిపతి',
    'node_agents': 'రాహు / కేతు ప్రాతినిధ్యం', 'node': 'ఛాయా గ్రహం', 'conjoined': 'ఒకే రాశిలోని గ్రహాలు',
    'kp_dasa': 'వింశోత్తరి దశ (కేపీ అయనాంశ)', 'vim_dasa': 'వింశోత్తరి దశ',
    'house_system': 'భావ పద్ధతి',
    'alp_title': 'అక్షయ లగ్న పద్ధతి', 'alp_birth_lagna': 'జనన లగ్నం', 'alp_lagna_now': 'నేటి అక్షయ లగ్నం',
    'alp_rule': 'నియమం', 'alp_sign_periods': 'రాశి వారీగా అక్షయ లగ్నం (ఒక్కొక్కటి 10 సంవత్సరాలు)',
    'alp_pada_periods': 'నక్షత్ర పాదం వారీగా అక్షయ లగ్నం', 'age': 'వయసు', 'age_from': 'వయసు నుండి', 'age_to': 'వయసు వరకు',
    'from': 'నుండి', 'to': 'వరకు', 'start': 'ప్రారంభం', 'end': 'ముగింపు', 'status': 'స్థితి',
    'completed': 'పూర్తయింది', 'current': 'ప్రస్తుతం', 'upcoming': 'రాబోయేది', 'years': 'సంవత్సరాలు',
    'y': 'సం', 'm': 'నె', 'd': 'రో', 'as_of': 'లెక్కించిన తేదీ', 'generated': 'రూపొందించిన తేదీ',
    'abbreviations': 'సంక్షిప్త రూపాలు', 'how_calculated': 'ఈ నివేదిక లెక్కించిన విధానం',
    'disclaimer': 'ఈ నివేదిక జ్యోతిష గణనలను మార్గదర్శనం కోసం మాత్రమే అందిస్తుంది.',
    'page': 'పేజీ',
}
LABELS['kn'] = {
    'brand': 'HoroscopeGen', 'report_title': 'ಜಾತಕ ವರದಿ', 'subtitle': 'ವೈದಿಕ · ಕೆಪಿ · ಅಕ್ಷಯ ಲಗ್ನ',
    'summary': 'ಸಾರಾಂಶ', 'vedic': 'ವೈದಿಕ', 'kp': 'ಕೆಪಿ', 'alp': 'ಅಕ್ಷಯ ಲಗ್ನ', 'dasa_sheet': 'ದಶೆ', 'notes': 'ಟಿಪ್ಪಣಿಗಳು',
    'birth_details': 'ಜನನ ವಿವರಗಳು', 'name': 'ಹೆಸರು', 'gender': 'ಲಿಂಗ', 'dob': 'ಜನ್ಮ ದಿನಾಂಕ',
    'tob': 'ಜನನ ಸಮಯ', 'pob': 'ಜನನ ಸ್ಥಳ', 'lat': 'ಅಕ್ಷಾಂಶ', 'lon': 'ರೇಖಾಂಶ',
    'tz': 'ಸಮಯ ವಲಯ', 'ayanamsha': 'ಅಯನಾಂಶ', 'kp_ayanamsha': 'ಕೆಪಿ ಅಯನಾಂಶ', 'nodes': 'ರಾಹು / ಕೇತು',
    'core': 'ಮುಖ್ಯ ವಿವರಗಳು', 'lagna': 'ಲಗ್ನ', 'janma_rasi': 'ರಾಶಿ (ಚಂದ್ರ ರಾಶಿ)', 'nakshatra': 'ನಕ್ಷತ್ರ',
    'pada': 'ಪಾದ', 'nak_lord': 'ನಕ್ಷತ್ರ ಅಧಿಪತಿ', 'tithi': 'ತಿಥಿ', 'vara': 'ವಾರ', 'yoga': 'ಯೋಗ',
    'karana': 'ಕರಣ', 'sunrise': 'ಸೂರ್ಯೋದಯ', 'sunset': 'ಸೂರ್ಯಾಸ್ತ', 'panchangam': 'ಜನನ ಪಂಚಾಂಗ',
    'mandi_rise': 'ಮಾಂದಿ ಉದಯ ಸಮಯ',
    'divisional': 'ವರ್ಗ ಚಕ್ರಗಳು', 'varga_table': '16 ವರ್ಗ ಚಕ್ರಗಳಲ್ಲಿ ಪ್ರತಿ ಗ್ರಹದ ರಾಶಿ',
    'vargottama': 'ವರ್ಗೋತ್ತಮ', 'vargottama_note': 'ವರ್ಗೋತ್ತಮ: ರಾಶಿ (D1) ಮತ್ತು ನವಾಂಶ (D9) ಎರಡರಲ್ಲೂ ಒಂದೇ ರಾಶಿ.',
    'varga_time_note': 'ಉನ್ನತ ವರ್ಗ ಚಕ್ರಗಳಿಗೆ ನಿಖರ ಜನನ ಸಮಯ ಅಗತ್ಯ: D60 ಲಗ್ನ ಸುಮಾರು ಪ್ರತಿ ಎರಡು ನಿಮಿಷಕ್ಕೆ ಬದಲಾಗುತ್ತದೆ.',
    'dasa_balance': 'ಜನನ ಸಮಯದ ದಶಾ ಶೇಷ', 'current_period': 'ಪ್ರಸ್ತುತ ಕಾಲ',
    'dasa': 'ದಶೆ', 'bhukti': 'ಭುಕ್ತಿ', 'antaram': 'ಅಂತರ', 'ends': 'ಮುಕ್ತಾಯ', 'until': 'ವರೆಗೆ',
    'planet': 'ಗ್ರಹ', 'rasi': 'ರಾಶಿ', 'degree': 'ಅಂಶ', 'rasi_lord': 'ರಾಶಿ ಅಧಿಪತಿ', 'star_lord': 'ನಕ್ಷತ್ರ ಅಧಿಪತಿ',
    'sub_lord': 'ಉಪ ಅಧಿಪತಿ', 'subsub_lord': 'ಉಪ-ಉಪ ಅಧಿಪತಿ', 'house': 'ಭಾವ', 'bhava': 'ಭಾವ ಚಲಿತ',
    'navamsa': 'ನವಾಂಶ', 'retro': 'ವಕ್ರ', 'combust': 'ಅಸ್ತಂಗತ', 'dignity': 'ಸ್ಥಿತಿ',
    'planet_positions': 'ಗ್ರಹ ಸ್ಥಿತಿಗಳು', 'bhava_table': 'ಭಾವಗಳು (ಶ್ರೀಪತಿ)', 'bhava_start': 'ಭಾವ ಆರಂಭ',
    'bhava_mid': 'ಭಾವ ಮಧ್ಯ',
    'rasi_chart': 'ರಾಶಿ ಚಕ್ರ (D1)', 'navamsa_chart': 'ನವಾಂಶ ಚಕ್ರ (D9)', 'bhava_chart': 'ಭಾವ ಚಕ್ರ',
    'kp_chart': 'ಕೆಪಿ ಭಾವ ಚಕ್ರ', 'alp_chart': 'ಅಕ್ಷಯ ಲಗ್ನ ಚಕ್ರ',
    'cusp': 'ಭಾವ ಸಂಧಿ', 'cusps': 'ಭಾವ ಸಂಧಿಗಳು (ಪ್ಲಾಸಿಡಸ್)', 'kp_planets': 'ಕೆಪಿ ಗ್ರಹ ಸ್ಥಿತಿಗಳು',
    'planet_sig': 'ಗ್ರಹ ಕಾರಕತ್ವ', 'house_sig': 'ಭಾವ ಕಾರಕರು',
    'level1': 'ಹಂತ 1: ನಕ್ಷತ್ರ ಅಧಿಪತಿ ಇರುವ ಭಾವ', 'level2': 'ಹಂತ 2: ಇರುವ ಭಾವ',
    'level3': 'ಹಂತ 3: ನಕ್ಷತ್ರ ಅಧಿಪತಿಯ ಭಾವಗಳು', 'level4': 'ಹಂತ 4: ಸ್ವಂತ ಭಾವಗಳು',
    'sig_a': 'A: ಭಾವಸ್ಥರ ನಕ್ಷತ್ರದಲ್ಲಿ', 'sig_b': 'B: ಭಾವಸ್ಥರು', 'sig_c': 'C: ಭಾವಾಧಿಪತಿಯ ನಕ್ಷತ್ರದಲ್ಲಿ', 'sig_d': 'D: ಭಾವಾಧಿಪತಿ',
    'ruling_planets': 'ಜನನ ಸಮಯದ ಆಳುವ ಗ್ರಹಗಳು', 'day_lord': 'ವಾರ ಅಧಿಪತಿ',
    'moon_sign_lord': 'ಚಂದ್ರ ರಾಶಿ ಅಧಿಪತಿ', 'moon_star_lord': 'ಚಂದ್ರ ನಕ್ಷತ್ರ ಅಧಿಪತಿ', 'moon_sub_lord': 'ಚಂದ್ರ ಉಪ ಅಧಿಪತಿ',
    'lagna_sign_lord': 'ಲಗ್ನ ರಾಶಿ ಅಧಿಪತಿ', 'lagna_star_lord': 'ಲಗ್ನ ನಕ್ಷತ್ರ ಅಧಿಪತಿ', 'lagna_sub_lord': 'ಲಗ್ನ ಉಪ ಅಧಿಪತಿ',
    'node_agents': 'ರಾಹು / ಕೇತು ಪ್ರತಿನಿಧಿತ್ವ', 'node': 'ಛಾಯಾ ಗ್ರಹ', 'conjoined': 'ಒಂದೇ ರಾಶಿಯ ಗ್ರಹಗಳು',
    'kp_dasa': 'ವಿಂಶೋತ್ತರಿ ದಶೆ (ಕೆಪಿ ಅಯನಾಂಶ)', 'vim_dasa': 'ವಿಂಶೋತ್ತರಿ ದಶೆ',
    'house_system': 'ಭಾವ ಪದ್ಧತಿ',
    'alp_title': 'ಅಕ್ಷಯ ಲಗ್ನ ಪದ್ಧತಿ', 'alp_birth_lagna': 'ಜನನ ಲಗ್ನ', 'alp_lagna_now': 'ಇಂದಿನ ಅಕ್ಷಯ ಲಗ್ನ',
    'alp_rule': 'ನಿಯಮ', 'alp_sign_periods': 'ರಾಶಿವಾರು ಅಕ್ಷಯ ಲಗ್ನ (ತಲಾ 10 ವರ್ಷ)',
    'alp_pada_periods': 'ನಕ್ಷತ್ರ ಪಾದವಾರು ಅಕ್ಷಯ ಲಗ್ನ', 'age': 'ವಯಸ್ಸು', 'age_from': 'ವಯಸ್ಸಿನಿಂದ', 'age_to': 'ವಯಸ್ಸಿನವರೆಗೆ',
    'from': 'ಇಂದ', 'to': 'ವರೆಗೆ', 'start': 'ಆರಂಭ', 'end': 'ಮುಕ್ತಾಯ', 'status': 'ಸ್ಥಿತಿ',
    'completed': 'ಮುಗಿದಿದೆ', 'current': 'ಪ್ರಸ್ತುತ', 'upcoming': 'ಮುಂಬರುವ', 'years': 'ವರ್ಷಗಳು',
    'y': 'ವ', 'm': 'ತಿ', 'd': 'ದಿ', 'as_of': 'ಲೆಕ್ಕ ಹಾಕಿದ ದಿನಾಂಕ', 'generated': 'ರಚಿಸಿದ ದಿನಾಂಕ',
    'abbreviations': 'ಸಂಕ್ಷಿಪ್ತ ರೂಪಗಳು', 'how_calculated': 'ಈ ವರದಿಯನ್ನು ಲೆಕ್ಕ ಹಾಕಿದ ವಿಧಾನ',
    'disclaimer': 'ಈ ವರದಿ ಜ್ಯೋತಿಷ್ಯ ಲೆಕ್ಕಾಚಾರಗಳನ್ನು ಮಾರ್ಗದರ್ಶನಕ್ಕಾಗಿ ಮಾತ್ರ ನೀಡುತ್ತದೆ.',
    'page': 'ಪುಟ',
}
LABELS['ml'] = {
    'brand': 'HoroscopeGen', 'report_title': 'ജാതക റിപ്പോർട്ട്', 'subtitle': 'വൈദിക · കെപി · അക്ഷയ ലഗ്നം',
    'summary': 'സംഗ്രഹം', 'vedic': 'വൈദിക', 'kp': 'കെപി', 'alp': 'അക്ഷയ ലഗ്നം', 'dasa_sheet': 'ദശ', 'notes': 'കുറിപ്പുകൾ',
    'birth_details': 'ജനന വിവരങ്ങൾ', 'name': 'പേര്', 'gender': 'ലിംഗം', 'dob': 'ജനന തീയതി',
    'tob': 'ജനന സമയം', 'pob': 'ജനന സ്ഥലം', 'lat': 'അക്ഷാംശം', 'lon': 'രേഖാംശം',
    'tz': 'സമയ മേഖല', 'ayanamsha': 'അയനാംശം', 'kp_ayanamsha': 'കെപി അയനാംശം', 'nodes': 'രാഹു / കേതു',
    'core': 'പ്രധാന വിവരങ്ങൾ', 'lagna': 'ലഗ്നം', 'janma_rasi': 'കൂറ് (ചന്ദ്ര രാശി)', 'nakshatra': 'നക്ഷത്രം',
    'pada': 'പാദം', 'nak_lord': 'നക്ഷത്രാധിപൻ', 'tithi': 'തിഥി', 'vara': 'ആഴ്ച', 'yoga': 'യോഗം',
    'karana': 'കരണം', 'sunrise': 'സൂര്യോദയം', 'sunset': 'സൂര്യാസ്തമയം', 'panchangam': 'ജനന പഞ്ചാംഗം',
    'mandi_rise': 'മാന്ദി ഉദയ സമയം',
    'divisional': 'വർഗ്ഗ ചക്രങ്ങൾ', 'varga_table': '16 വർഗ്ഗ ചക്രങ്ങളിൽ ഓരോ ഗ്രഹത്തിന്റെയും രാശി',
    'vargottama': 'വർഗ്ഗോത്തമം', 'vargottama_note': 'വർഗ്ഗോത്തമം: രാശി (D1), നവാംശം (D9) രണ്ടിലും ഒരേ രാശി.',
    'varga_time_note': 'ഉയർന്ന വർഗ്ഗ ചക്രങ്ങൾക്ക് കൃത്യമായ ജനന സമയം ആവശ്യം: D60 ലഗ്നം ഏകദേശം രണ്ട് മിനിറ്റിലൊരിക്കൽ മാറുന്നു.',
    'dasa_balance': 'ജനന സമയത്തെ ദശാ ശിഷ്ടം', 'current_period': 'നിലവിലെ കാലം',
    'dasa': 'ദശ', 'bhukti': 'അപഹാരം', 'antaram': 'ഛിദ്രം', 'ends': 'അവസാനം', 'until': 'വരെ',
    'planet': 'ഗ്രഹം', 'rasi': 'രാശി', 'degree': 'ഡിഗ്രി', 'rasi_lord': 'രാശ്യാധിപൻ', 'star_lord': 'നക്ഷത്രാധിപൻ',
    'sub_lord': 'ഉപാധിപൻ', 'subsub_lord': 'ഉപ-ഉപാധിപൻ', 'house': 'ഭാവം', 'bhava': 'ഭാവ ചലിതം',
    'navamsa': 'നവാംശം', 'retro': 'വക്രം', 'combust': 'മൗഢ്യം', 'dignity': 'സ്ഥിതി',
    'planet_positions': 'ഗ്രഹസ്ഥിതി', 'bhava_table': 'ഭാവങ്ങൾ (ശ്രീപതി)', 'bhava_start': 'ഭാവാരംഭം',
    'bhava_mid': 'ഭാവമധ്യം',
    'rasi_chart': 'രാശി ചക്രം (D1)', 'navamsa_chart': 'നവാംശ ചക്രം (D9)', 'bhava_chart': 'ഭാവ ചക്രം',
    'kp_chart': 'കെപി ഭാവ ചക്രം', 'alp_chart': 'അക്ഷയ ലഗ്ന ചക്രം',
    'cusp': 'ഭാവസന്ധി', 'cusps': 'ഭാവസന്ധികൾ (പ്ലാസിഡസ്)', 'kp_planets': 'കെപി ഗ്രഹസ്ഥിതി',
    'planet_sig': 'ഗ്രഹ കാരകത്വം', 'house_sig': 'ഭാവ കാരകർ',
    'level1': 'തലം 1: നക്ഷത്രാധിപൻ നിൽക്കുന്ന ഭാവം', 'level2': 'തലം 2: നിൽക്കുന്ന ഭാവം',
    'level3': 'തലം 3: നക്ഷത്രാധിപന്റെ ഭാവങ്ങൾ', 'level4': 'തലം 4: സ്വന്തം ഭാവങ്ങൾ',
    'sig_a': 'A: ഭാവസ്ഥരുടെ നക്ഷത്രത്തിൽ', 'sig_b': 'B: ഭാവസ്ഥർ', 'sig_c': 'C: ഭാവാധിപന്റെ നക്ഷത്രത്തിൽ', 'sig_d': 'D: ഭാവാധിപൻ',
    'ruling_planets': 'ജനന സമയത്തെ ഭരണ ഗ്രഹങ്ങൾ', 'day_lord': 'ആഴ്ചയുടെ അധിപൻ',
    'moon_sign_lord': 'ചന്ദ്ര രാശ്യാധിപൻ', 'moon_star_lord': 'ചന്ദ്ര നക്ഷത്രാധിപൻ', 'moon_sub_lord': 'ചന്ദ്ര ഉപാധിപൻ',
    'lagna_sign_lord': 'ലഗ്ന രാശ്യാധിപൻ', 'lagna_star_lord': 'ലഗ്ന നക്ഷത്രാധിപൻ', 'lagna_sub_lord': 'ലഗ്ന ഉപാധിപൻ',
    'node_agents': 'രാഹു / കേതു പ്രാതിനിധ്യം', 'node': 'ഛായാ ഗ്രഹം', 'conjoined': 'ഒരേ രാശിയിലെ ഗ്രഹങ്ങൾ',
    'kp_dasa': 'വിംശോത്തരി ദശ (കെപി അയനാംശം)', 'vim_dasa': 'വിംശോത്തരി ദശ',
    'house_system': 'ഭാവ സമ്പ്രദായം',
    'alp_title': 'അക്ഷയ ലഗ്ന പദ്ധതി', 'alp_birth_lagna': 'ജനന ലഗ്നം', 'alp_lagna_now': 'ഇന്നത്തെ അക്ഷയ ലഗ്നം',
    'alp_rule': 'നിയമം', 'alp_sign_periods': 'രാശി തിരിച്ച് അക്ഷയ ലഗ്നം (ഓരോന്നും 10 വർഷം)',
    'alp_pada_periods': 'നക്ഷത്ര പാദം തിരിച്ച് അക്ഷയ ലഗ്നം', 'age': 'വയസ്സ്', 'age_from': 'വയസ്സ് മുതൽ', 'age_to': 'വയസ്സ് വരെ',
    'from': 'മുതൽ', 'to': 'വരെ', 'start': 'ആരംഭം', 'end': 'അവസാനം', 'status': 'സ്ഥിതി',
    'completed': 'പൂർത്തിയായി', 'current': 'നിലവിൽ', 'upcoming': 'വരാനിരിക്കുന്നത്', 'years': 'വർഷം',
    'y': 'വ', 'm': 'മാ', 'd': 'ദി', 'as_of': 'കണക്കാക്കിയ തീയതി', 'generated': 'തയ്യാറാക്കിയ തീയതി',
    'abbreviations': 'ചുരുക്കെഴുത്തുകൾ', 'how_calculated': 'ഈ റിപ്പോർട്ട് കണക്കാക്കിയ രീതി',
    'disclaimer': 'ഈ റിപ്പോർട്ട് ജ്യോതിഷ ഗണനകൾ മാർഗ്ഗനിർദ്ദേശത്തിനായി മാത്രം നൽകുന്നു.',
    'page': 'പേജ്',
}
LABELS['bn'] = {
    'brand': 'HoroscopeGen', 'report_title': 'কোষ্ঠী রিপোর্ট', 'subtitle': 'বৈদিক · কেপি · অক্ষয় লগ্ন',
    'summary': 'সারাংশ', 'vedic': 'বৈদিক', 'kp': 'কেপি', 'alp': 'অক্ষয় লগ্ন', 'dasa_sheet': 'দশা', 'notes': 'টীকা',
    'birth_details': 'জন্ম বিবরণ', 'name': 'নাম', 'gender': 'লিঙ্গ', 'dob': 'জন্ম তারিখ',
    'tob': 'জন্ম সময়', 'pob': 'জন্মস্থান', 'lat': 'অক্ষাংশ', 'lon': 'দ্রাঘিমাংশ',
    'tz': 'সময় অঞ্চল', 'ayanamsha': 'অয়নাংশ', 'kp_ayanamsha': 'কেপি অয়নাংশ', 'nodes': 'রাহু / কেতু',
    'core': 'মূল বিবরণ', 'lagna': 'লগ্ন', 'janma_rasi': 'রাশি (চন্দ্র রাশি)', 'nakshatra': 'নক্ষত্র',
    'pada': 'পাদ', 'nak_lord': 'নক্ষত্র অধিপতি', 'tithi': 'তিথি', 'vara': 'বার', 'yoga': 'যোগ',
    'karana': 'করণ', 'sunrise': 'সূর্যোদয়', 'sunset': 'সূর্যাস্ত', 'panchangam': 'জন্ম পঞ্জিকা',
    'mandi_rise': 'মান্দি উদয় সময়',
    'divisional': 'বর্গ চক্র', 'varga_table': '16টি বর্গ চক্রে প্রতিটি গ্রহের রাশি',
    'vargottama': 'বর্গোত্তম', 'vargottama_note': 'বর্গোত্তম: রাশি (D1) ও নবাংশ (D9) দুটিতেই একই রাশি।',
    'varga_time_note': 'উচ্চতর বর্গ চক্রের জন্য সঠিক জন্ম সময় জরুরি: D60 লগ্ন প্রায় প্রতি দুই মিনিটে বদলায়।',
    'dasa_balance': 'জন্মকালীন দশা শেষ', 'current_period': 'বর্তমান কাল',
    'dasa': 'দশা', 'bhukti': 'অন্তর্দশা', 'antaram': 'প্রত্যন্তর', 'ends': 'শেষ', 'until': 'পর্যন্ত',
    'planet': 'গ্রহ', 'rasi': 'রাশি', 'degree': 'অংশ', 'rasi_lord': 'রাশি অধিপতি', 'star_lord': 'নক্ষত্র অধিপতি',
    'sub_lord': 'উপ অধিপতি', 'subsub_lord': 'উপ-উপ অধিপতি', 'house': 'ভাব', 'bhava': 'ভাব চলিত',
    'navamsa': 'নবাংশ', 'retro': 'বক্রী', 'combust': 'অস্ত', 'dignity': 'অবস্থা',
    'planet_positions': 'গ্রহ অবস্থান', 'bhava_table': 'ভাব (শ্রীপতি)', 'bhava_start': 'ভাব আরম্ভ',
    'bhava_mid': 'ভাব মধ্য',
    'rasi_chart': 'রাশি চক্র (D1)', 'navamsa_chart': 'নবাংশ চক্র (D9)', 'bhava_chart': 'ভাব চক্র',
    'kp_chart': 'কেপি ভাব চক্র', 'alp_chart': 'অক্ষয় লগ্ন চক্র',
    'cusp': 'ভাব সন্ধি', 'cusps': 'ভাব সন্ধি (প্লাসিডাস)', 'kp_planets': 'কেপি গ্রহ অবস্থান',
    'planet_sig': 'গ্রহ কারকত্ব', 'house_sig': 'ভাব কারক',
    'level1': 'স্তর 1: নক্ষত্র অধিপতি যে ভাবে', 'level2': 'স্তর 2: যে ভাবে অবস্থিত',
    'level3': 'স্তর 3: নক্ষত্র অধিপতির ভাব', 'level4': 'স্তর 4: নিজের ভাব',
    'sig_a': 'A: ভাবস্থ গ্রহের নক্ষত্রে', 'sig_b': 'B: ভাবস্থ গ্রহ', 'sig_c': 'C: ভাবেশের নক্ষত্রে', 'sig_d': 'D: ভাবেশ',
    'ruling_planets': 'জন্মকালীন শাসক গ্রহ', 'day_lord': 'বারের অধিপতি',
    'moon_sign_lord': 'চন্দ্র রাশি অধিপতি', 'moon_star_lord': 'চন্দ্র নক্ষত্র অধিপতি', 'moon_sub_lord': 'চন্দ্র উপ অধিপতি',
    'lagna_sign_lord': 'লগ্ন রাশি অধিপতি', 'lagna_star_lord': 'লগ্ন নক্ষত্র অধিপতি', 'lagna_sub_lord': 'লগ্ন উপ অধিপতি',
    'node_agents': 'রাহু / কেতু প্রতিনিধিত্ব', 'node': 'ছায়া গ্রহ', 'conjoined': 'একই রাশির গ্রহ',
    'kp_dasa': 'বিংশোত্তরী দশা (কেপি অয়নাংশ)', 'vim_dasa': 'বিংশোত্তরী দশা',
    'house_system': 'ভাব পদ্ধতি',
    'alp_title': 'অক্ষয় লগ্ন পদ্ধতি', 'alp_birth_lagna': 'জন্ম লগ্ন', 'alp_lagna_now': 'আজকের অক্ষয় লগ্ন',
    'alp_rule': 'নিয়ম', 'alp_sign_periods': 'রাশি অনুযায়ী অক্ষয় লগ্ন (প্রতিটি 10 বছর)',
    'alp_pada_periods': 'নক্ষত্র পাদ অনুযায়ী অক্ষয় লগ্ন', 'age': 'বয়স', 'age_from': 'বয়স থেকে', 'age_to': 'বয়স পর্যন্ত',
    'from': 'থেকে', 'to': 'পর্যন্ত', 'start': 'শুরু', 'end': 'শেষ', 'status': 'অবস্থা',
    'completed': 'সম্পূর্ণ', 'current': 'বর্তমান', 'upcoming': 'আসন্ন', 'years': 'বছর',
    'y': 'ব', 'm': 'মা', 'd': 'দি', 'as_of': 'গণনার তারিখ', 'generated': 'তৈরির তারিখ',
    'abbreviations': 'সংক্ষিপ্ত রূপ', 'how_calculated': 'এই রিপোর্ট গণনার পদ্ধতি',
    'disclaimer': 'এই রিপোর্ট জ্যোতিষ গণনা কেবল দিকনির্দেশের জন্য উপস্থাপন করে।',
    'page': 'পৃষ্ঠা',
}
LABELS['mr'] = dict(LABELS['hi'])
LABELS['mr'].update({
    'report_title': 'कुंडली अहवाल', 'subtitle': 'वैदिक · केपी · अक्षय लग्न', 'alp': 'अक्षय लग्न',
    'notes': 'टिपा', 'birth_details': 'जन्म तपशील', 'name': 'नाव', 'dob': 'जन्म तारीख', 'tob': 'जन्म वेळ',
    'tz': 'वेळ क्षेत्र', 'core': 'मुख्य तपशील', 'janma_rasi': 'राशी (चंद्र राशी)', 'rasi': 'राशी',
    'nak_lord': 'नक्षत्र स्वामी', 'mandi_rise': 'मांदी उदय वेळ',
    'divisional': 'वर्ग कुंडल्या', 'varga_table': '16 वर्ग कुंडल्यांमधील प्रत्येक ग्रहाची राशी',
    'vargottama_note': 'वर्गोत्तम: राशी (D1) आणि नवांश (D9) दोन्हीत एकच राशी.',
    'varga_time_note': 'उच्च वर्ग कुंडल्या अचूक जन्मवेळेवर अवलंबून असतात: D60 लग्न सुमारे दर दोन मिनिटांनी बदलते.',
    'dasa_balance': 'जन्मवेळी दशा शिल्लक', 'current_period': 'चालू काळ', 'ends': 'समाप्ती', 'until': 'पर्यंत',
    'rasi_lord': 'राशी स्वामी', 'dignity': 'स्थिती', 'planet_positions': 'ग्रह स्थिती',
    'bhava_start': 'भाव आरंभ', 'kp_chart': 'केपी भाव कुंडली', 'alp_chart': 'अक्षय लग्न कुंडली',
    'level1': 'स्तर 1: नक्षत्र स्वामी ज्या भावात', 'level2': 'स्तर 2: स्वतः ज्या भावात',
    'level3': 'स्तर 3: नक्षत्र स्वामीचे भाव', 'level4': 'स्तर 4: स्वतःचे भाव',
    'ruling_planets': 'जन्मवेळी शासक ग्रह', 'moon_sign_lord': 'चंद्र राशी स्वामी', 'lagna_sign_lord': 'लग्न राशी स्वामी',
    'conjoined': 'एकाच राशीतील ग्रह', 'house_system': 'भाव पद्धती',
    'alp_title': 'अक्षय लग्न पद्धती', 'alp_lagna_now': 'आजचे अक्षय लग्न', 'alp_rule': 'नियम',
    'alp_sign_periods': 'राशीनुसार अक्षय लग्न (प्रत्येकी 10 वर्षे)', 'alp_pada_periods': 'नक्षत्र चरणानुसार अक्षय लग्न',
    'age': 'वय', 'age_from': 'वयापासून', 'age_to': 'वयापर्यंत', 'from': 'पासून', 'to': 'पर्यंत',
    'start': 'सुरुवात', 'end': 'समाप्ती', 'status': 'स्थिती', 'completed': 'पूर्ण', 'current': 'चालू',
    'upcoming': 'आगामी', 'years': 'वर्षे', 'as_of': 'गणना तारीख', 'generated': 'निर्मिती तारीख',
    'abbreviations': 'संक्षेप', 'how_calculated': 'या अहवालाची गणना पद्धत',
    'disclaimer': 'हा अहवाल ज्योतिषीय गणना केवळ मार्गदर्शनासाठी सादर करतो.', 'page': 'पान',
})


def _base(lang):
    """Language used for single-script lookups ('bi' draws charts in English)."""
    return 'en' if lang == 'bi' else lang


def _pair(en, other):
    return en if (not other or other == en) else f'{en} / {other}'


def L(key, lang='en'):
    """Report label. Bilingual shows 'English / தமிழ்'."""
    en = LABELS['en'].get(key, key)
    if lang == 'bi':
        return _pair(en, LABELS['ta'].get(key))
    return LABELS.get(lang, LABELS['en']).get(key, en)


def Lv(key, lang='en'):
    """Label used inside a value: one language only (English when bilingual)."""
    return L(key, _base(lang))


def Lj(keys, lang='en'):
    """Several labels joined into one phrase, e.g. 'Current Dasa / நடப்பு தசை'."""
    if lang == 'bi':
        return _pair(' '.join(LABELS['en'][k] for k in keys), ' '.join(LABELS['ta'][k] for k in keys))
    return ' '.join(L(k, lang) for k in keys)


def varga_name(key, lang='en'):
    """'D9 Navamsa' in the report language (bilingual shows both names)."""
    en = VARGA_NAMES['en'][key]
    if lang == 'bi':
        return f"{key} {_pair(en, VARGA_NAMES['ta'][key])}"
    return f"{key} {VARGA_NAMES.get(lang, VARGA_NAMES['en'])[key]}"


def varga_purpose(key, lang='en'):
    """One-line description of what a divisional chart is used for."""
    en = VARGA_PURPOSE['en'][key]
    if lang == 'bi':
        return _pair(en, VARGA_PURPOSE['ta'][key])
    return VARGA_PURPOSE.get(lang, VARGA_PURPOSE['en'])[key]


def planet(name, lang='en'):
    en = PLANETS['en'].get(name, name)
    if lang == 'bi':
        return _pair(en, PLANETS['ta'].get(name))
    return PLANETS.get(lang, PLANETS['en']).get(name, en)


def planets(names, lang='en', sep=', '):
    return sep.join(planet(n, lang) for n in names) if names else '—'


def abbr(name, lang='en'):
    table = ABBR.get(_base(lang), ABBR['en'])
    return table.get(name, ABBR['en'].get(name, name[:2]))


def retro_mark(lang='en'):
    return RETRO_MARK.get(_base(lang), '(R)')


def rasi(idx, lang='en', short=False):
    table = RASIS_SHORT if short else RASIS
    en = table['en'][idx]
    if lang == 'bi':
        return en if short else _pair(en, table['ta'][idx])
    return table.get(lang, table['en'])[idx]


def nak(idx, lang='en'):
    en = NAKS['en'][idx]
    if lang == 'bi':
        return _pair(en, NAKS['ta'][idx])
    return NAKS.get(lang, NAKS['en'])[idx]


def weekday(name, lang='en'):
    if lang == 'bi':
        return _pair(name, WEEKDAYS['ta'].get(name))
    return WEEKDAYS.get(lang, WEEKDAYS['en']).get(name, name)


def tithi(name, lang='en'):
    if lang == 'bi':
        return _pair(name, TITHIS['ta'].get(name))
    return TITHIS.get(lang, {}).get(name, name)


def word(value, lang='en'):
    if not value:
        return ''
    if lang == 'bi':
        return _pair(value, WORDS['ta'].get(value))
    return WORDS.get(lang, {}).get(value, value)


def script_of(lang):
    """Font family key needed for a language."""
    return {'ta': 'tamil', 'bi': 'tamil', 'hi': 'devanagari', 'mr': 'devanagari',
            'te': 'telugu', 'kn': 'kannada', 'ml': 'malayalam', 'bn': 'bengali'}.get(lang, 'latin')


def bundle(lang='en'):
    """Every name and label for one language, for the web page to display results."""
    names = ['Lagna', 'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu', 'Mandi']
    return {
        'lang': lang,
        'planets': {n: planet(n, lang) for n in names},
        'abbr': {n: abbr(n, lang) for n in names + ['ALP']},
        'rasis': [rasi(i, lang) for i in range(12)],
        'naks': [nak(i, lang) for i in range(27)],
        'weekdays': {d: weekday(d, lang) for d in WEEKDAYS['en']},
        'tithis': {t: tithi(t, lang) for t in TITHIS['ta']},
        'words': {w: word(w, lang) for w in WORDS['ta']},
        'labels': {k: L(k, lang) for k in LABELS['en']},
        'rasis_short': [rasi(i, lang, short=True) for i in range(12)],
        'retro': retro_mark(lang),
    }


# ── MARRIAGE MATCHING ─────────────────────────────────────────────────────────
# Kept apart from LABELS on purpose: bundle() sends every key of LABELS to the
# web page with each horoscope, and that answer must stay as it is.
# All eight languages (te, kn, ml, bn and Marathi's own tables are below
# MATCH_TREES_TA). Values of the chart and timing rows (groups D and E) are
# sentences and stay in English in every language.

MATCH_LABELS = {
    'en': {
        'marriage': 'Marriage', 'marriage_title': 'Marriage Matching', 'boy': 'Boy', 'girl': 'Girl',
        'check': 'Check', 'result': 'Result', 'points': 'Points', 'note': 'Exception / Note',
        'exception': 'Exception', 'group': 'Group',
        'summary_of_results': 'Summary of Results', 'ten_poruthams': 'Ten poruthams',
        'ashtakoota_points': 'Ashtakoota points',
        'key_not_matched': 'Not matched among Rajju, Dinam, Ganam, Yoni, Rasi',
        'none': 'None', 'rule_based': 'Rule-based, not a prediction',
        'no_verdict': 'Counts of rule-based checks; no overall verdict is given.',
        'windows': 'Marriage Windows of Both (UTC)', 'from': 'From', 'to': 'To', 'days': 'Days',
        'boy_layers': "Boy's layers", 'girl_layers': "Girl's layers",
        'windows_shown': 'The first {n} of {total} spans are shown.',
        'windows_all_ai': 'All are on the sheet AI_MatchWindows.',
        'rules': 'Rules and Variants', 'sources': 'Where the Tables Were Checked',
        'not_included': 'Not Included', 'source': 'Details given', 'birth details': 'Birth details',
        'star only': 'Star only', 'rasi_lord': 'Rasi Lord', 'of': 'of',
        'matched': 'Matched', 'medium': 'Medium', 'not matched': 'Not matched',
        'not applicable': 'Not applicable', 'information': 'Information',
        'group_A': 'Ten Poruthams, with Nadi and Vriksha', 'group_B': 'Star Rules',
        'group_C': 'Ashtakoota (36 Points)', 'group_D': 'Chart Checks', 'group_E': 'Timing and KP',
        'settings': 'Settings', 'kuja_places': 'Places of Mars that count',
        'sandhi_months': 'Dasa sandhi: months', 'pada_unknown': 'pada not given',
        'milk tree': 'milk tree', 'not a milk tree': 'not a milk tree',
        'needs_birth_details': 'The birth details of both are needed',
    },
    'ta': {
        'marriage': 'திருமணப் பொருத்தம்', 'marriage_title': 'திருமணப் பொருத்தம்', 'boy': 'ஆண்', 'girl': 'பெண்',
        'check': 'பொருத்தம் / விதி', 'result': 'முடிவு', 'points': 'புள்ளி', 'note': 'விலக்கு / குறிப்பு',
        'exception': 'விலக்கு', 'group': 'பிரிவு',
        'summary_of_results': 'முடிவுகளின் சுருக்கம்', 'ten_poruthams': 'பத்துப் பொருத்தங்கள்',
        'ashtakoota_points': 'அஷ்டகூட புள்ளிகள்',
        'key_not_matched': 'ரஜ்ஜு, தினம், கணம், யோனி, ராசியில் இல்லாதவை',
        'none': 'இல்லை', 'rule_based': 'விதி அடிப்படையிலானது; பலன் கூறுவது அல்ல',
        'no_verdict': 'விதி அடிப்படையிலான ஆய்வுகளின் எண்ணிக்கை மட்டுமே; ஒட்டுமொத்த முடிவு கூறப்படவில்லை.',
        'windows': 'இருவரின் திருமண காலங்கள் (UTC)', 'from': 'தொடக்கம்', 'to': 'முடிவு', 'days': 'நாட்கள்',
        'boy_layers': 'ஆணின் அடுக்குகள்', 'girl_layers': 'பெண்ணின் அடுக்குகள்',
        'windows_shown': 'மொத்தம் {total} காலங்களில் முதல் {n} காட்டப்பட்டுள்ளன.',
        'windows_all_ai': 'அனைத்தும் AI_MatchWindows தாளில் உள்ளன.',
        'rules': 'விதிகளும் மாறுபாடுகளும்', 'sources': 'அட்டவணைகள் சரிபார்க்கப்பட்ட இடங்கள்',
        'not_included': 'சேர்க்கப்படாதவை', 'source': 'கொடுக்கப்பட்ட விவரம்', 'birth details': 'பிறப்பு விவரங்கள்',
        'star only': 'நட்சத்திரம் மட்டும்', 'rasi_lord': 'ராசி அதிபதி', 'of': '/',
        'matched': 'பொருத்தம் உண்டு', 'medium': 'மத்திமம்', 'not matched': 'பொருத்தம் இல்லை',
        'not applicable': 'இவ்விதி இல்லை', 'information': 'தகவல்',
        'group_A': 'பத்துப் பொருத்தங்கள் (நாடி, விருட்சம் உடன்)', 'group_B': 'நட்சத்திர விதிகள்',
        'group_C': 'அஷ்டகூடம் (36 புள்ளிகள்)', 'group_D': 'ஜாதக ஆய்வுகள்', 'group_E': 'கால ஆய்வு மற்றும் கே.பி.',
        'settings': 'அமைப்புகள்', 'kuja_places': 'செவ்வாய் தோஷத்திற்கான இடங்கள்',
        'sandhi_months': 'தசா சந்தி: மாதங்கள்', 'pada_unknown': 'பாதம் தரப்படவில்லை',
        'milk tree': 'பால் மரம்', 'not a milk tree': 'பால் இல்லா மரம்',
        'needs_birth_details': 'இருவரின் பிறப்பு விவரங்களும் தேவை',
    },
    'hi': {
        'marriage': 'विवाह मिलान', 'marriage_title': 'विवाह मिलान', 'boy': 'वर', 'girl': 'कन्या',
        'check': 'जाँच', 'result': 'परिणाम', 'points': 'अंक', 'note': 'अपवाद / टिप्पणी',
        'exception': 'अपवाद', 'group': 'समूह',
        'summary_of_results': 'परिणामों का सारांश', 'ten_poruthams': 'दस पोरुत्तम',
        'ashtakoota_points': 'अष्टकूट अंक',
        'key_not_matched': 'रज्जु, दिनम्, गणम्, योनि, राशि में जो नहीं मिले',
        'none': 'कोई नहीं', 'rule_based': 'नियम आधारित; भविष्यवाणी नहीं',
        'no_verdict': 'नियम आधारित जाँचों की गिनती मात्र; कोई समग्र निर्णय नहीं दिया गया है।',
        'windows': 'दोनों की विवाह अवधियाँ (UTC)', 'from': 'से', 'to': 'तक', 'days': 'दिन',
        'boy_layers': 'वर की परतें', 'girl_layers': 'कन्या की परतें',
        'windows_shown': 'कुल {total} अवधियों में से पहली {n} दिखाई गई हैं।',
        'windows_all_ai': 'सभी AI_MatchWindows शीट पर हैं।',
        'rules': 'नियम और भेद', 'sources': 'तालिकाएँ कहाँ जाँची गईं',
        'not_included': 'जो शामिल नहीं है', 'source': 'दिया गया विवरण', 'birth details': 'जन्म विवरण',
        'star only': 'केवल नक्षत्र', 'rasi_lord': 'राशि स्वामी', 'of': '/',
        'matched': 'मिलान है', 'medium': 'मध्यम', 'not matched': 'मिलान नहीं',
        'not applicable': 'लागू नहीं', 'information': 'जानकारी',
        'group_A': 'दस पोरुत्तम (नाड़ी और वृक्ष सहित)', 'group_B': 'नक्षत्र नियम',
        'group_C': 'अष्टकूट (36 अंक)', 'group_D': 'कुंडली जाँच', 'group_E': 'समय और केपी',
        'settings': 'सेटिंग', 'kuja_places': 'मंगल दोष के भाव',
        'sandhi_months': 'दशा संधि: माह', 'pada_unknown': 'पाद नहीं दिया गया',
        'milk tree': 'क्षीर वृक्ष', 'not a milk tree': 'क्षीर वृक्ष नहीं',
        'needs_birth_details': 'दोनों के जन्म विवरण चाहिए',
    },
}

# Names of the checks, by the key of the row (match_engine.CHECKS).
MATCH_CHECKS = {
    'ta': {
        'dinam': 'தினப் பொருத்தம்', 'ganam': 'கணப் பொருத்தம்', 'mahendram': 'மகேந்திரப் பொருத்தம்',
        'stree_deergham': 'ஸ்திரீ தீர்க்கப் பொருத்தம்', 'yoni': 'யோனிப் பொருத்தம்', 'rasi': 'ராசிப் பொருத்தம்',
        'rasi_adhipathi': 'ராசி அதிபதிப் பொருத்தம்', 'vasiyam': 'வசியப் பொருத்தம்', 'rajju': 'ரஜ்ஜுப் பொருத்தம்',
        'vedhai': 'வேதைப் பொருத்தம்', 'nadi': 'நாடிப் பொருத்தம்', 'vriksha': 'விருட்சப் பொருத்தம் (மரம்)',
        'tara_boy': 'ஆண் நட்சத்திரத்தின் தாரை', 'tara_girl': 'பெண் நட்சத்திரத்தின் தாரை',
        'vadha': 'வதை (7-வது நட்சத்திரம்)', 'vainasika': 'வைநாசிகம் (22-வது நட்சத்திரம்)',
        'vainasika_pada': 'வைநாசிக பாதம் (88-வது பாதம்)', 'star_27': '27-வது நட்சத்திரம்',
        'eka_nakshatra': 'ஏக நட்சத்திரம்', 'eka_rasi': 'ஏக ராசி',
        'ak_varna': 'வர்ணம் (1)', 'ak_vashya': 'வசியம் (2)', 'ak_tara': 'தாரை (3)', 'ak_yoni': 'யோனி (4)',
        'ak_graha_maitri': 'கிரக மைத்ரி (5)', 'ak_gana': 'கணம் (6)', 'ak_bhakoot': 'பகூடம் (7)', 'ak_nadi': 'நாடி (8)',
        'kuja_lagna': 'லக்னத்திலிருந்து செவ்வாய் தோஷம்', 'kuja_moon': 'சந்திரனிலிருந்து செவ்வாய் தோஷம்',
        'kuja_venus': 'சுக்கிரனிலிருந்து செவ்வாய் தோஷம்',
        'kuja_x_2nd': 'செவ்வாய் தோஷ விலக்கு: 2-ல் செவ்வாய், மிதுனம் அல்லது கன்னியில்',
        'kuja_x_12th': 'செவ்வாய் தோஷ விலக்கு: 12-ல் செவ்வாய், ரிஷபம் அல்லது துலாத்தில்',
        'kuja_x_4th': 'செவ்வாய் தோஷ விலக்கு: 4-ல் செவ்வாய், மேஷம் அல்லது விருச்சிகத்தில்',
        'kuja_x_7th': 'செவ்வாய் தோஷ விலக்கு: 7-ல் செவ்வாய், மகரம் அல்லது கடகத்தில்',
        'kuja_x_8th': 'செவ்வாய் தோஷ விலக்கு: 8-ல் செவ்வாய், தனுசு அல்லது மீனத்தில்',
        'kuja_x_sign': 'செவ்வாய் தோஷ விலக்கு: செவ்வாய் சிம்மம் அல்லது கும்பத்தில்',
        'kuja_x_joined': 'செவ்வாய் தோஷ விலக்கு: செவ்வாய் குரு அல்லது சந்திரனுடன் ஒரே ராசியில்',
        'kuja_balance': 'இருவருக்கும் செவ்வாய் தோஷம்',
        'kuja_balance_after': 'இருவருக்கும் செவ்வாய் தோஷம் (விலக்குகளுக்குப் பின்)',
        'sarpa': 'ராகு - கேது', 'kalathra_seventh': 'களத்திரம்: 7-ல் உள்ள கிரகங்கள்',
        'kalathra_lord': 'களத்திரம்: 7-ம் அதிபதி', 'kalathra_venus': 'களத்திரம்: சுக்கிரன்',
        'papa_count': 'பாப சாம்யம் (எண்ணிக்கை)', 'papa_weighted': 'பாப சாம்யம் (எடையிட்டது)',
        'punarpoo': 'புனர்பூ (சனி - சந்திரன்)', 'kala_sarpa': 'கால சர்ப்பம்',
        'lagna_position': 'இருவரின் லக்னம்', 'seventh_lords': '7-ம் அதிபதிகள்', 'navamsa': 'நவாம்சம் (D9)',
        'venus_mars': 'சுக்கிரன் - செவ்வாய் (இரு ஜாதகங்களிடையே)', 'fifth_house': '5-ம் வீடு மற்றும் குரு',
        'dasa_sandhi': 'தசா சந்தி', 'eka_dasa': 'இருவருக்கும் நடக்கும் தசைகள்',
        'kp_seventh': 'கே.பி.: 7-ம் பாவ முனையின் உப அதிபதி', 'marriage_windows': 'இருவரின் திருமண காலங்கள்',
    },
    'hi': {
        'dinam': 'दिनम्', 'ganam': 'गणम्', 'mahendram': 'माहेन्द्रम्', 'stree_deergham': 'स्त्री दीर्घम्',
        'yoni': 'योनि', 'rasi': 'राशि', 'rasi_adhipathi': 'राशि अधिपति', 'vasiyam': 'वश्यम्', 'rajju': 'रज्जु',
        'vedhai': 'वेध', 'nadi': 'नाड़ी', 'vriksha': 'वृक्ष',
        'tara_boy': 'वर के नक्षत्र की तारा', 'tara_girl': 'कन्या के नक्षत्र की तारा',
        'vadha': 'वध (7वाँ नक्षत्र)', 'vainasika': 'वैनाशिक (22वाँ नक्षत्र)',
        'vainasika_pada': 'वैनाशिक पाद (88वाँ पाद)', 'star_27': '27वाँ नक्षत्र',
        'eka_nakshatra': 'एक नक्षत्र', 'eka_rasi': 'एक राशि',
        'ak_varna': 'वर्ण (1)', 'ak_vashya': 'वश्य (2)', 'ak_tara': 'तारा (3)', 'ak_yoni': 'योनि (4)',
        'ak_graha_maitri': 'ग्रह मैत्री (5)', 'ak_gana': 'गण (6)', 'ak_bhakoot': 'भकूट (7)', 'ak_nadi': 'नाड़ी (8)',
        'kuja_lagna': 'लग्न से मंगल दोष', 'kuja_moon': 'चंद्र से मंगल दोष', 'kuja_venus': 'शुक्र से मंगल दोष',
        'kuja_x_2nd': 'मंगल दोष अपवाद: दूसरे भाव में मंगल, मिथुन या कन्या में',
        'kuja_x_12th': 'मंगल दोष अपवाद: बारहवें भाव में मंगल, वृष या तुला में',
        'kuja_x_4th': 'मंगल दोष अपवाद: चौथे भाव में मंगल, मेष या वृश्चिक में',
        'kuja_x_7th': 'मंगल दोष अपवाद: सातवें भाव में मंगल, मकर या कर्क में',
        'kuja_x_8th': 'मंगल दोष अपवाद: आठवें भाव में मंगल, धनु या मीन में',
        'kuja_x_sign': 'मंगल दोष अपवाद: मंगल सिंह या कुंभ में',
        'kuja_x_joined': 'मंगल दोष अपवाद: मंगल गुरु या चंद्र के साथ एक राशि में',
        'kuja_balance': 'दोनों कुंडलियों में मंगल दोष',
        'kuja_balance_after': 'दोनों कुंडलियों में मंगल दोष (अपवादों के बाद)',
        'sarpa': 'राहु - केतु', 'kalathra_seventh': 'कलत्र: सप्तम भाव के ग्रह',
        'kalathra_lord': 'कलत्र: सप्तमेश', 'kalathra_venus': 'कलत्र: शुक्र',
        'papa_count': 'पाप साम्य (गणना)', 'papa_weighted': 'पाप साम्य (भारित)',
        'punarpoo': 'पुनर्फू (शनि - चंद्र)', 'kala_sarpa': 'काल सर्प',
        'lagna_position': 'दोनों के लग्न', 'seventh_lords': 'सप्तमेश', 'navamsa': 'नवांश (D9)',
        'venus_mars': 'शुक्र - मंगल (दोनों कुंडलियों के बीच)', 'fifth_house': 'पंचम भाव और गुरु',
        'dasa_sandhi': 'दशा संधि', 'eka_dasa': 'साथ चलने वाली दशाएँ',
        'kp_seventh': 'केपी: सप्तम भाव संधि का उप स्वामी', 'marriage_windows': 'दोनों की विवाह अवधियाँ',
    },
}

# Single-word values of the star rows (groups A to C).
MATCH_WORDS = {
    'ta': {
        'Deva': 'தேவ கணம்', 'Manushya': 'மனுஷ கணம்', 'Rakshasa': 'ராட்சஸ கணம்',
        'Horse': 'குதிரை', 'Elephant': 'யானை', 'Sheep': 'ஆடு', 'Serpent': 'பாம்பு', 'Dog': 'நாய்', 'Cat': 'பூனை',
        'Rat': 'எலி', 'Cow': 'பசு', 'Buffalo': 'எருமை', 'Tiger': 'புலி', 'Deer': 'மான்', 'Monkey': 'குரங்கு',
        'Mongoose': 'கீரி', 'Lion': 'சிங்கம்',
        'Pada': 'பாத ரஜ்ஜு', 'Kati': 'தொடை ரஜ்ஜு', 'Nabhi': 'உதர ரஜ்ஜு', 'Kantha': 'கண்ட ரஜ்ஜு', 'Siro': 'சிரசு ரஜ்ஜு',
        'Aadi': 'ஆதி நாடி', 'Madhya': 'மத்திய நாடி', 'Antya': 'அந்திய நாடி',
        'Janma': 'ஜென்ம தாரை', 'Sampat': 'சம்பத்து', 'Vipat': 'விபத்து', 'Kshema': 'க்ஷேமம்', 'Pratyari': 'பிரத்யரி',
        'Sadhaka': 'சாதகம்', 'Vadha': 'வதை', 'Mitra': 'மைத்ரம்', 'Parama Mitra': 'பரம மைத்ரம்',
        'Brahmin': 'பிராமண வர்ணம்', 'Kshatriya': 'க்ஷத்திரிய வர்ணம்', 'Vaishya': 'வைசிய வர்ணம்',
        'Shudra': 'சூத்திர வர்ணம்',
        'Chatushpada': 'சதுஷ்பாதம்', 'Manava': 'மானவம்', 'Jalachara': 'ஜலசரம்', 'Vanachara': 'வனசரம்', 'Keeta': 'கீடம்',
    },
    'hi': {
        'Deva': 'देव गण', 'Manushya': 'मनुष्य गण', 'Rakshasa': 'राक्षस गण',
        'Horse': 'अश्व', 'Elephant': 'गज', 'Sheep': 'मेष (भेड़)', 'Serpent': 'सर्प', 'Dog': 'श्वान', 'Cat': 'मार्जार',
        'Rat': 'मूषक', 'Cow': 'गौ', 'Buffalo': 'महिष', 'Tiger': 'व्याघ्र', 'Deer': 'मृग', 'Monkey': 'वानर',
        'Mongoose': 'नकुल', 'Lion': 'सिंह',
        'Pada': 'पाद रज्जु', 'Kati': 'कटि रज्जु', 'Nabhi': 'नाभि रज्जु', 'Kantha': 'कंठ रज्जु', 'Siro': 'शिरो रज्जु',
        'Aadi': 'आदि नाड़ी', 'Madhya': 'मध्य नाड़ी', 'Antya': 'अंत्य नाड़ी',
        'Janma': 'जन्म तारा', 'Sampat': 'संपत', 'Vipat': 'विपत', 'Kshema': 'क्षेम', 'Pratyari': 'प्रत्यरि',
        'Sadhaka': 'साधक', 'Vadha': 'वध', 'Mitra': 'मित्र', 'Parama Mitra': 'परम मित्र',
        'Brahmin': 'ब्राह्मण वर्ण', 'Kshatriya': 'क्षत्रिय वर्ण', 'Vaishya': 'वैश्य वर्ण', 'Shudra': 'शूद्र वर्ण',
        'Chatushpada': 'चतुष्पद', 'Manava': 'मानव', 'Jalachara': 'जलचर', 'Vanachara': 'वनचर', 'Keeta': 'कीट',
    },
}

# The tree of each star in Tamil, by the name match_engine.TREE uses.
MATCH_TREES_TA = {
    'Etti': 'எட்டி', 'Nelli': 'நெல்லி', 'Athi': 'அத்தி', 'Naval': 'நாவல்', 'Karungali': 'கருங்காலி',
    'Sengarungali': 'செங்கருங்காலி', 'Moongil': 'மூங்கில்', 'Arasu': 'அரசு', 'Punnai': 'புன்னை', 'Aal': 'ஆல்',
    'Pala': 'பலா', 'Alari': 'அலரி', 'Velam': 'வேலம்', 'Vilvam': 'வில்வம்', 'Marutham': 'மருதம்', 'Vila': 'விளா',
    'Magizh': 'மகிழ்', 'Pirai': 'பிராய்', 'Maa': 'மா', 'Vanji': 'வஞ்சி', 'Erukku': 'எருக்கு', 'Vanni': 'வன்னி',
    'Kadambu': 'கடம்பு', 'Thema': 'தேமா', 'Vembu': 'வேம்பு', 'Iluppai': 'இலுப்பை',
}

# ── te, kn, ml, bn and Marathi's own marriage tables ─────────────────────────
MATCH_LABELS['te'] = {
    'marriage': 'వివాహ పొంతన', 'marriage_title': 'వివాహ పొంతన', 'boy': 'వరుడు', 'girl': 'వధువు',
    'check': 'పరిశీలన', 'result': 'ఫలితం', 'points': 'పాయింట్లు', 'note': 'మినహాయింపు / గమనిక',
    'exception': 'మినహాయింపు', 'group': 'విభాగం',
    'summary_of_results': 'ఫలితాల సారాంశం', 'ten_poruthams': 'పది పొంతనలు',
    'ashtakoota_points': 'అష్టకూట పాయింట్లు',
    'key_not_matched': 'రజ్జు, దినం, గణం, యోని, రాశిలో కుదరనివి',
    'none': 'ఏదీ లేదు', 'rule_based': 'నియమాల ఆధారంగా; ఫలజ్యోతిషం కాదు',
    'no_verdict': 'నియమాల పరిశీలనల లెక్క మాత్రమే; మొత్తం తీర్పు ఇవ్వబడలేదు.',
    'windows': 'ఇద్దరి వివాహ కాలాలు (UTC)', 'from': 'నుండి', 'to': 'వరకు', 'days': 'రోజులు',
    'boy_layers': 'వరుని పొరలు', 'girl_layers': 'వధువు పొరలు',
    'windows_shown': 'మొత్తం {total} కాలాల్లో మొదటి {n} చూపబడ్డాయి.',
    'windows_all_ai': 'అన్నీ AI_MatchWindows షీట్‌లో ఉన్నాయి.',
    'rules': 'నియమాలు మరియు భేదాలు', 'sources': 'పట్టికలు ఎక్కడ సరిచూశాం',
    'not_included': 'చేర్చనివి', 'source': 'ఇచ్చిన వివరాలు', 'birth details': 'జనన వివరాలు',
    'star only': 'నక్షత్రం మాత్రమే', 'rasi_lord': 'రాశి అధిపతి', 'of': '/',
    'matched': 'కుదిరింది', 'medium': 'మధ్యమం', 'not matched': 'కుదరలేదు',
    'not applicable': 'వర్తించదు', 'information': 'సమాచారం',
    'group_A': 'పది పొంతనలు (నాడి, వృక్షంతో)', 'group_B': 'నక్షత్ర నియమాలు',
    'group_C': 'అష్టకూటం (36 పాయింట్లు)', 'group_D': 'జాతక పరిశీలనలు', 'group_E': 'కాలం మరియు కేపీ',
    'settings': 'అమరికలు', 'kuja_places': 'కుజ దోషానికి లెక్కించే స్థానాలు',
    'sandhi_months': 'దశా సంధి: నెలలు', 'pada_unknown': 'పాదం ఇవ్వలేదు',
    'milk tree': 'క్షీర వృక్షం', 'not a milk tree': 'క్షీర వృక్షం కాదు',
    'needs_birth_details': 'ఇద్దరి జనన వివరాలు అవసరం',
}
MATCH_LABELS['kn'] = {
    'marriage': 'ವಿವಾಹ ಹೊಂದಾಣಿಕೆ', 'marriage_title': 'ವಿವಾಹ ಹೊಂದಾಣಿಕೆ', 'boy': 'ವರ', 'girl': 'ವಧು',
    'check': 'ಪರಿಶೀಲನೆ', 'result': 'ಫಲಿತಾಂಶ', 'points': 'ಅಂಕಗಳು', 'note': 'ವಿನಾಯಿತಿ / ಟಿಪ್ಪಣಿ',
    'exception': 'ವಿನಾಯಿತಿ', 'group': 'ವಿಭಾಗ',
    'summary_of_results': 'ಫಲಿತಾಂಶಗಳ ಸಾರಾಂಶ', 'ten_poruthams': 'ಹತ್ತು ಕೂಟಗಳು',
    'ashtakoota_points': 'ಅಷ್ಟಕೂಟ ಅಂಕಗಳು',
    'key_not_matched': 'ರಜ್ಜು, ದಿನ, ಗಣ, ಯೋನಿ, ರಾಶಿಯಲ್ಲಿ ಹೊಂದದವು',
    'none': 'ಯಾವುದೂ ಇಲ್ಲ', 'rule_based': 'ನಿಯಮ ಆಧಾರಿತ; ಭವಿಷ್ಯವಲ್ಲ',
    'no_verdict': 'ನಿಯಮ ಆಧಾರಿತ ಪರಿಶೀಲನೆಗಳ ಎಣಿಕೆ ಮಾತ್ರ; ಒಟ್ಟು ತೀರ್ಪು ನೀಡಿಲ್ಲ.',
    'windows': 'ಇಬ್ಬರ ವಿವಾಹ ಕಾಲಗಳು (UTC)', 'from': 'ಇಂದ', 'to': 'ವರೆಗೆ', 'days': 'ದಿನಗಳು',
    'boy_layers': 'ವರನ ಪದರಗಳು', 'girl_layers': 'ವಧುವಿನ ಪದರಗಳು',
    'windows_shown': 'ಒಟ್ಟು {total} ಕಾಲಗಳಲ್ಲಿ ಮೊದಲ {n} ತೋರಿಸಲಾಗಿದೆ.',
    'windows_all_ai': 'ಎಲ್ಲವೂ AI_MatchWindows ಶೀಟ್‌ನಲ್ಲಿವೆ.',
    'rules': 'ನಿಯಮಗಳು ಮತ್ತು ಭೇದಗಳು', 'sources': 'ಕೋಷ್ಟಕಗಳನ್ನು ಎಲ್ಲಿ ಪರಿಶೀಲಿಸಲಾಗಿದೆ',
    'not_included': 'ಸೇರಿಸದವು', 'source': 'ನೀಡಿದ ವಿವರ', 'birth details': 'ಜನನ ವಿವರಗಳು',
    'star only': 'ನಕ್ಷತ್ರ ಮಾತ್ರ', 'rasi_lord': 'ರಾಶಿ ಅಧಿಪತಿ', 'of': '/',
    'matched': 'ಹೊಂದುತ್ತದೆ', 'medium': 'ಮಧ್ಯಮ', 'not matched': 'ಹೊಂದುವುದಿಲ್ಲ',
    'not applicable': 'ಅನ್ವಯಿಸುವುದಿಲ್ಲ', 'information': 'ಮಾಹಿತಿ',
    'group_A': 'ಹತ್ತು ಕೂಟಗಳು (ನಾಡಿ, ವೃಕ್ಷ ಸಹಿತ)', 'group_B': 'ನಕ್ಷತ್ರ ನಿಯಮಗಳು',
    'group_C': 'ಅಷ್ಟಕೂಟ (36 ಅಂಕ)', 'group_D': 'ಜಾತಕ ಪರಿಶೀಲನೆಗಳು', 'group_E': 'ಕಾಲ ಮತ್ತು ಕೆಪಿ',
    'settings': 'ಸೆಟ್ಟಿಂಗ್‌ಗಳು', 'kuja_places': 'ಕುಜ ದೋಷಕ್ಕೆ ಎಣಿಸುವ ಸ್ಥಾನಗಳು',
    'sandhi_months': 'ದಶಾ ಸಂಧಿ: ತಿಂಗಳುಗಳು', 'pada_unknown': 'ಪಾದ ನೀಡಿಲ್ಲ',
    'milk tree': 'ಕ್ಷೀರ ವೃಕ್ಷ', 'not a milk tree': 'ಕ್ಷೀರ ವೃಕ್ಷವಲ್ಲ',
    'needs_birth_details': 'ಇಬ್ಬರ ಜನನ ವಿವರಗಳು ಬೇಕು',
}
MATCH_LABELS['ml'] = {
    'marriage': 'വിവാഹ പൊരുത്തം', 'marriage_title': 'വിവാഹ പൊരുത്തം', 'boy': 'വരൻ', 'girl': 'വധു',
    'check': 'പരിശോധന', 'result': 'ഫലം', 'points': 'പോയിന്റ്', 'note': 'ഇളവ് / കുറിപ്പ്',
    'exception': 'ഇളവ്', 'group': 'വിഭാഗം',
    'summary_of_results': 'ഫലങ്ങളുടെ സംഗ്രഹം', 'ten_poruthams': 'പത്ത് പൊരുത്തങ്ങൾ',
    'ashtakoota_points': 'അഷ്ടകൂട പോയിന്റുകൾ',
    'key_not_matched': 'രജ്ജു, ദിനം, ഗണം, യോനി, രാശി എന്നിവയിൽ ചേരാത്തവ',
    'none': 'ഒന്നുമില്ല', 'rule_based': 'നിയമാധിഷ്ഠിതം; ഫലപ്രവചനമല്ല',
    'no_verdict': 'നിയമാധിഷ്ഠിത പരിശോധനകളുടെ എണ്ണം മാത്രം; മൊത്തം തീർപ്പ് നൽകിയിട്ടില്ല.',
    'windows': 'ഇരുവരുടെയും വിവാഹ കാലങ്ങൾ (UTC)', 'from': 'മുതൽ', 'to': 'വരെ', 'days': 'ദിവസം',
    'boy_layers': 'വരന്റെ തലങ്ങൾ', 'girl_layers': 'വധുവിന്റെ തലങ്ങൾ',
    'windows_shown': 'ആകെ {total} കാലങ്ങളിൽ ആദ്യത്തെ {n} കാണിച്ചിരിക്കുന്നു.',
    'windows_all_ai': 'എല്ലാം AI_MatchWindows ഷീറ്റിലുണ്ട്.',
    'rules': 'നിയമങ്ങളും ഭേദങ്ങളും', 'sources': 'പട്ടികകൾ പരിശോധിച്ച ഇടങ്ങൾ',
    'not_included': 'ഉൾപ്പെടുത്താത്തവ', 'source': 'നൽകിയ വിവരം', 'birth details': 'ജനന വിവരങ്ങൾ',
    'star only': 'നക്ഷത്രം മാത്രം', 'rasi_lord': 'രാശ്യാധിപൻ', 'of': '/',
    'matched': 'ചേരുന്നു', 'medium': 'മധ്യമം', 'not matched': 'ചേരുന്നില്ല',
    'not applicable': 'ബാധകമല്ല', 'information': 'വിവരം',
    'group_A': 'പത്ത് പൊരുത്തങ്ങൾ (നാഡി, വൃക്ഷം ഉൾപ്പെടെ)', 'group_B': 'നക്ഷത്ര നിയമങ്ങൾ',
    'group_C': 'അഷ്ടകൂടം (36 പോയിന്റ്)', 'group_D': 'ജാതക പരിശോധനകൾ', 'group_E': 'കാലവും കെപിയും',
    'settings': 'ക്രമീകരണങ്ങൾ', 'kuja_places': 'ചൊവ്വാദോഷത്തിന് കണക്കാക്കുന്ന സ്ഥാനങ്ങൾ',
    'sandhi_months': 'ദശാസന്ധി: മാസങ്ങൾ', 'pada_unknown': 'പാദം നൽകിയിട്ടില്ല',
    'milk tree': 'ക്ഷീര വൃക്ഷം', 'not a milk tree': 'ക്ഷീര വൃക്ഷമല്ല',
    'needs_birth_details': 'ഇരുവരുടെയും ജനന വിവരങ്ങൾ ആവശ്യമാണ്',
}
MATCH_LABELS['bn'] = {
    'marriage': 'বিবাহ মিলন', 'marriage_title': 'বিবাহ মিলন', 'boy': 'পাত্র', 'girl': 'পাত্রী',
    'check': 'যাচাই', 'result': 'ফলাফল', 'points': 'পয়েন্ট', 'note': 'ব্যতিক্রম / টীকা',
    'exception': 'ব্যতিক্রম', 'group': 'বিভাগ',
    'summary_of_results': 'ফলাফলের সারাংশ', 'ten_poruthams': 'দশটি পোরুথম',
    'ashtakoota_points': 'অষ্টকূট পয়েন্ট',
    'key_not_matched': 'রজ্জু, দিনম, গণ, যোনি, রাশির মধ্যে যা মেলেনি',
    'none': 'কিছুই না', 'rule_based': 'নিয়মভিত্তিক; ভবিষ্যদ্বাণী নয়',
    'no_verdict': 'শুধু নিয়মভিত্তিক যাচাইয়ের গণনা; কোনো সামগ্রিক রায় দেওয়া হয়নি।',
    'windows': 'দুজনের বিবাহ কাল (UTC)', 'from': 'থেকে', 'to': 'পর্যন্ত', 'days': 'দিন',
    'boy_layers': 'পাত্রের স্তর', 'girl_layers': 'পাত্রীর স্তর',
    'windows_shown': 'মোট {total}টি কালের মধ্যে প্রথম {n}টি দেখানো হয়েছে।',
    'windows_all_ai': 'সবগুলি AI_MatchWindows শিটে আছে।',
    'rules': 'নিয়ম ও ভেদ', 'sources': 'সারণি কোথায় যাচাই করা হয়েছে',
    'not_included': 'যা অন্তর্ভুক্ত নয়', 'source': 'দেওয়া বিবরণ', 'birth details': 'জন্ম বিবরণ',
    'star only': 'শুধু নক্ষত্র', 'rasi_lord': 'রাশি অধিপতি', 'of': '/',
    'matched': 'মিলেছে', 'medium': 'মধ্যম', 'not matched': 'মেলেনি',
    'not applicable': 'প্রযোজ্য নয়', 'information': 'তথ্য',
    'group_A': 'দশটি পোরুথম (নাড়ী ও বৃক্ষসহ)', 'group_B': 'নক্ষত্রের নিয়ম',
    'group_C': 'অষ্টকূট (36 পয়েন্ট)', 'group_D': 'কুণ্ডলী যাচাই', 'group_E': 'সময় ও কেপি',
    'settings': 'সেটিংস', 'kuja_places': 'মঙ্গল দোষের জন্য গণ্য ভাব',
    'sandhi_months': 'দশা সন্ধি: মাস', 'pada_unknown': 'পাদ দেওয়া হয়নি',
    'milk tree': 'ক্ষীর বৃক্ষ', 'not a milk tree': 'ক্ষীর বৃক্ষ নয়',
    'needs_birth_details': 'দুজনেরই জন্ম বিবরণ প্রয়োজন',
}
MATCH_LABELS['mr'] = dict(MATCH_LABELS['hi'])
MATCH_LABELS['mr'].update({
    'marriage': 'विवाह जुळणी', 'marriage_title': 'विवाह जुळणी', 'boy': 'वर', 'girl': 'वधू',
    'check': 'तपासणी', 'result': 'निकाल', 'note': 'अपवाद / टीप', 'group': 'गट',
    'summary_of_results': 'निकालांचा सारांश', 'ten_poruthams': 'दहा पोरुत्तम',
    'key_not_matched': 'रज्जू, दिनम्, गणम्, योनी, राशी यांपैकी न जुळलेले',
    'none': 'काहीही नाही', 'rule_based': 'नियमांवर आधारित; भविष्य नव्हे',
    'no_verdict': 'नियमाधारित तपासण्यांची फक्त गणना; एकूण निर्णय दिलेला नाही.',
    'windows': 'दोघांचे विवाह काळ (UTC)', 'from': 'पासून', 'to': 'पर्यंत', 'days': 'दिवस',
    'boy_layers': 'वराचे स्तर', 'girl_layers': 'वधूचे स्तर',
    'windows_shown': 'एकूण {total} काळांपैकी पहिले {n} दाखवले आहेत.',
    'windows_all_ai': 'सर्व AI_MatchWindows शीटवर आहेत.',
    'rules': 'नियम आणि भेद', 'sources': 'तक्ते कुठे तपासले',
    'not_included': 'समाविष्ट नाही', 'source': 'दिलेला तपशील', 'birth details': 'जन्म तपशील',
    'star only': 'फक्त नक्षत्र', 'rasi_lord': 'राशी स्वामी',
    'matched': 'जुळते', 'not matched': 'जुळत नाही', 'not applicable': 'लागू नाही', 'information': 'माहिती',
    'group_A': 'दहा पोरुत्तम (नाडी आणि वृक्षासह)', 'group_B': 'नक्षत्र नियम',
    'group_C': 'अष्टकूट (36 गुण)', 'group_D': 'कुंडली तपासणी', 'group_E': 'काळ आणि केपी',
    'settings': 'सेटिंग्ज', 'kuja_places': 'मंगळ दोषासाठी मोजली जाणारी स्थाने',
    'sandhi_months': 'दशा संधी: महिने', 'pada_unknown': 'चरण दिलेले नाही',
    'milk tree': 'क्षीर वृक्ष', 'not a milk tree': 'क्षीर वृक्ष नाही',
    'needs_birth_details': 'दोघांचे जन्म तपशील आवश्यक',
    'ashtakoota_points': 'अष्टकूट गुण', 'points': 'गुण',
})


MATCH_CHECKS['te'] = {
    'dinam': 'దిన పొంతన', 'ganam': 'గణ పొంతన', 'mahendram': 'మాహేంద్ర పొంతన', 'stree_deergham': 'స్త్రీ దీర్ఘ పొంతన',
    'yoni': 'యోని పొంతన', 'rasi': 'రాశి పొంతన', 'rasi_adhipathi': 'రాశ్యాధిపతి పొంతన', 'vasiyam': 'వశ్య పొంతన',
    'rajju': 'రజ్జు పొంతన', 'vedhai': 'వేధ పొంతన', 'nadi': 'నాడి పొంతన', 'vriksha': 'వృక్ష పొంతన',
    'tara_boy': 'వరుని నక్షత్ర తార', 'tara_girl': 'వధువు నక్షత్ర తార',
    'vadha': 'వధ (7వ నక్షత్రం)', 'vainasika': 'వైనాశిక (22వ నక్షత్రం)', 'vainasika_pada': 'వైనాశిక పాదం (88వ పాదం)',
    'star_27': '27వ నక్షత్రం', 'eka_nakshatra': 'ఏక నక్షత్రం', 'eka_rasi': 'ఏక రాశి',
    'ak_varna': 'వర్ణం (1)', 'ak_vashya': 'వశ్యం (2)', 'ak_tara': 'తార (3)', 'ak_yoni': 'యోని (4)',
    'ak_graha_maitri': 'గ్రహ మైత్రి (5)', 'ak_gana': 'గణం (6)', 'ak_bhakoot': 'భకూటం (7)', 'ak_nadi': 'నాడి (8)',
    'kuja_lagna': 'లగ్నం నుండి కుజ దోషం', 'kuja_moon': 'చంద్రుని నుండి కుజ దోషం', 'kuja_venus': 'శుక్రుని నుండి కుజ దోషం',
    'kuja_x_2nd': 'కుజ దోష మినహాయింపు: 2వ భావంలో కుజుడు, మిథునం లేదా కన్యలో',
    'kuja_x_12th': 'కుజ దోష మినహాయింపు: 12వ భావంలో కుజుడు, వృషభం లేదా తులలో',
    'kuja_x_4th': 'కుజ దోష మినహాయింపు: 4వ భావంలో కుజుడు, మేషం లేదా వృశ్చికంలో',
    'kuja_x_7th': 'కుజ దోష మినహాయింపు: 7వ భావంలో కుజుడు, మకరం లేదా కర్కాటకంలో',
    'kuja_x_8th': 'కుజ దోష మినహాయింపు: 8వ భావంలో కుజుడు, ధనుస్సు లేదా మీనంలో',
    'kuja_x_sign': 'కుజ దోష మినహాయింపు: కుజుడు సింహం లేదా కుంభంలో',
    'kuja_x_joined': 'కుజ దోష మినహాయింపు: కుజుడు గురువు లేదా చంద్రునితో ఒకే రాశిలో',
    'kuja_balance': 'ఇద్దరికీ కుజ దోషం', 'kuja_balance_after': 'ఇద్దరికీ కుజ దోషం (మినహాయింపుల తర్వాత)',
    'sarpa': 'రాహువు - కేతువు', 'kalathra_seventh': 'కళత్రం: 7వ భావ గ్రహాలు',
    'kalathra_lord': 'కళత్రం: సప్తమాధిపతి', 'kalathra_venus': 'కళత్రం: శుక్రుడు',
    'papa_count': 'పాప సామ్యం (లెక్క)', 'papa_weighted': 'పాప సామ్యం (బరువుతో)',
    'punarpoo': 'పునర్ఫూ (శని - చంద్రుడు)', 'kala_sarpa': 'కాల సర్పం',
    'lagna_position': 'ఇద్దరి లగ్నాలు', 'seventh_lords': 'సప్తమాధిపతులు', 'navamsa': 'నవాంశ (D9)',
    'venus_mars': 'శుక్రుడు - కుజుడు (రెండు జాతకాల మధ్య)', 'fifth_house': '5వ భావం మరియు గురువు',
    'dasa_sandhi': 'దశా సంధి', 'eka_dasa': 'ఇద్దరికీ ఒకేసారి నడిచే దశలు',
    'kp_seventh': 'కేపీ: 7వ భావ సంధి ఉప అధిపతి', 'marriage_windows': 'ఇద్దరి వివాహ కాలాలు',
}
MATCH_CHECKS['kn'] = {
    'dinam': 'ದಿನ ಕೂಟ', 'ganam': 'ಗಣ ಕೂಟ', 'mahendram': 'ಮಾಹೇಂದ್ರ ಕೂಟ', 'stree_deergham': 'ಸ್ತ್ರೀ ದೀರ್ಘ ಕೂಟ',
    'yoni': 'ಯೋನಿ ಕೂಟ', 'rasi': 'ರಾಶಿ ಕೂಟ', 'rasi_adhipathi': 'ರಾಶ್ಯಾಧಿಪತಿ ಕೂಟ', 'vasiyam': 'ವಶ್ಯ ಕೂಟ',
    'rajju': 'ರಜ್ಜು ಕೂಟ', 'vedhai': 'ವೇಧ ಕೂಟ', 'nadi': 'ನಾಡಿ ಕೂಟ', 'vriksha': 'ವೃಕ್ಷ ಕೂಟ',
    'tara_boy': 'ವರನ ನಕ್ಷತ್ರದ ತಾರಾ', 'tara_girl': 'ವಧುವಿನ ನಕ್ಷತ್ರದ ತಾರಾ',
    'vadha': 'ವಧ (7ನೇ ನಕ್ಷತ್ರ)', 'vainasika': 'ವೈನಾಶಿಕ (22ನೇ ನಕ್ಷತ್ರ)', 'vainasika_pada': 'ವೈನಾಶಿಕ ಪಾದ (88ನೇ ಪಾದ)',
    'star_27': '27ನೇ ನಕ್ಷತ್ರ', 'eka_nakshatra': 'ಏಕ ನಕ್ಷತ್ರ', 'eka_rasi': 'ಏಕ ರಾಶಿ',
    'ak_varna': 'ವರ್ಣ (1)', 'ak_vashya': 'ವಶ್ಯ (2)', 'ak_tara': 'ತಾರಾ (3)', 'ak_yoni': 'ಯೋನಿ (4)',
    'ak_graha_maitri': 'ಗ್ರಹ ಮೈತ್ರಿ (5)', 'ak_gana': 'ಗಣ (6)', 'ak_bhakoot': 'ಭಕೂಟ (7)', 'ak_nadi': 'ನಾಡಿ (8)',
    'kuja_lagna': 'ಲಗ್ನದಿಂದ ಕುಜ ದೋಷ', 'kuja_moon': 'ಚಂದ್ರನಿಂದ ಕುಜ ದೋಷ', 'kuja_venus': 'ಶುಕ್ರನಿಂದ ಕುಜ ದೋಷ',
    'kuja_x_2nd': 'ಕುಜ ದೋಷ ವಿನಾಯಿತಿ: 2ನೇ ಭಾವದಲ್ಲಿ ಕುಜ, ಮಿಥುನ ಅಥವಾ ಕನ್ಯಾದಲ್ಲಿ',
    'kuja_x_12th': 'ಕುಜ ದೋಷ ವಿನಾಯಿತಿ: 12ನೇ ಭಾವದಲ್ಲಿ ಕುಜ, ವೃಷಭ ಅಥವಾ ತುಲಾದಲ್ಲಿ',
    'kuja_x_4th': 'ಕುಜ ದೋಷ ವಿನಾಯಿತಿ: 4ನೇ ಭಾವದಲ್ಲಿ ಕುಜ, ಮೇಷ ಅಥವಾ ವೃಶ್ಚಿಕದಲ್ಲಿ',
    'kuja_x_7th': 'ಕುಜ ದೋಷ ವಿನಾಯಿತಿ: 7ನೇ ಭಾವದಲ್ಲಿ ಕುಜ, ಮಕರ ಅಥವಾ ಕರ್ಕಾಟಕದಲ್ಲಿ',
    'kuja_x_8th': 'ಕುಜ ದೋಷ ವಿನಾಯಿತಿ: 8ನೇ ಭಾವದಲ್ಲಿ ಕುಜ, ಧನು ಅಥವಾ ಮೀನದಲ್ಲಿ',
    'kuja_x_sign': 'ಕುಜ ದೋಷ ವಿನಾಯಿತಿ: ಕುಜ ಸಿಂಹ ಅಥವಾ ಕುಂಭದಲ್ಲಿ',
    'kuja_x_joined': 'ಕುಜ ದೋಷ ವಿನಾಯಿತಿ: ಕುಜ ಗುರು ಅಥವಾ ಚಂದ್ರನೊಂದಿಗೆ ಒಂದೇ ರಾಶಿಯಲ್ಲಿ',
    'kuja_balance': 'ಇಬ್ಬರಿಗೂ ಕುಜ ದೋಷ', 'kuja_balance_after': 'ಇಬ್ಬರಿಗೂ ಕುಜ ದೋಷ (ವಿನಾಯಿತಿಗಳ ನಂತರ)',
    'sarpa': 'ರಾಹು - ಕೇತು', 'kalathra_seventh': 'ಕಳತ್ರ: 7ನೇ ಭಾವದ ಗ್ರಹಗಳು',
    'kalathra_lord': 'ಕಳತ್ರ: ಸಪ್ತಮಾಧಿಪತಿ', 'kalathra_venus': 'ಕಳತ್ರ: ಶುಕ್ರ',
    'papa_count': 'ಪಾಪ ಸಾಮ್ಯ (ಎಣಿಕೆ)', 'papa_weighted': 'ಪಾಪ ಸಾಮ್ಯ (ತೂಕದೊಂದಿಗೆ)',
    'punarpoo': 'ಪುನರ್ಫೂ (ಶನಿ - ಚಂದ್ರ)', 'kala_sarpa': 'ಕಾಲ ಸರ್ಪ',
    'lagna_position': 'ಇಬ್ಬರ ಲಗ್ನಗಳು', 'seventh_lords': 'ಸಪ್ತಮಾಧಿಪತಿಗಳು', 'navamsa': 'ನವಾಂಶ (D9)',
    'venus_mars': 'ಶುಕ್ರ - ಕುಜ (ಎರಡು ಜಾತಕಗಳ ನಡುವೆ)', 'fifth_house': '5ನೇ ಭಾವ ಮತ್ತು ಗುರು',
    'dasa_sandhi': 'ದಶಾ ಸಂಧಿ', 'eka_dasa': 'ಇಬ್ಬರಿಗೂ ಒಟ್ಟಿಗೆ ನಡೆಯುವ ದಶೆಗಳು',
    'kp_seventh': 'ಕೆಪಿ: 7ನೇ ಭಾವ ಸಂಧಿಯ ಉಪ ಅಧಿಪತಿ', 'marriage_windows': 'ಇಬ್ಬರ ವಿವಾಹ ಕಾಲಗಳು',
}
MATCH_CHECKS['ml'] = {
    'dinam': 'ദിനപ്പൊരുത്തം', 'ganam': 'ഗണപ്പൊരുത്തം', 'mahendram': 'മാഹേന്ദ്രപ്പൊരുത്തം', 'stree_deergham': 'സ്ത്രീദീർഘപ്പൊരുത്തം',
    'yoni': 'യോനിപ്പൊരുത്തം', 'rasi': 'രാശിപ്പൊരുത്തം', 'rasi_adhipathi': 'രാശ്യാധിപപ്പൊരുത്തം', 'vasiyam': 'വശ്യപ്പൊരുത്തം',
    'rajju': 'രജ്ജുപ്പൊരുത്തം', 'vedhai': 'വേധപ്പൊരുത്തം', 'nadi': 'നാഡിപ്പൊരുത്തം', 'vriksha': 'വൃക്ഷപ്പൊരുത്തം',
    'tara_boy': 'വരന്റെ നക്ഷത്രത്തിന്റെ താര', 'tara_girl': 'വധുവിന്റെ നക്ഷത്രത്തിന്റെ താര',
    'vadha': 'വധം (7-ാം നക്ഷത്രം)', 'vainasika': 'വൈനാശികം (22-ാം നക്ഷത്രം)', 'vainasika_pada': 'വൈനാശിക പാദം (88-ാം പാദം)',
    'star_27': '27-ാം നക്ഷത്രം', 'eka_nakshatra': 'ഏക നക്ഷത്രം', 'eka_rasi': 'ഏക രാശി',
    'ak_varna': 'വർണ്ണം (1)', 'ak_vashya': 'വശ്യം (2)', 'ak_tara': 'താര (3)', 'ak_yoni': 'യോനി (4)',
    'ak_graha_maitri': 'ഗ്രഹമൈത്രി (5)', 'ak_gana': 'ഗണം (6)', 'ak_bhakoot': 'ഭകൂടം (7)', 'ak_nadi': 'നാഡി (8)',
    'kuja_lagna': 'ലഗ്നത്തിൽ നിന്ന് ചൊവ്വാദോഷം', 'kuja_moon': 'ചന്ദ്രനിൽ നിന്ന് ചൊവ്വാദോഷം', 'kuja_venus': 'ശുക്രനിൽ നിന്ന് ചൊവ്വാദോഷം',
    'kuja_x_2nd': 'ചൊവ്വാദോഷ ഇളവ്: 2-ൽ ചൊവ്വ, മിഥുനത്തിലോ കന്നിയിലോ',
    'kuja_x_12th': 'ചൊവ്വാദോഷ ഇളവ്: 12-ൽ ചൊവ്വ, ഇടവത്തിലോ തുലാത്തിലോ',
    'kuja_x_4th': 'ചൊവ്വാദോഷ ഇളവ്: 4-ൽ ചൊവ്വ, മേടത്തിലോ വൃശ്ചികത്തിലോ',
    'kuja_x_7th': 'ചൊവ്വാദോഷ ഇളവ്: 7-ൽ ചൊവ്വ, മകരത്തിലോ കർക്കടകത്തിലോ',
    'kuja_x_8th': 'ചൊവ്വാദോഷ ഇളവ്: 8-ൽ ചൊവ്വ, ധനുവിലോ മീനത്തിലോ',
    'kuja_x_sign': 'ചൊവ്വാദോഷ ഇളവ്: ചൊവ്വ ചിങ്ങത്തിലോ കുംഭത്തിലോ',
    'kuja_x_joined': 'ചൊവ്വാദോഷ ഇളവ്: ചൊവ്വ വ്യാഴത്തോടോ ചന്ദ്രനോടോ ഒരേ രാശിയിൽ',
    'kuja_balance': 'ഇരുവർക്കും ചൊവ്വാദോഷം', 'kuja_balance_after': 'ഇരുവർക്കും ചൊവ്വാദോഷം (ഇളവുകൾക്ക് ശേഷം)',
    'sarpa': 'രാഹു - കേതു', 'kalathra_seventh': 'കളത്രം: 7-ലെ ഗ്രഹങ്ങൾ',
    'kalathra_lord': 'കളത്രം: 7-ാം ഭാവാധിപൻ', 'kalathra_venus': 'കളത്രം: ശുക്രൻ',
    'papa_count': 'പാപസാമ്യം (എണ്ണം)', 'papa_weighted': 'പാപസാമ്യം (തൂക്കം)',
    'punarpoo': 'പുനർഫൂ (ശനി - ചന്ദ്രൻ)', 'kala_sarpa': 'കാലസർപ്പം',
    'lagna_position': 'ഇരുവരുടെയും ലഗ്നം', 'seventh_lords': '7-ാം ഭാവാധിപന്മാർ', 'navamsa': 'നവാംശം (D9)',
    'venus_mars': 'ശുക്രൻ - ചൊവ്വ (രണ്ട് ജാതകങ്ങൾ തമ്മിൽ)', 'fifth_house': '5-ാം ഭാവവും വ്യാഴവും',
    'dasa_sandhi': 'ദശാസന്ധി', 'eka_dasa': 'ഇരുവർക്കും ഒരേ സമയം നടക്കുന്ന ദശകൾ',
    'kp_seventh': 'കെപി: 7-ാം ഭാവസന്ധിയുടെ ഉപാധിപൻ', 'marriage_windows': 'ഇരുവരുടെയും വിവാഹ കാലങ്ങൾ',
}
MATCH_CHECKS['bn'] = {
    'dinam': 'দিনম', 'ganam': 'গণ', 'mahendram': 'মাহেন্দ্র', 'stree_deergham': 'স্ত্রী দীর্ঘ',
    'yoni': 'যোনি', 'rasi': 'রাশি', 'rasi_adhipathi': 'রাশি অধিপতি', 'vasiyam': 'বশ্য',
    'rajju': 'রজ্জু', 'vedhai': 'বেধ', 'nadi': 'নাড়ী', 'vriksha': 'বৃক্ষ',
    'tara_boy': 'পাত্রের নক্ষত্রের তারা', 'tara_girl': 'পাত্রীর নক্ষত্রের তারা',
    'vadha': 'বধ (7ম নক্ষত্র)', 'vainasika': 'বৈনাশিক (22তম নক্ষত্র)', 'vainasika_pada': 'বৈনাশিক পাদ (88তম পাদ)',
    'star_27': '27তম নক্ষত্র', 'eka_nakshatra': 'এক নক্ষত্র', 'eka_rasi': 'এক রাশি',
    'ak_varna': 'বর্ণ (1)', 'ak_vashya': 'বশ্য (2)', 'ak_tara': 'তারা (3)', 'ak_yoni': 'যোনি (4)',
    'ak_graha_maitri': 'গ্রহ মৈত্রী (5)', 'ak_gana': 'গণ (6)', 'ak_bhakoot': 'ভকূট (7)', 'ak_nadi': 'নাড়ী (8)',
    'kuja_lagna': 'লগ্ন থেকে মঙ্গল দোষ', 'kuja_moon': 'চন্দ্র থেকে মঙ্গল দোষ', 'kuja_venus': 'শুক্র থেকে মঙ্গল দোষ',
    'kuja_x_2nd': 'মঙ্গল দোষের ব্যতিক্রম: দ্বিতীয় ভাবে মঙ্গল, মিথুন বা কন্যায়',
    'kuja_x_12th': 'মঙ্গল দোষের ব্যতিক্রম: দ্বাদশ ভাবে মঙ্গল, বৃষ বা তুলায়',
    'kuja_x_4th': 'মঙ্গল দোষের ব্যতিক্রম: চতুর্থ ভাবে মঙ্গল, মেষ বা বৃশ্চিকে',
    'kuja_x_7th': 'মঙ্গল দোষের ব্যতিক্রম: সপ্তম ভাবে মঙ্গল, মকর বা কর্কটে',
    'kuja_x_8th': 'মঙ্গল দোষের ব্যতিক্রম: অষ্টম ভাবে মঙ্গল, ধনু বা মীনে',
    'kuja_x_sign': 'মঙ্গল দোষের ব্যতিক্রম: মঙ্গল সিংহ বা কুম্ভে',
    'kuja_x_joined': 'মঙ্গল দোষের ব্যতিক্রম: মঙ্গল বৃহস্পতি বা চন্দ্রের সঙ্গে একই রাশিতে',
    'kuja_balance': 'দুজনেরই মঙ্গল দোষ', 'kuja_balance_after': 'দুজনেরই মঙ্গল দোষ (ব্যতিক্রমের পরে)',
    'sarpa': 'রাহু - কেতু', 'kalathra_seventh': 'কলত্র: সপ্তম ভাবের গ্রহ',
    'kalathra_lord': 'কলত্র: সপ্তমেশ', 'kalathra_venus': 'কলত্র: শুক্র',
    'papa_count': 'পাপ সাম্য (গণনা)', 'papa_weighted': 'পাপ সাম্য (ভারযুক্ত)',
    'punarpoo': 'পুনর্ফু (শনি - চন্দ্র)', 'kala_sarpa': 'কাল সর্প',
    'lagna_position': 'দুজনের লগ্ন', 'seventh_lords': 'সপ্তমেশ', 'navamsa': 'নবাংশ (D9)',
    'venus_mars': 'শুক্র - মঙ্গল (দুই কুণ্ডলীর মধ্যে)', 'fifth_house': 'পঞ্চম ভাব ও বৃহস্পতি',
    'dasa_sandhi': 'দশা সন্ধি', 'eka_dasa': 'দুজনের একসঙ্গে চলা দশা',
    'kp_seventh': 'কেপি: সপ্তম ভাব সন্ধির উপ অধিপতি', 'marriage_windows': 'দুজনের বিবাহ কাল',
}
MATCH_CHECKS['mr'] = dict(MATCH_CHECKS['hi'])
MATCH_CHECKS['mr'].update({
    'rajju': 'रज्जू', 'nadi': 'नाडी', 'rasi': 'राशी', 'rasi_adhipathi': 'राशी अधिपती',
    'tara_boy': 'वराच्या नक्षत्राची तारा', 'tara_girl': 'वधूच्या नक्षत्राची तारा',
    'vadha': 'वध (7 वे नक्षत्र)', 'vainasika': 'वैनाशिक (22 वे नक्षत्र)', 'vainasika_pada': 'वैनाशिक चरण (88 वे चरण)',
    'star_27': '27 वे नक्षत्र', 'eka_rasi': 'एक राशी', 'ak_nadi': 'नाडी (8)',
    'kuja_lagna': 'लग्नापासून मंगळ दोष', 'kuja_moon': 'चंद्रापासून मंगळ दोष', 'kuja_venus': 'शुक्रापासून मंगळ दोष',
    'kuja_x_2nd': 'मंगळ दोष अपवाद: दुसऱ्या भावात मंगळ, मिथुन किंवा कन्येत',
    'kuja_x_12th': 'मंगळ दोष अपवाद: बाराव्या भावात मंगळ, वृषभ किंवा तुळेत',
    'kuja_x_4th': 'मंगळ दोष अपवाद: चौथ्या भावात मंगळ, मेष किंवा वृश्चिकेत',
    'kuja_x_7th': 'मंगळ दोष अपवाद: सातव्या भावात मंगळ, मकर किंवा कर्केत',
    'kuja_x_8th': 'मंगळ दोष अपवाद: आठव्या भावात मंगळ, धनु किंवा मीनेत',
    'kuja_x_sign': 'मंगळ दोष अपवाद: मंगळ सिंह किंवा कुंभेत',
    'kuja_x_joined': 'मंगळ दोष अपवाद: मंगळ गुरू किंवा चंद्रासोबत एकाच राशीत',
    'kuja_balance': 'दोघांनाही मंगळ दोष', 'kuja_balance_after': 'दोघांनाही मंगळ दोष (अपवादांनंतर)',
    'sarpa': 'राहू - केतू', 'kalathra_seventh': 'कलत्र: सप्तम भावातील ग्रह',
    'papa_count': 'पाप साम्य (संख्या)', 'papa_weighted': 'पाप साम्य (भारित)',
    'punarpoo': 'पुनर्फू (शनी - चंद्र)', 'lagna_position': 'दोघांचे लग्न',
    'venus_mars': 'शुक्र - मंगळ (दोन कुंडल्यांमध्ये)', 'fifth_house': 'पंचम भाव आणि गुरू',
    'eka_dasa': 'दोघांच्या एकाच वेळी चालणाऱ्या दशा', 'kp_seventh': 'केपी: सप्तम भाव संधीचा उप स्वामी',
    'marriage_windows': 'दोघांचे विवाह काळ',
})

MATCH_WORDS['te'] = {
    'Deva': 'దేవ గణం', 'Manushya': 'మనుష్య గణం', 'Rakshasa': 'రాక్షస గణం',
    'Horse': 'గుర్రం', 'Elephant': 'ఏనుగు', 'Sheep': 'గొర్రె', 'Serpent': 'పాము', 'Dog': 'కుక్క', 'Cat': 'పిల్లి',
    'Rat': 'ఎలుక', 'Cow': 'ఆవు', 'Buffalo': 'గేదె', 'Tiger': 'పులి', 'Deer': 'జింక', 'Monkey': 'కోతి',
    'Mongoose': 'ముంగిస', 'Lion': 'సింహం',
    'Pada': 'పాద రజ్జు', 'Kati': 'కటి రజ్జు', 'Nabhi': 'నాభి రజ్జు', 'Kantha': 'కంఠ రజ్జు', 'Siro': 'శిరో రజ్జు',
    'Aadi': 'ఆది నాడి', 'Madhya': 'మధ్య నాడి', 'Antya': 'అంత్య నాడి',
    'Janma': 'జన్మ తార', 'Sampat': 'సంపత్', 'Vipat': 'విపత్', 'Kshema': 'క్షేమ', 'Pratyari': 'ప్రత్యరి',
    'Sadhaka': 'సాధక', 'Vadha': 'వధ', 'Mitra': 'మిత్ర', 'Parama Mitra': 'పరమ మిత్ర',
    'Brahmin': 'బ్రాహ్మణ వర్ణం', 'Kshatriya': 'క్షత్రియ వర్ణం', 'Vaishya': 'వైశ్య వర్ణం', 'Shudra': 'శూద్ర వర్ణం',
    'Chatushpada': 'చతుష్పాద', 'Manava': 'మానవ', 'Jalachara': 'జలచర', 'Vanachara': 'వనచర', 'Keeta': 'కీట',
}
MATCH_WORDS['kn'] = {
    'Deva': 'ದೇವ ಗಣ', 'Manushya': 'ಮನುಷ್ಯ ಗಣ', 'Rakshasa': 'ರಾಕ್ಷಸ ಗಣ',
    'Horse': 'ಕುದುರೆ', 'Elephant': 'ಆನೆ', 'Sheep': 'ಕುರಿ', 'Serpent': 'ಹಾವು', 'Dog': 'ನಾಯಿ', 'Cat': 'ಬೆಕ್ಕು',
    'Rat': 'ಇಲಿ', 'Cow': 'ಹಸು', 'Buffalo': 'ಎಮ್ಮೆ', 'Tiger': 'ಹುಲಿ', 'Deer': 'ಜಿಂಕೆ', 'Monkey': 'ಕೋತಿ',
    'Mongoose': 'ಮುಂಗುಸಿ', 'Lion': 'ಸಿಂಹ',
    'Pada': 'ಪಾದ ರಜ್ಜು', 'Kati': 'ಕಟಿ ರಜ್ಜು', 'Nabhi': 'ನಾಭಿ ರಜ್ಜು', 'Kantha': 'ಕಂಠ ರಜ್ಜು', 'Siro': 'ಶಿರೋ ರಜ್ಜು',
    'Aadi': 'ಆದಿ ನಾಡಿ', 'Madhya': 'ಮಧ್ಯ ನಾಡಿ', 'Antya': 'ಅಂತ್ಯ ನಾಡಿ',
    'Janma': 'ಜನ್ಮ ತಾರಾ', 'Sampat': 'ಸಂಪತ್', 'Vipat': 'ವಿಪತ್', 'Kshema': 'ಕ್ಷೇಮ', 'Pratyari': 'ಪ್ರತ್ಯರಿ',
    'Sadhaka': 'ಸಾಧಕ', 'Vadha': 'ವಧ', 'Mitra': 'ಮಿತ್ರ', 'Parama Mitra': 'ಪರಮ ಮಿತ್ರ',
    'Brahmin': 'ಬ್ರಾಹ್ಮಣ ವರ್ಣ', 'Kshatriya': 'ಕ್ಷತ್ರಿಯ ವರ್ಣ', 'Vaishya': 'ವೈಶ್ಯ ವರ್ಣ', 'Shudra': 'ಶೂದ್ರ ವರ್ಣ',
    'Chatushpada': 'ಚತುಷ್ಪಾದ', 'Manava': 'ಮಾನವ', 'Jalachara': 'ಜಲಚರ', 'Vanachara': 'ವನಚರ', 'Keeta': 'ಕೀಟ',
}
MATCH_WORDS['ml'] = {
    'Deva': 'ദേവഗണം', 'Manushya': 'മനുഷ്യഗണം', 'Rakshasa': 'അസുരഗണം',
    'Horse': 'കുതിര', 'Elephant': 'ആന', 'Sheep': 'ആട്', 'Serpent': 'പാമ്പ്', 'Dog': 'നായ', 'Cat': 'പൂച്ച',
    'Rat': 'എലി', 'Cow': 'പശു', 'Buffalo': 'പോത്ത്', 'Tiger': 'പുലി', 'Deer': 'മാൻ', 'Monkey': 'കുരങ്ങ്',
    'Mongoose': 'കീരി', 'Lion': 'സിംഹം',
    'Pada': 'പാദ രജ്ജു', 'Kati': 'കടി രജ്ജു', 'Nabhi': 'നാഭി രജ്ജു', 'Kantha': 'കണ്ഠ രജ്ജു', 'Siro': 'ശിരോ രജ്ജു',
    'Aadi': 'ആദി നാഡി', 'Madhya': 'മധ്യ നാഡി', 'Antya': 'അന്ത്യ നാഡി',
    'Janma': 'ജന്മ താര', 'Sampat': 'സമ്പത്ത്', 'Vipat': 'വിപത്ത്', 'Kshema': 'ക്ഷേമം', 'Pratyari': 'പ്രത്യരി',
    'Sadhaka': 'സാധകം', 'Vadha': 'വധം', 'Mitra': 'മിത്രം', 'Parama Mitra': 'പരമമിത്രം',
    'Brahmin': 'ബ്രാഹ്മണ വർണ്ണം', 'Kshatriya': 'ക്ഷത്രിയ വർണ്ണം', 'Vaishya': 'വൈശ്യ വർണ്ണം', 'Shudra': 'ശൂദ്ര വർണ്ണം',
    'Chatushpada': 'ചതുഷ്പാദം', 'Manava': 'മാനവം', 'Jalachara': 'ജലചരം', 'Vanachara': 'വനചരം', 'Keeta': 'കീടം',
}
MATCH_WORDS['bn'] = {
    'Deva': 'দেব গণ', 'Manushya': 'মনুষ্য গণ', 'Rakshasa': 'রাক্ষস গণ',
    'Horse': 'অশ্ব', 'Elephant': 'হাতি', 'Sheep': 'মেষ (ভেড়া)', 'Serpent': 'সর্প', 'Dog': 'কুকুর', 'Cat': 'বিড়াল',
    'Rat': 'ইঁদুর', 'Cow': 'গরু', 'Buffalo': 'মহিষ', 'Tiger': 'বাঘ', 'Deer': 'হরিণ', 'Monkey': 'বানর',
    'Mongoose': 'নকুল', 'Lion': 'সিংহ',
    'Pada': 'পাদ রজ্জু', 'Kati': 'কটি রজ্জু', 'Nabhi': 'নাভি রজ্জু', 'Kantha': 'কণ্ঠ রজ্জু', 'Siro': 'শিরো রজ্জু',
    'Aadi': 'আদি নাড়ী', 'Madhya': 'মধ্য নাড়ী', 'Antya': 'অন্ত্য নাড়ী',
    'Janma': 'জন্ম তারা', 'Sampat': 'সম্পৎ', 'Vipat': 'বিপৎ', 'Kshema': 'ক্ষেম', 'Pratyari': 'প্রত্যরি',
    'Sadhaka': 'সাধক', 'Vadha': 'বধ', 'Mitra': 'মিত্র', 'Parama Mitra': 'পরম মিত্র',
    'Brahmin': 'ব্রাহ্মণ বর্ণ', 'Kshatriya': 'ক্ষত্রিয় বর্ণ', 'Vaishya': 'বৈশ্য বর্ণ', 'Shudra': 'শূদ্র বর্ণ',
    'Chatushpada': 'চতুষ্পদ', 'Manava': 'মানব', 'Jalachara': 'জলচর', 'Vanachara': 'বনচর', 'Keeta': 'কীট',
}
MATCH_WORDS['mr'] = dict(MATCH_WORDS['hi'])
MATCH_WORDS['mr'].update({'Aadi': 'आदी नाडी', 'Madhya': 'मध्य नाडी', 'Antya': 'अंत्य नाडी',
                          'Pada': 'पाद रज्जू', 'Kati': 'कटी रज्जू', 'Nabhi': 'नाभी रज्जू', 'Kantha': 'कंठ रज्जू',
                          'Siro': 'शिरो रज्जू', 'Sheep': 'मेष (मेंढी)'})


def ML(key, lang='en'):
    """Label of the marriage pages. Bilingual shows 'English / தமிழ்'."""
    en = MATCH_LABELS['en'].get(key, key)
    if lang == 'bi':
        return _pair(en, MATCH_LABELS['ta'].get(key))
    return MATCH_LABELS.get(lang, MATCH_LABELS['en']).get(key, en)


def match_check(key, name, lang='en'):
    """Name of a check: name is the English one from match_engine."""
    if lang == 'bi':
        return _pair(name, MATCH_CHECKS['ta'].get(key))
    return MATCH_CHECKS.get(lang, {}).get(key, name)


def match_value(text, lang='en'):
    """
    A value of a matching row in the report language. Star, rasi and planet
    names and the single-word values of the star rows are translated; any
    other text (the sentences of the chart and timing rows) is returned as it
    is. Bilingual reports keep the English value, as the charts do.
    """
    if text is None or text == '':
        return '—'
    text = str(text)
    if lang in ('en', 'bi'):
        return text
    words = MATCH_WORDS.get(lang, {})
    if text in words:
        return words[text]
    if text in NAKS['en']:
        return nak(NAKS['en'].index(text), lang)
    star, sep, pada = text.rpartition(' pada ')
    if sep and star in NAKS['en'] and pada in ('1', '2', '3', '4'):
        return f"{nak(NAKS['en'].index(star), lang)} - {Lv('pada', lang)} {pada}"
    if text in RASIS['en']:
        return rasi(RASIS['en'].index(text), lang)
    if text in PLANETS['en']:
        return planet(text, lang)
    tree, sep, kind = text.partition(' (')
    if sep and kind.rstrip(')') in ('milk tree', 'not a milk tree') and tree in MATCH_TREES_TA:
        name = MATCH_TREES_TA[tree] if lang == 'ta' else tree
        return f"{name} ({ML(kind.rstrip(')'), lang)})"
    return text


# ── SAPTARISHI: era year, gotra lineage, Arundhati note ───────────────────────
# Kept apart from LABELS for the same reason as MATCH_LABELS. Unlike the other
# report labels these exist in all eight languages; 'bi' pairs English with
# Tamil as everywhere else. Translations other than Tamil and Hindi are
# machine-assisted and need review by a native reader.

SAPTA_LABELS = {
    'en': {
        'samvat': 'Saptarishi Samvat',
        'samvat_note': 'Saptarishi Samvat (Laukika era) is a traditional era in which the Saptarishis are said to '
                       'stay 100 years in each nakshatra; it is a calendar convention, not an astronomical position.',
        'gotra_section': 'Gotra & Rishi Lineage', 'gotra': 'Gotra', 'rishi': 'Root Rishi',
        'mandala': 'Saptarishi Mandala', 'not_in_list': 'Not in the lookup table',
        'lineage_note': 'Lineage as commonly listed; traditions differ between families and regions.',
        'same_gotra': 'Same gotra', 'info_only': 'For information only; it does not change any porutham result.',
        'yes': 'Yes', 'no': 'No', 'not_given': 'Not given',
        'boy': 'Boy', 'girl': 'Girl',
        'arundhati_title': 'Arundhati Darshan',
        'arundhati_text': 'In traditional weddings, the couple is shown the star pair Vasishtha and Arundhati in the '
                          'Saptarishi Mandala, the seven bright stars known as the Big Dipper. Arundhati, the faint '
                          'star Alcor, stays always beside Vasishtha, the star Mizar, and stands for devotion and '
                          'lifelong companionship. To find them, look north on a clear evening: in the curved handle '
                          'of the great ladle of seven stars, the middle star has a faint companion right beside it.',
    },
    'ta': {
        'samvat': 'சப்தரிஷி சம்வத்',
        'samvat_note': 'சப்தரிஷி சம்வத் (லௌகிக சகம்) ஒரு பாரம்பரிய ஆண்டுக் கணக்கு; சப்தரிஷிகள் ஒவ்வொரு '
                       'நட்சத்திரத்திலும் 100 ஆண்டுகள் தங்குவதாகக் கூறப்படுகிறது. இது ஒரு நாட்காட்டி மரபு, வானியல் நிலை அல்ல.',
        'gotra_section': 'கோத்திரமும் ரிஷி மரபும்', 'gotra': 'கோத்திரம்', 'rishi': 'மூல ரிஷி',
        'mandala': 'சப்தரிஷி மண்டலம்', 'not_in_list': 'பட்டியலில் இல்லை',
        'lineage_note': 'பொதுவாகக் குறிப்பிடப்படும் மரபு; குடும்பங்கள், பகுதிகளிடையே மரபுகள் வேறுபடலாம்.',
        'same_gotra': 'ஒரே கோத்திரம்', 'info_only': 'தகவலுக்காக மட்டும்; எந்தப் பொருத்த முடிவையும் இது மாற்றாது.',
        'yes': 'ஆம்', 'no': 'இல்லை', 'not_given': 'தரப்படவில்லை',
        'boy': 'ஆண்', 'girl': 'பெண்',
        'arundhati_title': 'அருந்ததி தரிசனம்',
        'arundhati_text': 'பாரம்பரியத் திருமணங்களில், சப்தரிஷி மண்டலத்தில் உள்ள வசிஷ்டர் – அருந்ததி நட்சத்திர இணையை '
                          'மணமக்களுக்குக் காட்டுவது வழக்கம். மங்கலான அருந்ததி நட்சத்திரம் (Alcor) எப்போதும் '
                          'வசிஷ்டரின் (Mizar) அருகிலேயே இருக்கிறது; அது பக்திக்கும் வாழ்நாள் முழுவதுமான துணைக்கும் '
                          'அடையாளம். காண்பதற்கு, தெளிவான மாலை வானில் வடக்கே பாருங்கள்: ஏழு நட்சத்திரங்களால் ஆன '
                          'பெரிய அகப்பை வடிவத்தின் வளைந்த கைப்பிடியில், நடு நட்சத்திரத்தின் அருகே ஒரு மங்கலான துணை '
                          'நட்சத்திரம் தெரியும்.',
    },
    'hi': {
        'samvat': 'सप्तर्षि संवत्',
        'samvat_note': 'सप्तर्षि संवत् (लौकिक संवत्) एक पारंपरिक संवत् है, जिसमें सप्तर्षियों का प्रत्येक नक्षत्र में '
                       '100 वर्ष रहना माना जाता है; यह एक पंचांग परंपरा है, खगोलीय स्थिति नहीं।',
        'gotra_section': 'गोत्र और ऋषि परंपरा', 'gotra': 'गोत्र', 'rishi': 'मूल ऋषि',
        'mandala': 'सप्तर्षि मंडल', 'not_in_list': 'सूची में नहीं',
        'lineage_note': 'सामान्यतः बताई जाने वाली परंपरा; परिवारों और क्षेत्रों में परंपराएँ भिन्न हो सकती हैं।',
        'same_gotra': 'समान गोत्र', 'info_only': 'केवल जानकारी के लिए; इससे किसी भी पोरुत्तम परिणाम में बदलाव नहीं होता।',
        'yes': 'हाँ', 'no': 'नहीं', 'not_given': 'नहीं दिया गया',
        'boy': 'वर', 'girl': 'कन्या',
        'arundhati_title': 'अरुंधती दर्शन',
        'arundhati_text': 'पारंपरिक विवाहों में वर-वधू को सप्तर्षि मंडल का वशिष्ठ और अरुंधती तारा-युगल दिखाया जाता '
                          'है। मंद तारा अरुंधती (Alcor) सदा वशिष्ठ (Mizar) के पास रहती हैं और निष्ठा तथा आजीवन साथ '
                          'का प्रतीक हैं। इन्हें देखने के लिए साफ़ शाम को उत्तर दिशा में देखें: सात तारों से बनी बड़ी '
                          'कलछी के मुड़े हुए हत्थे में बीच वाले तारे के ठीक पास एक मंद साथी तारा दिखता है।',
    },
    'te': {
        'samvat': 'సప్తర్షి సంవత్',
        'samvat_note': 'సప్తర్షి సంవత్ (లౌకిక శకం) ఒక సంప్రదాయ శకం; సప్తర్షులు ప్రతి నక్షత్రంలో 100 సంవత్సరాలు '
                       'ఉంటారని చెప్పబడుతుంది. ఇది పంచాంగ సంప్రదాయం మాత్రమే, ఖగోళ స్థానం కాదు.',
        'gotra_section': 'గోత్రం మరియు ఋషి వంశం', 'gotra': 'గోత్రం', 'rishi': 'మూల ఋషి',
        'mandala': 'సప్తర్షి మండలం', 'not_in_list': 'జాబితాలో లేదు',
        'lineage_note': 'సాధారణంగా చెప్పబడే వంశం; కుటుంబాలు, ప్రాంతాల మధ్య సంప్రదాయాలు మారవచ్చు.',
        'same_gotra': 'ఒకే గోత్రం', 'info_only': 'సమాచారం కోసం మాత్రమే; ఇది ఏ పొరుత్తం ఫలితాన్నీ మార్చదు.',
        'yes': 'అవును', 'no': 'కాదు', 'not_given': 'ఇవ్వలేదు',
        'boy': 'వరుడు', 'girl': 'వధువు',
        'arundhati_title': 'అరుంధతీ దర్శనం',
        'arundhati_text': 'సంప్రదాయ వివాహాలలో, సప్తర్షి మండలంలోని వసిష్ఠుడు – అరుంధతి నక్షత్ర జంటను వధూవరులకు '
                          'చూపిస్తారు. మసకగా కనిపించే అరుంధతి (Alcor) ఎల్లప్పుడూ వసిష్ఠుని (Mizar) పక్కనే ఉంటుంది; '
                          'ఇది భక్తికి, జీవితాంతం తోడుకు సంకేతం. చూడాలంటే, నిర్మలమైన సాయంత్రం ఉత్తర దిశగా చూడండి: '
                          'ఏడు నక్షత్రాలతో ఏర్పడిన పెద్ద గరిటె ఆకారపు వంపు పిడిలో, మధ్య నక్షత్రం పక్కనే ఒక మసక తోడు '
                          'నక్షత్రం కనిపిస్తుంది.',
    },
    'kn': {
        'samvat': 'ಸಪ್ತರ್ಷಿ ಸಂವತ್',
        'samvat_note': 'ಸಪ್ತರ್ಷಿ ಸಂವತ್ (ಲೌಕಿಕ ಶಕ) ಒಂದು ಸಾಂಪ್ರದಾಯಿಕ ಶಕ; ಸಪ್ತರ್ಷಿಗಳು ಪ್ರತಿ ನಕ್ಷತ್ರದಲ್ಲಿ 100 ವರ್ಷ '
                       'ಇರುತ್ತಾರೆ ಎಂದು ಹೇಳಲಾಗುತ್ತದೆ. ಇದು ಪಂಚಾಂಗದ ಸಂಪ್ರದಾಯ, ಖಗೋಳದ ಸ್ಥಾನವಲ್ಲ.',
        'gotra_section': 'ಗೋತ್ರ ಮತ್ತು ಋಷಿ ಪರಂಪರೆ', 'gotra': 'ಗೋತ್ರ', 'rishi': 'ಮೂಲ ಋಷಿ',
        'mandala': 'ಸಪ್ತರ್ಷಿ ಮಂಡಲ', 'not_in_list': 'ಪಟ್ಟಿಯಲ್ಲಿ ಇಲ್ಲ',
        'lineage_note': 'ಸಾಮಾನ್ಯವಾಗಿ ಹೇಳಲಾಗುವ ಪರಂಪರೆ; ಕುಟುಂಬ, ಪ್ರದೇಶಗಳ ನಡುವೆ ಸಂಪ್ರದಾಯ ಬೇರೆಯಾಗಿರಬಹುದು.',
        'same_gotra': 'ಒಂದೇ ಗೋತ್ರ', 'info_only': 'ಮಾಹಿತಿಗಾಗಿ ಮಾತ್ರ; ಇದು ಯಾವುದೇ ಪೊರುತ್ತಂ ಫಲಿತಾಂಶವನ್ನು ಬದಲಿಸುವುದಿಲ್ಲ.',
        'yes': 'ಹೌದು', 'no': 'ಇಲ್ಲ', 'not_given': 'ನೀಡಿಲ್ಲ',
        'boy': 'ವರ', 'girl': 'ವಧು',
        'arundhati_title': 'ಅರುಂಧತಿ ದರ್ಶನ',
        'arundhati_text': 'ಸಾಂಪ್ರದಾಯಿಕ ವಿವಾಹಗಳಲ್ಲಿ, ಸಪ್ತರ್ಷಿ ಮಂಡಲದ ವಸಿಷ್ಠ – ಅರುಂಧತಿ ನಕ್ಷತ್ರ ಜೋಡಿಯನ್ನು ವಧೂವರರಿಗೆ '
                          'ತೋರಿಸಲಾಗುತ್ತದೆ. ಮಂದವಾಗಿ ಕಾಣುವ ಅರುಂಧತಿ (Alcor) ಸದಾ ವಸಿಷ್ಠರ (Mizar) ಪಕ್ಕದಲ್ಲೇ ಇರುತ್ತಾಳೆ; '
                          'ಇದು ಭಕ್ತಿ ಮತ್ತು ಜೀವನಪೂರ್ತಿ ಜೊತೆಯ ಸಂಕೇತ. ಕಾಣಲು, ಶುಭ್ರ ಸಂಜೆ ಉತ್ತರ ದಿಕ್ಕಿಗೆ ನೋಡಿ: ಏಳು '
                          'ನಕ್ಷತ್ರಗಳ ದೊಡ್ಡ ಸೌಟಿನ ಬಾಗಿದ ಹಿಡಿಯಲ್ಲಿ, ನಡುವಿನ ನಕ್ಷತ್ರದ ಪಕ್ಕದಲ್ಲೇ ಒಂದು ಮಂದ ಜೊತೆ ನಕ್ಷತ್ರ '
                          'ಕಾಣುತ್ತದೆ.',
    },
    'ml': {
        'samvat': 'സപ്തർഷി സംവത്',
        'samvat_note': 'സപ്തർഷി സംവത് (ലൗകിക വർഷം) ഒരു പരമ്പരാഗത കാലഗണനയാണ്; സപ്തർഷികൾ ഓരോ നക്ഷത്രത്തിലും 100 '
                       'വർഷം നിൽക്കുന്നു എന്നാണ് സങ്കല്പം. ഇത് ഒരു പഞ്ചാംഗ സമ്പ്രദായമാണ്, ജ്യോതിശാസ്ത്രപരമായ സ്ഥാനമല്ല.',
        'gotra_section': 'ഗോത്രവും ഋഷി പരമ്പരയും', 'gotra': 'ഗോത്രം', 'rishi': 'മൂല ഋഷി',
        'mandala': 'സപ്തർഷി മണ്ഡലം', 'not_in_list': 'പട്ടികയിൽ ഇല്ല',
        'lineage_note': 'സാധാരണയായി പറയപ്പെടുന്ന പരമ്പര; കുടുംബങ്ങൾക്കും പ്രദേശങ്ങൾക്കും ഇടയിൽ സമ്പ്രദായങ്ങൾ വ്യത്യാസപ്പെടാം.',
        'same_gotra': 'ഒരേ ഗോത്രം', 'info_only': 'വിവരത്തിനു മാത്രം; ഇത് ഒരു പൊരുത്ത ഫലത്തെയും മാറ്റുന്നില്ല.',
        'yes': 'അതെ', 'no': 'അല്ല', 'not_given': 'നൽകിയിട്ടില്ല',
        'boy': 'വരൻ', 'girl': 'വധു',
        'arundhati_title': 'അരുന്ധതീ ദർശനം',
        'arundhati_text': 'പരമ്പരാഗത വിവാഹങ്ങളിൽ, സപ്തർഷി മണ്ഡലത്തിലെ വസിഷ്ഠൻ – അരുന്ധതി നക്ഷത്രജോഡിയെ '
                          'വധൂവരന്മാർക്ക് കാണിക്കാറുണ്ട്. മങ്ങിയ നക്ഷത്രമായ അരുന്ധതി (Alcor) എപ്പോഴും വസിഷ്ഠന്റെ '
                          '(Mizar) അരികിൽ നിൽക്കുന്നു; ഭക്തിയുടെയും ആജീവനാന്ത കൂട്ടിന്റെയും പ്രതീകമാണ് ഇത്. കാണാൻ, '
                          'തെളിഞ്ഞ സന്ധ്യയിൽ വടക്കോട്ട് നോക്കുക: ഏഴു നക്ഷത്രങ്ങൾ ചേർന്ന വലിയ തവിയുടെ വളഞ്ഞ പിടിയിൽ, '
                          'നടുവിലെ നക്ഷത്രത്തിന് തൊട്ടരികിൽ ഒരു മങ്ങിയ കൂട്ടുനക്ഷത്രം കാണാം.',
    },
    'mr': {
        'samvat': 'सप्तर्षी संवत',
        'samvat_note': 'सप्तर्षी संवत (लौकिक संवत) ही एक पारंपरिक कालगणना आहे; सप्तर्षी प्रत्येक नक्षत्रात 100 वर्षे '
                       'राहतात असे मानले जाते. ही पंचांगाची परंपरा आहे, खगोलीय स्थिती नव्हे.',
        'gotra_section': 'गोत्र आणि ऋषी परंपरा', 'gotra': 'गोत्र', 'rishi': 'मूळ ऋषी',
        'mandala': 'सप्तर्षी मंडळ', 'not_in_list': 'यादीत नाही',
        'lineage_note': 'सामान्यतः सांगितली जाणारी परंपरा; कुटुंबे आणि प्रदेशांनुसार परंपरा वेगळ्या असू शकतात.',
        'same_gotra': 'समान गोत्र', 'info_only': 'केवळ माहितीसाठी; याने कोणत्याही पोरुत्तम निकालात बदल होत नाही.',
        'yes': 'होय', 'no': 'नाही', 'not_given': 'दिलेले नाही',
        'boy': 'वर', 'girl': 'वधू',
        'arundhati_title': 'अरुंधती दर्शन',
        'arundhati_text': 'पारंपरिक विवाहांमध्ये वधू-वरांना सप्तर्षी मंडळातील वसिष्ठ आणि अरुंधती ही तारका-जोडी '
                          'दाखवली जाते. मंद तारका अरुंधती (Alcor) सदैव वसिष्ठांच्या (Mizar) शेजारी असते; ती निष्ठा आणि '
                          'आयुष्यभराच्या सोबतीचे प्रतीक आहे. पाहण्यासाठी स्वच्छ संध्याकाळी उत्तरेकडे पाहा: सात '
                          'ताऱ्यांच्या मोठ्या पळीच्या वाकलेल्या दांड्यात मधल्या ताऱ्याच्या अगदी शेजारी एक मंद सोबती '
                          'तारा दिसतो.',
    },
    'bn': {
        'samvat': 'সপ্তর্ষি সংবৎ',
        'samvat_note': 'সপ্তর্ষি সংবৎ (লৌকিক অব্দ) একটি প্রথাগত অব্দ; বলা হয় সপ্তর্ষিরা প্রতিটি নক্ষত্রে 100 বছর '
                       'থাকেন। এটি পঞ্জিকার একটি প্রথা, জ্যোতির্বৈজ্ঞানিক অবস্থান নয়।',
        'gotra_section': 'গোত্র ও ঋষি পরম্পরা', 'gotra': 'গোত্র', 'rishi': 'মূল ঋষি',
        'mandala': 'সপ্তর্ষিমণ্ডল', 'not_in_list': 'তালিকায় নেই',
        'lineage_note': 'সাধারণত যে পরম্পরা বলা হয়; পরিবার ও অঞ্চলভেদে প্রথা আলাদা হতে পারে।',
        'same_gotra': 'একই গোত্র', 'info_only': 'কেবল তথ্যের জন্য; এটি কোনো পোরুত্তম ফল বদলায় না।',
        'yes': 'হ্যাঁ', 'no': 'না', 'not_given': 'দেওয়া হয়নি',
        'boy': 'বর', 'girl': 'কনে',
        'arundhati_title': 'অরুন্ধতী দর্শন',
        'arundhati_text': 'প্রথাগত বিবাহে বর-কনেকে সপ্তর্ষিমণ্ডলের বশিষ্ঠ ও অরুন্ধতী তারাযুগল দেখানো হয়। ক্ষীণ তারা '
                          'অরুন্ধতী (Alcor) সর্বদা বশিষ্ঠের (Mizar) পাশে থাকেন; তিনি নিষ্ঠা ও আজীবন সাহচর্যের প্রতীক। '
                          'দেখতে হলে পরিষ্কার সন্ধ্যায় উত্তর দিকে তাকান: সাতটি তারার বড় হাতার বাঁকানো হাতলে মাঝের '
                          'তারাটির ঠিক পাশে একটি ক্ষীণ সঙ্গী তারা দেখা যায়।',
    },
}

# Root rishis, their line, and the two that are also stars of the Mandala.
RISHI_NAMES = {
    'en': {'kashyapa': 'Kashyapa', 'atri': 'Atri', 'vasishtha': 'Vasishtha', 'vishvamitra': 'Vishvamitra',
           'gautama': 'Gautama', 'jamadagni': 'Jamadagni', 'bharadvaja': 'Bharadvaja', 'agastya': 'Agastya',
           'bhrigu': 'Bhrigu line', 'angirasa': 'Angirasa line', 'mizar': 'Mizar', 'megrez': 'Megrez'},
    'ta': {'kashyapa': 'காசியபர்', 'atri': 'அத்திரி', 'vasishtha': 'வசிஷ்டர்', 'vishvamitra': 'விஸ்வாமித்திரர்',
           'gautama': 'கௌதமர்', 'jamadagni': 'ஜமதக்னி', 'bharadvaja': 'பரத்வாஜர்', 'agastya': 'அகத்தியர்',
           'bhrigu': 'பிருகு மரபு', 'angirasa': 'ஆங்கீரச மரபு', 'mizar': 'மிசார்', 'megrez': 'மெக்ரெஸ்'},
    'hi': {'kashyapa': 'कश्यप', 'atri': 'अत्रि', 'vasishtha': 'वशिष्ठ', 'vishvamitra': 'विश्वामित्र',
           'gautama': 'गौतम', 'jamadagni': 'जमदग्नि', 'bharadvaja': 'भरद्वाज', 'agastya': 'अगस्त्य',
           'bhrigu': 'भृगु परंपरा', 'angirasa': 'आंगिरस परंपरा', 'mizar': 'मिज़ार', 'megrez': 'मेग्रेज़'},
    'te': {'kashyapa': 'కశ్యపుడు', 'atri': 'అత్రి', 'vasishtha': 'వసిష్ఠుడు', 'vishvamitra': 'విశ్వామిత్రుడు',
           'gautama': 'గౌతముడు', 'jamadagni': 'జమదగ్ని', 'bharadvaja': 'భరద్వాజుడు', 'agastya': 'అగస్త్యుడు',
           'bhrigu': 'భృగు వంశం', 'angirasa': 'ఆంగీరస వంశం', 'mizar': 'మిజార్', 'megrez': 'మెగ్రెజ్'},
    'kn': {'kashyapa': 'ಕಶ್ಯಪ', 'atri': 'ಅತ್ರಿ', 'vasishtha': 'ವಸಿಷ್ಠ', 'vishvamitra': 'ವಿಶ್ವಾಮಿತ್ರ',
           'gautama': 'ಗೌತಮ', 'jamadagni': 'ಜಮದಗ್ನಿ', 'bharadvaja': 'ಭರದ್ವಾಜ', 'agastya': 'ಅಗಸ್ತ್ಯ',
           'bhrigu': 'ಭೃಗು ಪರಂಪರೆ', 'angirasa': 'ಆಂಗೀರಸ ಪರಂಪರೆ', 'mizar': 'ಮಿಜಾರ್', 'megrez': 'ಮೆಗ್ರೆಜ್'},
    'ml': {'kashyapa': 'കശ്യപൻ', 'atri': 'അത്രി', 'vasishtha': 'വസിഷ്ഠൻ', 'vishvamitra': 'വിശ്വാമിത്രൻ',
           'gautama': 'ഗൗതമൻ', 'jamadagni': 'ജമദഗ്നി', 'bharadvaja': 'ഭരദ്വാജൻ', 'agastya': 'അഗസ്ത്യൻ',
           'bhrigu': 'ഭൃഗു പരമ്പര', 'angirasa': 'ആംഗിരസ പരമ്പര', 'mizar': 'മിസാർ', 'megrez': 'മെഗ്രെസ്'},
    'mr': {'kashyapa': 'कश्यप', 'atri': 'अत्री', 'vasishtha': 'वसिष्ठ', 'vishvamitra': 'विश्वामित्र',
           'gautama': 'गौतम', 'jamadagni': 'जमदग्नी', 'bharadvaja': 'भरद्वाज', 'agastya': 'अगस्ती',
           'bhrigu': 'भृगू परंपरा', 'angirasa': 'आंगिरस परंपरा', 'mizar': 'मिझार', 'megrez': 'मेग्रेझ'},
    'bn': {'kashyapa': 'কশ্যপ', 'atri': 'অত্রি', 'vasishtha': 'বশিষ্ঠ', 'vishvamitra': 'বিশ্বামিত্র',
           'gautama': 'গৌতম', 'jamadagni': 'জমদগ্নি', 'bharadvaja': 'ভরদ্বাজ', 'agastya': 'অগস্ত্য',
           'bhrigu': 'ভৃগু পরম্পরা', 'angirasa': 'আঙ্গিরস পরম্পরা', 'mizar': 'মিজার', 'megrez': 'মেগ্রেজ'},
}

# Gotra names by the key of data/gotra_rishi.json. Order: en ta hi te kn ml mr bn.
_GOTRA_ROWS = {
    'kashyapa':      ('Kashyapa', 'காசியப', 'कश्यप', 'కాశ్యప', 'ಕಾಶ್ಯಪ', 'കാശ്യപ', 'काश्यप', 'কাশ্যপ'),
    'shandilya':     ('Shandilya', 'சாண்டில்ய', 'शांडिल्य', 'శాండిల్య', 'ಶಾಂಡಿಲ್ಯ', 'ശാണ്ഡില്യ', 'शांडिल्य', 'শাণ্ডিল্য'),
    'naidhruva':     ('Naidhruva', 'நைத்ருவ', 'नैध्रुव', 'నైధ్రువ', 'ನೈಧ್ರುವ', 'നൈധ്രുവ', 'नैध्रुव', 'নৈধ্রুব'),
    'rebha':         ('Rebha', 'ரேப', 'रेभ', 'రేభ', 'ರೇಭ', 'രേഭ', 'रेभ', 'রেভ'),
    'atreya':        ('Atreya', 'ஆத்ரேய', 'आत्रेय', 'ఆత్రేయ', 'ಆತ್ರೇಯ', 'ആത്രേയ', 'आत्रेय', 'আত্রেয়'),
    'gavishthira':   ('Gavishthira', 'கவிஷ்டிர', 'गविष्ठिर', 'గవిష్ఠిర', 'ಗವಿಷ್ಠಿರ', 'ഗവിഷ്ഠിര', 'गविष्ठिर', 'গবিষ্ঠির'),
    'vasishtha':     ('Vasishtha', 'வசிஷ்ட', 'वशिष्ठ', 'వాసిష్ఠ', 'ವಾಸಿಷ್ಠ', 'വാസിഷ്ഠ', 'वसिष्ठ', 'বশিষ্ঠ'),
    'kaundinya':     ('Kaundinya', 'கௌண்டின்ய', 'कौण्डिन्य', 'కౌండిన్య', 'ಕೌಂಡಿನ್ಯ', 'കൗണ്ഡിന്യ', 'कौंडिण्य', 'কৌণ্ডিন্য'),
    'parashara':     ('Parashara', 'பராசர', 'पराशर', 'పరాశర', 'ಪರಾಶರ', 'പരാശര', 'पराशर', 'পরাশর'),
    'upamanyu':      ('Upamanyu', 'உபமன்யு', 'उपमन्यु', 'ఉపమన్యు', 'ಉಪಮನ್ಯು', 'ഉപമന്യു', 'उपमन्यू', 'উপমন্যু'),
    'kaushika':      ('Kaushika', 'கௌசிக', 'कौशिक', 'కౌశిక', 'ಕೌಶಿಕ', 'കൗശിക', 'कौशिक', 'কৌশিক'),
    'vishvamitra':   ('Vishvamitra', 'விஸ்வாமித்திர', 'विश्वामित्र', 'విశ్వామిత్ర', 'ವಿಶ್ವಾಮಿತ್ರ', 'വിശ്വാമിത്ര', 'विश्वामित्र', 'বিশ্বামিত্র'),
    'kata':          ('Kata', 'கத', 'कत', 'కత', 'ಕತ', 'കത', 'कत', 'কত'),
    'aghamarshana':  ('Aghamarshana', 'அகமர்ஷண', 'अघमर्षण', 'అఘమర్షణ', 'ಅಘಮರ್ಷಣ', 'അഘമർഷണ', 'अघमर्षण', 'অঘমর্ষণ'),
    'gautama':       ('Gautama', 'கௌதம', 'गौतम', 'గౌతమ', 'ಗೌತಮ', 'ഗൗതമ', 'गौतम', 'গৌতম'),
    'srivatsa':      ('Srivatsa', 'ஸ்ரீவத்ச', 'श्रीवत्स', 'శ్రీవత్స', 'ಶ್ರೀವತ್ಸ', 'ശ്രീവത്സ', 'श्रीवत्स', 'শ্রীবৎস'),
    'bhargava':      ('Bhargava', 'பார்கவ', 'भार्गव', 'భార్గవ', 'ಭಾರ್ಗವ', 'ഭാർഗവ', 'भार्गव', 'ভার্গব'),
    'jamadagni':     ('Jamadagni', 'ஜமதக்னி', 'जमदग्नि', 'జమదగ్ని', 'ಜಮದಗ್ನಿ', 'ജമദഗ്നി', 'जमदग्नी', 'জমদগ্নি'),
    'bharadvaja':    ('Bharadvaja', 'பாரத்வாஜ', 'भारद्वाज', 'భారద్వాజ', 'ಭಾರದ್ವಾಜ', 'ഭാരദ്വാജ', 'भारद्वाज', 'ভরদ্বাজ'),
    'garga':         ('Garga', 'கர்க', 'गर्ग', 'గర్గ', 'ಗರ್ಗ', 'ഗർഗ', 'गर्ग', 'গর্গ'),
    'mudgala':       ('Mudgala', 'முத்கல', 'मुद्गल', 'ముద్గల', 'ಮುದ್ಗಲ', 'മുദ്ഗല', 'मुद्गल', 'মুদ্গল'),
    'vishnuvriddha': ('Vishnuvriddha', 'விஷ்ணுவிருத்த', 'विष्णुवृद्ध', 'విష్ణువృద్ధ', 'ವಿಷ್ಣುವೃದ್ಧ', 'വിഷ്ണുവൃദ്ധ', 'विष्णुवृद्ध', 'বিষ্ণুবৃদ্ধ'),
    'kanva':         ('Kanva', 'கண்வ', 'कण्व', 'కణ్వ', 'ಕಣ್ವ', 'കണ്വ', 'कण्व', 'কণ্ব'),
    'agastya':       ('Agastya', 'அகஸ்திய', 'अगस्त्य', 'అగస్త్య', 'ಅಗಸ್ತ್ಯ', 'അഗസ്ത്യ', 'अगस्त्य', 'অগস্ত্য'),
}
GOTRA_NAMES = {lang: {k: row[i] for k, row in _GOTRA_ROWS.items()}
               for i, lang in enumerate(['en', 'ta', 'hi', 'te', 'kn', 'ml', 'mr', 'bn'])}


def _from(table, key, lang):
    en = table['en'].get(key, key)
    if lang == 'bi':
        return _pair(en, table['ta'].get(key))
    return table.get(lang, table['en']).get(key, en)


def SL(key, lang='en'):
    """Saptarishi label or sentence. Bilingual shows 'English / தமிழ்'."""
    return _from(SAPTA_LABELS, key, lang)


def rishi_name(key, lang='en'):
    """Root rishi, line ('bhrigu', 'angirasa') or star ('mizar', 'megrez')."""
    return _from(RISHI_NAMES, key, lang)


def gotra_name(key, lang='en'):
    return _from(GOTRA_NAMES, key, lang)


# ── FAMILY READING ────────────────────────────────────────────────────────────
# Labels of the family report, in all eight languages:
# key: (en, ta, hi, te, kn, ml, mr, bn)
_FAMILY_ROWS = {
    'family_title': ('Family Reading', 'குடும்ப ஜாதக பலன்', 'पारिवारिक कुंडली विश्लेषण', 'కుటుంబ జాతక విశ్లేషణ',
                     'ಕುಟುಂಬ ಜಾತಕ ವಿಶ್ಲೇಷಣೆ', 'കുടുംബ ജാതക വിശകലനം', 'कौटुंबिक कुंडली विश्लेषण', 'পারিবারিক কোষ্ঠী বিশ্লেষণ'),
    'members': ('Members', 'உறுப்பினர்கள்', 'सदस्य', 'సభ్యులు', 'ಸದಸ್ಯರು', 'അംഗങ്ങൾ', 'सदस्य', 'সদস্য'),
    'member': ('Member', 'உறுப்பினர்', 'सदस्य', 'సభ్యుడు', 'ಸದಸ್ಯ', 'അംഗം', 'सदस्य', 'সদস্য'),
    'relation': ('Relation', 'உறவு', 'संबंध', 'సంబంధం', 'ಸಂಬಂಧ', 'ബന്ധം', 'नाते', 'সম্পর্ক'),
    'anchor': ('Anchor (Self)', 'மையம் (தான்)', 'केंद्र (स्वयं)', 'కేంద్రం (స్వయం)', 'ಕೇಂದ್ರ (ಸ್ವತಃ)',
               'കേന്ദ്രം (സ്വയം)', 'केंद्र (स्वतः)', 'কেন্দ্র (নিজে)'),
    'lagna': ('Lagna', 'லக்னம்', 'लग्न', 'లగ్నం', 'ಲಗ್ನ', 'ലഗ്നം', 'लग्न', 'লগ্ন'),
    'moon_sign': ('Moon sign', 'ராசி', 'चंद्र राशि', 'చంద్ర రాశి', 'ಚಂದ್ರ ರಾಶಿ', 'ചന്ദ്ര രാശി', 'चंद्र रास', 'চন্দ্র রাশি'),
    'star': ('Star', 'நட்சத்திரம்', 'नक्षत्र', 'నక్షత్రం', 'ನಕ್ಷತ್ರ', 'നക്ഷത്രം', 'नक्षत्र', 'নক্ষত্র'),
    'dasa_bhukti': ('Dasa / Bhukti', 'தசை / புக்தி', 'दशा / अंतर्दशा', 'దశ / భుక్తి', 'ದಶೆ / ಭುಕ್ತಿ', 'ദശ / ഭുക്തി',
                    'दशा / अंतर्दशा', 'দশা / অন্তর্দশা'),
    'until': ('until', 'வரை', 'तक', 'వరకు', 'ವರೆಗೆ', 'വരെ', 'पर्यंत', 'পর্যন্ত'),
    'saturn_from_moon': ('Saturn from Moon', 'சந்திரனிலிருந்து சனி', 'चंद्र से शनि', 'చంద్రుని నుండి శని',
                         'ಚಂದ್ರನಿಂದ ಶನಿ', 'ചന്ദ്രനിൽ നിന്ന് ശനി', 'चंद्रापासून शनी', 'চন্দ্র থেকে শনি'),
    'jupiter_from_moon': ('Jupiter from Moon', 'சந்திரனிலிருந்து குரு', 'चंद्र से गुरु', 'చంద్రుని నుండి గురు',
                          'ಚಂದ್ರನಿಂದ ಗುರು', 'ചന്ദ്രനിൽ നിന്ന് ഗുരു', 'चंद्रापासून गुरु', 'চন্দ্র থেকে বৃহস্পতি'),
    'sec_A': ('Members', 'உறுப்பினர்கள்', 'सदस्य', 'సభ్యులు', 'ಸದಸ್ಯರು', 'അംഗങ്ങൾ', 'सदस्य', 'সদস্য'),
    'sec_B': ('Relations and family houses', 'உறவுகள் மற்றும் குடும்ப பாவங்கள்', 'संबंध और पारिवारिक भाव',
              'సంబంధాలు మరియు కుటుంబ భావాలు', 'ಸಂಬಂಧಗಳು ಮತ್ತು ಕುಟುಂಬ ಭಾವಗಳು', 'ബന്ധങ്ങളും കുടുംബ ഭാവങ്ങളും',
              'नाती आणि कौटुंबिक भाव', 'সম্পর্ক ও পারিবারিক ভাব'),
    'sec_C': ('Pairs', 'இணைகள்', 'जोड़ियाँ', 'జంటలు', 'ಜೋಡಿಗಳು', 'ജോഡികൾ', 'जोड्या', 'জোড়া'),
    'sec_D': ('Shared patterns', 'பொதுவான அமைப்புகள்', 'साझा योग', 'ఉమ్మడి అమరికలు', 'ಸಾಮಾನ್ಯ ಅಂಶಗಳು',
              'പൊതുവായ ഘടകങ്ങൾ', 'सामायिक योग', 'সাধারণ বৈশিষ্ট্য'),
    'sec_E': ('Family timeline', 'குடும்ப கால வரிசை', 'पारिवारिक समयरेखा', 'కుటుంబ కాలక్రమం', 'ಕುಟುಂಬ ಕಾಲರೇಖೆ',
              'കുടുംബ സമയരേഖ', 'कौटुंबिक कालरेषा', 'পারিবারিক সময়রেখা'),
    'sec_F': ('Transits', 'கோசாரம்', 'गोचर', 'గోచారం', 'ಗೋಚಾರ', 'ഗോചാരം', 'गोचर', 'গোচর'),
    'sec_G': ('Family rules', 'குடும்ப விதிகள்', 'पारिवारिक नियम', 'కుటుంబ నియమాలు', 'ಕುಟುಂಬ ನಿಯಮಗಳು',
              'കുടുംബ നിയമങ്ങൾ', 'कौटुंबिक नियम', 'পারিবারিক নিয়ম'),
    'sec_H': ('Summary', 'சுருக்கம்', 'सारांश', 'సారాంశం', 'ಸಾರಾಂಶ', 'സംഗ്രഹം', 'सारांश', 'সারসংক্ষেপ'),
    'family_houses': ('Family houses of the anchor', 'மையத்தின் குடும்ப பாவங்கள்', 'केंद्र के पारिवारिक भाव',
                      'కేంద్ర వ్యక్తి కుటుంబ భావాలు', 'ಕೇಂದ್ರ ವ್ಯಕ್ತಿಯ ಕುಟುಂಬ ಭಾವಗಳು', 'കേന്ദ്ര വ്യക്തിയുടെ കുടുംബ ഭാവങ്ങൾ',
                      'केंद्राचे कौटुंबिक भाव', 'কেন্দ্রের পারিবারিক ভাব'),
    'relation_houses': ('Houses of each relation', 'ஒவ்வொரு உறவின் பாவம்', 'प्रत्येक संबंध का भाव',
                        'ప్రతి సంబంధం యొక్క భావం', 'ಪ್ರತಿ ಸಂಬಂಧದ ಭಾವ', 'ഓരോ ബന്ധത്തിന്റെയും ഭാവം',
                        'प्रत्येक नात्याचा भाव', 'প্রতিটি সম্পর্কের ভাব'),
    'read_back': ('Read back from each member', 'ஒவ்வொருவரின் ஜாதகத்திலிருந்து', 'प्रत्येक सदस्य की कुंडली से',
                  'ప్రతి సభ్యుని జాతకం నుండి', 'ಪ್ರತಿ ಸದಸ್ಯರ ಜಾತಕದಿಂದ', 'ഓരോ അംഗത്തിന്റെയും ജാതകത്തിൽ നിന്ന്',
                  'प्रत्येक सदस्याच्या कुंडलीतून', 'প্রত্যেক সদস্যের কোষ্ঠী থেকে'),
    'overlays': ('Planets falling on each other', 'ஒருவர் கிரகம் மற்றவர் மீது', 'एक के ग्रह दूसरे पर',
                 'ఒకరి గ్రహాలు మరొకరిపై', 'ಒಬ್ಬರ ಗ್ರಹ ಇನ್ನೊಬ್ಬರ ಮೇಲೆ', 'ഒരാളുടെ ഗ്രഹം മറ്റൊരാളിൽ',
                 'एकाचे ग्रह दुसऱ्यावर', 'একজনের গ্রহ অন্যজনের উপর'),
    'yogas': ('Yogas and ancestral factors', 'யோகங்கள் மற்றும் பித்ரு அமைப்புகள்', 'योग और पितृ कारक',
              'యోగాలు మరియు పితృ అంశాలు', 'ಯೋಗಗಳು ಮತ್ತು ಪಿತೃ ಅಂಶಗಳು', 'യോഗങ്ങളും പിതൃ ഘടകങ്ങളും',
              'योग आणि पितृ घटक', 'যোগ ও পিতৃ কারক'),
    'windows': ('Family windows', 'குடும்ப காலங்கள்', 'पारिवारिक अवधियाँ', 'కుటుంబ కాలాలు', 'ಕುಟುಂಬ ಅವಧಿಗಳು',
                'കുടുംബ കാലഘട്ടങ്ങൾ', 'कौटुंबिक कालावधी', 'পারিবারিক সময়কাল'),
    'timeline_grid': ('Year by year', 'ஆண்டு வாரியாக', 'वर्षवार', 'సంవత్సరాల వారీగా', 'ವರ್ಷವಾರು', 'വർഷം തോറും',
                      'वर्षनिहाय', 'বছর অনুযায়ী'),
    'sandhi': ('Dasa changes close together', 'அருகருகே வரும் தசை மாற்றங்கள்', 'निकट दशा परिवर्तन',
               'దగ్గరగా వచ్చే దశ మార్పులు', 'ಹತ್ತಿರದ ದಶಾ ಬದಲಾವಣೆಗಳು', 'അടുത്തടുത്ത ദശാ മാറ്റങ്ങൾ',
               'जवळचे दशा बदल', 'কাছাকাছি দশা পরিবর্তন'),
    'transits_now': ('Transits now', 'தற்போதைய கோசாரம்', 'वर्तमान गोचर', 'ప్రస్తుత గోచారం', 'ಈಗಿನ ಗೋಚಾರ',
                     'ഇപ്പോഴത്തെ ഗോചാരം', 'सध्याचे गोचर', 'বর্তমান গোচর'),
    'transit_changes': ('Sign changes ahead', 'வரவிருக்கும் ராசி மாற்றங்கள்', 'आगामी राशि परिवर्तन',
                        'రాబోయే రాశి మార్పులు', 'ಮುಂದಿನ ರಾಶಿ ಬದಲಾವಣೆಗಳು', 'വരാനിരിക്കുന്ന രാശി മാറ്റങ്ങൾ',
                        'येणारे राशी बदल', 'আসন্ন রাশি পরিবর্তন'),
    'shared_topics': ('Where members agree', 'உறுப்பினர்கள் ஒத்துப்போகும் இடம்', 'जहाँ सदस्य सहमत हैं',
                      'సభ్యులు ఏకీభవించే చోట', 'ಸದಸ್ಯರು ಒಪ್ಪುವಲ್ಲಿ', 'അംഗങ്ങൾ യോജിക്കുന്നിടം',
                      'जिथे सदस्य सहमत', 'যেখানে সদস্যরা একমত'),
    'supportive': ('Supportive', 'சாதகம்', 'अनुकूल', 'అనుకూలం', 'ಅನುಕೂಲ', 'അനുകൂലം', 'अनुकूल', 'অনুকূল'),
    'mixed': ('Mixed', 'கலப்பு', 'मिश्रित', 'మిశ్రమం', 'ಮಿಶ್ರ', 'സമ്മിശ്രം', 'मिश्र', 'মিশ্র'),
    'pressured': ('Pressured', 'அழுத்தம்', 'दबावपूर्ण', 'ఒత్తిడి', 'ಒತ್ತಡ', 'സമ്മർദം', 'दबावाचा', 'চাপযুক্ত'),
    'strained': ('Needs care', 'கவனம் தேவை', 'ध्यान आवश्यक', 'జాగ్రత్త అవసరం', 'ಎಚ್ಚರ ಅಗತ್ಯ', 'ശ്രദ്ധ വേണം',
                 'काळजी आवश्यक', 'যত্ন প্রয়োজন'),
    'from': ('From', 'முதல்', 'से', 'నుండి', 'ಇಂದ', 'മുതൽ', 'पासून', 'থেকে'),
    'to': ('To', 'வரை', 'तक', 'వరకు', 'ವರೆಗೆ', 'വരെ', 'पर्यंत', 'পর্যন্ত'),
    'months': ('Months', 'மாதங்கள்', 'महीने', 'నెలలు', 'ತಿಂಗಳುಗಳು', 'മാസങ്ങൾ', 'महिने', 'মাস'),
    'status': ('Status', 'நிலை', 'स्थिति', 'స్థితి', 'ಸ್ಥಿತಿ', 'നില', 'स्थिती', 'অবস্থা'),
    'family_row': ('Family', 'குடும்பம்', 'परिवार', 'కుటుంబం', 'ಕುಟುಂಬ', 'കുടുംബം', 'कुटुंब', 'পরিবার'),
    'rules': ('Rules used', 'பயன்படுத்திய விதிகள்', 'प्रयुक्त नियम', 'వాడిన నియమాలు', 'ಬಳಸಿದ ನಿಯಮಗಳು',
              'ഉപയോഗിച്ച നിയമങ്ങൾ', 'वापरलेले नियम', 'ব্যবহৃত নিয়ম'),
    'not_included': ('Not included', 'சேர்க்கப்படாதவை', 'शामिल नहीं', 'చేర్చనివి', 'ಸೇರಿಸಿಲ್ಲ', 'ഉൾപ്പെടുത്തിയിട്ടില്ല',
                     'समाविष्ट नाही', 'অন্তর্ভুক্ত নয়'),
    'rule_based': ('Rule-based, not a prediction', 'விதி அடிப்படையிலானது, கணிப்பு அல்ல', 'नियम आधारित, भविष्यवाणी नहीं',
                   'నియమాల ఆధారంగా, భవిష్యవాణి కాదు', 'ನಿಯಮ ಆಧಾರಿತ, ಭವಿಷ್ಯವಾಣಿ ಅಲ್ಲ', 'നിയമാധിഷ്ഠിതം, പ്രവചനമല്ല',
                   'नियमाधारित, भविष्यवाणी नाही', 'নিয়মভিত্তিক, ভবিষ্যদ্বাণী নয়'),
    'legend': ('G good period · M mixed · D difficult · S sade sati · A ashtama · J Jupiter favourable',
               'G நல்ல காலம் · M கலப்பு · D கடினம் · S ஏழரைச் சனி · A அஷ்டமச் சனி · J குரு சாதகம்',
               'G शुभ काल · M मिश्रित · D कठिन · S साढ़ेसाती · A अष्टम शनि · J गुरु अनुकूल',
               'G మంచి కాలం · M మిశ్రమం · D కష్టం · S ఏలినాటి శని · A అష్టమ శని · J గురు అనుకూలం',
               'G ಒಳ್ಳೆಯ ಕಾಲ · M ಮಿಶ್ರ · D ಕಷ್ಟ · S ಸಾಡೇಸಾತಿ · A ಅಷ್ಟಮ ಶನಿ · J ಗುರು ಅನುಕೂಲ',
               'G നല്ല കാലം · M സമ്മിശ്രം · D പ്രയാസം · S ഏഴരശ്ശനി · A അഷ്ടമശ്ശനി · J ഗുരു അനുകൂലം',
               'G शुभ काळ · M मिश्र · D कठीण · S साडेसाती · A अष्टम शनी · J गुरु अनुकूल',
               'G শুভ সময় · M মিশ্র · D কঠিন · S সাড়েসাতি · A অষ্টম শনি · J বৃহস্পতি অনুকূল'),
    'self': ('Self', 'தான்', 'स्वयं', 'స్వయం', 'ಸ್ವತಃ', 'സ്വയം', 'स्वतः', 'নিজে'),
    'spouse': ('Spouse', 'வாழ்க்கைத் துணை', 'जीवनसाथी', 'జీవిత భాగస్వామి', 'ಸಂಗಾತಿ', 'ജീവിതപങ്കാളി', 'जोडीदार', 'জীবনসঙ্গী'),
    'father': ('Father', 'தந்தை', 'पिता', 'తండ్రి', 'ತಂದೆ', 'അച്ഛൻ', 'वडील', 'বাবা'),
    'mother': ('Mother', 'தாய்', 'माता', 'తల్లి', 'ತಾಯಿ', 'അമ്മ', 'आई', 'মা'),
    'father-in-law': ('Father-in-law', 'மாமனார்', 'ससुर', 'మామగారు', 'ಮಾವ', 'ഭർതൃ/ഭാര്യാ പിതാവ്', 'सासरे', 'শ্বশুর'),
    'mother-in-law': ('Mother-in-law', 'மாமியார்', 'सास', 'అత్తగారు', 'ಅತ್ತೆ', 'ഭർതൃ/ഭാര്യാ മാതാവ്', 'सासू', 'শাশুড়ি'),
    'son': ('Son', 'மகன்', 'पुत्र', 'కుమారుడు', 'ಮಗ', 'മകൻ', 'मुलगा', 'ছেলে'),
    'daughter': ('Daughter', 'மகள்', 'पुत्री', 'కుమార్తె', 'ಮಗಳು', 'മകൾ', 'मुलगी', 'মেয়ে'),
    'brother': ('Brother', 'சகோதரன்', 'भाई', 'సోదరుడు', 'ಸಹೋದರ', 'സഹോദരൻ', 'भाऊ', 'ভাই'),
    'sister': ('Sister', 'சகோதரி', 'बहन', 'సోదరి', 'ಸಹೋದರಿ', 'സഹോദരി', 'बहीण', 'বোন'),
    'grandfather': ('Grandfather', 'தாத்தா', 'दादा / नाना', 'తాత', 'ಅಜ್ಜ', 'മുത്തച്ഛൻ', 'आजोबा', 'দাদু'),
    'grandmother': ('Grandmother', 'பாட்டி', 'दादी / नानी', 'నాయనమ్మ / అమ్మమ్మ', 'ಅಜ್ಜಿ', 'മുത്തശ്ശി', 'आजी', 'ঠাকুমা / দিদিমা'),
    'grandson': ('Grandson', 'பேரன்', 'पोता / नाती', 'మనవడు', 'ಮೊಮ್ಮಗ', 'പേരക്കുട്ടി (ആൺ)', 'नातू', 'নাতি'),
    'granddaughter': ('Granddaughter', 'பேத்தி', 'पोती / नातिन', 'మనవరాలు', 'ಮೊಮ್ಮಗಳು', 'പേരക്കുട്ടി (പെൺ)', 'नात', 'নাতনি'),
    'daughter-in-law': ('Daughter-in-law', 'மருமகள்', 'बहू', 'కోడలు', 'ಸೊಸೆ', 'മരുമകൾ', 'सून', 'পুত্রবধূ'),
    'son-in-law': ('Son-in-law', 'மருமகன்', 'दामाद', 'అల్లుడు', 'ಅಳಿಯ', 'മരുമകൻ', 'जावई', 'জামাই'),
    'maternal uncle': ('Maternal uncle', 'தாய்மாமன்', 'मामा', 'మేనమామ', 'ಸೋದರಮಾವ', 'അമ്മാവൻ', 'मामा', 'মামা'),
    'sec_I': ('Relationships over time', 'காலப்போக்கில் உறவுகள்', 'समय के साथ संबंध', 'కాలక్రమంలో సంబంధాలు',
              'ಕಾಲಕ್ರಮದಲ್ಲಿ ಸಂಬಂಧಗಳು', 'കാലക്രമത്തിൽ ബന്ധങ്ങൾ', 'काळानुसार नाती', 'সময়ের সঙ্গে সম্পর্ক'),
    'other': ('Other', 'மற்றவர்', 'अन्य', 'ఇతరులు', 'ಇತರ', 'മറ്റുള്ളവർ', 'इतर', 'অন্যান্য'),
}
FAMILY_LABELS = {lang: {k: row[i] for k, row in _FAMILY_ROWS.items()}
                 for i, lang in enumerate(['en', 'ta', 'hi', 'te', 'kn', 'ml', 'mr', 'bn'])}


def FL(key, lang='en'):
    """Label of the family report. Bilingual shows 'English / தமிழ்'."""
    return _from(FAMILY_LABELS, key, lang)


def relation_name(relation, lang='en'):
    """A relation from family_engine.RELATIONS in the report language."""
    return FL(relation.lower(), lang) if relation.lower() in _FAMILY_ROWS else relation
