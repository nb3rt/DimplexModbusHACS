# Dimplex WPM — Home Assistant (HACS) — Projekt integracji

> Status: **DRAFT do wspólnej iteracji**. Dokument roboczy redesignu repo
> `nb3rt/DimplexModbusHACS` (domena `dimplex_wpm`). Scala trzy źródła:
> lokalne YAML (`existing integration/`), `nb3rt/DimplexModbusHA` (mapa
> rejestrów), `nb3rt/DimplexModbusHACS` (szkielet komponentu).

---

## 1. Cel i zakres

Pełnoprawna integracja custom (HACS, docelowo zgłoszenie do HA core) dla pomp
ciepła Dimplex sterowanych kontrolerem **WPM/NWPM przez Modbus TCP**:

- natywne encje (sensor / binary_sensor / number / select / climate),
- **natywny silnik estymacji** energii i ciepła (moc el. z Hz, COP, ciepło,
  rozdział dom/instalacja, przepływ) — główny wyróżnik,
- natywne kWh gotowe pod Energy Dashboard,
- zapisy/sterowanie za bramką trybu zaawansowanego,
- gotowe dashboardy (i opcjonalnie karta Lovelace),
- testy, CI, brands, dokumentacja, quality scale.

### Decyzje zatwierdzone (z rozmowy)
- Estymacja: **natywnie, pełny zakres**.
- Energia: **oba** (natywne kWh + udokumentowane helpery HA).
- Sterowanie: **SG Ready + nastawy (number) + climate**, wszystko za bramką
  trybu zaawansowanego (read-only domyślnie).
- Modele: **LAK9 first**, architektura pod profile innych pomp;
  **mapa rejestrów WPM identyczna dla wszystkich modeli**.

---

## 2. Pozycjonowanie i licencja (wątek strategiczny — do decyzji osobno)

- Istnieje `ay-kay/homeassistant-dimplex` — **chmura (Home Cloud API), domena
  `dimplex`**. My robimy **lokalne Modbus, domena `dimplex_wpm`** → brak kolizji,
  podejścia komplementarne.
- W `home-assistant/brands` brak `dimplex`/`dimplex_wpm` → do HACS-default i do
  core trzeba osobno wysłać brand assets (PR do `home-assistant/brands`).

### Licencjonowanie / open-core / add-on
Cel użytkownika: rozważyć licencjonowanie *części* rozwiązania. Kluczowe
ograniczenia, które determinują architekturę:

1. **HACS-default oraz HA core wymagają kodu OSS.** Płatna/zamknięta warstwa
   **nie może** żyć wewnątrz integracji zgłoszonej do HACS-default/core. Musi być
   *osobną dystrybucją*.
2. **Pułapka GPLv3:** repo `nb3rt/DimplexModbusHA` jest na GPLv3 i ma **drugiego
   kontrybutora** (dar3khudy — czujniki gazu/wilgotności). Reużycie tego kodu
   wymusza GPLv3 na pochodnych i **nie da się go relicencjonować** bez zgody
   wszystkich autorów. Lokalne YAML to Twój kod (możesz licencjonować dowolnie).
   → Aby zachować swobodę licencyjną dla warstwy premium: **clean-room mapa
   rejestrów z oficjalnej dokumentacji Dimplex** (fakty/adresy rejestrów nie są
   chronione; chroniony jest konkretny kod), bez kopiowania kodu z GPLv3 repo.

