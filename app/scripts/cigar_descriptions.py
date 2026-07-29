#!/usr/bin/env python3
"""Kurirani opisi linija cigara -> scripts/cigar_descriptions.json.

Katalog vecinom nosi generirane `notes` iz atributa ("Nikaragva, Habano pokrov
— jace snage, punijeg tijela. Okusi: ..."). To nije opis nego ponavljanje onoga
sto je vec na kartici, pa ih app ne prikazuje (vidi src/lib/cigarNote.ts).

Ovdje zive pravi, urednicki opisi: sto linija JEST — tvornica, blend, mjesto u
ponudi marke, karakter. Pisani su za linije koje se stvarno mogu kupiti u HR.
Linije za koje nema pouzdanog izvora namjerno NISU ovdje — bolje bez opisa nego
izmisljen opis.

Uredi ovu datoteku, pa pokreni:
    python3 scripts/cigar_descriptions.py          # regeneriraj JSON
    python3 scripts/apply-cigar-descriptions.py    # upisi u src/data/cigars.json
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# id -> (hr, en)
DESCRIPTIONS: dict[str, tuple[str, str]] = {
    # ---------------------------------------------------------------- Kuba
    "cig-bolivar-belicosos-finos": (
        "Klasik marke i jedna od najpoznatijih kubanskih figurado vitola — kratki "
        "piramid koji Bolívarov snažan, zemljano-paprenit profil drži zbijenim i "
        "izravnim od prve trećine.",
        "The marca's signature and one of Cuba's best-known figurados — a short "
        "pyramid that keeps Bolívar's powerful, earthy-peppery profile compact and "
        "direct from the first third.",
    ),
    "cig-cohiba-medio-siglo": (
        "Uvedena 2017. za pola stoljeća Cohibe: petit robusto s ringom 52 koji "
        "prepoznatljivu Cohiba travnato-medenu slatkoću daje u pola sata, bez "
        "skraćivanja blenda.",
        "Introduced in 2017 for Cohiba's half-century: a ring-52 petit robusto that "
        "delivers the house's grassy, honeyed sweetness in half an hour without "
        "thinning the blend.",
    ),
    "cig-cohiba-piramides-extra": (
        "Prva redovna Cohiba piramida (2012.) — dulji figurado s medio tiempo "
        "listom Línea Clásica, koji koncentriranim vrhom pojačava začin, a prema "
        "kraju otvara kremastu slatkoću.",
        "Cohiba's first regular pyramid (2012) — a longer figurado carrying the "
        "Línea Clásica's medio tiempo leaf; the tapered head concentrates spice "
        "before a creamy sweetness opens up later on.",
    ),
    "cig-cuaba-distinguidos": (
        "Cuaba je 1996. vratila dvostruki figurado, oblik napušten pola stoljeća "
        "prije. Distinguidos je najveći redovni format linije — ručno zahtjevan "
        "oblik koji dim postupno mijenja kako se ring širi pa sužava.",
        "Cuaba revived the double figurado in 1996, a shape abandoned half a century "
        "earlier. Distinguidos is the line's largest regular size — a demanding shape "
        "whose smoke shifts as the ring widens then tapers again.",
    ),
    "cig-cuaba-exclusivos": (
        "Srednji dvostruki figurado u Cuabinoj ponudi — isti oblik i blend kao ostatak "
        "linije, u formatu koji traje oko sat vremena.",
        "The mid-size double figurado in Cuaba's range — the same shape and blend as "
        "the rest of the line, in a format that runs about an hour.",
    ),
    "cig-cuaba-tradicionales": (
        "Najduži klasični Cuaba figurado — vitka, na oba kraja sužena cigara koja "
        "traži strpljivo paljenje, a zauzvrat daje najduži i najslojevitiji dim linije.",
        "Cuaba's longest classic figurado — a slim cigar tapered at both ends that "
        "asks for a patient light and returns the line's longest, most layered smoke.",
    ),
    "cig-el-rey-del-mundo-del-mundo-demi-tasse": (
        "Najmanji format najblaže kubanske marke — cigara uz kavu, gotova prije nego "
        "što se šalica ohladi, s laganim cedrovo-kremastim tonom po kojem je El Rey "
        "del Mundo poznat.",
        "The smallest size from Cuba's mildest marca — a coffee-break cigar, done "
        "before the cup cools, with the light cedar-and-cream tone El Rey del Mundo "
        "is known for.",
    ),
    "cig-fonseca-cosacos": (
        "Fonseca je jedina kubanska marka koja cigare pakira u bijeli japanski "
        "papir. Cosacos je klasična lonsdale — blaga, brašnasto-kremasta, među "
        "najpitkijim kubankama za početak dana.",
        "Fonseca is the only Cuban marca to wrap its cigars in white Japanese tissue. "
        "Cosacos is a classic lonsdale — mild and doughy-creamy, among the easiest "
        "Cubans to start a day with.",
    ),
    "cig-guantanamera-decimos": (
        "Guantanamera je kubanska strojno rađena linija kratkog punjenja — jeftin, "
        "izravan ulaz u kubanski profil. Decimos je najmanji format, za petnaestak "
        "minuta.",
        "Guantanamera is Cuba's machine-made short-filler line — an inexpensive, "
        "direct way into the Cuban profile. Decimos is the smallest size, good for "
        "about fifteen minutes.",
    ),
    "cig-hoyo-de-monterrey-elegantes": (
        "Vitka panetela iz najlakše kubanske kuće — tanak ring drži dim suh i "
        "cvjetan, s prepoznatljivom Hoyo slatkoćom sijena.",
        "A slim panetela from Cuba's lightest house — the thin ring keeps the smoke "
        "dry and floral, with Hoyo's signature hay-like sweetness.",
    ),
    "cig-hoyo-de-monterrey-palmas-extra": (
        "Duga, tanka Hoyo vitola — format koji naglašava pokrov: cvjetno, kremasto i "
        "suho, bez težine koju donosi širi ring.",
        "A long, thin Hoyo size — a format that puts the wrapper forward: floral, "
        "creamy and dry, without the weight a wider ring brings.",
    ),
    "cig-hoyo-de-monterrey-souvenir-de-luxe": (
        "Kratka petit corona iz Hoyove tradicionalne ponude — blaga, cvjetna i gotova "
        "za pola sata; klasičan format za jutro.",
        "A short petit corona from Hoyo's traditional range — mild, floral and done in "
        "half an hour; a classic morning format.",
    ),
    "cig-jose-l-piedra-l-piedra-brevas": (
        "José L. Piedra je kubanska linija kratkog punjenja iz Vuelta Arriba regije — "
        "izrazito povoljna, rustikalna i izravna. Brevas je kratki format za brzo "
        "pušenje.",
        "José L. Piedra is Cuba's short-filler line from the Vuelta Arriba region — "
        "notably cheap, rustic and direct. Brevas is the short, quick format.",
    ),
    "cig-jose-l-piedra-l-piedra-caballeros": (
        "Najmanji José L. Piedra — kratko punjenje, gori brzo i toplo, s grubim "
        "zemljanim tonom koji marku i definira.",
        "The smallest José L. Piedra — short filler, burning fast and hot, with the "
        "rough earthy tone that defines the marca.",
    ),
    "cig-jose-l-piedra-l-piedra-cazadores": (
        "Najveći format linije — ista rustikalna kubanska smjesa kratkog punjenja u "
        "duljoj cigari, za oko četrdesetak minuta.",
        "The line's largest size — the same rustic Cuban short-filler blend in a "
        "longer cigar, running about forty minutes.",
    ),
    "cig-jose-l-piedra-l-piedra-conservas": (
        "Srednji José L. Piedra — pun, zemljano-paprenit kubanski karakter po cijeni "
        "kakvu Habanos rijetko nudi.",
        "The mid-size José L. Piedra — full, earthy-peppery Cuban character at a price "
        "Habanos rarely offers.",
    ),
    "cig-la-gloria-cubana-glorias": (
        "Kubanska La Gloria Cubana (ne dominikanska imenjakinja) — mala, klasična "
        "vitola marke koju Habanos drži u ograničenoj ponudi, s cedrovo-začinskim "
        "profilom srednje težine.",
        "The Cuban La Gloria Cubana (not its Dominican namesake) — a small classic "
        "size from a marca Habanos keeps in a limited range, with a medium "
        "cedar-and-spice profile.",
    ),
    "cig-partagas-lusitanias": (
        "Ikona kubanskog kataloga: dvostruka corona duga 194 mm, referentni format za "
        "Partagásov zemljano-kožnati profil. Traje preko dva sata i traži miran "
        "termin.",
        "An icon of the Cuban catalogue: a 194 mm double corona, the reference format "
        "for Partagás's earthy, leathery profile. It runs past two hours and asks for "
        "an unhurried slot.",
    ),
    "cig-partagas-mille-fleurs": (
        "Mala Partagás za kratko vrijeme — isti prepoznatljiv zemljano-paprenit "
        "karakter marke sabijen u pola sata.",
        "A small Partagás for a short window — the marca's recognisable earthy-peppery "
        "character compressed into half an hour.",
    ),
    "cig-partagas-serie-e": (
        "Deblja moderna Partagás linija (ring 54) — širi ring hladi dim i zaobljuje "
        "začin, pa je Serie E puna, ali mekša od klasičnih Partagás vitola.",
        "The thicker modern Partagás line (ring 54) — the wider ring cools the smoke "
        "and rounds the spice, so Serie E reads full but softer than the classic "
        "Partagás sizes.",
    ),
    "cig-por-larranaga-50": (
        "Por Larrañaga je najstarija kubanska marka u kontinuiranoj proizvodnji (1834.) "
        "i tradicionalno najslađa — kremasta, s tonom vanilije i medenog kolača.",
        "Por Larrañaga is Cuba's oldest marca in continuous production (1834) and "
        "traditionally its sweetest — creamy, with vanilla and honey-cake notes.",
    ),
    "cig-por-larranaga-montecarlos": (
        "Duga, tanka Por Larrañaga vitola — tanak ring pojačava pokrov, pa slatkoća "
        "marke dolazi izravnije i suše.",
        "A long, thin Por Larrañaga size — the narrow ring pushes the wrapper forward, "
        "so the marca's sweetness arrives more directly and drier.",
    ),
    "cig-quai-d-orsay-dorsay-no-50": (
        "Quai d'Orsay je kubanska marka stvorena 1970-ih za francusko tržište — "
        "namjerno suzdržana, cvjetno-kremasta i suha. No. 50 je moderni robusto iz "
        "obnove linije 2017.",
        "Quai d'Orsay is the Cuban marca created in the 1970s for the French market — "
        "deliberately restrained, floral-creamy and dry. No. 50 is the modern robusto "
        "from the 2017 relaunch.",
    ),
    "cig-quintero-petit-quintero": (
        "Quintero je kubanska marka kratkog punjenja iz Cienfuegosa — najpovoljniji "
        "ulaz u kubanski okus. Petit Quintero je najmanji format, za dvadesetak minuta.",
        "Quintero is Cuba's short-filler marca from Cienfuegos — the cheapest way into "
        "the Cuban taste. Petit Quintero is the smallest size, about twenty minutes.",
    ),
    "cig-rafael-gonzalez-gonzalez-perlas": (
        "Rafael González je jedna od najlakših kubanskih marki, povijesno vezana uz "
        "Lonsdale format. Perlas je sitna vitola — blaga, cvjetna, za jutarnju kavu.",
        "Rafael González is among Cuba's lightest marcas, historically tied to the "
        "Lonsdale format. Perlas is a tiny size — mild, floral, for a morning coffee.",
    ),
    "cig-ramon-allones-gigantes": (
        "Ramón Allones nosi najintenzivniji tamnovoćni, gotovo vinski profil kubanskog "
        "kataloga. Gigantes je dvostruka corona — najveći redovni format marke i njezin "
        "najpuniji izraz.",
        "Ramón Allones carries the most intense dark-fruit, almost wine-like profile in "
        "the Cuban catalogue. Gigantes is the double corona — the marca's largest "
        "regular size and its fullest expression.",
    ),
    "cig-ramon-allones-small-club": (
        "Mala Ramón Allones vitola — tamnovoćni, slatko-zemljani karakter marke u "
        "formatu od dvadesetak minuta.",
        "A small Ramón Allones — the marca's dark-fruit, sweet-earthy character in a "
        "twenty-minute format.",
    ),
    "cig-romeo-y-julieta-cedros-de-luxe": (
        "Serija koju Romeo y Julieta isporučuje u pojedinačnim cedrovim listovima — "
        "cedrovina dodatno naglašava drvenasto-slatki profil marke.",
        "The series Romeo y Julieta ships wrapped in individual cedar sheets — the "
        "cedar leans further into the marca's woody-sweet profile.",
    ),
    "cig-romeo-y-julieta-churchills": (
        "Cigara koja je formatu dala ime: Churchill je nazvan po Winstonu Churchillu, "
        "a Romeo y Julieta Churchills je njegov izvorni nositelj — 178 mm klasične "
        "kubanske ravnoteže cedrovine i slatkoće.",
        "The cigar that named the format: the Churchill is named for Winston Churchill, "
        "and Romeo y Julieta Churchills is its original bearer — 178 mm of classic "
        "Cuban balance between cedar and sweetness.",
    ),
    "cig-romeo-y-julieta-exhibicion": (
        "Tradicionalna Romeo y Julieta serija u nekoliko klasičnih formata — "
        "srednje tijelo, cedrovina i suha slatkoća, referentna kubanka za svaki dan.",
        "A traditional Romeo y Julieta series across several classic formats — medium "
        "body, cedar and dry sweetness, the reference everyday Cuban.",
    ),
    "cig-romeo-y-julieta-mille-fleurs": (
        "Mala Romeo y Julieta za kratku pauzu — cedrovo-slatki profil marke u pola sata.",
        "A small Romeo y Julieta for a short break — the marca's cedar-sweet profile in "
        "half an hour.",
    ),
    "cig-romeo-y-julieta-petit-royales": (
        "Kratki, deblji format iz moderne Romeo y Julieta ponude — širi ring drži dim "
        "hladnijim i kremastijim nego kod klasičnih tankih vitola.",
        "A short, thicker size from the modern Romeo y Julieta range — the wider ring "
        "keeps the smoke cooler and creamier than the classic thin sizes.",
    ),
    "cig-romeo-y-julieta-sports-largos": (
        "Kubanska cigara kratkog punjenja iz Romeo y Julieta ponude — brza, povoljna i "
        "izravna, bez pretenzija dugog punjenja.",
        "A Cuban short-filler from the Romeo y Julieta range — quick, affordable and "
        "direct, with none of the long-filler pretence.",
    ),
    "cig-sancho-panza-25": (
        "Sancho Panza je među najblažim kubanskim markama, poznata po suhom, "
        "orašasto-cvjetnom tonu i dugom, mirnom gorenju.",
        "Sancho Panza is among Cuba's mildest marcas, known for a dry, nutty-floral "
        "tone and a long, calm burn.",
    ),
    "cig-trinidad-coloniales": (
        "Trinidad je do 1998. bila diplomatski poklon, ne roba. Coloniales je corona "
        "s tradicionalnim pigtailom — svijetla, cvjetna i suha, prepoznatljivo lakša "
        "od Cohibe.",
        "Until 1998 Trinidad was a diplomatic gift, not merchandise. Coloniales is a "
        "corona with the traditional pigtail — bright, floral and dry, noticeably "
        "lighter than Cohiba.",
    ),
    "cig-trinidad-media-luna": (
        "Kratki, deblji Trinidad iz moderne ponude — cvjetni, medeni profil marke u "
        "formatu od pola sata.",
        "A short, thicker Trinidad from the modern range — the marca's floral, honeyed "
        "profile in a half-hour format.",
    ),
    "cig-trinidad-topes": (
        "Trinidad Topes je extra-vitola uvedena 2016. u redovnu ponudu — blagi figurado "
        "koji Trinidadovu cvjetnu slatkoću drži u dužoj, sporijoj liniji.",
        "Trinidad Topes joined the regular range in 2016 — a gently tapered figurado "
        "that carries Trinidad's floral sweetness through a longer, slower burn.",
    ),
    # ------------------------------------------------ Dominikanska Republika
    "cig-arturo-fuente-anejo": (
        "Añejo je nastao nakon uragana Georges 1998., kad je Fuente ostao bez Opus X "
        "pokrova: Connecticut Broadleaf odležan u bačvama konjaka, na tržištu samo u "
        "ograničenim godišnjim isporukama.",
        "Añejo was born after Hurricane Georges in 1998 left Fuente without Opus X "
        "wrapper: Connecticut Broadleaf aged in cognac barrels, released only in "
        "limited annual drops.",
    ),
    "cig-arturo-fuente-brevas-royales": (
        "Klasična Fuenteova serija pristupačnih formata — dominikansko punjenje i "
        "blaga, kremasta ravnoteža koja liniju drži među najprodavanijima kuće.",
        "Fuente's classic affordable series — Dominican filler and a mild, creamy "
        "balance that keeps the line among the house's best sellers.",
    ),
    "cig-arturo-fuente-chateau-fuente": (
        "Château Fuente je robusto serija kuće — kratka, široka i kremasta, dugo "
        "referentni dominikanski robusto srednje snage.",
        "Château Fuente is the house robusto series — short, wide and creamy, long a "
        "reference Dominican robusto of medium strength.",
    ),
    "cig-arturo-fuente-curly-head": (
        "Fuenteova povoljna serija s kamerunskim pokrovom i karakterističnim uvijenim "
        "vrhom — blaga, orašasto-slatka cigara za svaki dan.",
        "Fuente's value series with a Cameroon wrapper and the signature twisted head — "
        "a mild, nutty-sweet everyday cigar.",
    ),
    "cig-arturo-fuente-gran-reserva": (
        "Najšira Fuenteova linija: kamerunski pokrov preko dominikanskog punjenja, u "
        "desetak klasičnih formata. Blago, kremasto i orašasto — kuća u svom "
        "najpitkijem izdanju.",
        "Fuente's broadest line: a Cameroon wrapper over Dominican filler across a "
        "dozen classic sizes. Mild, creamy and nutty — the house at its most "
        "approachable.",
    ),
    "cig-arturo-fuente-hemingway": (
        "Serija figurada sa zatvorenom nogom, nazvana po Hemingwayu i valjana od "
        "najiskusnijih Fuenteovih torcedora. Short Story je njezin najpoznatiji "
        "format — mala cigara s dugim, slatkim finišem.",
        "A closed-foot figurado series named for Hemingway and rolled by Fuente's most "
        "experienced torcedores. Short Story is its best-known size — a small cigar "
        "with a long, sweet finish.",
    ),
    "cig-arturo-fuente-opus-x": (
        "Prva dominikanska cigara s dominikanskim pokrovom — Fuente je 1995. dokazao "
        "da se wrapper može uzgojiti na Chateau de la Fuente. Rijetka, puna i "
        "začinjena; godinama najtraženija cigara na tržištu.",
        "The first Dominican puro with a Dominican wrapper — in 1995 Fuente proved "
        "wrapper leaf could be grown at Chateau de la Fuente. Scarce, full and spicy; "
        "for years the most sought-after cigar on the market.",
    ),
    "cig-ashton-aged-maduro": (
        "Ashtonov maduro: Connecticut Broadleaf odležan dulje od standarda kuće, preko "
        "dominikanskog punjenja iz Fuenteove tvornice — tamno slatko, bez oštrine.",
        "Ashton's maduro: Connecticut Broadleaf aged longer than the house standard "
        "over Dominican filler from the Fuente factory — darkly sweet, with no edge.",
    ),
    "cig-ashton-heritage": (
        "Heritage Puro Sol nosi ekvadorski Sumatra pokrov sušen na suncu — punija i "
        "začinjenija Ashton linija od klasične bijele serije.",
        "Heritage Puro Sol carries a sun-grown Ecuadorian Sumatra wrapper — a fuller, "
        "spicier Ashton than the classic white-label series.",
    ),
    "cig-davidoff-demi-tasse": (
        "Najmanji Davidoff — cigareta uz espresso, gotova za deset do petnaest minuta, "
        "s prepoznatljivo suhom, cvjetnom Davidoff signaturom.",
        "The smallest Davidoff — an espresso-side smoke, done in ten to fifteen minutes, "
        "with the house's recognisably dry, floral signature.",
    ),
    "cig-davidoff-escurio": (
        "Escurio je iz Davidoffove Discovery serije: brazilski Cubra pokrov i "
        "brazilski Mata Fina u punjenju daju neuobičajeno voćnu, gotovo kiselkastu "
        "notu za tu kuću.",
        "Escurio comes from Davidoff's Discovery series: a Brazilian Cubra wrapper and "
        "Brazilian Mata Fina in the filler give an unusually fruity, almost tart note "
        "for the house.",
    ),
    "cig-davidoff-millennium": (
        "Millennium Blend je Davidoffova punija linija — više Piloto Cubano u punjenju "
        "i ekvadorski Habano pokrov, s izraženijom kavom i kožom nego bijela serija.",
        "The Millennium Blend is Davidoff's fuller line — more Piloto Cubano in the "
        "filler and an Ecuadorian Habano wrapper, with more coffee and leather than the "
        "white label.",
    ),
    "cig-davidoff-primeros": (
        "Primeros je Davidoffov mali format za kratko vrijeme — dostupan u nekoliko "
        "blendova kuće, uvijek kao petnaestominutna verzija veće linije.",
        "Primeros is Davidoff's small short-format line — offered in several house "
        "blends, always as the fifteen-minute version of a larger line.",
    ),
    "cig-davidoff-winston-churchill-the-late-hour": (
        "The Late Hour koristi duhane odležane u bačvama single malt viskija — "
        "najtamnija i najzačinjenija linija Winston Churchill serije, zamišljena za "
        "kraj večeri.",
        "The Late Hour uses tobaccos aged in single malt whisky casks — the darkest and "
        "spiciest line in the Winston Churchill series, built for the end of the "
        "evening.",
    ),
    "cig-davidoff-yamasa": (
        "Yamasa je rezultat desetljeća pokušaja da se u dominikanskoj regiji Yamasá "
        "uzgoji upotrebljiv duhan — kisela, željezovita zemlja daje neuobičajeno "
        "tamnu, mineralnu cigaru za Davidoff.",
        "Yamasa is the result of a decade spent making the Dominican Yamasá region grow "
        "usable tobacco — its acidic, iron-rich soil yields an unusually dark, mineral "
        "cigar for Davidoff.",
    ),
    "cig-e-p-carrillo-new-wave-connecticut": (
        "New Wave Connecticut je blaga linija Ernesta Pereza-Carrilla — ekvadorski "
        "Connecticut preko nikaragvanskog i dominikanskog punjenja, kremasto i "
        "orašasto, ali s više karaktera od tipične jutarnje cigare.",
        "New Wave Connecticut is Ernesto Perez-Carrillo's mild line — Ecuadorian "
        "Connecticut over Nicaraguan and Dominican filler, creamy and nutty but with "
        "more character than the typical morning cigar.",
    ),
    "cig-la-aurora-115-anniversary": (
        "Izdanje za 115 godina La Aurore, najstarije dominikanske tvornice (1903.) — "
        "svečani blend s nikaragvanskim i dominikanskim duhanima ispod ekvadorskog "
        "pokrova.",
        "The release for La Aurora's 115th year — the oldest Dominican factory, founded "
        "in 1903 — a celebratory blend of Nicaraguan and Dominican leaf under an "
        "Ecuadorian wrapper.",
    ),
    "cig-la-galera-1936-box-pressed": (
        "La Galera je vlastita marka tvornice Tabacalera Palma; 1936 nosi godinu njezina "
        "osnutka. Box-press verzija zbija dim i pojačava slatkoću.",
        "La Galera is the house brand of Tabacalera Palma; 1936 marks the year the "
        "factory was founded. The box-pressed version tightens the smoke and lifts the "
        "sweetness.",
    ),
    "cig-la-galera-habano": (
        "Habano izdanje La Galere — ekvadorski Habano pokrov preko dominikanskog "
        "punjenja iz Tabacalera Palme, srednje snage i klasično začinjeno.",
        "La Galera's Habano edition — an Ecuadorian Habano wrapper over Dominican filler "
        "from Tabacalera Palma, medium in strength and classically spicy.",
    ),
    "cig-la-galera-imperial-jade": (
        "Imperial Jade je viša linija La Galere — dulje odležani duhani i pažljiviji "
        "izbor listova nego u osnovnoj seriji.",
        "Imperial Jade is La Galera's upper line — longer-aged tobaccos and a more "
        "selective leaf grade than the core series.",
    ),
    "cig-la-galera-maduro": (
        "Maduro izdanje La Galere — tamni, dulje fermentirani pokrov nad istim "
        "dominikanskim punjenjem; slađe i zemljanije od Habano verzije.",
        "La Galera's maduro edition — a dark, longer-fermented wrapper over the same "
        "Dominican filler; sweeter and earthier than the Habano version.",
    ),
    "cig-la-instructora-delicado": (
        "La Instructora je butik marka tvornice Tabacalera Palma (Jochy Blanco), na "
        "tržištu od 2017. Delicado nosi američki Connecticut Shade pokrov — blago, "
        "kremasto i slatkasto.",
        "La Instructora is a boutique brand from Tabacalera Palma (Jochy Blanco), on the "
        "market since 2017. Delicado carries a US Connecticut Shade wrapper — mild, "
        "creamy and lightly sweet.",
    ),
    "cig-la-instructora-perfection": (
        "Perfection je punija La Instructora: ekvadorski Habano pokrov, dominikanski "
        "Criollo 98 vezivo i punjenje od Piloto i Criollo 98 — srednja snaga s jasnim "
        "začinom.",
        "Perfection is the fuller La Instructora: an Ecuadorian Habano wrapper, Dominican "
        "Criollo 98 binder and a Piloto and Criollo 98 filler — medium strength with "
        "clear spice.",
    ),
    "cig-la-instructora-perfection-extra": (
        "Veći format Perfection linije — isti blend Tabacalera Palme u duljoj cigari, "
        "s više vremena da se začin smiri u slatkoću.",
        "The larger Perfection size — the same Tabacalera Palma blend in a longer cigar, "
        "with more time for the spice to settle into sweetness.",
    ),
    "cig-pdr-1878": (
        "PDR (Pinar del Río) je dominikanska tvornica Abea Floresa, a 1878 njezina "
        "povoljna serija kraćeg odležavanja — zemljana i izravna.",
        "1878 is the value series from PDR (Pinar del Río), Abe Flores's Dominican "
        "factory — shorter-aged, earthy and direct.",
    ),
    "cig-pdr-a-flores-gran-reserva": (
        "Gran Reserva je vrh PDR ponude i osobni blend Abea Floresa — dulje odležani "
        "duhani, gušći dim i izraženija slatkoća od ostatka kuće.",
        "Gran Reserva is the top of PDR's range and Abe Flores's personal blend — "
        "longer-aged tobaccos, denser smoke and more pronounced sweetness than the rest "
        "of the house.",
    ),
    "cig-pdr-el-criollito": (
        "Mali format PDR-a s criollo pokrovom — kratko, začinjeno pušenje za pauzu.",
        "PDR's small criollo-wrapped size — a short, spicy break-time smoke.",
    ),
    "cig-pdr-flores-y-rodriguez-10th-anniversary": (
        "Jubilarni blend Floresa i Rodrígueza — ograničena serija dulje odležanih "
        "duhana, punija i slojevitija od redovne PDR ponude.",
        "The Flores y Rodríguez anniversary blend — a limited run of longer-aged "
        "tobaccos, fuller and more layered than PDR's regular range.",
    ),
    "cig-pdr-value-line-reserve-connecticut": (
        "Povoljna PDR linija s Connecticut pokrovom — blaga, kremasta cigara za svaki "
        "dan, bez ambicije da bude više od toga.",
        "PDR's value line under a Connecticut wrapper — a mild, creamy everyday cigar "
        "with no pretence of being more.",
    ),
    "cig-saga-solaz": (
        "Saga je linija tvornice De Los Reyes (Aging Room), a Solaz njezin pristupačan "
        "ulaz — dominikansko punjenje i blago, kremasto tijelo.",
        "Saga is a line from the De Los Reyes factory (Aging Room), and Solaz is its "
        "affordable entry — Dominican filler and a mild, creamy body.",
    ),
    # -------------------------------------------------------------- Nikaragva
    "cig-aganorsa-leaf-arsenio": (
        "Arsenio nosi ime Arsenija Ramosa, dugogodišnjeg majstora Aganorse. Corojo "
        "pokrov nad vlastitim nikaragvanskim duhanom farme — gust, uljast dim i "
        "izražena snaga.",
        "Arsenio is named for Arsenio Ramos, Aganorsa's long-serving master. A corojo "
        "wrapper over the farm's own Nicaraguan leaf — dense, oily smoke and real "
        "strength.",
    ),
    "cig-aging-room-quattro-nicaragua-espressivo": (
        "Quattro Nicaragua je Rafaela Nodala nikaragvanska serija u tvornici De Los "
        "Reyes. Espressivo je blaži format linije — sumatranski pokrov, kava i kakao "
        "bez težine.",
        "Quattro Nicaragua is Rafael Nodal's Nicaraguan series made at the De Los Reyes "
        "factory. Espressivo is the line's lighter size — a Sumatra wrapper, coffee and "
        "cocoa without the weight.",
    ),
    "cig-aging-room-quattro-nicaragua-maestro": (
        "Maestro je najjači format Quattro Nicaragua linije — figurado koji "
        "koncentrira začin i drži punu snagu kroz cijelu cigaru.",
        "Maestro is the strongest size in the Quattro Nicaragua line — a figurado that "
        "concentrates the spice and holds full strength throughout.",
    ),
    "cig-asylum-13-13": (
        "Asylum 13 je linija Christiana Eiroe i Toma Lazuke poznata po ekstremnim "
        "ringovima — nikaragvanski Habano pokrov i puna snaga, bez zaobilaženja.",
        "Asylum 13 is the Christian Eiroa and Tom Lazuka line known for extreme ring "
        "gauges — a Nicaraguan Habano wrapper and full strength, with nothing softened.",
    ),
    "cig-asylum-13-connecticut": (
        "Blaga strana Asyluma — ekvadorski Connecticut Shade nad hondureškim punjenjem, "
        "kremasto i orašasto, u istim velikim formatima kao ostatak marke.",
        "Asylum's mild side — Ecuadorian Connecticut Shade over Honduran filler, creamy "
        "and nutty, in the same oversized formats as the rest of the brand.",
    ),
    "cig-asylum-13-insidious-short": (
        "Insidious je pristupačnija Asylum linija; Short je njezin kratki format s "
        "ekvadorskim Connecticut pokrovom — blago i brzo.",
        "Insidious is Asylum's more affordable line; Short is its compact size under an "
        "Ecuadorian Connecticut wrapper — mild and quick.",
    ),
    "cig-camacho-ecuador": (
        "Camacho Ecuador je iz serije 'Master Built' — ekvadorski Habano pokrov nad "
        "hondureškim i dominikanskim punjenjem, s Camachovom prepoznatljivom "
        "izravnošću u mekšem izdanju.",
        "Camacho Ecuador comes from the Master Built series — an Ecuadorian Habano "
        "wrapper over Honduran and Dominican filler, with Camacho's trademark "
        "directness in a softer register.",
    ),
    "cig-camacho-nicaragua": (
        "Nikaragvanski član Camachove Master Built serije — puro iz Estelíja i Jalape, "
        "zemljan i paprenit, izrazito jak čak i za tu kuću.",
        "The Nicaraguan member of Camacho's Master Built series — a puro from Estelí and "
        "Jalapa, earthy and peppery, and notably strong even for this house.",
    ),
    "cig-joya-de-nicaragua-cinco-decadas": (
        "Cinco Décadas obilježava pedeset godina Joye de Nicaragua, najstarije "
        "nikaragvanske tvornice — ograničena serija s duhanima koje kuća drži izvan "
        "redovne proizvodnje.",
        "Cinco Décadas marks fifty years of Joya de Nicaragua, the country's oldest "
        "factory — a limited series using tobaccos the house keeps out of regular "
        "production.",
    ),
    "cig-joya-de-nicaragua-clasico-medio-siglo": (
        "Clásico je izvorni blend kuće iz 1968., najblaža Joya — kremasta i cvjetna, "
        "daleko od snage po kojoj je Nikaragva danas poznata.",
        "Clásico is the house's original 1968 blend and the mildest Joya — creamy and "
        "floral, far from the strength Nicaragua is known for today.",
    ),
    "cig-joya-de-nicaragua-cuatro-cinco-reserva-especial": (
        "Cuatro Cinco je nastao za 45 godina tvornice — duhani odležani pet godina u "
        "bačvama, s izraženom slatkoćom i mekim, dugim finišem.",
        "Cuatro Cinco was built for the factory's 45th year — tobaccos aged five years "
        "in barrels, with pronounced sweetness and a soft, long finish.",
    ),
    "cig-joya-de-nicaragua-joya-black": (
        "Joya Black je najtamnija u modernoj Joya seriji — meksički San Andrés pokrov, "
        "espresso i tamna čokolada, izrazito noćni profil.",
        "Joya Black is the darkest of the modern Joya series — a Mexican San Andrés "
        "wrapper, espresso and dark chocolate, an unmistakably late-night profile.",
    ),
    "cig-joya-de-nicaragua-joya-silver": (
        "Joya Silver je najblaža u modernoj seriji — ekvadorski Connecticut pokrov nad "
        "nikaragvanskim punjenjem; laganija, ali ne bezlična.",
        "Joya Silver is the mildest of the modern series — an Ecuadorian Connecticut "
        "wrapper over Nicaraguan filler; lighter, but not characterless.",
    ),
    "cig-la-aroma-de-cuba-base-line": (
        "Osnovna linija La Aroma de Cuba, koju za Ashton blenda Jose 'Pepin' Garcia u "
        "Nikaragvi — meksički San Andrés pokrov, kakao i zemlja srednje snage.",
        "The core La Aroma de Cuba line, blended for Ashton by Jose 'Pepin' Garcia in "
        "Nicaragua — a Mexican San Andrés wrapper, cocoa and earth at medium strength.",
    ),
    "cig-la-aroma-de-cuba-connecticut": (
        "Blaga verzija La Aroma de Cuba — ekvadorski Connecticut nad nikaragvanskim "
        "punjenjem, kremasto i orašasto, uz zadržan Pepinov začin u pozadini.",
        "The mild La Aroma de Cuba — Ecuadorian Connecticut over Nicaraguan filler, "
        "creamy and nutty, with Pepin's spice still present in the background.",
    ),
    "cig-la-aroma-de-cuba-edicion-especial-no-3": (
        "Edición Especial je punija La Aroma de Cuba linija — nikaragvansko punjenje "
        "pod tamnijim pokrovom, s više začina i dužim finišem od osnovne serije.",
        "Edición Especial is the fuller La Aroma de Cuba line — Nicaraguan filler under "
        "a darker wrapper, with more spice and a longer finish than the core series.",
    ),
    "cig-la-aroma-de-cuba-mi-amor": (
        "Mi Amor je najpoznatija La Aroma de Cuba — meksički San Andrés maduro nad "
        "nikaragvanskim punjenjem, s gustom čokoladno-espresso slatkoćom.",
        "Mi Amor is the best-known La Aroma de Cuba — Mexican San Andrés maduro over "
        "Nicaraguan filler, with a dense chocolate-and-espresso sweetness.",
    ),
    "cig-la-aroma-de-cuba-pasion": (
        "Pasión je linija koju je Pepin Garcia zamislio kao najzačinjeniju u seriji — "
        "puna snaga, papar i tamna zemlja.",
        "Pasión is the line Pepin Garcia built as the series' spiciest — full strength, "
        "pepper and dark earth.",
    ),
    "cig-nub-cameroon": (
        "Nub je Olivin koncept: cigara skraćena na dio u kojem je blend najbolji, s "
        "ringom 60 na svega desetak centimetara. Kamerunska verzija je najslađa i "
        "najblaža u seriji.",
        "Nub is Oliva's concept: a cigar cut down to the stretch where the blend peaks, "
        "ring 60 over barely ten centimetres. The Cameroon version is the sweetest and "
        "mildest of the series.",
    ),
    "cig-nub-sun-grown": (
        "Sun Grown Nub je punija verzija koncepta — na suncu uzgojen pokrov daje više "
        "začina i snage u istom kratkom, širokom formatu.",
        "The Sun Grown Nub is the fuller take on the concept — a sun-grown wrapper "
        "brings more spice and strength to the same short, wide format.",
    ),
    "cig-padilla-88th-aniversario": (
        "Izdanje Ernesta Padille za 88. godišnjicu — nikaragvanski blend s dulje "
        "odležanim duhanima i punijim, začinjenijim profilom od redovne ponude.",
        "Ernesto Padilla's 88th anniversary release — a Nicaraguan blend with "
        "longer-aged tobaccos and a fuller, spicier profile than the regular range.",
    ),
    "cig-plasencia-alma-del-fuego": (
        "Alma del Fuego koristi duhan uzgojen na vulkanskom tlu otoka Ometepe — "
        "Plasencia ga opisuje kao 'dušu vatre'; mineralno, začinjeno i izrazito "
        "prepoznatljivo.",
        "Alma del Fuego uses tobacco grown on the volcanic soil of Ometepe island — "
        "Plasencia calls it the soul of fire; mineral, spicy and unmistakable.",
    ),
    "cig-plasencia-cosecha-149": (
        "Cosecha 149 obilježava 149. berbu obitelji Plasencia — jednogodišnja berba "
        "hondureških duhana s Jamastran polja, u ograničenoj proizvodnji.",
        "Cosecha 149 marks the Plasencia family's 149th harvest — a single-vintage run "
        "of Honduran leaf from the Jamastrán fields, made in limited numbers.",
    ),
    "cig-plasencia-cosecha-151": (
        "Cosecha 151 nastavlja seriju berbi — nikaragvanski duhani iz jedne godine, "
        "punijeg i zemljanijeg profila od prethodnog izdanja.",
        "Cosecha 151 continues the harvest series — single-year Nicaraguan tobaccos, "
        "fuller and earthier than the previous release.",
    ),
    "cig-plasencia-ehtefal": (
        "Ehtefal ('slavlje' na arapskom) je Plasencijino izdanje za bliskoistočno "
        "tržište — svečan blend, ograničena dostupnost.",
        "Ehtefal — Arabic for celebration — is Plasencia's release for the Middle "
        "Eastern market: a celebratory blend in limited supply.",
    ),
    "cig-plasencia-year-of-the-tiger": (
        "Izdanje za kinesku godinu tigra — Plasencijina ograničena serija s posebnim "
        "pakiranjem i blendom izvan redovne ponude.",
        "The release for the Chinese year of the tiger — a limited Plasencia series with "
        "special packaging and a blend outside the regular range.",
    ),
    "cig-rocky-patel-aged-limited-rare-second-edition": (
        "ALR (Aged, Limited, Rare) je Rocky Patelova serija dulje odležanih duhana — "
        "druga edicija donosi punije tijelo i izraženiju slatkoću od prve.",
        "ALR (Aged, Limited, Rare) is Rocky Patel's longer-aged series — the second "
        "edition brings a fuller body and more pronounced sweetness than the first.",
    ),
    "cig-rocky-patel-conviction": (
        "Conviction je Rocky Patelova punija linija — nikaragvansko punjenje i tamniji "
        "pokrov, s naglašenim začinom i kožom.",
        "Conviction is one of Rocky Patel's fuller lines — Nicaraguan filler and a "
        "darker wrapper, leaning on spice and leather.",
    ),
    "cig-rocky-patel-grand-reserve": (
        "Grand Reserve je pristupačnija Rocky Patel serija — nikaragvansko punjenje, "
        "srednja snaga i klasičan kakao-kava profil.",
        "Grand Reserve is one of Rocky Patel's more affordable series — Nicaraguan "
        "filler, medium strength and a classic cocoa-and-coffee profile.",
    ),
    # ---------------------------------------------------------------- Honduras
    "cig-cle-25th-anniversary": (
        "CLE su inicijali Christiana Luisa Eiroe, nekadašnjeg vlasnika Camacha. "
        "25th Anniversary obilježava njegovih 25 godina u duhanu — hondureški blend "
        "pune snage.",
        "CLE are the initials of Christian Luis Eiroa, once the owner of Camacho. The "
        "25th Anniversary marks his quarter-century in tobacco — a full-strength "
        "Honduran blend.",
    ),
    "cig-cle-connecticut": (
        "Blaga CLE linija — Connecticut pokrov nad hondureškim punjenjem s obiteljskih "
        "Eiroa polja u dolini Jamastrán.",
        "CLE's mild line — a Connecticut wrapper over Honduran filler from the Eiroa "
        "family fields in the Jamastrán valley.",
    ),
    "cig-cle-criollo": (
        "Criollo verzija CLE-a — hondureški criollo pokrov daje suši, začinjeniji "
        "profil od Connecticut linije, uz istu obiteljsku podlogu.",
        "The criollo CLE — a Honduran criollo wrapper gives a drier, spicier profile "
        "than the Connecticut line over the same family-grown base.",
    ),
    "cig-cle-prieto": (
        "Prieto je najtamniji CLE — maduro pokrov i gušće punjenje, s izraženom "
        "čokoladno-zemljanom slatkoćom.",
        "Prieto is the darkest CLE — a maduro wrapper and denser filler, with "
        "pronounced chocolate-and-earth sweetness.",
    ),
    "cig-cumpay-numero-xv": (
        "Cumpay je nikaragvanska marka Maye Selve (1999.), sestrinska Flor de Selvi — "
        "100% duhan iz doline Jalapa, s pečenom kavom, lješnjakom i kožom. Numero XV "
        "je jubilarno izdanje linije.",
        "Cumpay is Maya Selva's Nicaraguan brand (1999), sibling to Flor de Selva — "
        "100% Jalapa valley tobacco, with roasted coffee, hazelnut and leather. Numero "
        "XV is the line's anniversary release.",
    ),
    "cig-cumpay-robusto": (
        "Klasični Cumpay robusto — nikaragvanski puro iz doline Jalapa, srednje-puno "
        "tijelo s tonovima pečene kave i lješnjaka.",
        "The classic Cumpay robusto — a Nicaraguan puro from the Jalapa valley, "
        "medium-full with roasted coffee and hazelnut.",
    ),
    "cig-cumpay-short": (
        "Kratki Cumpay format — isti jalapski puro u cigari za pauzu od pola sata.",
        "The short Cumpay — the same Jalapa puro in a half-hour break format.",
    ),
    "cig-cumpay-volcan-maduro": (
        "Maduro izdanje Cumpaya — tamniji, dulje fermentirani pokrov nad nikaragvanskim "
        "punjenjem; slađe i zemljanije od standardne linije.",
        "Cumpay's maduro — a darker, longer-fermented wrapper over Nicaraguan filler; "
        "sweeter and earthier than the standard line.",
    ),
    "cig-eiroa-20-years-maduro": (
        "Christian Eiroa je Eiroa liniju posvetio duhanu s obiteljskih polja. 20 Years "
        "Maduro nosi dulje odležan tamni pokrov i najslađi je izraz serije.",
        "Christian Eiroa built the Eiroa line around leaf from the family's own fields. "
        "20 Years Maduro carries a longer-aged dark wrapper and is the sweetest "
        "expression of the series.",
    ),
    "cig-eiroa-cbt": (
        "CBT znači Connecticut Broadleaf Talls — Eiroa koristi gornje listove biljke, "
        "koji nose više ulja i slatkoće od uobičajenih.",
        "CBT stands for Connecticut Broadleaf Talls — Eiroa uses the plant's upper "
        "leaves, which carry more oil and sweetness than the usual grades.",
    ),
    "cig-eiroa-cbt-maduro": (
        "Maduro verzija CBT-a — dodatna fermentacija broadleaf pokrova daje tamniju, "
        "čokoladniju cigaru bez gubitka Eiroine hondureške podloge.",
        "The maduro CBT — extra fermentation of the broadleaf wrapper gives a darker, "
        "more chocolatey cigar without losing Eiroa's Honduran base.",
    ),
    "cig-eiroa-classic": (
        "Osnovna Eiroa linija — hondureški puro s obiteljskih polja u dolini "
        "Jamastrán, srednje-pune snage i s izraženim zemljanim tonom.",
        "The core Eiroa line — a Honduran puro from the family fields in the Jamastrán "
        "valley, medium-full with a pronounced earthy tone.",
    ),
    "cig-flor-de-selva-fino": (
        "Vitki Flor de Selva format — tanak ring naglašava pokrov i elegantnu, cvjetnu "
        "stranu hondureškog blenda.",
        "The slim Flor de Selva — a thin ring that puts the wrapper and the blend's "
        "elegant, floral side forward.",
    ),
    "cig-flor-de-selva-maduro": (
        "Maduro izdanje Flor de Selve — tamni pokrov nad istim hondureškim punjenjem "
        "iz doline Jamastrán; slađe i punije od klasične linije.",
        "Flor de Selva's maduro — a dark wrapper over the same Honduran Jamastrán "
        "filler; sweeter and fuller than the classic line.",
    ),
    "cig-flor-de-selva-grand-presse-maduro": (
        "Box-pressano maduro izdanje — prešani oblik zbija dim i pojačava tamnu "
        "slatkoću pokrova.",
        "The box-pressed maduro — the pressed shape tightens the smoke and lifts the "
        "wrapper's dark sweetness.",
    ),
    "cig-flor-de-selva-no-20": (
        "No. 20 je jedan od klasičnih Flor de Selva formata — srednje tijelo i mirno, "
        "ujednačeno gorenje po kojem je kuća prepoznatljiva.",
        "No. 20 is one of the classic Flor de Selva sizes — medium body and the calm, "
        "even burn the house is known for.",
    ),
    "cig-flor-de-selva-numero-xv": (
        "Numero XV je izdanje za petnaest godina Flor de Selve — svečaniji blend s "
        "dulje odležanim listovima.",
        "Numero XV marks fifteen years of Flor de Selva — a more celebratory blend with "
        "longer-aged leaf.",
    ),
    "cig-flor-de-selva-tempo": (
        "Tempo je kraći Flor de Selva format — ista hondureška elegancija u cigari za "
        "pola sata.",
        "Tempo is the shorter Flor de Selva — the same Honduran elegance in a half-hour "
        "cigar.",
    ),
    "cig-flor-de-selva-year-of-the-dragon-2024": (
        "Izdanje za kinesku godinu zmaja — ograničena Flor de Selva serija s posebnim "
        "pakiranjem.",
        "The release for the Chinese year of the dragon — a limited Flor de Selva series "
        "with special packaging.",
    ),
    "cig-flor-de-selva-coffret": (
        "Coffret je poklon-kutija Flor de Selve — nekoliko formata linije u jednom "
        "pakiranju, kao pregled stila kuće.",
        "The Coffret is Flor de Selva's gift box — several of the line's sizes in one "
        "package, as a survey of the house style.",
    ),
    "cig-jfr-connecticut": (
        "JFR (Just For Retailers) je linija obitelji Perez-Carrillo koja se prodaje "
        "isključivo preko trgovina — velike vitole po niskoj cijeni. Connecticut je "
        "njezina blaga verzija.",
        "JFR (Just For Retailers) is the Perez-Carrillo family line sold only through "
        "shops — large sizes at low prices. Connecticut is its mild version.",
    ),
    "cig-leaf-by-oscar-by-oscar-connecticut": (
        "Leaf by Oscar dolazi omotana duhanskim listom umjesto celofana — Oscar "
        "Valladares tako štiti cigaru u transportu. Connecticut verzija je blaga i "
        "kremasta.",
        "Leaf by Oscar ships wrapped in a tobacco leaf instead of cellophane — Oscar "
        "Valladares's way of protecting the cigar in transit. The Connecticut version is "
        "mild and creamy.",
    ),
    "cig-leaf-by-oscar-by-oscar-corojo": (
        "Corojo verzija Leaf by Oscara — ista prepoznatljiva ovojnica od duhanskog "
        "lista, ali punija i začinjenija cigara ispod nje.",
        "The corojo Leaf by Oscar — the same distinctive tobacco-leaf sleeve, with a "
        "fuller, spicier cigar underneath.",
    ),
    "cig-maestranza-baron": (
        "Maestranzu proizvodi belgijska duhanska obitelj Meerapfel — ručno valjana u "
        "Hondurasu, s nikaragvanskim i hondureškim punjenjem pod kostarikanskim "
        "pokrovom. Baron je corona format.",
        "Maestranza is produced by the Belgian Meerapfel tobacco family — rolled in "
        "Honduras with Nicaraguan and Honduran filler under a Costa Rican wrapper. Baron "
        "is the corona size.",
    ),
    "cig-maestranza-conde": (
        "Conde je robusto format Maestranze — izravniji i gušći od Barona, uz istu "
        "eleganciju koja marku definira.",
        "Conde is Maestranza's robusto — more direct and denser than the Baron, with the "
        "same elegance that defines the brand.",
    ),
    "cig-maestranza-marques": (
        "Marques je toro format Maestranze — najduži u seriji, s uravnoteženim začinom "
        "kroz cijelo pušenje.",
        "Marques is Maestranza's toro — the longest in the series, with balanced spice "
        "throughout.",
    ),
    "cig-omar-ortez-original": (
        "Omar Ortez je povoljna hondureška linija Alec Bradleyja — jednostavna, "
        "zemljana cigara za svaki dan, bez pretenzija.",
        "Omar Ortez is Alec Bradley's value Honduran line — a simple, earthy everyday "
        "cigar with no pretensions.",
    ),
    "cig-omar-ortez-connecticut": (
        "Connecticut verzija Omara Orteza — blaža i kremastija od originala, uz istu "
        "pristupačnu cijenu.",
        "The Connecticut Omar Ortez — milder and creamier than the original, at the same "
        "accessible price.",
    ),
    "cig-omar-ortez-maduro": (
        "Maduro Omar Ortez — tamni pokrov donosi slatkoću kakaa i kave uz isto "
        "hondureško punjenje.",
        "The maduro Omar Ortez — a dark wrapper brings cocoa and coffee sweetness over "
        "the same Honduran filler.",
    ),
    "cig-villa-zamorano-bouquet": (
        "Villa Zamorano je treća marka Maye Selve — hondureška cigara srednjeg punjenja "
        "po pristupačnoj cijeni, zamišljena kao svakodnevna.",
        "Villa Zamorano is Maya Selva's third brand — an affordable Honduran cigar built "
        "as an everyday smoke.",
    ),
    # ------------------------------------------------------------- Nikaragva/DR
    "cig-1502-special-edition-blue-sapphire": (
        "1502 je nazvana po godini kad su Europljani prvi put vidjeli duhan u "
        "Nikaragvi. Blue Sapphire je posebno izdanje linije — Habano pokrov i "
        "uravnotežen, cedrovo-začinski profil.",
        "1502 is named for the year Europeans first saw tobacco in Nicaragua. Blue "
        "Sapphire is the line's special edition — a Habano wrapper and a balanced "
        "cedar-and-spice profile.",
    ),
    "cig-cao-bones": (
        "CAO Bones je nikaragvanska linija nazvana po kockarskim izrazima — vitole nose "
        "imena Chicken Foot i Blind Hughie iz igre domina. Meksički San Andrés pokrov "
        "daje tamnu, čokoladno-zemljanu slatkoću.",
        "CAO Bones is a Nicaraguan line named after gambling slang — its sizes are "
        "called Chicken Foot and Blind Hughie after domino plays. A Mexican San Andrés "
        "wrapper gives dark, chocolate-and-earth sweetness.",
    ),
    "cig-casa-1910-as-de-oro": (
        "Casa 1910 nosi ime po godini meksičke revolucije, a linije po njezinim "
        "likovima i motivima. As de Oro je izdanje s meksičkim San Andrés duhanom — "
        "zemljano i slatko.",
        "Casa 1910 is named for the year of the Mexican Revolution, its lines for its "
        "figures and motifs. As de Oro is the San Andrés release — earthy and sweet.",
    ),
    "cig-casa-1910-jilguero": (
        "Jilguero je jedan od blažih Casa 1910 blendova — meksički duhan u finijem, "
        "cvjetnijem izdanju.",
        "Jilguero is one of Casa 1910's milder blends — Mexican leaf in a finer, more "
        "floral register.",
    ),
    "cig-casa-1910-la-coronela": (
        "La Coronela nosi ime po ženama koje su vodile revolucionarne odrede — punija "
        "Casa 1910 linija s izraženim začinom.",
        "La Coronela is named for the women who led revolutionary units — a fuller Casa "
        "1910 line with pronounced spice.",
    ),
    "cig-casa-1910-lucero": (
        "Lucero je Casa 1910 blend srednje snage — meksički duhan s kakao-zemljanim "
        "tonom i mirnim gorenjem.",
        "Lucero is Casa 1910's medium blend — Mexican leaf with a cocoa-and-earth tone "
        "and a calm burn.",
    ),
    "cig-casa-1910-sampetrina": (
        "Sampetrina je jedno od izdanja Casa 1910 s meksičkim duhanom — prepoznatljiv "
        "zemljano-slatki profil kuće.",
        "Sampetrina is one of Casa 1910's Mexican-leaf releases — the house's "
        "recognisable earthy-sweet profile.",
    ),
    "cig-casa-1910-teniente-angela": (
        "Teniente Angela je nazvana po revolucionarki Ángeli Jiménez — punija Casa 1910 "
        "cigara s tamnim pokrovom.",
        "Teniente Angela is named for the revolutionary Ángela Jiménez — a fuller Casa "
        "1910 under a dark wrapper.",
    ),
    "cig-casa-1910-tierra-blanca": (
        "Tierra Blanca je blaži kraj Casa 1910 ponude — svjetliji pokrov i kremastiji, "
        "mekši dim.",
        "Tierra Blanca is the milder end of Casa 1910's range — a lighter wrapper and a "
        "creamier, softer smoke.",
    ),
    "cig-k-fire-k-fire-by-karen-berger": (
        "Karen Berger je marku pokrenula da nastavi ostavštinu svog supruga, poznatog "
        "kao Don Kiki; cigare se valjaju u Tabacalera Estelí u Nikaragvi. K-Fire je "
        "punija linija serije.",
        "Karen Berger started the brand to continue the legacy of her husband, known as "
        "Don Kiki; the cigars are rolled at Tabacalera Estelí in Nicaragua. K-Fire is "
        "the series' fuller line.",
    ),
    "cig-karen-berger-cameroon": (
        "Kamerunska verzija K by Karen Berger — valjana u Estelíju, s tipičnom "
        "kamerunskom slatkoćom i suhim, orašastim tonom.",
        "The Cameroon K by Karen Berger — rolled in Estelí, with Cameroon's typical "
        "sweetness and a dry, nutty tone.",
    ),
    "cig-karen-berger-connecticut": (
        "Connecticut K by Karen Berger — najblaža u seriji, kremasta i glatka, "
        "zamišljena za opušteno pušenje.",
        "The Connecticut K by Karen Berger — the mildest of the series, creamy and "
        "smooth, built for relaxed smoking.",
    ),
    "cig-karen-berger-habano": (
        "Habano K by Karen Berger — klasičan začin i srednje tijelo, srednja točka "
        "između Connecticut i Cameroon izdanja.",
        "The Habano K by Karen Berger — classic spice and a medium body, the midpoint "
        "between the Connecticut and Cameroon editions.",
    ),
    "cig-aj-fernandez-k-by-karen-berger": (
        "Izdanje K by Karen Berger valjano kod AJ Fernandeza — nikaragvansko punjenje i "
        "punija, začinjenija interpretacija linije.",
        "The K by Karen Berger release rolled at AJ Fernandez — Nicaraguan filler and a "
        "fuller, spicier reading of the line.",
    ),
    "cig-lunatic-el-loquito": (
        "Lunatic je linija Casdagli/Aganorsa suradnje poznata po neobičnim oblicima; "
        "El Loquito je njezin mali, zdepasti format pune snage.",
        "Lunatic is a line known for odd shapes; El Loquito is its small, stubby "
        "full-strength format.",
    ),
    "cig-the-oscar-11": (
        "The Oscar je vlastita linija Oscara Valladaresa iz Danlíja u Hondurasu — "
        "pažljivije birani listovi nego u ostatku njegove ponude.",
        "The Oscar is Oscar Valladares's own line from Danlí in Honduras — a more "
        "selective leaf grade than the rest of his range.",
    ),
    # ------------------------------------------------------------------ Sampleri
    "cig-la-galera-robusto-sampler": (
        "Sampler robusto formata iz La Galere — nekoliko blendova Tabacalera Palme u "
        "istoj vitoli, za usporedbu pokrova.",
        "A La Galera robusto sampler — several Tabacalera Palma blends in the same size, "
        "for comparing wrappers.",
    ),
    "cig-la-galera-toro-sampler": (
        "Isti princip u toro formatu — La Galera blendovi jedan uz drugi, u duljoj "
        "vitoli.",
        "The same idea in toro — La Galera blends side by side in a longer size.",
    ),
    "cig-la-galera-rojo-gift-pack": (
        "Poklon-pakiranje La Galere — izbor formata kuće u kutiji za darivanje.",
        "A La Galera gift pack — a selection of the house's sizes boxed for giving.",
    ),
    "cig-oliva-robusto-sampler": (
        "Sampler Olivinih robusta — Serie G, Serie O i srodne linije u istom formatu, "
        "kao pregled ponude kuće.",
        "A sampler of Oliva robustos — Serie G, Serie O and related lines in one size, "
        "as a survey of the house.",
    ),
    "cig-nub-sampler-tubos": (
        "Nub sampler u tubama — nekoliko pokrova istog kratkog, širokog koncepta, za "
        "usporedbu.",
        "A tubed Nub sampler — several wrappers of the same short, wide concept, for "
        "comparison.",
    ),
    "cig-oscar-valladares-sampler": (
        "Sampler Oscara Valladaresa — presjek njegovih hondureških linija, uključujući "
        "prepoznatljivu Leaf by Oscar ovojnicu.",
        "An Oscar Valladares sampler — a cross-section of his Honduran lines, including "
        "the distinctive Leaf by Oscar sleeve.",
    ),
}


def main() -> None:
    out = {k: {"hr": hr, "en": en} for k, (hr, en) in DESCRIPTIONS.items()}
    path = HERE / "cigar_descriptions.json"
    path.write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(out)} descriptions -> {path}")


if __name__ == "__main__":
    main()
