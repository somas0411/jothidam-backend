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
WEEKDAYS['mr'] = WEEKDAYS['hi']

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
WORDS['mr'] = WORDS['hi']

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
VARGA_PURPOSE['mr'] = VARGA_PURPOSE['hi']

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
LABELS['mr'] = LABELS['hi']


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
# English, Tamil and Hindi (Marathi reuses Hindi); other languages fall back
# to English, as the report labels do. Values of the chart and timing rows
# (groups D and E) are sentences and stay in English in every language.

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
MATCH_LABELS['mr'] = MATCH_LABELS['hi']

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
MATCH_CHECKS['mr'] = MATCH_CHECKS['hi']

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
MATCH_WORDS['mr'] = MATCH_WORDS['hi']

# The tree of each star in Tamil, by the name match_engine.TREE uses.
MATCH_TREES_TA = {
    'Etti': 'எட்டி', 'Nelli': 'நெல்லி', 'Athi': 'அத்தி', 'Naval': 'நாவல்', 'Karungali': 'கருங்காலி',
    'Sengarungali': 'செங்கருங்காலி', 'Moongil': 'மூங்கில்', 'Arasu': 'அரசு', 'Punnai': 'புன்னை', 'Aal': 'ஆல்',
    'Pala': 'பலா', 'Alari': 'அலரி', 'Velam': 'வேலம்', 'Vilvam': 'வில்வம்', 'Marutham': 'மருதம்', 'Vila': 'விளா',
    'Magizh': 'மகிழ்', 'Pirai': 'பிராய்', 'Maa': 'மா', 'Vanji': 'வஞ்சி', 'Erukku': 'எருக்கு', 'Vanni': 'வன்னி',
    'Kadambu': 'கடம்பு', 'Thema': 'தேமா', 'Vembu': 'வேம்பு', 'Iluppai': 'இலுப்பை',
}


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
