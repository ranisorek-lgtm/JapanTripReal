from flask import Flask, render_template_string, request, redirect, url_for
import os

app = Flask(__name__)

# מבנה הנתונים המלא עם מידע מורחב ומפורט על כל האטרקציות
trip_data = {
    "flights": [
        {"id": "f1", "name": "טיסות בינלאומיות (תל אביב - אוסקה הלוך ושוב)", "price_ils": 17300.0}
    ],
    "hotels": [
        {"id": "h1", "name": "Keio Plaza Hotel Sapporo (11.9–14.9)", "price_ils": 2290.0},
        {"id": "h2", "name": "Yutorelo Toyako (14.9–15.9)", "price_ils": 542.0},
        {"id": "h3", "name": "Daiwa Roynet Hotel Aomori (15.9–18.9)", "price_ils": 1015.0},
        {"id": "h4", "name": "Tokyu Stay Aoyama Premier (18.9–23.9)", "price_ils": 3168.0},
        {"id": "h5", "name": "Hotel and spa gift Takayama (24.9–26.9)", "price_ils": 813.0},
        {"id": "h6", "name": "Hotel Gracery Kyoto Sanjo (26.9–1.10)", "price_ils": 2015.0},
        {"id": "h7", "name": "Oyado Nono Namba Natural Hot Spring (1.10–4.10)", "price_ils": 2603.0},
    ],
    "trains": [
        {"id": "t1", "name": "סאפורו ==> אגם טויה (14.9)", "price_ils": 270.19},
        {"id": "t2", "name": "אגם טויה <== אאומורי (15.9 - מקטע 1)", "price_ils": 219.68},
        {"id": "t3", "name": "אגם טויה <== אאומורי (15.9 - מקטע 2)", "price_ils": 317.04},
        {"id": "t4", "name": "אאומורי ==> טוקיו (18.9)", "price_ils": 376.34},
        {"id": "t5", "name": "טוקיו ==> טאקאיאמה (23.9)", "price_ils": 346.15},
        {"id": "t6", "name": "טאקאיאמה ==> קיוטו (26.9)", "price_ils": 230.74},
        {"id": "t7", "name": "קיוטו ==> אוסקה (1.10)", "price_ils": 31.04},
    ],
    "attractions": {
        "סאפורו": [
            {
                "id": "a1", 
                "name": "פארק אודורי (Odori Park)", 
                "price_ils": 0, 
                "desc": "שדרה ירוקה וארוכה המשתרעת לאורך 1.5 קילומטרים וחוצה את לב ליבה של סאפורו. הפארק משמש כריאה הירוקה המרכזית של העיר וכולל מדשאות מטופחות, עשרות סוגי עצים, מזרקות מרשימות, פסלי אמנות ויצירות מעניינות. לאורך השנה מתקיימים בו פסטיבלים ענקיים כמו פסטיבל השלג בחורף ופסטיבל הבירה בקיץ.", 
                "img": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=500"
            },
            {
                "id": "a2", 
                "name": "הר מואיווה (Mount Moiwa)", 
                "price_ils": 52, 
                "desc": "הר בגובה 531 מטרים בדרום מערב סאפורו, המפורסם בזכות תצפית הלילה הפנורמית המרהיבה ממנו, המדורגת כאחת משלוש תצפיות הלילה הטובות ביותר ביפן. העלייה נעשית באמצעות שילוב של רכבל וקרונית ייחודית (Mini Cable Car) המטפסת אל הפסגה, שם ישנה מרפסת תצפית רומנטית ופעמון אוהבים.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a3", 
                "name": "פארק שירוי קויביטו (Shiroi Koibito Park)", 
                "price_ils": 30, 
                "desc": "מתחם קסום המוקדש כולו לשוקולד, ממתקים ולעוגיית הדגל של הוקאידו - 'שירוי קויביטו' (מאהב לבן). המקום מעוצב בסגנון אגדות אירופאיות וכולל מפעל ייצור שניתן לצפות ממנו על תהליך הכנת העוגיות, מוזיאון עתיקות שוקולד, שעון קוקייה ענק שמופעל בכל שעה, וגנים מטופחים.", 
                "img": "https://images.unsplash.com/photo-1549488344-cbb6c34cf08b?w=500"
            },
            {
                "id": "a4", 
                "name": "מקדש הוקאידו (Hokkaido Jingu)", 
                "price_ils": 0, 
                "desc": "מקדש השינטו החשוב והמרכזי ביותר באי הוקאידו, שהוקם בשנת 1869 לפי הוראת הקיסר מייג'י. המקדש שוכן בתוך פארק מארויאמה העצום והשקט, המוקף ביער טבעי עשיר בסנאים ובצמחייה פראית. זהו מקום מושלם לחוות שקט רוחני, לטייל בשבילים המוצלים ולראות טקסים מסורתיים.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a5", 
                "name": "שוק ניג'ו (Nijo Market)", 
                "price_ils": 50, 
                "desc": "שוק דגים היסטורי שפעיל כבר למעלה מ-100 שנה בלב סאפורו. השוק צפוף, צבעוני וגדוש בדוכנים המציעים את השלל הימי המשובח ביותר של הוקאידו: סרטנים ענקיים, ביצי סלמון בוהקות, קיפודי ים טריים ודגים שזה עתה נדוגו. במקום ישנן מסעדות קטנות המגישות 'קאיסנדון' (קערת אורז עמוסה בדגים טריים) לארוחת בוקר וצהריים מושלמת.", 
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
                "desc": "רכבל המטפס אל פסגת הר הגעש הפעיל אוסו, ומציע תצפיות עוצרות נשימה על אגם טויה הכחול, מפרץ אובורוקו, והמכתשים הוולקניים הנוספים באזור (כמו מכתש שוואקה). האזור מלא בתצורות גיאולוגיות ייחודיות ומסלולי הליכה נוחים המאפשרים הצצה לעוצמת הטבע.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a8", 
                "name": "שייט באגם טויה (Lake Toya Cruise)", 
                "price_ils": 35, 
                "desc": "שייט תענוגות מרגיע על גבי ספינות המעוצבות כטירות קטנות, הנמשך כ-50 דקות סביב האיים המרכזיים בלב האגם (ארבעה איים מיוערים המכונים יחד 'קאונו'). במהלך השייט ניתן להאכיל את השחפים הרבים המלווים את הספינה וליהנות מהרוח הצוננת ומהנוף ההררי המסביב.", 
                "img": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=500"
            },
            {
                "id": "a9", 
                "name": "מופע הזיקוקים הלילי (Toyako Long-Run Fireworks)", 
                "price_ils": 0, 
                "desc": "מסורת מרהיבה שמתקיימת מדי ערב בין חודשים אפריל לאוקטובר. מדי לילה בשעה 20:45 משוגרים מאות זיקוקים צבעוניים מעל פני אגם טויה. ניתן לצפות במופע ישירות מחלונות המלונות שלאורך הטיילת, או בישיבה רומנטית על שפת האגם בזמן שהזיקוקים משתקפים במים.", 
                "img": "https://images.unsplash.com/photo-1513151233558-d860c5398176?w=500"
            },
            {
                "id": "a10", 
                "name": "מוזיאון המדע הוולקני", 
                "price_ils": 15, 
                "desc": "מוזיאון מודרני ומרתק הממוקם למרגלות ההר, ומספר את סיפורן של ההתפרצויות הגעשיות באזור, בדגש על ההתפרצות הדרמטית של שנת 2000. המוזיאון כולל מיצגים ויזואליים מרשימים, סימולציות והסברים גיאולוגיים הממחישים את כוחות הטבע האדירים שעיצבו את האזור.", 
                "img": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=500"
            }
        ],
        "אאומורי": [
            {
                "id": "a11", 
                "name": "מרכז Nokkedon (Aomori Gyosai Center)", 
                "price_ils": 50, 
                "desc": "חוויה קולינרית ייחודית שבה מרכיבים לבד את ארוחת הדגים המושלמת. בכניסה קונים כרטיסייה עם קופונים, ניגשים לדוכני השוק השונים וממירים קופונים באורז חם ובמבחר עצום של דגים טריים, טונה שומנית, שרימפס, צדפות וקוויאר שבוחרים באופן אישי.", 
                "img": "https://images.unsplash.com/photo-1553163147-622ab57be1c2?w=500"
            },
            {
                "id": "a12", 
                "name": "מרכז התיירות ASPAM", 
                "price_ils": 0, 
                "desc": "מבנה ארכיטקטוני בולט בצורת משולש ענק הממוקם על קו המים של נמל אאומורי. המבנה מסמל את האות הראשונה של העיר (A) ומשמש כמרכז מידע אזורי, כולל חנויות לממכר מוצרי תפוחים מקומיים (האזור מפורסם בתפוחים שלו), מסעדות דגים ומרפסת תצפית פנורמית בקומה העליונה.", 
                "img": "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=500"
            },
            {
                "id": "a13", 
                "name": "נחל אואיראסה (Oirase Gorge)", 
                "price_ils": 0, 
                "desc": "אחד מנתיבי הטבע היפים ביותר ביפן. נחל הררי צלול הזורם לאורך כ-14 קילומטרים בתוך עמק מיוער וירוק עמוק, המלא במפלי מים שונים, סלעים עטופי טחב ירוק ועצי אשור ענקיים. המקום מציע שבילי הליכה נוחים ונגישים המאפשרים לטבול את החושים בשקט ובאוויר הצלול.", 
                "img": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=500"
            },
            {
                "id": "a14", 
                "name": "אגם טוואדה (Lake Towada)", 
                "price_ils": 0, 
                "desc": "אגם לוע הר געש ענק ועמוק, הידוע במים הצלולים והכחולים שלו שמשקפים את ההרים מסביב כמראה. האגם מוקף ביערות עבותים ומציע נקודות תצפית פסטורליות, אפשרויות שייט רגועות, ומקדש טוואדה העתיק והנסתר השוכן בסמוך לשפת המים.", 
                "img": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=500"
            },
            {
                "id": "a15", 
                "name": "הר האקודה (Mount Hakkoda)", 
                "price_ils": 60, 
                "desc": "קבוצת הרי געש מרשימה המציעה נופים אלפיניים דרמטיים. רכבל האקודה מוביל את המטיילים מהמורדות ועד לפסגת הר 'טאמורודאקה', משם נפרשת פנורמה מרהיבה של הרים, ביצות הרריות ושבילי הליכה מעגליים יפהפיים המשתנים בצבעיהם לפי עונות השנה.", 
                "img": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=500"
            }
        ],
        "טוקיו": [
            {
                "id": "a16", 
                "name": "מקדש Meiji Shrine ויערות מייג'י", 
                "price_ils": 0, 
                "desc": "מקדש שינטו מרכזי המוקדש לקיסר מייג'י ולקיסרית שוקן, השוכן בלב אזור המושך אליו מיליונים. המקדש מוקף ביער מלאכותי עצום ובו למעלה מ-120,000 עצים מכל רחבי יפן, מה שיוצר תחושת ניתוק מוחלטת מהרעש וההמולה של העיר הגדולה מיד כשעוברים את שערי העץ הענקיים (טורי).", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a17", 
                "name": "רחוב Takeshita ואופנת הרחוב ב-Harajuku", 
                "price_ils": 20, 
                "desc": "הרחוב התוסס, הצבעוני והאקסצנטרי ביותר בטוקיו, המהווה את מוקד תרבות הצעירים ואופנת הרחוב היפנית. הרחוב גדוש בחנויות בגדים ייחודיות, חנויות קונספט צבעוניות, בוטיקים קטנים ודוכנים המוכרים קרפ יפני מפורסם עמוס קצפת ותוספות.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a18", 
                "name": "שדרת הארכיטקטורה Omotesando", 
                "price_ils": 0, 
                "desc": "שדרת היוקרה והארכיטקטורה המודרנית של טוקיו, המכונה לעיתים 'השדרה החמישית של טוקיו'. השדרה רחבה, מוצלת בעצי זית ואלון, ומציעה בנייני מעצבים בינלאומיים בעיצובים ארכיטקטוניים פורצי דרך, לצד מרכזי קניות מעוצבים ובתי קפה שיקיים.", 
                "img": "https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?w=500"
            },
            {
                "id": "a19", 
                "name": "פארק Shinjuku Gyoen", 
                "price_ils": 15, 
                "desc": "אחד הפארקים הגדולים והיפים ביותר בטוקיו, המשלב שלושה סגנונות עיצוב שונים: גן יפני מסורתי עם בריכות ובתי תה, גן אנגלי רחב ידיים עם מדשאות ענק פתוחות, וגן צרפתי פורמלי. הפארק מהווה מקלט של שקט וירוק בלב רובע הבילויים הסואן שינג'וקו.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a20", 
                "name": "תצפית בניין הממשל", 
                "price_ils": 0, 
                "desc": "בניין הממשל המטרופוליני של טוקיו בשינג'וקו, המתוכנן בידי האדריכל קנזו טנגה. בבניין ישנן שתי קומות תצפית פנורמיות בגובה של כ-202 מטרים המציעות כניסה חופשית לציבור. בימים בהירים ניתן לראות מהתצפית את מגדל פוג'י, רחובות העיר העצומים ומפרץ טוקיו.", 
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
            }
        ],
        "טאקאיאמה": [
            {
                "id": "a24", 
                "name": "קאמיקוצ'י (Kamikochi)", 
                "price_ils": 60, 
                "desc": "שמורת טבע אלפינית פופולרית ומדהימה ביופייה, השוכנת בלב הרי האלפים היפניים. השמורה מציעה עמק הררי רחב ידיים שבו זורם נהר אזוסה (Azusa River) הצלול כבדולח, מוקף בפסגות מחודדות המכוסות שלג בחלקן ובשבילי הליכה נוחים המעניקים חוויית טבע בתולי עוצר נשימה.", 
                "img": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=500"
            },
            {
                "id": "a25", 
                "name": "רכבל שינהוטאקה (Shinhotaka Ropeway)", 
                "price_ils": 120, 
                "desc": "רכבל ייחודי ומרשים בעל שתי קומות המטפס לגובה של למעלה מ-2,000 מטרים לתוך האלפים היפניים. הרכבל מספק תצפית פנורמית מדהימה של 360 מעלות על הרים נישאים, עמקים מוריקים ומדרונות תלולים, וכולל מרפסת תצפית על הגג ממנה נשקיף נוף עוצר נשימה.", 
                "img": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=500"
            },
            {
                "id": "a26", 
                "name": "שיזוקאווה-גו (Shirakawa-go)", 
                "price_ils": 50, 
                "desc": "כפר היסטורי ציורי המוכר בזכות בתי החווה העתיקים שלו הבנויים בסגנון 'גאשו-זוקורי' (Gassho-zukuri), שפירושו 'ידיים משולבות בתפילה' – המתייחס לגגות הקש התלולים שנועדו לשאת את כובד השלגים המקומיים בחורף. הכפר הוכר כאתר מורשת עולמית של אונסק\"ו ונראה כאילו נלקח מתוך אגדה עתיקה.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a27", 
                "name": "העיר העתיקה (Sanmachi Suji)", 
                "price_ils": 0, 
                "desc": "רובע היסטורי משומר היטב המורכב משלושה רחובות ראשיים בטאקאיאמה, המאופיינים בבתים מסורתיים שחורים מתקופת אדו. האזור שוקק חיים וכולל חנויות אומנים מסורתיות, מבשלות סאكي מקומיות המסומנות בכד עצי ענק (סאבאיאקי), ודוכנים המוכרים נתחי בשר הידה צלויים על שיפודים.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a28", 
                "name": "סדנת בובה", 
                "price_ils": 122, 
                "desc": "סדנה מקומית (23.9 עד 15:30).", 
                "img": "https://images.unsplash.com/photo-1553163147-622ab57be1c2?w=500"
            }
        ],
        "קיוטו": [
            {
                "id": "a29", 
                "name": "Arashiyama Bamboo Grove (יער הבמבוק)", 
                "price_ils": 0, 
                "desc": "שבילי הליכה קסומים העוברים בתוך יער עצי במבוק עצומים וגבוהים ברובע אראשיאמה. האור השמש המסנן דרך קני הבמבוק והקול הייחודי שיוצרת הרוח הנושבת בצמרות הגבוהות מעניקים למקום אווירה קסומה, מיסטית ושלווה במיוחד.", 
                "img": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=500"
            },
            {
                "id": "a30", 
                "name": "Kinkakuji Golden Pavilion (מקדש הזהב)", 
                "price_ils": 25, 
                "desc": "מקדש זן בודהיסטי מרהיב ביופיו ששתי קומותיו העליונות מצופות כולן בעלי זהב טהור. המקדש שוכן על שפת בריכת מים צלולה ('בריכת המראה') המדגישה את יופיו, והוא מוקף בגן יפני קלאסי ומטופח המשתלב בהרמוניה מושלמת עם הטבע המסביב.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a31", 
                "name": "Fushimi Inari Shrine", 
                "price_ils": 0, 
                "desc": "מקדש השינטו המפורסם והמצולם ביותר ביפן, המוקדש לאינארי – אל האורז והשגשוג. המקדש ידוע בעיקר בשל אלפי שערי ה'טורי' הכתומים-אדומים היוצרים מנהרות צבעוניות אינסופיות המטפסות במעלה ההר הקדוש אינארי בין עצים ושבילים נסתרים.", 
                "img": "https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?w=500"
            },
            {
                "id": "a32", 
                "name": "סיור הליכה בקיוטו", 
                "price_ils": 154, 
                "desc": "סיור מודרך בתאריך 26.9 בשעה 18:20.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            }
        ],
        "אוסקה": [
            {
                "id": "a33", 
                "name": "Dotonbori", 
                "price_ils": 0, 
                "desc": "רובע הבילויים, התאורה והקולינריה המרכזי של אוסקה, השוכן לאורך תעלת דוטונבורי. האזור שוקק חיים מסביב לשעון ומפורסם בשלטי הניאון הענקיים שלו (כמו שלט 'גליקו' המפורסם), באווירה התוססת ובשפע עצום של דוכני אוכל רחוב המציעים מנות אגדיות כמו טקויאקי ואוקונומיאקי.", 
                "img": "https://images.unsplash.com/photo-1590523277543-a94d2e4eb00b?w=500"
            },
            {
                "id": "a34", 
                "name": "Osaka Castle", 
                "price_ils": 30, 
                "desc": "אחת הטירות ההיסטוריות והמרשימות ביותר ביפן, הממוקמת בלב פארק ענק המוקף חומות אבן אדירות ותעלות מים רחבות. הטירה המקורית נבנתה במאה ה-16 ומילאה תפקיד מפתח באיחוד יפן. כיום פועל בתוכה מוזיאון היסטורי מרתק, וממפקדת הגג שלה נשקיף נוף פנורמי של העיר.", 
                "img": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=500"
            },
            {
                "id": "a35", 
                "name": "Aquarium Kaiyukan", 
                "price_ils": 100, 
                "desc": "אחד האקווריומים הגדולים, המרשימים והמתקדמים ביותר בעולם. האקווריום מדמה את המערכות האקולוגיות של אזור האוקיינוס השקט סביב טבעת האש, והאטרקציה המרכזית בו היא מיכל ענק המאכלס כריש לושת ענק (Whale Shark) לצד מאות מיני דגים ויצורים ימיים אחרים.", 
                "img": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=500"
            },
            {
                "id": "a36", 
                "name": "סיור בישול ארוחת בוקר יפנית", 
                "price_ils": 270, 
                "desc": "שיעור בישול (2.10 בשעה 10:00).", 
                "img": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=500"
            },
            {
                "id": "a37", 
                "name": "17 טעמים של טקויאקי", 
                "price_ils": 212, 
                "desc": "הכנה ואכילה ללא הגבלה (1.10 בשעה 18:00).", 
                "img": "https://images.unsplash.com/photo-1553163147-622ab57be1c2?w=500"
            }
        ]
    }
}

LAYOUT = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>תכנון טיול ליפן 🇯🇵</title>
    <style>
        :root {
            --bg-color: #0f111a;
            --card-bg: #1a1c29;
            --border-color: #2b2f42;
            --text-color: #e2e8f0;
            --text-muted: #94a3b8;
            --accent-color: #ff4757;
            --accent-hover: #ff6b81;
            --success-color: #2ed573;
        }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background-color: var(--bg-color); 
            color: var(--text-color); 
            margin: 0; 
            padding: 15px; 
        }
        .container { 
            max-width: 1100px; 
            margin: auto; 
            background: var(--card-bg); 
            padding: 20px; 
            border-radius: 16px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
            border: 1px solid var(--border-color);
        }
        @media(min-width: 768px) {
            body { padding: 30px; }
            .container { padding: 40px; }
        }

        h1, h2, h3 { 
            color: #fff; 
            text-align: center; 
            font-weight: 700;
        }
        h1 { color: var(--accent-color); font-size: 1.8rem; margin-bottom: 10px; }
        @media(min-width: 768px) {
            h1 { font-size: 2.2rem; }
        }
        
        nav { 
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin-bottom: 30px; 
            background: #131520; 
            padding: 10px; 
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        nav a { 
            color: var(--text-muted); 
            text-decoration: none; 
            padding: 8px 12px;
            border-radius: 8px;
            font-weight: 600; 
            font-size: 14px; 
            transition: all 0.3s ease;
            text-align: center;
        }
        nav a:hover { 
            color: #fff; 
            background: var(--accent-color); 
        }

        .table-responsive {
            width: 100%;
            overflow-x: auto;
            margin-bottom: 30px;
            -webkit-overflow-scrolling: touch;
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            background: #141622;
            border-radius: 8px;
            overflow: hidden;
            min-width: 320px;
        }
        th, td { 
            padding: 12px 15px; 
            border-bottom: 1px solid var(--border-color); 
            text-align: right; 
            font-size: 14px;
        }
        th { 
            background-color: #1f2233; 
            color: #fff;
            font-weight: 600;
        }
        tr:hover { background-color: #1a1c29; }

        input[type="number"] { 
            width: 80px; 
            padding: 8px; 
            font-size: 14px; 
            background: #0f111a;
            border: 1px solid var(--border-color);
            color: #fff;
            border-radius: 6px;
            text-align: center;
        }
        @media(min-width: 768px) {
            input[type="number"] { width: 100px; }
        }
        input[type="number"]:focus {
            border-color: var(--accent-color);
            outline: none;
        }

        button { 
            background-color: var(--accent-color); 
            color: white; 
            border: none; 
            padding: 12px 25px; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 16px; 
            font-weight: bold; 
            transition: background 0.3s;
            box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3);
            width: 100%;
        }
        @media(min-width: 768px) {
            button { width: auto; }
        }
        button:hover { background-color: var(--accent-hover); }

        .total-box { 
            background: linear-gradient(135deg, #1f2233 0%, #141622 100%);
            border: 1px solid var(--border-color);
            padding: 20px; 
            border-radius: 12px; 
            text-align: center; 
            font-size: 20px; 
            font-weight: bold; 
            margin-top: 30px; 
            color: var(--success-color);
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.2);
        }
        @media(min-width: 768px) {
            .total-box { font-size: 26px; padding: 25px; }
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
            background: #141622; 
            border: 1px solid var(--border-color); 
            border-radius: 12px; 
            overflow: hidden; 
            display: flex; 
            flex-direction: column; 
            justify-content: space-between;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .attraction-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
            border-color: #3b4259;
        }
        .attraction-card img { 
            width: 100%; 
            height: 160px; 
            object-fit: cover; 
            cursor: pointer;
            transition: opacity 0.2s;
        }
        .attraction-card img:hover {
            opacity: 0.85;
        }
        .attraction-body { 
            padding: 16px; 
        }
        .attraction-body h4 { 
            margin: 0 0 8px 0; 
            color: #fff; 
            font-size: 17px;
            cursor: pointer;
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
            background: #181b28; 
            border-top: 1px solid var(--border-color); 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            font-size: 14px;
            color: var(--text-muted);
        }
        .city-title {
            color: #38ef7d;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 8px;
            margin-top: 35px;
            margin-bottom: 20px;
            font-size: 1.3rem;
        }

        /* עיצוב המודאל (חלון קופץ) הותאם לטלפון */
        .modal {
            display: none; 
            position: fixed; 
            z-index: 1000; 
            left: 0;
            top: 0;
            width: 100%; 
            height: 100%; 
            background-color: rgba(0,0,0,0.85); 
            backdrop-filter: blur(5px);
            align-items: center;
            justify-content: center;
            padding: 15px;
            box-sizing: border-box;
        }
        .modal-content {
            background-color: #161925;
            border: 1px solid var(--border-color);
            padding: 20px;
            border-radius: 16px;
            width: 100%;
            max-width: 500px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.6);
            position: relative;
            text-align: right;
            animation: modalOpen 0.3s ease;
            max-height: 85vh;
            overflow-y: auto;
        }
        @media(min-width: 768px) {
            .modal-content { padding: 30px; }
        }
        @keyframes modalOpen {
            from {transform: scale(0.9); opacity: 0;}
            to {transform: scale(1); opacity: 1;}
        }
        .modal-content img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        @media(min-width: 768px) {
            .modal-content img { height: 250px; margin-bottom: 20px; }
        }
        .modal-content h3 {
            margin-top: 0;
            color: #fff;
            font-size: 20px;
        }
        @media(min-width: 768px) {
            .modal-content h3 { font-size: 22px; }
        }
        .modal-content p {
            color: var(--text-muted);
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        @media(min-width: 768px) {
            .modal-content p { font-size: 15px; }
        }
        .close-btn {
            background: var(--accent-color);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            width: 100%;
        }
        @media(min-width: 768px) {
            .close-btn { width: auto; float: left; }
        }
        .close-btn:hover {
            background: var(--accent-hover);
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
    </nav>
    {{ content | safe }}
</div>

<!-- חלון מודאל כללי להצגת פרטי אטרקציה -->
<div id="infoModal" class="modal">
    <div class="modal-content">
        <img id="modalImg" src="" alt="">
        <h3 id="modalTitle"></h3>
        <p id="modalDesc"></p>
        <button class="close-btn" onclick="closeModal()">סגור</button>
        <div style="clear: both;"></div>
    </div>
</div>

<script>
    function openModal(name, desc, img) {
        document.getElementById('modalTitle').innerText = name;
        document.getElementById('modalDesc').innerText = desc;
        document.getElementById('modalImg').src = img;
        document.getElementById('infoModal').style.display = 'flex';
    }

    function closeModal() {
        document.getElementById('infoModal').style.display = 'none';
    }

    // סגירת המודאל בלחיצה מחוץ לתיבה
    window.onclick = function(event) {
        var modal = document.getElementById('infoModal');
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    total = (
        sum(item['price_ils'] for item in trip_data['trains']) +
        sum(item['price_ils'] for item in trip_data['hotels']) +
        sum(item['price_ils'] for item in trip_data['flights']) +
        sum(item['price_ils'] for city_attrs in trip_data['attractions'].values() for item in city_attrs)
    )
    content = f"""
    <h1>מסע קסום ליפן 2026 🇯🇵</h1>
    <p style="text-align: center; color: #94a3b8; font-size: 15px; margin-bottom: 30px;">מערכת ניהול מתקדמת לתקציב ולמסלול הטיול שלך. בחר בתפריט מעלה לעדכון מחירים.</p>
    <div class="total-box">
        סך הכל כללי משוער לטיול: ₪{total:,.2f}
    </div>
    """
    return render_template_string(LAYOUT, content=content)

@app.route('/stays', methods=['GET', 'POST'])
def stays():
    if request.method == 'POST':
        for key, value in request.form.items():
            try:
                val_float = float(value)
                if key.startswith('hotel_'):
                    hid = key.replace('hotel_', '')
                    for h in trip_data['hotels']:
                        if h['id'] == hid:
                            h['price_ils'] = val_float
                elif key.startswith('flight_'):
                    fid = key.replace('flight_', '')
                    for f in trip_data['flights']:
                        if f['id'] == fid:
                            f['price_ils'] = val_float
            except ValueError:
                continue
        return redirect(url_for('stays'))

    content = """
    <h2>ניהול טיסות ומלונות</h2>
    <form method="POST">
        <h3 style="text-align: right; color: #ff4757; margin-top: 25px;">✈️ טיסות בינלאומיות</h3>
        <div class="table-responsive">
            <table>
                <tr><th>תיאור</th><th>מחיר ב-₪</th></tr>
                """ + "".join([f"<tr><td>{f['name']}</td><td><input type='number' step='0.01' name='flight_{f['id']}' value='{f['price_ils']}'></td></tr>" for f in trip_data['flights']]) + """
            </table>
        </div>

        <h3 style="text-align: right; color: #ff4757; margin-top: 35px;">🏨 מלונות לאורך המסלול</h3>
        <div class="table-responsive">
            <table>
                <tr><th>מלון / תאריכים</th><th>מחיר ב-₪</th></tr>
                """ + "".join([f"<tr><td>{h['name']}</td><td><input type='number' step='0.01' name='hotel_{h['id']}' value='{h['price_ils']}'></td></tr>" for h in trip_data['hotels']]) + """
            </table>
        </div>
        <div style="text-align: center; margin-top: 30px;"><button type="submit">שמור שינויים</button></div>
    </form>
    """
    return render_template_string(LAYOUT, content=content)

@app.route('/trains', methods=['GET', 'POST'])
def trains():
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
        return redirect(url_for('attractions'))

    attrs_html = ""
    for city, attrs in trip_data['attractions'].items():
        attrs_html += f"<h3 class='city-title'>📍 {city}</h3><div class='attractions-grid'>"
        for a in attrs:
            # נרמול הטקסט למניעת שבירת המחרוזת ב-JavaScript
            safe_name = a['name'].replace("'", "\\'")
            safe_desc = a['desc'].replace("'", "\\'").replace('\n', ' ')
            
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
        attrs_html += "</div>"

    content = f"""
    <h2>אטרקציות ופעילויות לפי יעד</h2>
    <p style="text-align: center; color: #94a3b8; font-size: 14px; margin-bottom: 25px;">לחץ על התמונה או על שם האטרקציה כדי לפתוח חלון עם מידע מורחב.</p>
    <form method="POST">
        {attrs_html}
        <div style="text-align: center; margin-top: 40px;"><button type="submit">שמור שינויים באטרקציות</button></div>
    </form>
    """
    return render_template_string(LAYOUT, content=content)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)