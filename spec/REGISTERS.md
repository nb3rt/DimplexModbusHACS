# Dimplex NWPM (WPM Touch) — kanoniczna mapa rejestrów Modbus TCP

> **Jedyne źródło prawdy** dla generowania EntityDescription w komponencie
> `dimplex_wpm`. Scala: oficjalna wiki Dimplex (autorytet) + `DimplexModbusHA`
> + `DimplexModbusHACS` + lokalne YAML. Surowy zrzut wiki:
> [`dimplex_modbus_spec_raw.md`](dimplex_modbus_spec_raw.md).
> Sprzęt: NWPM Touch (art. 378800), Modbus TCP port 502, od WPM Software **M3.3**.
>
> **Status: ZWERYFIKOWANO (2026-06-21)** — adwersaryjna kontrola 4 agentami
> wobec surowego spec, rejestr po rejestrze. Zero błędów krytycznych/poważnych.

## 0. Reguły ogólne (ważne korekty względem dotychczasowych źródeł)

1. **Typy obiektów wg FC:** spec wspiera tylko `FC01 Read Coils`,
   `FC03 Read Holding`, `FC05/06/15/16 Write`. **Brak FC04 (input registers).**
   → Wszystkie wartości analogowe to **holding (FC03)**, cyfrowe to **coil (FC01)**.
   Lokalne YAML używało `input_type: input` (FC04) — **do zmiany na holding**.
   (To tłumaczy „register_strategy: auto/holding/input" w repo HACS — obejście.)
   **Domyślnie czytamy holding (FC03).**
2. **Energia 5096–5129 to grupy CYFR jednego licznika, nie kwartały.**
   `Wärmemenge = reg(9-12)·100000000 + reg(5-8)·10000 + reg(1-4)`. Nazwy „1-4 /
   5-8 / 9-12" = pozycje cyfr, **nie** miesiące. Dotychczasowa interpretacja
   kwartalna (3 osobne sensory `total_increasing`) jest **błędna** — liczymy
   jeden sumaryczny sensor kWh na kategorię.
3. **Adres rejestru status/blokada/błąd zależy od wersji softu** (patrz §1).
   L/M: 103/104/105/106 · J: 43/59/42/— · H: 14/94/13/—. Mapy wartości też się
   różnią. **Urządzenie użytkownika = software L/M** (potwierdzone: mapy
   status/lock/fault z lokalnego YAML zgadzają się 1:1 z kolumną L/M).
4. **Realne rejestry mocy istnieją (WPM M3.5+):** `5170` moc elektryczna,
   `5168` moc grzewcza (oddana), `W/10` → kW = `value·0.01`. **Gdy dostępne,
   preferujemy odczyt nad estymacją**; estymacja = fallback dla starszego softu
   i cross-check. (Uwaga: DPT podany jako uint16, ale zakres ±327670 → traktować
   jako int16 W/10 i zweryfikować znak na realnym urządzeniu.)
5. **Częstotliwość inwertera (114, 0.1 Hz) NIE jest w oficjalnym spec** — to
   reverse engineering użytkownika. Zostaje, oznaczone `RE/undocumented`;
   kluczowe dla LUT mocy (fallback gdy brak 5170).
6. **Konflikt:** stare repo mapowało `9/10` = skraplacz in/out — to **kłóci się**
   z oficjalnym `9` = temp. 2. obiegu, `10` = temp. 3. obiegu. Rejestry gazu/
   ssania/parownika (`8/98/108/109`) są prawdopodobne-niedokumentowane →
   `RE/verify` na realnym LAK9, poza domyślną mapą.
7. **Rejestr 10 jest współdzielony:** temp. 3. obiegu (R13) **albo** kolektor
   solarny (R23) — zależnie od konfiguracji instalacji (profil/moduł).
8. **Stuby z repo HACS rozwiązane:** BMS temp. zewn. `112` (R/W), Sperre Extern
   `5130` (R/W), Heartbeat `5063`(W)/`5064`(R).
9. **Programy czasowe multipleksują rejestr `5065`** (selektor 1..12) + `5066–5081`
   = parametry wybranego programu. Interfejs stanowy/ekspercki → **odłożone**
   (osobny milestone / premium „automatyzacja taryf").
10. **Nastawy z kodowaniem enum:** Parallelverschiebung `5036`/`5086` (0..38 →
    −19..+19 K), Kühlung Raumsoll `5089` (0..30 → 15.0..30.0 °C) — wymagają
    dekodera przy wyświetlaniu/zapisie.

Legenda: **Obj** = coil/holding · **R/W** wg spec · **Sc** = scale · **Ver** =
wersje softu · `†` = do potwierdzenia na realnym urządzeniu.

---

## 1. Status / diagnostyka (adres zależny od wersji!)

| Wartość | Obj | R/W | Typ | L/M addr | J addr | H addr | Nazwa |
|--:|--|--|--|--:|--:|--:|--|
| Status (Statusmeldungen) | holding | R | uint16 | **103** | 43 | 14 | kod stanu pracy → tekst |
| Blokada (Sperrmeldungen) | holding | R | uint16 | **104** | 59 | 94 | kod blokady → tekst |
| Błąd (Störmeldungen) | holding | R | uint16 | **105** | 42 | 13 | kod usterki → tekst |
| Sensor error (Sensorfehler) | holding | R | uint16 | **106** | — | — | tylko L/M |
| Software Version | holding | R | uint16 | 65 | 65 | 65 | 0:--,1:A…26:Z |
| Software Nummer | holding | R | uint16 | 66 | 66 | 66 | cyfra |
| Software Index | holding | R | uint16 | 67 | 67 | 67 | cyfra |

Wartości min/max: status 0–30, blokada 1–42, błąd 1–31, sensor error 1–27 (L/M).
(Uwaga: tabela enumów Sensorfehler ma wartości do 30 — niespójność po stronie
wiki; w mapie tekstów przyjmujemy pełen zakres do 30.)

---

## 2. Dane bieżące / temperatury (holding R, int16, scale 0.1 °C — chyba że zazn.)

| Addr | Nazwa (EN) | Moduł | Uwagi |
|--:|--|--|--|
| 1 | Outdoor temperature (R1) | controller | |
| 2 | Return temperature (R2) | hc1 | |
| 53 | Return setpoint temperature | hc1 | |
| 3 | DHW temperature (R3) | dhw | |
| 58 | DHW setpoint temperature | dhw | |
| 5 | Flow temperature (R9) | hc1 | |
| 6 | Source inlet temp (R24)† | source | gwiazdka w spec (wariant) |
| 7 | Source outlet temp (R6) | source | |
| 54 | HC2 setpoint | hc2_3 | |
| 9 | HC2 temperature (R5) | hc2_3 | konflikt: stare repo=skraplacz-in (błędne) |
| 55 | HC3 setpoint | hc2_3 | |
| 10 | HC3 temperature (R13) **/ Solar collector (R23)** | hc2_3/solar | współdzielony |
| 11 | Room temperature 1 / RT-RTH Econ | hc1 | (R/W w trybie BMS, patrz §13) |
| 12 | Room temperature 2 | hc1 | |
| 13 | Room humidity 1 (0.1 %) | hc1 | (R/W w trybie BMS) |
| 14 | Room humidity 2 (0.1 %) | hc1 | |
| 19 | Passive cooling flow temp (R11) | cooling | |
| 20 | Passive cooling return temp (R4) | cooling | |
| 21 | Passive/active cooling primary return (R24) | cooling | |
| 23 | Solar tank temp (R22) | solar | |
| 120 | Ventilation outdoor air temp | vent | |
| 121 | Ventilation supply air temp | vent | |
| 122 | Ventilation extract air temp | vent | |
| 123 | Ventilation exhaust air temp | vent | |
| 125 | Supply fan speed (1/min) | vent | scale 1 (int16) — **uwaga: coil 125 to inny obiekt** |
| 126 | Extract fan speed (1/min) | vent | scale 1 (int16) |

**RE/verify (poza domyślną mapą, profil LAK9 do potwierdzenia na sprzęcie):**
114 inverter frequency (0.1 Hz, RE), 8 hot gas†, 98 evaporator out†,
107 indoor humidity†, 108 suction gas†, 109 evaporator mid†.

---

## 3. Tryb pracy / wentylacja (holding R/W)

| Addr | Nazwa | Zakres | Enum |
|--:|--|--|--|
| 5015 | Operating mode (BA_aktiv) | 0–5 | 0:Sommer 1:Winter 2:Urlaub 3:Party 4:2.WE 5:Kühlen |
| 5016 | Party hours | 0–72 h | |
| 5017 | Holiday days | 0–150 d | |
| 5034 | Ventilation level | 0–5 | |
| 127 | Ventilation boost time | 15–90 | (holding R/W; coil 127≠) |

---

## 4. Runtime'y (holding R, uint16, h, total_increasing) — diagnostic

72 Verdichter1 · 73 Verdichter2 · 74 Primärpumpe/Ventilator(M11) ·
75 2.Wärmeerzeuger(E10) · 76 Heizungspumpe(M13) · 77 Warmwasserpumpe(M18) ·
78 Flanschheizung(E9) · 79 Schwimmbadpumpe(M19) · 71 Zusatzumwälzpumpe(M16) `ab L12`.

---

## 5. Energia / ilości ciepła (holding R, uint16, kWh) — grupy cyfr!

Kategorie: Heizen `5096/5097/5098`, Warmwasser `5099/5100/5101`,
Schwimmbad `5102/5103/5104`, Umwelt(środowiskowa) `5127/5128/5129`.
**Sensor wynikowy/kategoria:** `total = reg(9-12)·1e8 + reg(5-8)·1e4 + reg(1-4)`
→ `device_class: energy`, `state_class: total_increasing`. (NIE 3 osobne kwartały.)

---

## 6. Moc / EMS (holding)

| Addr | Nazwa | R/W | Typ | Sc/Unit | Uwagi |
|--:|--|--|--|--|--|
| 5168 | Heat output (Leist_Heiz) | R | int16† | ·0.01 kW (W/10) | M3.5+ |
| 5170 | Electrical power (Leist_Elekt) | R | int16† | ·0.01 kW (W/10) | M3.5+, preferowane nad estymacją |
| 5182 | PV surplus (PV_Ueberschuss) | R/W | int16† | ·0.01 kW (W/10) | obecnie tylko rejestracja |
| 112 | BMS outdoor temp (extern) | R/W | int16 | 0.1 °C | wstrzyk. temp. zewn. (stub HACS) |
| 5130 | External lock (Sperre Extern) | R/W | uint16 | 0–11 | 0:HW 10:nieaktywna 11:aktywna |
| 5063 | Heartbeat In | W | uint16 | 0–65535 | watchdog |
| 5064 | Heartbeat Out | R | uint16 | 0–65535 | watchdog |

---

## 7. Nastawy 1. obieg (holding R/W)

| Addr | Nazwa | Zakres | Unit | Uwagi |
|--:|--|--|--|--|
| 5036 | Parallelverschiebung (curve offset) | 0–38 | enum | dekod: `K = value − 19` (19→0) |
| 46 | Room temperature setpoint | 15.0–30.0 | °C | |
| 5037 | Fixed flow setpoint | 18–60 | °C | |
| 5038 | Heating curve end | 20–70 | °C | |
| 47 | Hysteresis | 0.5–5.0 | K | |
| 5043 | Cooling room setpoint (15°C AT) | 10–35 | °C | (≤L22.9 dynamiczna) |
| 5134 | Cooling room setpoint (35°C AT) | 10–35 | °C | ab L22.9 |

## 8. Nastawy 2./3. obieg (holding R/W)

5082 wybór obiegu (2/3) · 5084 curve end (20–70°C) · 5085 fixed temp (20–60°C) ·
5086 curve offset (0–38, dekod `K = value − 19`) · 5087 mixer run time (1–6 min) ·
93 mixer hysteresis (0.5–2.0 K) · 5088 max temp (30–70°C) ·
5089 cooling room setpoint (0–30, dekod `°C = 15.0 + value·0.5`).

## 9. Nastawy CWU (holding R/W)
5045 hysteresis (2–15 K) · 5047 setpoint (min..85°C) · 5145 setpoint min (10..soll) ·
5048 setpoint max (soll..85°C).

## 10. Nastawy basen / 2. źródło (holding R/W)
Basen: 5049 hysteresis (1–20 K) · 5051 setpoint (5–60°C).
2. źródło: 48 mixer hysteresis (0.5–2.0 K) · 5020 parallel limit temp
(**int16**, −25..35 °C — wartość ujemna ⇒ znakowany, mimo „uint16" w spec) ·
5021 mixer run time (30–85 min).

---

## 11. Smart Grid / SG Ready
- `5167` holding R/W (0–13): 0:Hardware 10:gelb 11:grün 12:rot 13:dunkelgrün.
- Coile wejść: `3` SmartGrid1, `4` SmartGrid2 (stan: rot=01, gelb=00, grün=10,
  dunkelgrün=11). `5` EVU-Sperre, `6` Sperre Extern (R).

## 12. Wyjścia (coile R, diagnostic) — `WPM J/L`
41 Verdichter1 · 42 Verdichter2 · 43 Primärpumpe(M11)/Ventilator(M2) ·
44 2.Wärmeerzeuger(E10) · 45 Heizungspumpe(M13) · 46 Warmwasserpumpe(M18) ·
47/48 Mischer M21 Auf/Zu · 49 Zusatzumwälzpumpe(M16) · 50 Flanschheizung(E9) ·
51 Heizungspumpe(M15) · 52/53 Mischer M22 Auf/Zu · 56 Schwimmbadpumpe(M19) ·
57 Sammelstörmeldung(H5) · 59 Heizungspumpe(M14) · 60 Kühlpumpe(M17) ·
61 Heizungspumpe(M20) · 66 Umschaltung Heizen/Kühlen(N9) ·
68 Primärpumpe Kühlen(M12) · 71 Solarpumpe(M23).
Coil R/W: `19` Freigabe Zirkulationspumpe.

---

## 13. Odłożone / eksperckie (osobny milestone)
- **Programy czasowe** (1./2./3. HK Absenk/Anheb, WW Sperre/Desinfektion/
  Zirkulation, Schwimmbad Sperre/Vorrang): multipleks `5065` (selektor) +
  `5066–5081`. Stanowe, ryzykowne — premium „automatyzacja taryf".
- **Zeitabgleich** (czas): 5006–5011 + coile 102–107 (set-flags W).
- **Raumtemperaturregelung BMS**: 5065 (adresy 50–79) + 11/13/5081/5164/coil 177.

---

## 14. Enum: wartości statusów (L/M = cel; J/H alternatywnie)

**Status (103 L/M):** 0 Off · 2 Heating · 3 Pool · 4 DHW · 5 Cooling ·
10 Defrost · 11 Flow monitoring · 24 Mode-switch delay · 30 Lock(→104).
**Blokada (104 L/M):** 2 Volumenstrom · 5 Funktionskontrolle · 6 Einsatzgrenze HT ·
7 Systemkontrolle · 8 Verzög. Kühlen · 9 Pumpenvorlauf · 10 Mindeststandzeit ·
11 Netzbelastung · 12 Schaltspielsperre · 13 WW Nacherwärmung · 14 Regenerativ ·
15 EVU-Sperre · 16 Sanftanlasser · 17 Durchfluss · 18 Einsatzgrenze WP ·
19 Hochdruck · 20 Niederdruck · 21 Einsatzgrenze Wärmequelle · 23 System Grenze ·
24 Last Primärkreis · 25 Sperre Extern · 29 Inverter · 31 Aufwärmen ·
33 EvD Init · 34 2.WE freigegeben · 35 Störung(→105).
**Błąd (105 L/M):** 0 brak · 1–4 N17.1–4 · 6 EEV · 10 WPIO · 12 Inverter ·
13 WQIF · 15 Sensorfehler(→106) · 16 Niederdruck Sole · 19 !Primärkreis ·
20 !Abtauen · 21 !Niederdruck Sole · 22 !Warmwasser · 23 !Last Verdichter ·
24 !Codierung · 25 !Niederdruck · 26 !Frostschutz · 28 !Hochdruck ·
29 !Temp.Differenz · 30 !Heißgas · 31 !Durchfluss · 32 !Aufwärmen.
**Sensor error (106 L/M):** 1 R1 outdoor · 2 R2 return · 3 R3 DHW · 4 R7 coding ·
5 R9 flow · 6 R5 HC2 · 7 R13 HC3 · 8 R13 regen · 9/10 room 1/2 · 11 R6 source out ·
12 R24 source in · 14 R23 collector · 15 R25 LP · 16 R26 HP · 17/18 room hum 1/2 ·
19 frost-cold · 20 hot gas · 21 R2.1 return · 22 R20 pool · 23 R11 pas.cool flow ·
24 R4 pas.cool return · 26 R22 solar tank · 28 R2.2 heat demand · 29 RTM Econ ·
30 R39 cool demand.

> Pełne kolumny J/H oraz blokady H/J — w [`dimplex_modbus_spec_raw.md`](dimplex_modbus_spec_raw.md)
> (sekcje Statusmeldungen/Sperrmeldungen/Störmeldungen). Do komponentu wnosimy
> jako mapy wersjonowane (jak w repo HACS), z **adresami** też wersjonowanymi.
