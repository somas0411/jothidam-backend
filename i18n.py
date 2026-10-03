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
    'en': {'Lagna': 'Lagna', 'Sun': 'Sun', 'Moon': 'Moon', 'Mars': 'Mars', 'Mercury': 'Mercury', 'Jupiter': 'Jupiter', 'Venus': 'Venus', 'Saturn': 'Saturn', 'Rahu': 'Rahu', 'Ketu': 'Ketu'},
    'ta': {'Lagna': 'லக்னம்', 'Sun': 'சூரியன்', 'Moon': 'சந்திரன்', 'Mars': 'செவ்வாய்', 'Mercury': 'புதன்', 'Jupiter': 'குரு', 'Venus': 'சுக்கிரன்', 'Saturn': 'சனி', 'Rahu': 'ராகு', 'Ketu': 'கேது'},
    'hi': {'Lagna': 'लग्न', 'Sun': 'सूर्य', 'Moon': 'चंद्र', 'Mars': 'मंगल', 'Mercury': 'बुध', 'Jupiter': 'गुरु', 'Venus': 'शुक्र', 'Saturn': 'शनि', 'Rahu': 'राहु', 'Ketu': 'केतु'},
    'te': {'Lagna': 'లగ్నం', 'Sun': 'సూర్యుడు', 'Moon': 'చంద్రుడు', 'Mars': 'కుజుడు', 'Mercury': 'బుధుడు', 'Jupiter': 'గురువు', 'Venus': 'శుక్రుడు', 'Saturn': 'శని', 'Rahu': 'రాహువు', 'Ketu': 'కేతువు'},
    'kn': {'Lagna': 'ಲಗ್ನ', 'Sun': 'ಸೂರ್ಯ', 'Moon': 'ಚಂದ್ರ', 'Mars': 'ಕುಜ', 'Mercury': 'ಬುಧ', 'Jupiter': 'ಗುರು', 'Venus': 'ಶುಕ್ರ', 'Saturn': 'ಶನಿ', 'Rahu': 'ರಾಹು', 'Ketu': 'ಕೇತು'},
    'ml': {'Lagna': 'ലഗ്നം', 'Sun': 'സൂര്യൻ', 'Moon': 'ചന്ദ്രൻ', 'Mars': 'ചൊവ്വ', 'Mercury': 'ബുധൻ', 'Jupiter': 'വ്യാഴം', 'Venus': 'ശുക്രൻ', 'Saturn': 'ശനി', 'Rahu': 'രാഹു', 'Ketu': 'കേതു'},
    'mr': {'Lagna': 'लग्न', 'Sun': 'रवि', 'Moon': 'चंद्र', 'Mars': 'मंगळ', 'Mercury': 'बुध', 'Jupiter': 'गुरु', 'Venus': 'शुक्र', 'Saturn': 'शनि', 'Rahu': 'राहू', 'Ketu': 'केतू'},
    'bn': {'Lagna': 'লগ্ন', 'Sun': 'সূর্য', 'Moon': 'চন্দ্র', 'Mars': 'মঙ্গল', 'Mercury': 'বুধ', 'Jupiter': 'বৃহস্পতি', 'Venus': 'শুক্র', 'Saturn': 'শনি', 'Rahu': 'রাহু', 'Ketu': 'কেতু'},
}

ABBR = {
    'en': {'Lagna': 'La', 'Sun': 'Su', 'Moon': 'Mo', 'Mars': 'Ma', 'Mercury': 'Me', 'Jupiter': 'Ju', 'Venus': 'Ve', 'Saturn': 'Sa', 'Rahu': 'Ra', 'Ketu': 'Ke', 'ALP': 'AL'},
    'ta': {'Lagna': 'லக்', 'Sun': 'சூ', 'Moon': 'சந்', 'Mars': 'செ', 'Mercury': 'பு', 'Jupiter': 'குரு', 'Venus': 'சுக்', 'Saturn': 'சனி', 'Rahu': 'ரா', 'Ketu': 'கே', 'ALP': 'அல'},
    'hi': {'Lagna': 'ल', 'Sun': 'सू', 'Moon': 'चं', 'Mars': 'मं', 'Mercury': 'बु', 'Jupiter': 'गु', 'Venus': 'शु', 'Saturn': 'श', 'Rahu': 'रा', 'Ketu': 'के', 'ALP': 'अल'},
    'te': {'Lagna': 'ల', 'Sun': 'సూ', 'Moon': 'చం', 'Mars': 'కు', 'Mercury': 'బు', 'Jupiter': 'గు', 'Venus': 'శు', 'Saturn': 'శ', 'Rahu': 'రా', 'Ketu': 'కే', 'ALP': 'AL'},
    'kn': {'Lagna': 'ಲ', 'Sun': 'ಸೂ', 'Moon': 'ಚಂ', 'Mars': 'ಕು', 'Mercury': 'ಬು', 'Jupiter': 'ಗು', 'Venus': 'ಶು', 'Saturn': 'ಶ', 'Rahu': 'ರಾ', 'Ketu': 'ಕೇ', 'ALP': 'AL'},
    'ml': {'Lagna': 'ല', 'Sun': 'സൂ', 'Moon': 'ച', 'Mars': 'ചൊ', 'Mercury': 'ബു', 'Jupiter': 'വ്യാ', 'Venus': 'ശു', 'Saturn': 'ശനി', 'Rahu': 'രാ', 'Ketu': 'കേ', 'ALP': 'AL'},
    'mr': {'Lagna': 'ल', 'Sun': 'र', 'Moon': 'चं', 'Mars': 'मं', 'Mercury': 'बु', 'Jupiter': 'गु', 'Venus': 'शु', 'Saturn': 'श', 'Rahu': 'रा', 'Ketu': 'के', 'ALP': 'अल'},
    'bn': {'Lagna': 'ল', 'Sun': 'সূ', 'Moon': 'চ', 'Mars': 'ম', 'Mercury': 'বু', 'Jupiter': 'বৃ', 'Venus': 'শু', 'Saturn': 'শ', 'Rahu': 'রা', 'Ketu': 'কে', 'ALP': 'AL'},
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
    names = ['Lagna', 'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
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
        'retro': retro_mark(lang),
    }