### Rekomendowany model: **open-core**
- **Core (OSS, np. Apache-2.0/MIT):** I/O Modbus, encje surowe (temperatury,
  status/lock/fault, runtime'y, energia z rejestrów, coile), SG Ready, profile.
  → to idzie do HACS i ewentualnie do core.
- **Premium „Analytics" (osobna dystrybucja, licencja wg uznania):** silnik
  estymacji COP/ciepło/przepływ + zaawansowana energia + dashboardy pro.
  Opcje techniczne: (a) osobny custom component z kluczem licencyjnym,
  (b) HA add-on (kontener Docker — tylko HAOS/Supervised), (c) usługa cloud.

> **Implikacja dla architektury (robimy ją tak od początku):** silnik estymacji
> jest **czysto odseparowanym modułem** (`estimation.py` + profile), zależnym
> tylko od danych coordinatora, bez sprzężeń z I/O. Dzięki temu wariant premium
> pozostaje możliwy bez przepisywania. **Sama decyzja licencyjna nie blokuje
> startu** — domyślnie budujemy całość jako OSS i ewentualnie wydzielamy później.

---

## 3. Architektura wysokopoziomowa

```
config_flow / options_flow
        │  (host, port, unit, scan, timeout, firmware H/J/L/M,
        │   profil urządzenia, flagi modułów, tryb zaawansowany/zapis)
        ▼
DataUpdateCoordinator ── modbus_client (AsyncModbusTcpClient, batch, reconnect)
        │  raw{addr:val}
        ├── decode.py     → temperatury/skale/znaki, mapy tekstowe (wersjonowane)
        ├── estimation.py → moc el., COP, ciepło, α, przepływ  (PROFIL)
        ├── energy.py     → Riemann (RestoreSensor, persist) → kWh
        ▼
   coordinator.data = { raw, decoded, derived, energy, meta }
        ▼
platformy: sensor / binary_sensor / number / select / climate
        ▼
device registry: 1 hub + pod-urządzenia (HC1, HC2/3, DHW, Pool, Vent, Solar,
                 Source, Smart Grid, Analytics)
```

Zasady:
- **Jeden coordinator** odpytuje wszystko w paczkach (batch ranges), jeden
  interwał bazowy (interwały „wolne" realizujemy decymacją — nie co cykl).
- **EntityDescription-driven**: encje deklaratywnie z dataclass (rozszerzony o
  `register`, `register_type`, `scale`, `signed`, `value_fn`, `module`,
  `entity_category`, `feature_flag`).
- **Profil urządzenia** dostarcza kalibrację + listę aktywnych modułów; mapa
  rejestrów wspólna.

---

## 4. Model profili urządzeń

```python
@dataclass(frozen=True)
class DeviceProfile:
    key: str                 # "lak9"
    name: str                # "Dimplex LAK 9S-TU"
    power_lut: tuple[tuple[float, float], ...]   # (Hz, W) — interpolacja
    cop_table: dict[int, dict[int, float]]       # {A:{W:COP}} EN14511
    heater_default_w: int                        # moc grzałki 2. źródła
    k_dhw: float; k_defrost: float; k_defrost_loss: float
    modules: frozenset[str]  # {"hc1","hc2_3","dhw","pool","solar","vent","sg"}
```

- `profiles/lak9.py` — pełna kalibracja z lokalnego YAML (LUT 16 pkt, COP 4×3).
- `profiles/generic_wpm.py` — bez kalibracji estymacji (tylko odczyty), wszystkie
  moduły opcjonalne.
- Wybór profilu w config_flow; **user-submitted** = PR z nowym plikiem profilu.
- Wartości `k_*`/`heater_w` z profilu = defaulty encji `number` (kalibrowalne).

### 4.1 Capabilities (per instalacja, nie per model!)

Profil = kalibracja modelu. **Capabilities = co ma KONKRETNA instalacja** —
osobna konfiguracja (config entry), bo dwie te same pompy mogą mieć różny sprzęt
pomiarowy. To kluczowe: **nie każda instalacja ma licznik prądu ani ciepłomierz**,
stąd estymacja jest pełnoprawnym źródłem, nie tylko awaryjnym.

```python
@dataclass
class Capabilities:
    has_electric_meter: bool   # rejestr 5170 wiarygodny (M3.5+ + sprzęt)
    has_heat_meter: bool       # rejestry 5168 / 5096–5129 (Wärmemengenzähler)
    has_flow_sensor: bool      # zewn. encja przepływu (np. sensor.aquaro_*)
    has_inverter_freq: bool    # rejestr 114 (RE) dostępny → warunek LUT prądu
    flow_sensor_entity: str|None
```

Ustalane: **deklaracja użytkownika** w config/options (pewne) + **auto-hint**
z próbnego odczytu przy setupie (5170/5168/114). Patrz macierz źródeł §6.

---

## 5. Katalog encji (logika encji)

Kategorie: **Primary** (domyślnie widoczne), **Diagnostic**
(`EntityCategory.DIAGNOSTIC`), **Config** (`EntityCategory.CONFIG`).
Pod-urządzenia w nawiasach. Encje modułowe tworzone tylko gdy profil/flaga włącza.

### 5.0 Konwencje i drzewo urządzeń (ZATWIERDZONE)

- **Drzewo: średnie.** Urządzenie główne **Controller** (`(DOMAIN, entry_id)`,
  manufacturer Dimplex, model z profilu, sw_version z rej. 65–67) + pod-urządzenia
  przez `via_device`, **tworzone tylko gdy capability/profil je aktywuje**:
  `HC1`, `HC2/3`, `DHW`, `Pool`, `Ventilation`, `Solar`, `Source`,
  oraz **Analytics** (wielkości pochodne: moc/COP/ciepło/przepływ/energia).
- **`has_entity_name = True`** — nazwy zależne od urządzenia (np. „Heating
  circuit 1 · Flow temperature"). `unique_id = {entry_id}_{module}_{key}`.
- **Capabilities (§4.1) bramkują** tworzenie encji measured (np. encje z rej.
  5170/5168/5096–5129 tylko gdy `has_*_meter`); brak sprzętu → encje estimated.
- **Encje energii/mocy/przepływu/COP** mają atrybut `source: measured|estimated`.
- **Kalibracja = encje `number` (kategoria Config), zawsze dostępne** (zapis do
  options HA, nie do pompy → NIE za bramką sterowania). **Zapis nastaw do pompy**
  (number/select/climate na rejestrach R/W) — **tylko za bramką** `enable_control`.

### 5.1 sensor (odczyt)
**Controller**
- outdoor_temperature (1), inverter_frequency (114), operating_mode (5015→tekst),
  party_mode_hours (5016), holiday_days (5017)
- status_code (103) [diag] + **status_text** (mapa wersjonowana)
- lock_code (104) [diag] + **lock_text**
- fault_code (105) [diag] + **fault_text**
- sensor_error_code (106) [diag] + **sensor_error_text**
- controller_info [diag] (host/port/unit/firmware/profil w atrybutach)
- runtime_* (71–79) [diag, total_increasing, h]

**HC1**: flow_temperature (5), return_temperature (2), return_setpoint (53),
room_temp_1/2 (11/12), room_humidity_1/2 (13/14)
**HC2/3**: hc2_return (9)†, hc3_return (10)†, hc2_setpoint (54), hc3_setpoint (55)
**DHW**: dhw_temperature (3), dhw_setpoint (58)
**Pool**: pool_setpoint (5051) …
**Source**: source_inlet (6), source_outlet (7), [gaz/skraplacz/parownik — †]
**Ventilation**: outdoor/supply/extract/exhaust air temp (120–123), fan speeds
(125/126), boost time (127), level (5034)
**Solar**: collector_temp (†22?), tank_temp (23)
**Smart Grid / EMS**: sg_ready_code (5167) [diag] + **sg_ready_text**,
sg_ready_state_inputs (z coili), pv_surplus (5182), heating_power (5168, kW),
electrical_power (5170, kW), energia z rejestrów 5096–5129 (kWardy kwartalne)

**Analytics (silnik estymacji)** — patrz §6:
- compressor_power_est (W/kW), heater_power_est, pump_power_est, total_power_est
- cop_en14511
- thermal_power_compressor, thermal_power_heater, thermal_power_defrost_loss,
  thermal_power_loop, thermal_power_to_house, thermal_power_to_installation
- estimated_flow (m³/h) [+ wygładzony — poprawione EMA]
- deltaT, ddeltaT_dt
- **energy_*_kwh** (compressor/heater/total electric; to_house/installation/
  defrost thermal) — total_increasing, RestoreSensor

### 5.2 binary_sensor
- fault_active, lock_active (device_class problem)
- SmartGrid input 1/2 (coil 3/4), utility_lockout (5), external_lockout (6)
- wyjścia (coile 41–71): compressor 1/2, primary pump, 2nd heat gen, pompy
  M13/M14/M15/M20, mieszacze, DHW pump, pool pump, solar pump, general fault…
  [diag]

### 5.3 number
**(a) Kalibracja estymacji — zawsze dostępne** (kategoria Config, persist w
options, zapis do HA): k_dhw, k_defrost, k_defrost_loss, heater_2nd_power_w,
pump_main/floor_power_w, alpha_base, alpha_sensitivity, alpha_deadband.
**(b) Nastawy pompy — tylko za bramką `enable_control`** (zapis do rejestrów R/W
potwierdzonych w §7–§10): dhw_setpoint (5047), hc1 curve_offset (5036)/fixed_flow
(5037)/curve_end (5038)/hysteresis (47), pool_setpoint (5051), … z walidacją
min/max i dekoderem enum (5036/5086/5089).

### 5.4 select (tylko gdy tryb zaawansowany)
- sg_ready_mode (5167) — Hardware/Yellow/Green/Red/Deep Green (jest)
- operating_mode (5015) — jeśli potwierdzony R/W

### 5.5 climate (tylko gdy tryb zaawansowany; etap późniejszy)
- HC1 (current=return/flow, target=setpoint/offset), DHW (current=dhw_temp,
  target=dhw_setpoint). Wymaga twardej walidacji zakresów z dokumentacji.

> † = adresy/typy do potwierdzenia autorytatywną mapą rejestrów (konflikty
> między źródłami — patrz §11). M.in.: solar collector w lokalnym YAML miał
> błędnie `address: 10` (duplikat HC3); typy 8/9/10/98/107/108/109 (input vs
> holding) różnią się między lokalnym a starym repo.

---

## 6. Pomiar i estymacja — macierz wyboru źródła

Każda wielkość energetyczna ma **rozwiązanie źródła** zależne od capabilities
(§4.1): jeśli jest sprzęt pomiarowy — czytamy rejestr; jeśli nie — estymujemy.
Encja niesie atrybut `source: measured|estimated` i `availability` zależną od
capability. Estymacja to nasz wyróżnik dla instalacji bez liczników.

| Wielkość | Źródło „measured" | Źródło „estimated" (fallback) |
|---|---|---|
| Moc elektryczna | rejestr **5170** (licznik) | LUT(Hz, status) — wymaga rej. 114 |
| Energia elektryczna | całka 5170 | całka mocy estymowanej |
| Moc cieplna (oddana) | rejestr **5168** (ciepłomierz) | **hydraulicznie** Q=V̇·cp·ΔT (gdy jest czujnik przepływu) **lub** P_el·COP |
| Energia cieplna | rejestry **5096–5129** (ciepłomierz) | całka mocy cieplnej estymowanej |
| Przepływ V̇ | zewn. **czujnik przepływu** | bilans Q/(cp·ΔT) z toru COP |
| COP (sprawność) | Q_measured / P_el | tabela EN14511(A,W) |

Zależności (ważne dla logiki encji):
- tor **hydrauliczny** ciepła wymaga realnego przepływu + ΔT (rej. 5/2) — gdy jest
  czujnik, jest dokładniejszy niż COP i wtedy COP raportujemy jako `Q/P_el`;
- tor **COP** ciepła wymaga mocy el. (5170 lub LUT) × COP(tabela) — działa bez
  żadnego dodatkowego sprzętu; z niego back-derive’ujemy przepływ estymowany;
- estymacja mocy el. wymaga rej. 114 (RE); gdy go brak i brak licznika — degradacja
  (np. on/off sprężarki × moc nominalna z profilu, oznaczone niską ufnością).

### 6.1 Silnik estymacji (natywny) — port „sosu" z YAML

Moduł `estimation.py` — czyste funkcje, wejście = zdekodowane dane + profil +
parametry; wyjście = wartości pochodne. Liczone w coordinatorze co cykl.

1. **Moc el. sprężarki**: interpolacja LUT(Hz→W) z profilu; status-aware
   (0 dla idle/off/lock/flow-monitoring); ×k_defrost (status 10), ×k_dhw (status 4).
2. **Moc grzałki**: heater_w gdy coil 2nd-heat-gen on, inaczej 0.
3. **Total** = sprężarka + grzałka (+ pompy opcjonalnie).
4. **COP EN14511**: interpolacja **2D biliniowa** z tabeli profilu, z clampem
   A∈[−7,10], W∈[35,55]. **Poprawka buga nawiasowania `round()`** z YAML.
5. **Ciepło**: Q_comp = P_el·COP (status CO/CWU); Q_heater = moc grzałki 1:1;
   strata defrostu = P_el·k_loss (status 10); Q_loop = comp+heater−defrost.
6. **α dom/instalacja**: heurystyka `α = base − sens·dΔT/dt` z deadbandem;
   ΔT i dΔT/dt liczone w coordinatorze (przechowujemy poprzedni ΔT + timestamp,
   okno ~5 min). Split: to_house = Q_loop·α, to_installation = reszta.
7. **Przepływ**: V̇ = Q_comp/(4180·ΔT)·3.6, tylko CO/CWU, ΔT>0.5 K,
   clamp 0–3.8 m³/h. **EMA naprawione** (realne wygładzanie, nie kopia 1:1).

Parametry kalibracji = encje `number` (Config). Mechanizm: wartości w
`entry.options`; zmiana number → zapis options → lekki recompute (bez pełnego
reloadu). Tabele LUT/COP z profilu (edycja przez profil/YAML; UI dla tabel —
later).

---

## 7. Model bezpieczeństwa zapisu

- **Domyślnie read-only.** Żadnych number/select/climate.
- Opcja **`enable_control`** (advanced) w options_flow → tworzy encje zapisu.
  Opcjonalnie podflagi: `enable_setpoints`, `enable_sg_ready`, `enable_climate`.
- Ostrzeżenia w `strings.json` + dokumentacja (ryzyko zapisu do sterownika).
- Zapis tylko do rejestrów potwierdzonych jako R/W w dokumentacji; walidacja
  zakresów min/max z profilu/dokumentacji przed `write_register`.
- (Nasza własna opcja, nie systemowy „advanced mode" usera HA — żeby działała
  niezależnie od konta.)

---

## 8. Energia i Energy Dashboard (oba)

- **Natywne** sensory mocy (device_class POWER) + **natywne kWh**
  (total_increasing, device_class ENERGY, `RestoreSensor` z persist last value +
  last timestamp, całkowanie trapezowe w `energy.py`) → działają wprost w Energy
  Dashboard (który sam robi rozbicie dzienne/mies.).
- **Udokumentowane** (opcjonalnie) helpery HA: `integration` + `utility_meter`
  dla użytkowników chcących własnych cykli/raportów (nie reimplementujemy
  kalendarzowych cykli w Pythonie).
- **Źródło per wielkość wg macierzy §6**: gdy jest ciepłomierz → energia cieplna
  z rejestrów **5096–5129** liczona jako **suma grup cyfr** (`reg(9-12)·1e8 +
  reg(5-8)·1e4 + reg(1-4)`, NIE kwartały) per kategoria (Heizen/WW/Schwimmbad/
  Umwelt); gdy brak → całka mocy cieplnej estymowanej. Analogicznie prąd:
  5170 albo całka estymaty. Encje energii zawsze `total_increasing`/`energy`,
  niezależnie od źródła, więc Energy Dashboard działa tak samo.

---

## 9. Dashboardy i karta

- **Etap 1:** przeniesienie 4 dashboardów z `existing integration/` na nowe
  entity_id (z poprawą błędów), jako importowalne YAML w `dashboards/`:
  Overview/Status, Energy & Heat, History, Calibration/Parameters.
- **Etap 2 (opcjonalny):** dedykowana karta Lovelace (osobne repo HACS
  „frontend") — np. karta przeglądowa pompy. Integracja backendu nie rejestruje
  kart bezpośrednio.

---

## 10. Jakość: testy, CI, brands, quality scale

- **Testy** (pytest + pytest-homeassistant-custom-component): coordinator z
  mockiem modbus, dekodery, **estymacja** (LUT/COP/flow — łatwe do testów
  jednostkowych), config_flow.
- **CI** (`.github/workflows`): `hacs/action`, `hassfest`, `ruff`, `mypy`,
  pytest + coverage.
- **brands**: PR do `home-assistant/brands` (icon 256×256 + logo).
- **Quality scale**: cel **Silver** na start (config_flow, obsługa awarii,
  unavailable, dokumentacja), potem **Gold** (tłumaczenia, discovery jeśli
  realne, pokrycie testami).
- **Ścieżka do HA core:** realnie najpierw dojrzałość w HACS. Uwaga: core bywa
  ostrożny wobec heurystyk (COP/flow estimation) — dlatego separacja core
  (odczyty) / analytics (estymacja) pomaga też tutaj.

---

## 11. Otwarte kwestie / potrzebne wejścia od Ciebie

1. **Autorytatywna mapa rejestrów** (oficjalny spec Dimplex NWPM Modbus TCP albo
   odczyt z realnego LAK9) — do rozstrzygnięcia konfliktów:
   - solar collector (lokalnie błędny `address: 10`),
   - typy 8/9/10/98/107/108/109 (input vs holding) i ich znaczenie,
   - które rejestry nastaw są faktycznie **R/W** (do number/select/climate),
   - potwierdzenie skali/znaku dla mocy 5168/5170 i energii 5096–5129.
2. **Decyzja licencyjna** (open-core teraz vs wszystko OSS, premium później) —
   wpływa tylko na to, czy od razu trzymamy clean-room separację (proponuję: tak).
3. **Zgoda kontrybutora GPLv3** (jeśli chcesz reużyć kod ze starego repo) —
   albo idziemy clean-room.

---

## 12. Roadmapa (proponowane etapy)

- **M0 — Fundament**: clean-room mapa rejestrów (`registers.py`), profile
  (`lak9`, `generic_wpm`), rozbudowa coordinatora o batch wszystkich zakresów +
  `decode.py`. Encje sensor/binary_sensor (pełny odczyt), drzewo urządzeń.
- **M1 — Estymacja**: `estimation.py` (moc/COP/ciepło/α/flow) + `energy.py`
  (kWh) + encje Analytics + number kalibracyjne. Testy jednostkowe estymacji.
- **M2 — Sterowanie**: bramka `enable_control`, select/number nastaw, walidacja.
- **M3 — UX & jakość**: dashboardy YAML, tłumaczenia (en/pl/de), strings,
  CI (hacs/hassfest/ruff/mypy/pytest), brands, README/dokumentacja.
- **M4 — Premium/karta (opcjonalnie)**: wydzielenie analytics / karta Lovelace.
- **M5 — Zgłoszenia**: HACS-default, brands PR; przygotowanie pod core.
