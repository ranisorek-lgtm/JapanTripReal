from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import json
import os

DATA_FILE = "trip_data.json"

# מבנה ברירת המחדל המלא של הנתונים (ללא רשימות צ'ק-ליסט בהתחלה)
DEFAULT_TRIP_DATA = {
    "flights": [
        {"id": "f1", "name": "טיסות בינלאומיות (תל אביב - אוסקה הלוך ושוב)", "price_ils": 17300.0}
    ],
    "hotels": [
        {"id": "h1", "name": "Keio Plaza Hotel Sapporo (11.9–14.9)", "price_ils": 2290.0, "address": "2 Chome-2-1 Kita 5 Jonishi, Chuo Ward, Sapporo, Hokkaido 060-0005, Japan"},
        {"id": "h2", "name": "Yutorelo Toyako (14.9–15.9)", "price_ils": 542.0, "address": "68-1 Maruyama, Abuta-gun, Toyako-cho, Hokkaido 049-5721, Japan"},
        {"id": "h3", "name": "Daiwa Roynet Hotel Aomori (15.9–18.9)", "price_ils": 1015.0, "address": "1 Chome-1-23 Shinmachi, Aomori, 030-0801, Japan"},
        {"id": "h4", "name": "Tokyu Stay Aoyama Premier (18.9–23.9)", "price_ils": 3168.0, "address": "2 Chome-7-18 Minamiaoyama, Minato City, Tokyo 107-0062, Japan"},
        {"id": "h8", "name": "Takayama Ouan - פמילי רום עם ארוחת בוקר (23.9–24.9) [הוזמן ב-32,071 מיילים]", "price_ils": 0.0, "address": "4 Chome-327 Hanakokuracho, Takayama, Gifu 506-0007, Japan"},
        {"id": "h5", "name": "Hotel and spa gift Takayama (24.9–26.9)", "price_ils": 813.0, "address": "6 Chome-888-1 Nishinoisshicho, Takayama, Gifu 506-0031, Japan"},
        {"id": "h6", "name": "Hotel Gracery Kyoto Sanjo (26.9–1.10)", "price_ils": 2015.0, "address": "420 Nakajimacho, Nakagyo Ward, Kyoto, 604-8032, Japan"},
        {"id": "h7", "name": "Oyado Nono Namba Natural Hot Spring (1.10–4.10)", "price_ils": 2603.0, "address": "1 Chome-4-17 Nipponbashi, Chuo Ward, Osaka, 542-0073, Japan"},
    ],
    "trains": [
        {"id": "t1", "name": "סאפורו <== אגם טויה (14.9)", "price_ils": 270.19},
        {"id": "t2", "name": "אגם טויה ==> אאומורי (15.9 - מקטע 1)", "price_ils": 219.68},
        {"id": "t3", "name": "אגם טויה ==> אאומורי (15.9 - מקטע 2)", "price_ils": 317.04},
        {"id": "t4", "name": "אאומורי ==> טוקיו (18.9)", "price_ils": 376.34},
        {"id": "t5", "name": "טוקיו ==> טאקאיאמה (23.9)", "price_ils": 346.15},
        {"id": "t6", "name": "טאקאיאמה ==> קיוטו (26.9)", "price_ils": 230.74},
        {"id": "t7", "name": "קיוטו ==> אוסקה (1.10)", "price_ils": 31.04},
    ],
    "checklists": {},
    "attractions": {
        "סאפורו": [
            {
                "id": "a1", 
                "name": "פארק אודורי (Odori Park)", 
                "price_ils": 0, 
                "desc": "זהו שדרה ירוקה וארוכה החוצה את מרכז העיר. הפארק משמש כמקום מפגש מרכזי וכולל מזרקות, אזורי ישיבה ופסלים. בחורף הוא הופך למוקד המרכזי של \"פסטיבל השלג\" המפורסם, שם מציבים פסלי קרח ענקיים.", 
                "img": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=500"
            },
            {
                "id": "a2", 
                "name": "הר מואיווה (Mount Moiwa)", 
                "price_ils": 52, 
                "desc": "ההגעה לפסגה נעשית באמצעות רכבל המציע חוויה ויזואלית מרהיבה. בראש ההר נמצאת תצפית המאפשרת לראות את כל העיר סאפורו, במיוחד את אורות העיר בלילה, מה שנחשב לאחד מהמראות היפים ביותר ביפן (\"Midnight City View\").", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a3", 
                "name": "פארק שירוי קויביטו (Shiroi Koibito Park)", 
                "price_ils": 30, 
                "desc": "זהו מתחם מרהיב בנושא שוקולד וסוכריות, השייך לחברת העוגיות המפורסמת של הוקאידו. תוכלו לראות את קווי הייצור של העוגיות, להשתתף בסדנאות הכנת ממתקים קטנות, וליהנות מהגנים האירופאיים המטופחים שסביב המבנה.", 
                "img": "https://images.unsplash.com/photo-1549488344-cbb6c34cf08b?w=500"
            },
            {
                "id": "a4", 
                "name": "מקדש הוקאידו (Hokkaido Jingu)", 
                "price_ils": 0, 
                "desc": "זהו מקדש שינטו מכובד ומרכזי המוקף בפארק מארויאמה (Maruyama Park). זה מקום שקט מאוד המציע אתנחתא מהעיר, עם שבילים יפים ביער וארכיטקטורה יפנית מסורתית.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a5", 
                "name": "שוק ניג'ו (Nijo Market)", 
                "price_ils": 50, 
                "desc": "שוק דגים היסטורי בן למעלה מ-100 שנה. הוא מציע אווירה יפנית אותנטית עם דוכנים שמוכרים מוצרי ים טריים (סרטנים, קיפודי ים, דגים), פירות וירקות מקומיים. המקום מפורסם בדוכני האוכל הקטנים שבהם אפשר לאכול קערות \"קאיסנדון\" (דג נא על אורז) טריות מאוד לארוחת בוקר או צהריים.", 
                "img": "https://images.unsplash.com/photo-1553163147-622ab57be1c2?w=500"
            },
            {
                "id": "a6", 
                "name": "סיור עם אוכל ים", 
                "price_ils": 330, 
                "desc": "סיור מודרך בתאריך 12.9 בשעה 10:30.", 
                "img": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=500"
            }
        ],
        "אגם טויה": [
            {
                "id": "a7", 
                "name": "רכבל הר אוסו (Usuzan Ropeway)", 
                "price_ils": 47, 
                "desc": "מביא אתכם לנקודת תצפית מרהיבה על האגם ועל המכתש הוולקני של הר אוסו. אפשר לטייל שם בשבילים מסודרים ולראות את האדים העולים מהאדמה (עדות לפעילות הוולקנית הפעילה).", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a8", 
                "name": "שייט באגם טויה (Lake Toya Cruise)", 
                "price_ils": 35, 
                "desc": "שייט של כ-50 דקות המאפשר לראות את האגם מהמרכז. השייט עובר ליד האיים שבמרכז האגם (Nakanoshima). בחלק מהעונות (עד סוף אוקטובר) יש גם שייט מיוחד לצפייה בזיקוקים.", 
                "img": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=500"
            },
            {
                "id": "a9", 
                "name": "מופע הזיקוקים הלילי (Toyako Long-Run Fireworks)", 
                "price_ils": 0, 
                "desc": "אטרקציה ייחודית של האזור. החל מסוף אפריל ועד סוף אוקטובר, משוגרים זיקוקים מעל האגם מדי לילה ב-20:45 למשך כ-20 דקות. מכיוון שהם משוגרים מספינה שנודדת באגם, ניתן לצפות בהם מרוב נקודות החוף או מחדרי המלונות באזור האונסן.", 
                "img": "https://images.unsplash.com/photo-1513151233558-d860c5398176?w=500"
            },
            {
                "id": "a10", 
                "name": "מוזיאון המדע הוולקני", 
                "price_ils": 15, 
                "desc": "מקום מצוין להבין את ההיסטוריה הגיאולוגית של האזור, במיוחד אם אתם מתכננים לעלות להר אוסו, שכן המוזיאון מסביר על ההתפרצויות שהתרחשו באזור.", 
                "img": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=500"
            }
        ],
        "אאומורי": [
            {
                "id": "a11", 
                "name": "מרכז Nokkedon (Aomori Gyosai Center)", 
                "price_ils": 50, 
                "desc": "חוויה קולינרית ייחודית – אתם קונים קופון לאורז, ואז עוברים בין הדוכנים בשוק ובוחרים תוספות של דגים ופירות ים טריים לפי טעמכם האישי עד שהקערה מלאה. זו הדרך הטובה ביותר לטעום את הדגה המקומית המפורסמת של האזור.", 
                "img": "https://images.unsplash.com/photo-1553163147-622ab57be1c2?w=500"
            },
            {
                "id": "a12", 
                "name": "מרכז התיירות ASPAM", 
                "price_ils": 0, 
                "desc": "מבנה משולש ומפורסם על קו המים. הוא משמש כמרכז מידע לתיירים, אך גם כולל חנויות מזכרות, מסעדות מקומיות ומרפסת תצפית שמשקיפה על מפרץ אאומורי וגשר האאומורי הגדול.", 
                "img": "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=500"
            },
            {
                "id": "a13", 
                "name": "נחל אואיראסה (Oirase Gorge)", 
                "price_ils": 0, 
                "desc": "זהו ללא ספק אתר הטבע המפורסם והמומלץ ביותר באזור. מסלול מישורי ונוח באורך של כ-14 ק\"מ העובר לצד נחל צלול, מפלים רבים, ומנהרות של עצים ירוקים.", 
                "img": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500"
            },
            {
                "id": "a14", 
                "name": "אגם טוואדה (Lake Towada)", 
                "price_ils": 0, 
                "desc": "האגם עצמו הוא לוע הר געש כחול ועמוק, והאזור סביבו מיוער ושקט מאוד. כולל שבילי הליכה המובילים למקדש טוואדה ולפסל שתי הבנות.", 
                "img": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=500"
            },
            {
                "id": "a15", 
                "name": "הר האקודה (Mount Hakkoda)", 
                "price_ils": 60, 
                "desc": "אם אתם מחפשים משהו קצת יותר הררי ופחות \"מישורי\", זה המקום. יש כאן רכבל (Hakkoda Ropeway) שלוקח אתכם לגובה רב, ומשם יש מסלולי הליכה (Trekking) מעגליים יפהפיים.", 
                "img": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=500"
            }
        ],
        "טוקיו": [
            {
                "id": "a16", 
                "name": "מקדש Meiji Shrine ויערות מייג'י", 
                "price_ils": 0, 
                "desc": "הליכה מרגיעה בתוך יער עבות של אלפי עצים בלב העיר הגדולה. הכניסה למקדש השינטו המרכזי מציעה שקט מוחלט, שבילים רחבים ועצים עצומים שגורמים לשכוח שאתה נמצא במטרופולין.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a17", 
                "name": "רחוב Takeshita ואופנת הרחוב ב-Harajuku", 
                "price_ils": 20, 
                "desc": "מעבר מהשקט של המקדש אל הרחוב הכי צבעוני, משוגע ואופנתי של הצעירים ביפן. חנויות אופנה ייחודיות ואביזרים. חובה לנסות את הקרפ היפני המפורסם.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a18", 
                "name": "שדרת הארכיטקטורה Omotesando", 
                "price_ils": 0, 
                "desc": "שדרת הסטייל והארכיטקטורה של טוקיו (המכונה לעיתים ה\"שנז אליזה\" של טוקיו). שופינג של מותגים, מעצבים, חנויות קונספט מרשימות ובניינים בעיצוב אדריכלי מודרני מרהיב.", 
                "img": "https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?w=500"
            },
            {
                "id": "a19", 
                "name": "פארק Shinjuku Gyoen", 
                "price_ils": 15, 
                "desc": "אחד הפארקים היפים והמרשימים ביותר בטוקיו. משלב גנים בסגנון יפני מסורתי, אנגלי וצרפתי, מדשאות ענק ועצים מדהימים.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a20", 
                "name": "תצפית בניין הממשל", 
                "price_ils": 0, 
                "desc": "עלייה לתצפית פנורמית יפהפייה בקומה גבוהה על כל העיר. הכניסה חינם לגמרי.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a21", 
                "name": "סדנת בנטו", 
                "price_ils": 308, 
                "desc": "שיעור בישול אומנותי של בנטו עם דמויות חמודות (20.9 בשעה 11:30).", 
                "img": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500"
            },
            {
                "id": "a22", 
                "name": "סדנה להכנת צ'ופסטיקס", 
                "price_ils": 39, 
                "desc": "סדנה ייחודית (20.9 בשעה 15:30).", 
                "img": "https://images.unsplash.com/photo-1553163147-622ab57be1c2?w=500"
            },
            {
                "id": "a23", 
                "name": "הכנת סושי וסיור בשוק צוקיג'י", 
                "price_ils": 370, 
                "desc": "כולל טעימת טונה (19.9 בשעה 9:30).", 
                "img": "https://images.unsplash.com/photo-1553163147-622ab57be1c2?w=500"
            },
            {
                "id": "a38", 
                "name": "מתחם Hibiya Okuroji", 
                "price_ils": 0, 
                "desc": "סמטה מקורה, ארוכה ומעוצבת תחת קשתות הרכבת המלאה במסעדות קטנות, ברי יין, ודוכני אוכל איכותיים.", 
                "img": "https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=500"
            },
            {
                "id": "a39", 
                "name": "סמטאות Yurakucho Gachashita", 
                "price_ils": 0, 
                "desc": "סמטאות אותנטיות שמשקפות את החוויה הפרועה והאמיתית עם שולחנות ארגזי פלסטיק, ריח גריל פחמים ועשן.", 
                "img": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=500"
            },
            {
                "id": "a40", 
                "name": "קניות במרכזי השופינג של Shinjuku", 
                "price_ils": 0, 
                "desc": "אזור הקניות הענק של שינג'וקו הכולל מרכזי קניות ענקיים, כלבו יפניים מטורפים וחנויות ענק של מותגים.", 
                "img": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=500"
            },
            {
                "id": "a41", 
                "name": "סמטת Omoide Yokocho", 
                "price_ils": 0, 
                "desc": "סמטה צרה וציורית ליד תחנת שינג'וקו מלאה בדוכני יאקיטורי קטנים, שרפרפים צפופים ועשן גריל ריחני באווירה נוסטלגית.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a42", 
                "name": "ראש הגודזילה בשינג'וקו", 
                "price_ils": 0, 
                "desc": "ראש הגודזילה המפורסם שמציץ ומפחיד את העוברים ושבים מלמעלה, מעל בניין קולנוע Gracery.", 
                "img": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500"
            },
            {
                "id": "a43", 
                "name": "מקדש Asakusa & Nakamise-dori", 
                "price_ils": 0, 
                "desc": "ביקור במקדש Senso-ji – המקדש הבודהיסטי העתיק והמרשים ביותר בטוקיו, והליכה ברחוב Nakamise-dori השוקק.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a44", 
                "name": "גינות Hamarikyu Gardens", 
                "price_ils": 15, 
                "desc": "גן היסטורי מדהים הממוקם ממש על המים, משלב בריכות מי ים מתחלפות, מרחבים ירוקים ובית תה מסורתי.", 
                "img": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=500"
            },
            {
                "id": "a45", 
                "name": "שוק Ameyoko Market (Ueno)", 
                "price_ils": 0, 
                "desc": "שוק רחוב פתוח, תוסס ואותנטי באזור אונו, המלא בדוכני אוכל רחוב מקומי, פירות טריים ומציאות.", 
                "img": "https://images.unsplash.com/photo-1553163147-622ab57be1c2?w=500"
            },
            {
                "id": "a46", 
                "name": "פארק Ueno ואגם Shinobazu", 
                "price_ils": 0, 
                "desc": "פארק ענק, ירוק ויפהפה שכולל שבילי הליכה מוצלים ואגם פיונים ענק שבו אפשר לשכור סירות פדלים.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            }
        ],
        "טאקאיאמה": [
            {
                "id": "a24", 
                "name": "קאמיקוצ'י (Kamikochi)", 
                "price_ils": 60, 
                "desc": "זהו אחד המקומות הכי יפים בכל יפן – עמק אלפיני עצום המוקף בפסגות מחודדות של האלפים הצפוניים, נהר כחול וצלול (Azusa River) ויערות ענקיים.", 
                "img": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=500"
            },
            {
                "id": "a25", 
                "name": "רכבל שינהוטאקה (Shinhotaka Ropeway)", 
                "price_ils": 120, 
                "desc": "רכבל דו-קומתי מרהיב שלוקח אותך גבוה אל פסגות האלפים היפניים. למעלה יש מרפסת תצפית ענקית בגג הבניין שמציעה נוף פנורמי מטורף של 360 מעלות.", 
                "img": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=500"
            },
            {
                "id": "a26", 
                "name": "שיזוקאווה-גו (Shirakawa-go)", 
                "price_ils": 50, 
                "desc": "כפר ציורי ומפורסם ברמה עולמית המוכר בזכות בתי העץ העתיקים שלו הבנויים בסגנון Gassho-zukuri – גגות קש תלולים מאוד שנראים כמו ידיים בתפילה.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a27", 
                "name": "העיר העתיקה (Sanmachi Suji)", 
                "price_ils": 0, 
                "desc": "סמטאות שימור היסטוריות מתקופת אדו, מלאות בבתי עץ שחורים עתיקים, חנויות למכירת יינות אורז מקומיים (Sake Breweries), חנויות אומנות ומסעדות קטנות.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a28", 
                "name": "סדנת בובה", 
                "price_ils": 122, 
                "desc": "סדנה מקומית (23.9 עד 15:30).", 
                "img": "https://images.unsplash.com/photo-1553163147-622ab57be1c2?w=500"
            },
            {
                "id": "a47", 
                "name": "שווקי הבוקר (Miyagawa / Jinya-mae)", 
                "price_ils": 0, 
                "desc": "שווקים צבעוניים שפועלים בבוקר לאורך הנהר, בהם חקלאים מקומיים מוכרים תוצרת טרייה, חמוצים, מזכרות ועבודות יד.", 
                "img": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=500"
            },
            {
                "id": "a48", 
                "name": "הרובע המסורתי Takayama Jinya", 
                "price_ils": 30, 
                "desc": "מתחם של ממשלת העיר הישנה מתקופת הסמוראים – מבנה ממשלתי עתיק ומרשים ששמור בצורה מדהימה.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a49", 
                "name": "מסלול המקדשים (Higashiyama)", 
                "price_ils": 0, 
                "desc": "מסלול הליכה נעים ושקט דרך יער ויותר מתריסר מקדשים ומקדש בודהיסטי אחד שקט, שמתחבר גם למבצר הישן.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            }
        ],
        "קיוטו": [
            {
                "id": "a29", 
                "name": "Arashiyama Bamboo Grove (יער הבמבוק)", 
                "price_ils": 0, 
                "desc": "שבילי הליכה מוקפים עצי במבוק עצומים (מומלץ להגיע מוקדם בבוקר לשקט ולבד מרוב התיירים).", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a30", 
                "name": "Kinkakuji Golden Pavilion (מקדש הזהב)", 
                "price_ils": 25, 
                "desc": "מקדש זן בודהיסטי מפורסם שחלקו העליון מצופה זהב טהור ומשתקף בבריכת מים גדולה.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a31", 
                "name": "Fushimi Inari Shrine", 
                "price_ils": 0, 
                "desc": "מקדש השינטו המפורסם עם אינסוף שערי טורי כתומים שיוצרים שבילי הליכה מטפסים במעלה ההר.", 
                "img": "https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?w=500"
            },
            {
                "id": "a32", 
                "name": "סיור הליכה בקיוטו", 
                "price_ils": 154, 
                "desc": "סיור מודרך בתאריך 26.9 בשעה 18:20.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a50", 
                "name": "Iwatayama Monkey Park (פארק הקופים)", 
                "price_ils": 30, 
                "desc": "טיפוס קצר במעלה ההר שמוביל לתצפית מעולה על העיר ולמפגש עם קופים חופשיים.", 
                "img": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=500"
            },
            {
                "id": "a51", 
                "name": "Hozu River Cruise (שייט על נהר הוזו)", 
                "price_ils": 100, 
                "desc": "שייט מסורתי של כשעתיים בסירות עץ בין קניונים הרריים וירוקים שמתחבר לאזור אראשיימה.", 
                "img": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=500"
            },
            {
                "id": "a52", 
                "name": "Nijo Castle (טירת ניג'ו)", 
                "price_ils": 40, 
                "desc": "ארמון שוגון היסטורי המפורסם ב\"רצפות הזמיר\" המצייצות כשדורכים עליהן כאמצעי הגנה עתיק נגד מתנקשים.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a53", 
                "name": "Nishiki Market (שוק נישיקי)", 
                "price_ils": 0, 
                "desc": "שוק אוכל מקורה וצפוף המכונה \"המטבח של קיוטו\" – מושלם לטעימות של מאכלים מקומיים, מנות קטנות ואוכל רחוב.", 
                "img": "https://images.unsplash.com/photo-1553163147-622ab57be1c2?w=500"
            },
            {
                "id": "a54", 
                "name": "Sanjusangendo Temple", 
                "price_ils": 30, 
                "desc": "מקדש מרתק שבו שוכנים בדיוק 1,001 פסלי בודהה מוזהבים שעומדים בשורות צפופות.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a55", 
                "name": "Gion & Pontocho Alley (רובע גיון)", 
                "price_ils": 0, 
                "desc": "רובע הגיישות ההיסטורי של קיוטו וסמטאות צרות מלאות בבתי עץ מסורתיים, פנסים ומסעדות.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a56", 
                "name": "Kiyomizu-dera Temple (מקדש קיומיזו-דרה)", 
                "price_ils": 40, 
                "desc": "מקדש מפורסם על ההר עם מרפסת עץ ענקית הבנויה ללא מסמרים ומשקיפה על נוף פנורמי של העיר.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a57", 
                "name": "Ninenzaka & Sannenzaka", 
                "price_ils": 0, 
                "desc": "הסמטאות העתיקות והציוריות ביותר ביפן המובילות למקדש קיומיזו-דרה, מלאות בבתי עץ וחנויות.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a58", 
                "name": "Ginkaku-ji Temple (מקדש הכסף)", 
                "price_ils": 30, 
                "desc": "מקדש זן שקט ומוקף בגני חול ואסתטיקה יפנית נקייה ומאופקת.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a59", 
                "name": "Philosopher's Path (שביל הפילוסוף)", 
                "price_ils": 0, 
                "desc": "שביל הליכה פסטורלי לאורך תעלת מים שקטה המוצלת בעצי דובדבן.", 
                "img": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=500"
            },
            {
                "id": "a60", 
                "name": "Kyoto Imperial Palace (הארמון הקיסרי)", 
                "price_ils": 0, 
                "desc": "מתחם עצום בלב העיר ששימש כמשכנם של קיסרי יפן, מוקף בגנים רחבי ידיים.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a61", 
                "name": "Kyoto Railway Museum", 
                "price_ils": 50, 
                "desc": "מוזיאון ענק ומרתק המציג רכבות היסטוריות וסימולטורים של נהיגה.", 
                "img": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=500"
            },
            {
                "id": "a62", 
                "name": "Kawaramachi & Shijo-dori", 
                "price_ils": 0, 
                "desc": "לב השופינג המודרני, משלב קניונים עצומים, חנויות אופנה בינלאומיות ויפניות ורחובות קניות ראשיים.", 
                "img": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=500"
            },
            {
                "id": "a63", 
                "name": "Teramachi & Shinkyogoku Arcades", 
                "price_ils": 0, 
                "desc": "שתי מגלשות שופינג זו לצד זו עם אווירה צעירה, חנויות בגדים, מזכרות וארקיידים.", 
                "img": "https://images.unsplash.com/photo-1553163147-622ab57be1c2?w=500"
            },
            {
                "id": "a64", 
                "name": "Kyoto Station / The Cube / Porta", 
                "price_ils": 0, 
                "desc": "מפלצת שופינג עם קניון ענק, מתחמי ראמן ושווקי מזכרות ואוכל.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a65", 
                "name": "Kyoto Handicraft Center", 
                "price_ils": 0, 
                "desc": "בניין בן כמה קומות שמוקדש לאמנות ומלאכת יד יפנית מקורית (חרבות, קימונו, חרס וכדומה).", 
                "img": "https://images.unsplash.com/photo-1549488344-cbb6c34cf08b?w=500"
            }
        ],
        "אוסקה": [
            {
                "id": "a33", 
                "name": "Dotonbori", 
                "price_ils": 0, 
                "desc": "שדרה צבעונית, רועשת וחיה עם שילוט ניאון מטורף ואוכל רחוב מהמעולים שתאכל ביפן.", 
                "img": "https://images.unsplash.com/photo-1590523277543-a94d2e4eb00b?w=500"
            },
            {
                "id": "a34", 
                "name": "Osaka Castle", 
                "price_ils": 30, 
                "desc": "אחת הסמלים הבולטים ביותר של העיר. טירה היסטורית מרשימה שממוקמת בתוך פארק ענק ויפהפה מוקף תעלות מים וחומה.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a35", 
                "name": "Aquarium Kaiyukan", 
                "price_ils": 100, 
                "desc": "אקווריום עצום ומרשים מהגדולים בעולם.", 
                "img": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=500"
            },
            {
                "id": "a36", 
                "name": "סיור בישול ארוחת בוקר יפנית", 
                "price_ils": 270, 
                "desc": "שיעור בישול של ארוחת בוקר יפנית (2.10 בשעה 10:00).", 
                "img": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500"
            },
            {
                "id": "a37", 
                "name": "17 טעמים של טקויאקי", 
                "price_ils": 212, 
                "desc": "הכינו כמה שאתם יכולים לאכול ולשתות (1.10 בשעה 18:00).", 
                "img": "https://images.unsplash.com/photo-1553163147-622ab57be1c2?w=500"
            },
            {
                "id": "a66", 
                "name": "Rikuro’s Cheesecake", 
                "price_ils": 30, 
                "desc": "חנות עוגות הגבינה המפורסמת - להגיע מוקדם, כי התור יכול להימשך כשעה.", 
                "img": "https://images.unsplash.com/photo-1549488344-cbb6c34cf08b?w=500"
            },
            {
                "id": "a67", 
                "name": "Katsuo-Ji Temple", 
                "price_ils": 25, 
                "desc": "מקדש מיוחד עם מאות בובות אדומות בכל פינה.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a68", 
                "name": "Orange Street", 
                "price_ils": 0, 
                "desc": "רחוב מעוצב עם חנויות עיצוב, רהיטים ובגדים טרנדיים.", 
                "img": "https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?w=500"
            },
            {
                "id": "a69", 
                "name": "Tempozan Giant Ferris Wheel", 
                "price_ils": 40, 
                "desc": "גלגל ענק עם תצפית מטורפת על העיר, ליד האקווריום.", 
                "img": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=500"
            },
            {
                "id": "a70", 
                "name": "Kuromon Market", 
                "price_ils": 0, 
                "desc": "שוק אוכל ותוצרת יפנית מקומית. לטעום!", 
                "img": "https://images.unsplash.com/photo-1553163147-622ab57be1c2?w=500"
            },
            {
                "id": "a71", 
                "name": "Umeda Sky Building", 
                "price_ils": 50, 
                "desc": "תצפית בגובה ונוף של כל אוסקה.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a72", 
                "name": "Namba Yasaka Shrine", 
                "price_ils": 0, 
                "desc": "מקדש עם ראש אריה ענק.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a73", 
                "name": "Shinsekai", 
                "price_ils": 0, 
                "desc": "שכונה צבעונית עם אווירה, מגדל טסוטנקקו ואוכל רחוב.", 
                "img": "https://images.unsplash.com/photo-1590523277543-a94d2e4eb00b?w=500"
            },
            {
                "id": "a74", 
                "name": "Timeout Osaka (שוק אוכל)", 
                "price_ils": 0, 
                "desc": "שוק אוכל חדש - לעבור בין הדוכנים ולטעום מנות קטנות.", 
                "img": "https://images.unsplash.com/photo-1553163147-622ab57be1c2?w=500"
            },
            {
                "id": "a75", 
                "name": "Den Den Town", 
                "price_ils": 0, 
                "desc": "אזור האלקטרוניקה והאנימה של אוסקה.", 
                "img": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=500"
            },
            {
                "id": "a76", 
                "name": "Shitenno-ji Temple", 
                "price_ils": 30, 
                "desc": "אחד המקדשים הבודהיסטיים העתיקים ביותר ביפן (נבנה במאה ה-6) עם פגודה בת 5 קומות.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a77", 
                "name": "Hozenji Yokocho", 
                "price_ils": 0, 
                "desc": "סמטה צרה ומרוצפת אבן קרובה לדוטונבורי עם פנסים מסורתיים ומקדש עם פסל בודהה מכוסה טחב.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a78", 
                "name": "Amerikamura", 
                "price_ils": 0, 
                "desc": "השכונה ה\"אלטרנטיבית\" והצעירה של אוסקה עם אופנת רחוב, חנויות וינטג' ואמנות רחוב.", 
                "img": "https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?w=500"
            },
            {
                "id": "a79", 
                "name": "Nakazakicho", 
                "price_ils": 0, 
                "desc": "שכונה וינטג'ית ומקסימה עם בתי עץ ישנים מימי פוסט מלחמת העולם השנייה, בתי קפה בוטיקיים וגלריות.", 
                "img": "https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=500"
            }
        ]
    }
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                for key in DEFAULT_TRIP_DATA:
                    if key not in data:
                        data[key] = DEFAULT_TRIP_DATA[key]
                return data
            except json.JSONDecodeError:
                return DEFAULT_TRIP_DATA
    return DEFAULT_TRIP_DATA

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

app = Flask(__name__)

LAYOUT = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>תכנון טיול ליפן 🇯🇵</title>
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#6366f1">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="טיול ליפן">
    <style>
        :root {
            --bg-color: #0b0c10;
            --card-bg: #14151b;
            --card-hover: #1c1e26;
            --border-color: #272935;
            --text-color: #f4f4f5;
            --text-muted: #94a3b8;
            --accent-color: #6366f1;
            --accent-hover: #818cf8;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            --success-color: #10b981;
            --danger-color: #ef4444;
        }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            background-color: var(--bg-color); 
            color: var(--text-color); 
            margin: 0; 
            padding: 15px; 
            -webkit-font-smoothing: antialiased;
        }
        
        .container { 
            max-width: 1100px; 
            margin: auto; 
            background: var(--card-bg); 
            padding: 24px; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.6); 
            border: 1px solid var(--border-color);
        }
        
        @media(min-width: 768px) {
            body { padding: 40px; }
            .container { padding: 40px; }
        }

        h1, h2, h3 { 
            color: #fff; 
            text-align: center; 
            font-weight: 700;
        }
        
        h1 { 
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2rem; 
            margin-bottom: 8px; 
        }
        
        @media(min-width: 768px) {
            h1 { font-size: 2.6rem; }
        }
        
        nav { 
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 8px;
            margin-bottom: 30px; 
            background: #0f1015; 
            padding: 8px; 
            border-radius: 14px;
            border: 1px solid var(--border-color);
        }
        
        nav a { 
            color: var(--text-muted); 
            text-decoration: none; 
            padding: 10px 16px;
            border-radius: 10px;
            font-weight: 600; 
            font-size: 14px; 
            transition: all 0.2s ease;
            text-align: center;
        }
        
        nav a:hover { 
            color: #fff; 
            background: rgba(99, 102, 241, 0.15); 
        }

        .table-responsive {
            width: 100%;
            overflow-x: auto;
            margin-bottom: 30px;
            -webkit-overflow-scrolling: touch;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        
        table { 
            width: 100%; 
            border-collapse: collapse; 
            background: #111218;
            min-width: 320px;
        }
        
        th, td { 
            padding: 14px 18px; 
            border-bottom: 1px solid var(--border-color); 
            text-align: right; 
            font-size: 14px;
        }
        
        th { 
            background-color: #181922; 
            color: #fff;
            font-weight: 600;
            letter-spacing: 0.03em;
        }
        
        tr:last-child td {
            border-bottom: none;
        }
        
        tr:hover td { 
            background-color: var(--card-hover); 
        }

        input[type="number"], input[type="text"] { 
            padding: 10px 14px; 
            font-size: 14px; 
            background: #0b0c10;
            border: 1px solid var(--border-color);
            color: #fff;
            border-radius: 10px;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        
        input[type="number"] { width: 90px; text-align: center; }
        
        @media(min-width: 768px) {
            input[type="number"] { width: 120px; }
        }
        
        input[type="text"] { width: 100%; box-sizing: border-box; }
        
        input:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
            outline: none;
        }

        button { 
            background: var(--accent-gradient);
            color: white; 
            border: none; 
            padding: 12px 28px; 
            border-radius: 12px; 
            cursor: pointer; 
            font-size: 15px; 
            font-weight: 600; 
            transition: transform 0.1s ease, opacity 0.2s;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
            width: 100%;
        }
        
        @media(min-width: 768px) {
            button { width: auto; }
        }
        
        button:hover { opacity: 0.9; }
        button:active { transform: scale(0.98); }

        .copy-btn {
            background-color: #21232d;
            color: #e2e8f0;
            border: 1px solid var(--border-color);
            padding: 6px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.2s;
            width: auto;
            box-shadow: none;
        }
        
        .copy-btn:hover {
            background-color: var(--accent-color);
            border-color: var(--accent-color);
            color: #fff;
        }

        .danger-btn {
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
            padding: 6px 12px;
            font-size: 12px;
            border-radius: 8px;
            width: auto;
            box-shadow: none;
        }
        
        .danger-btn:hover {
            background-color: var(--danger-color);
            color: #fff;
        }

        .total-box { 
            background: linear-gradient(135deg, #181922 0%, #111218 100%);
            border: 1px solid var(--border-color);
            padding: 24px; 
            border-radius: 16px; 
            text-align: center; 
            font-size: 22px; 
            font-weight: bold; 
            margin-top: 35px; 
            color: var(--success-color);
            box-shadow: inset 0 2px 6px rgba(0,0,0,0.3);
        }
        
        @media(min-width: 768px) {
            .total-box { font-size: 28px; padding: 30px; }
        }
        
        .filter-nav {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 8px;
            margin-bottom: 30px;
        }
        
        .filter-btn {
            background-color: #111218;
            color: var(--text-muted);
            border: 1px solid var(--border-color);
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.2s ease;
            box-shadow: none;
            width: auto;
        }
        
        .filter-btn:hover, .filter-btn.active {
            background: var(--accent-gradient);
            color: #fff;
            border-color: transparent;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }

        .attractions-grid { 
            display: grid; 
            grid-template-columns: 1fr; 
            gap: 20px; 
            margin-bottom: 35px; 
        }
        
        @media(min-width: 600px) {
            .attractions-grid { grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
        }

        .attraction-card { 
            background: #111218; 
            border: 1px solid var(--border-color); 
            border-radius: 16px; 
            overflow: hidden; 
            display: flex; 
            flex-direction: column; 
            justify-content: space-between;
            transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s;
        }
        
        .attraction-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 30px rgba(0,0,0,0.5);
            border-color: rgba(99, 102, 241, 0.4);
        }
        
        .attraction-card img { 
            width: 100%; 
            height: 160px; 
            object-fit: cover; 
            cursor: pointer;
            transition: opacity 0.2s;
        }
        
        .attraction-card img:hover {
            opacity: 0.9;
        }
        
        .attraction-body { 
            padding: 16px; 
        }
        
        .attraction-body h4 { 
            margin: 0 0 8px 0; 
            color: #fff; 
            font-size: 16px;
            cursor: pointer;
            transition: color 0.2s;
        }
        
        .attraction-body h4:hover {
            color: var(--accent-hover);
        }
        
        .attraction-body p { 
            font-size: 13px; 
            color: var(--text-muted); 
            margin: 0;
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .attraction-footer { 
            padding: 12px 16px; 
            background: #15161f; 
            border-top: 1px solid var(--border-color); 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            font-size: 13px;
            color: var(--text-muted);
        }
        
        .city-section {
            margin-bottom: 30px;
        }
        
        .city-title {
            color: var(--success-color);
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 10px;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 1.4rem;
            text-align: right;
        }

        .checklist-card {
            background: #111218;
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 25px;
            transition: border-color 0.2s;
        }
        
        .checklist-card:hover {
            border-color: rgba(99, 102, 241, 0.3);
        }
        
        .checklist-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 12px;
            margin-bottom: 15px;
            cursor: pointer;
            user-select: none;
        }
        
        .checklist-header h3 {
            margin: 0;
            color: #fff;
            font-size: 1.15rem;
            text-align: right;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .toggle-icon {
            font-size: 12px;
            color: var(--text-muted);
            transition: transform 0.3s ease;
        }
        
        .checklist-card.collapsed .toggle-icon {
            transform: rotate(-90deg);
        }
        
        .checklist-content-wrapper {
            max-height: 2000px;
            overflow: hidden;
            transition: max-height 0.4s ease, opacity 0.3s ease;
            opacity: 1;
        }
        
        .checklist-card.collapsed .checklist-content-wrapper {
            max-height: 0;
            opacity: 0;
            margin: 0;
            padding: 0;
        }
        
        .checklist-items {
            list-style: none;
            padding: 0;
            margin: 0 0 15px 0;
        }
        
        .checklist-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px dashed var(--border-color);
        }
        
        .checklist-item label {
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            font-size: 14px;
            flex-grow: 1;
        }
        
        .checklist-item input[type="checkbox"] {
            width: 20px;
            height: 20px;
            accent-color: var(--success-color);
            cursor: pointer;
            border-radius: 4px;
        }
        
        .checklist-item.done span {
            text-decoration: line-through;
            color: var(--text-muted);
            opacity: 0.7;
        }
        
        .add-item-form {
            display: flex;
            gap: 10px;
        }
        
        .add-item-form input {
            flex-grow: 1;
        }
        
        .add-item-form button {
            width: auto;
            padding: 10px 20px;
            font-size: 14px;
            background: var(--success-color);
            box-shadow: none;
        }
        
        .add-item-form button:hover {
            opacity: 0.9;
        }

        .modal {
            display: none; 
            position: fixed; 
            z-index: 1000; 
            left: 0;
            top: 0;
            width: 100%; 
            height: 100%; 
            background-color: rgba(5,6,8,0.85); 
            backdrop-filter: blur(8px);
            align-items: center;
            justify-content: center;
            padding: 15px;
            box-sizing: border-box;
        }
        
        .modal-content {
            background-color: #14151b;
            border: 1px solid var(--border-color);
            padding: 24px;
            border-radius: 20px;
            width: 100%;
            max-width: 500px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.7);
            position: relative;
            text-align: right;
            animation: modalOpen 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            max-height: 85vh;
            overflow-y: auto;
        }
        
        @keyframes modalOpen {
            from {transform: scale(0.92); opacity: 0;}
            to {transform: scale(1); opacity: 1;}
        }
        
        .modal-content img {
            width: 100%;
            height: 220px;
            object-fit: cover;
            border-radius: 12px;
            margin-bottom: 16px;
        }
        
        .modal-content h3 {
            margin-top: 0;
            color: #fff;
            font-size: 20px;
            text-align: right;
        }
        
        .modal-content p {
            color: var(--text-muted);
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 24px;
            text-align: right;
        }
        
        .close-btn {
            background: var(--border-color);
            color: #fff;
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            width: 100%;
            box-shadow: none;
        }
        
        @media(min-width: 768px) {
            .close-btn { width: auto; float: left; }
        }
        
        .close-btn:hover {
            background: #3f4255;
            opacity: 1;
        }
        
        .toast {
            visibility: hidden;
            min-width: 220px;
            background-color: var(--success-color);
            color: #fff;
            text-align: center;
            border-radius: 10px;
            padding: 12px 20px;
            position: fixed;
            z-index: 2000;
            left: 50%;
            bottom: 30px;
            transform: translateX(-50%);
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
        }
        
        .toast.show {
            visibility: visible;
            animation: fadein 0.4s, fadeout 0.4s 2.2s;
        }
        
        @keyframes fadein {
            from {bottom: 0; opacity: 0;}
            to {bottom: 30px; opacity: 1;}
        }
        
        @keyframes fadeout {
            from {bottom: 30px; opacity: 1;}
            to {bottom: 0; opacity: 0;}
        }
    </style>
</head>
<body>
<div class="container">
    <nav>
        <a href="/">דף הבית וסיכום</a>
        <a href="/stays">טיסות ומלונות</a>
        <a href="/trains">רכבות</a>
        <a href="/attractions">אטרקציות ופעילויות</a>
        <a href="/checklists">רשימות צ'ק-ליסט</a>
        <a href="/converter">💱 ממיר מטבע</a>
    </nav>
    {{ content | safe }}
</div>

<div id="infoModal" class="modal">
    <div class="modal-content">
        <img id="modalImg" src="" alt="">
        <h3 id="modalTitle"></h3>
        <p id="modalDesc"></p>
        <button class="close-btn" onclick="closeModal()">סגור</button>
        <div style="clear: both;"></div>
    </div>
</div>

<div id="toast" class="toast">הכתובת הועתקה ללוח! 📋</div>

<script>
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js')
                .then(reg => console.log('Service Worker registered! scope:', reg.scope))
                .catch(err => console.log('Service Worker registration failed:', err));
        });
    }

    function openModal(name, desc, img) {
        document.getElementById('modalTitle').innerText = name;
        document.getElementById('modalDesc').innerText = desc;
        document.getElementById('modalImg').src = img;
        document.getElementById('infoModal').style.display = 'flex';
    }

    function closeModal() {
        document.getElementById('infoModal').style.display = 'none';
    }

    window.onclick = function(event) {
        var modal = document.getElementById('infoModal');
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }

    function copyAddress(addressText) {
        var textarea = document.createElement("textarea");
        textarea.value = addressText;
        textarea.style.position = "fixed";  
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();

        try {
            var successful = document.execCommand('copy');
            if (successful) {
                var toast = document.getElementById("toast");
                toast.className = "toast show";
                setTimeout(() => { toast.className = toast.className.replace("show", ""); }, 2500);
            } else {
                alert("ההעתקה נכשלה. נסה להעתיק ידנית.");
            }
        } catch (err) {
            console.error('Failed to copy text: ', err);
            alert("שגיאה בהעתקת הטקסט.");
        }

        document.body.removeChild(textarea);
    }

    function toggleChecklist(headerElem) {
        var card = headerElem.closest('.checklist-card');
        card.classList.toggle('collapsed');
    }

    function filterAttractions(cityName, btnElem) {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btnElem.classList.add('active');

        document.querySelectorAll('.city-section').forEach(section => {
            if (cityName === 'all' || section.getAttribute('data-city') === cityName) {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        });
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    trip_data = load_data()
    total = (
        sum(item['price_ils'] for item in trip_data['trains']) +
        sum(item['price_ils'] for item in trip_data['hotels']) +
        sum(item['price_ils'] for item in trip_data['flights']) +
        sum(item['price_ils'] for city_attrs in trip_data['attractions'].values() for item in city_attrs)
    )
    content = f"""
    <h1>טיול ליפן 2026 🇯🇵</h1>
    <p style="text-align: center; color: var(--text-muted); font-size: 15px; margin-bottom: 30px;">מערכת ניהול מתקדמת לתקציב ולמסלול הטיול שלך. בחר בתפריט מעלה לעדכון מחירים.</p>
    <div class="total-box">
        סך הכל כללי משוער לטיול: ₪{total:,.2f}
    </div>

    <!-- ווידג'ט ממיר מטבע מהיר בדף הבית -->
    <div class="checklist-card" style="margin-top: 30px;">
        <h3 style="text-align: right; margin-top: 0; color: #fff; font-size: 1.2rem;">💱 ממיר שקל (ILS) ל-ין יפני (JPY) בזמן אמת</h3>
        <p style="color: var(--text-muted); font-size: 13px; text-align: right; margin-bottom: 20px;">השער מתעדכן אוטומטית מול הרשת.</p>
        <div style="display: flex; gap: 15px; flex-wrap: wrap; justify-content: center; align-items: center;">
            <div style="flex: 1; min-width: 200px;">
                <label style="display: block; font-size: 13px; color: var(--text-muted); margin-bottom: 6px; text-align: right;">שקלים (₪):</label>
                <input type="number" id="ilsInput" placeholder="הכנס סכום ב-₪" style="width: 100%; box-sizing: border-box;" oninput="convertFromIls()">
            </div>
            <div style="font-size: 24px; color: var(--accent-hover); font-weight: bold; align-self: flex-end; padding-bottom: 8px;">⇄</div>
            <div style="flex: 1; min-width: 200px;">
                <label style="display: block; font-size: 13px; color: var(--text-muted); margin-bottom: 6px; text-align: right;">ין יפני (¥):</label>
                <input type="number" id="jpyInput" placeholder="הכנס סכום ב-¥" style="width: 100%; box-sizing: border-box;" oninput="convertFromJpy()">
            </div>
        </div>
        <div id="rateStatus" style="text-align: center; font-size: 12px; color: var(--text-muted); margin-top: 15px;">טוען שער חליפין חי...</div>
    </div>

    <script>
        let liveRate = 40.0; // ברירת מחדל זמנית עד שה-API מטעין
        
        async function fetchExchangeRate() {{
            try {{
                let response = await fetch('https://open.er-api.com/v6/latest/ILS');
                let data = await response.json();
                if (data && data.rates && data.rates.JPY) {{
                    liveRate = data.rates.JPY;
                    document.getElementById('rateStatus').innerText = `שער חליפין מעודכן: 1 ₪ = ${{liveRate.toFixed(2)}} ¥`;
                }}
            }} catch(e) {{
                document.getElementById('rateStatus').innerText = 'משתמש בשער ברירת מחדל (שגיאת חיבור לרשת)';
            }}
        }}

        function convertFromIls() {{
            let ils = parseFloat(document.getElementById('ilsInput').value);
            if (isNaN(ils)) {{
                document.getElementById('jpyInput').value = '';
                return;
            }}
            document.getElementById('jpyInput').value = (ils * liveRate).toFixed(2);
        }}

        function convertFromJpy() {{
            let jpy = parseFloat(document.getElementById('jpyInput').value);
            if (isNaN(jpy)) {{
                document.getElementById('ilsInput').value = '';
                return;
            }}
            document.getElementById('ilsInput').value = (jpy / liveRate).toFixed(2);
        }}

        fetchExchangeRate();
    </script>
    """
    return render_template_string(LAYOUT, content=content)

@app.route('/converter')
def converter():
    content = f"""
    <h2>ממיר מטבע מתקדם (שקל ⇄ ין)</h2>
    <p style="text-align: center; color: var(--text-muted); font-size: 14px; margin-bottom: 25px;">המרה מדויקת ועדכנית לכל הוצאה או קנייה ביפן.</p>
    
    <div class="checklist-card" style="max-width: 600px; margin: auto; background: #14151b;">
        <div style="margin-bottom: 20px;">
            <label style="display: block; font-size: 14px; color: var(--text-muted); margin-bottom: 8px; text-align: right;">סכום בשקלים (ILS):</label>
            <input type="number" id="pageIlsInput" placeholder="הקלד שקלים..." style="width: 100%; box-sizing: border-box; font-size: 16px; padding: 14px;" oninput="pageConvertFromIls()">
        </div>
        <div style="margin-bottom: 20px;">
            <label style="display: block; font-size: 14px; color: var(--text-muted); margin-bottom: 8px; text-align: right;">סכום ביין יפני (JPY):</label>
            <input type="number" id="pageJpyInput" placeholder="הקלד ין..." style="width: 100%; box-sizing: border-box; font-size: 16px; padding: 14px;" oninput="pageConvertFromJpy()">
        </div>
        <div id="pageRateStatus" style="text-align: center; font-size: 13px; color: var(--success-color); font-weight: 600; margin-top: 15px;">טוען שער חליפין מהאינטרנט...</div>
    </div>

    <script>
        let pageLiveRate = 40.0;
        
        async function fetchPageExchangeRate() {{
            try {{
                let response = await fetch('https://open.er-api.com/v6/latest/ILS');
                let data = await response.json();
                if (data && data.rates && data.rates.JPY) {{
                    pageLiveRate = data.rates.JPY;
                    document.getElementById('pageRateStatus').innerText = `שער חי פעיל: 1 ILS = ${{pageLiveRate.toFixed(2)}} JPY`;
                }}
            }} catch(e) {{
                document.getElementById('pageRateStatus').innerText = 'משתמש בשער קבוע עקב תקשורת';
            }}
        }}

        function pageConvertFromIls() {{
            let ils = parseFloat(document.getElementById('pageIlsInput').value);
            if (isNaN(ils)) {{
                document.getElementById('pageJpyInput').value = '';
                return;
            }}
            document.getElementById('pageJpyInput').value = (ils * pageLiveRate).toFixed(2);
        }}

        function pageConvertFromJpy() {{
            let jpy = parseFloat(document.getElementById('pageJpyInput').value);
            if (isNaN(jpy)) {{
                document.getElementById('pageIlsInput').value = '';
                return;
            }}
            document.getElementById('pageIlsInput').value = (jpy / pageLiveRate).toFixed(2);
        }}

        fetchPageExchangeRate();
    </script>
    """
    return render_template_string(LAYOUT, content=content)

@app.route('/sw.js')
def service_worker():
    sw_code = """
    const CACHE_NAME = 'japan-trip-v1';
    const urlsToCache = [
        '/',
        '/stays',
        '/trains',
        '/attractions',
        '/checklists',
        '/converter',
        '/manifest.json'
    ];

    self.addEventListener('install', event => {
        event.waitUntil(
            caches.open(CACHE_NAME)
                .then(cache => cache.addAll(urlsToCache))
        );
    });

    self.addEventListener('fetch', event => {
        event.respondWith(
            caches.match(event.request)
                .then(response => {
                    if (response) {
                        return response;
                    }
                    return fetch(event.request).catch(() => {
                        if (event.request.mode === 'navigate') {
                            return caches.match('/');
                        }
                    });
                })
        );
    });
    """
    return sw_code, 200, {'Content-Type': 'application/javascript'}

@app.route('/stays', methods=['GET', 'POST'])
def stays():
    trip_data = load_data()
    if request.method == 'POST':
        return redirect(url_for('stays'))

    content = """
    <h2>ניהול טיסות ומלונות</h2>
    <p style="text-align: center; color: var(--text-muted); font-size: 14px; margin-bottom: 25px;">מחירי הטיסות והמלונות נעולים ואינם ניתנים לשינוי. ניתן להעתיק את כתובת המלון בלחיצה.</p>
    <form method="POST">
        <h3 style="text-align: right; color: var(--accent-hover); margin-top: 25px;">✈️ טיסות בינלאומיות</h3>
        <div class="table-responsive">
            <table>
                <tr><th>תיאור</th><th>מחיר ב-₪ (נעול)</th></tr>
    """
    
    for f in trip_data['flights']:
        content += f"<tr><td>{f['name']}</td><td><input type='number' step='0.01' name='flight_{f['id']}' value='{f['price_ils']}' readonly style='background-color: #14151b; color: #64748b; cursor: not-allowed;'></td></tr>"

    content += """
            </table>
        </div>

        <h3 style="text-align: right; color: var(--accent-hover); margin-top: 35px;">🏨 מלונות לאורך המסלול</h3>
        <div class="table-responsive">
            <table>
                <tr><th>מלון / תאריכים וכתובת</th><th>מחיר ב-₪ (נעול)</th></tr>
    """

    for h in trip_data['hotels']:
        safe_addr = h['address'].replace("'", "\\'").replace('"', '&quot;')
        content += f"""<tr>
            <td>
                <div style="font-weight: 600; margin-bottom: 4px; color: #fff;">{h['name']}</div>
                <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">{h['address']}</div>
                <button type="button" class="copy-btn" onclick="copyAddress('{safe_addr}')">📋 העתק כתובת</button>
            </td>
            <td><input type='number' step='0.01' name='hotel_{h['id']}' value='{h['price_ils']}' readonly style='background-color: #14151b; color: #64748b; cursor: not-allowed;'></td>
        </tr>"""

    content += """
            </table>
        </div>
    </form>
    """
    
    return render_template_string(LAYOUT, content=content)

@app.route('/manifest.json')
def manifest():
    return jsonify({
        "name": "תכנון טיול ליפן 2026",
        "short_name": "טיול ליפן",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0b0c10",
        "theme_color": "#6366f1",
        "icons": [
            {
                "src": "https://img.icons8.com/color/512/japan.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    })

@app.route('/trains', methods=['GET', 'POST'])
def trains():
    trip_data = load_data()
    if request.method == 'POST':
        for key, value in request.form.items():
            try:
                val_float = float(value)
                if key.startswith('train_'):
                    tid = key.replace('train_', '')
                    for t in trip_data['trains']:
                        if t['id'] == tid:
                            t['price_ils'] = val_float
            except ValueError:
                continue
        save_data(trip_data)
        return redirect(url_for('trains'))

    content = """
    <h2>ניהול רכבות בין עירוניות</h2>
    <form method="POST">
        <div class="table-responsive">
            <table>
                <tr><th>קו רכבת</th><th>מחיר ב-₪</th></tr>
                """ + "".join([f"<tr><td>{t['name']}</td><td><input type='number' step='0.01' name='train_{t['id']}' value='{t['price_ils']}'></td></tr>" for t in trip_data['trains']]) + """
            </table>
        </div>
        <div style="text-align: center; margin-top: 30px;"><button type="submit">שמור שינויים</button></div>
    </form>
    """
    return render_template_string(LAYOUT, content=content)

@app.route('/attractions', methods=['GET', 'POST'])
def attractions():
    trip_data = load_data()
    if request.method == 'POST':
        for key, value in request.form.items():
            try:
                val_float = float(value)
                if key.startswith('attr_'):
                    aid = key.replace('attr_', '')
                    for city_attrs in trip_data['attractions'].values():
                        for a in city_attrs:
                            if a['id'] == aid:
                                a['price_ils'] = val_float
            except ValueError:
                continue
        save_data(trip_data)
        return redirect(url_for('attractions'))

    filter_buttons_html = "<div class='filter-nav'><button type='button' class='filter-btn active' onclick=\"filterAttractions('all', this)\">הצג הכל</button>"
    for city in trip_data['attractions'].keys():
        filter_buttons_html += f"<button type='button' class='filter-btn' onclick=\"filterAttractions('{city}', this)\">{city}</button>"
    filter_buttons_html += "</div>"

    attrs_html = ""
    for city, attrs in trip_data['attractions'].items():
        attrs_html += f"""
        <div class="city-section" data-city="{city}">
            <h3 class='city-title'>📍 {city}</h3>
            <div class='attractions-grid'>
        """
        for a in attrs:
            safe_name = a['name'].replace("'", "&#39;").replace('"', '&quot;')
            safe_desc = a['desc'].replace("'", "&#39;").replace('"', '&quot;').replace('\n', ' ')
            
            attrs_html += f"""
            <div class="attraction-card">
                <img src="{a['img']}" alt="{a['name']}" onclick="openModal('{safe_name}', '{safe_desc}', '{a['img']}')">
                <div class="attraction-body">
                    <h4 onclick="openModal('{safe_name}', '{safe_desc}', '{a['img']}')">{a['name']}</h4>
                    <p>{a['desc']}</p>
                </div>
                <div class="attraction-footer">
                    <span>מחיר (₪):</span>
                    <input type="number" step="0.01" name="attr_{a['id']}" value="{a['price_ils']}">
                </div>
            </div>
            """
        attrs_html += "</div></div>"

    content = f"""
    <h2>אטרקציות ופעילויות לפי יעד</h2>
    <p style="text-align: center; color: var(--text-muted); font-size: 14px; margin-bottom: 25px;">לחץ על התמונה או על שם האטרקציה כדי לפתוח חלון עם מידע מורחב.</p>
    {filter_buttons_html}
    <form method="POST">
        {attrs_html}
        <div style="text-align: center; margin-top: 40px;"><button type="submit">שמור שינויים באטרקציות</button></div>
    </form>
    """
    return render_template_string(LAYOUT, content=content)

@app.route('/checklists', methods=['GET', 'POST'])
def checklists():
    trip_data = load_data()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_list':
            title = request.form.get('list_title', '').strip()
            if title:
                new_id = 'c_' + str(os.urandom(4).hex())
                trip_data['checklists'][new_id] = {
                    "title": title,
                    "items": []
                }
                save_data(trip_data)
                
        elif action == 'delete_list':
            cid = request.form.get('list_id')
            if cid in trip_data['checklists']:
                del trip_data['checklists'][cid]
                save_data(trip_data)
                
        elif action == 'add_item':
            cid = request.form.get('list_id')
            text = request.form.get('item_text', '').strip()
            if cid in trip_data['checklists'] and text:
                new_item_id = 'i_' + str(os.urandom(4).hex())
                trip_data['checklists'][cid]['items'].append({
                    "id": new_item_id,
                    "text": text,
                    "done": False
                })
                save_data(trip_data)
                
        elif action == 'delete_item':
            cid = request.form.get('list_id')
            iid = request.form.get('item_id')
            if cid in trip_data['checklists']:
                trip_data['checklists'][cid]['items'] = [
                    item for item in trip_data['checklists'][cid]['items'] if item['id'] != iid
                ]
                save_data(trip_data)
                
        elif action == 'toggle_item':
            cid = request.form.get('list_id')
            iid = request.form.get('item_id')
            # אם ה-checkbox מסומן, הוא נשלח ב-request. אם לא, הוא לא נשלח בכלל.
            is_done = request.form.get('is_done') == 'on'
            if cid in trip_data['checklists']:
                for item in trip_data['checklists'][cid]['items']:
                    if item['id'] == iid:
                        item['done'] = is_done
                save_data(trip_data)
                
        return redirect(url_for('checklists'))

    lists_html = ""
    for cid, cdata in trip_data['checklists'].items():
        items_html = ""
        for item in cdata['items']:
            done_class = "done" if item['done'] else ""
            checked_attr = "checked" if item['done'] else ""
            items_html += f"""
        <li class="checklist-item {done_class}">
            <form method="POST" id="form_toggle_{item['id']}" style="display: flex; align-items: center; width: 100%; margin: 0;">
                <input type="hidden" name="action" value="toggle_item">
                <input type="hidden" name="list_id" value="{cid}">
                <input type="hidden" name="item_id" value="{item['id']}">
                <label style="display: flex; align-items: center; gap: 12px; width: 100%; cursor: pointer;">
                    <input type="checkbox" name="is_done" value="on" {checked_attr} onchange="this.form.submit()" style="width: 20px; height: 20px; cursor: pointer;">
                    <span>{item['text']}</span>
                </label>
            </form>
            <form method="POST" style="margin: 0;">
                <input type="hidden" name="action" value="delete_item">
                <input type="hidden" name="list_id" value="{cid}">
                <input type="hidden" name="item_id" value="{item['id']}">
                <button type="submit" class="danger-btn" title="מחק פריט">✕</button>
            </form>
        </li>
        """
        
        lists_html += f"""
        <div class="checklist-card">
            <div class="checklist-header" onclick="toggleChecklist(this)">
                <h3>
                    <span class="toggle-icon">▼</span>
                    📋 {cdata['title']}
                </h3>
                <form method="POST" style="margin: 0;" onsubmit="event.stopPropagation(); return confirm('האם למחוק את כל הרשימה?')">
                    <input type="hidden" name="action" value="delete_list">
                    <input type="hidden" name="list_id" value="{cid}">
                    <button type="submit" class="danger-btn" onclick="event.stopPropagation()">מחק רשימה</button>
                </form>
            </div>
            <div class="checklist-content-wrapper">
                <ul class="checklist-items">
                    {items_html if items_html else '<p style="color: var(--text-muted); font-size: 13px; text-align: center; margin: 10px 0;">אין עדיין פריטים ברשימה זו.</p>'}
                </ul>
                <form method="POST" class="add-item-form">
                    <input type="hidden" name="action" value="add_item">
                    <input type="hidden" name="list_id" value="{cid}">
                    <input type="text" name="item_text" placeholder="הוסף פריט חדש..." required>
                    <button type="submit">הוסף</button>
                </form>
            </div>
        </div>
        """

    content = f"""
    <h2>רשימות צ'ק-ליסט ומשימות</h2>
    <p style="text-align: center; color: var(--text-muted); font-size: 14px; margin-bottom: 25px;">צור רשימות חדשות לניהול הציוד, הקניות או המשימות לקראת הטיול.</p>
    
    <div class="checklist-card" style="background: #14151b; border-color: rgba(99, 102, 241, 0.4);">
        <h3 style="text-align: right; margin-top: 0; margin-bottom: 15px; color: #fff; font-size: 1.1rem; display: block;">✨ הוספת רשימה חדשה</h3>
        <form method="POST" class="add-item-form">
            <input type="hidden" name="action" value="add_list">
            <input type="text" name="list_title" placeholder="שם הרשימה החדשה (לדוגמה: ציוד צילום, קניות בטוקיו...)" required>
            <button type="submit">צור רשימה</button>
        </form>
    </div>

    <div style="margin-top: 30px;">
        {lists_html if lists_html else '<p style="text-align: center; color: var(--text-muted);">טרם נוצרו רשימות. התחל ביצירת רשימה למעלה.</p>'}
    </div>
    """
    return render_template_string(LAYOUT, content=content)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)