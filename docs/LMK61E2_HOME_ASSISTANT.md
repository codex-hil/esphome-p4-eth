# LMK61E2 sterowany z Home Assistant

Projekt: `device-lmk61e2.yaml`, Waveshare ESP32-P4-ETH z Ethernetem. Korzysta z bazowego `device.yaml`, pakietów `common/` i prywatnego `secrets.yaml`. Sterowanie idzie przez szyfrowane natywne API ESPHome; MQTT discovery nie jest wymagane.

## Podłączenie i uruchomienie

GPIO7/SDA → EVM J4 pin 1, GPIO8/SCL → J4 pin 2, GND → J4 pin 5. Obie płytki zasilane przez własne USB, bez łączenia szyn zasilania. LMK pod adresem 0x59, I²C 100 kHz. Nie sterować równolegle magistralą z USB2ANY/MSP430.

```bash
./scripts/esphome compile device-lmk61e2.yaml
./scripts/esphome upload device-lmk61e2.yaml --device 192.168.2.14
```

Dla nowej instalacji utwórz własny `secrets.yaml` zgodnie z głównym README. Firmware zawiera sekrety; nie publikuj plików binarnych. Obecna płytka ma skonfigurowane prywatne klucze.

## Home Assistant

1. Otwórz **Ustawienia → Urządzenia i usługi → Dodaj integrację → ESPHome**.
2. Podaj host **192.168.2.14**, port **6053**. Jeżeli urządzenie jest już dodane, encje pojawią się automatycznie.
3. Wklej wartość lokalnego `api_encryption_key` z `secrets.yaml`, gdy integracja poprosi o klucz szyfrowania.
4. W urządzeniu **P4 Ethernet Controller** znajdziesz encję **Clock frequency**. Wpisuj MHz, np. `125` albo `122.88`.

Encje: nastawa częstotliwości, nominalna częstotliwość wyliczona przez planer, format LVPECL/LVDS/HCSL, włącznik wyjścia i status PLL. Przyciski presetów: 10, 20, 25, 50, 80, 100, 122.88, 125, 156.25 i 200 MHz. Przyciski uruchamiają akcję z dokładną stałą double; encja number używa float.

Opcjonalna karta dashboardu: `home-assistant/lmk61e2-card.yaml`. Dodaj ręczną kartę i wklej YAML. Zastąp przykładowe identyfikatory encji rzeczywistymi ID widocznymi w ustawieniach encji; istniejąca integracja może zachować wcześniejsze nazwy.

Przykład automatyzacji, po podstawieniu własnego ID:

```yaml
actions:
  - action: number.set_value
    target:
      entity_id: number.p4_ethernet_controller_clock_frequency
    data:
      value: 125
```

## Zachowanie

Po restarcie: 100 MHz, LVPECL, wyjście włączone. Nastawa z HA nie jest zapisywana do EEPROM ani odtwarzana z pamięci ESP32. Zakres LVPECL 10–1000 MHz, LVDS do 900 MHz, HCSL do 400 MHz. Nastawy poza zakresem bieżącego formatu są odrzucane. Zmiana częstotliwości chwilowo wycisza wyjście i kalibruje PLL.

Profil fractional jest włączony świadomie (`allow_fractional: true`); funkcjonalnie sprawdzono 122.88 MHz, bez kwalifikacji jitteru. Sensor nominalnej częstotliwości nie jest pomiarem oscyloskopowym. Zmieniając format, zapewnij odpowiednią terminację odbiornika; aktualny tor EVM/CH4 przetestowano w LVPECL. Układ nie oferuje regulacji mocy dBm.

Nie zmieniać EEPROM LMK ani firmware MSP430. Test bezpośredniego I²C z P4 potwierdził wszystkie dziesięć presetów i sterowanie wyjściem.

## Walidacja projektu HA

Firmware `lmk61e2-ha-002` skompilowano i wgrano OTA. Szyfrowane API potwierdziło tożsamość P4 i build. Nastawa number 125 MHz oraz preset 122.88 MHz przeszły pomiar CH4; wyłączenie wyjścia również przeszło. Przywrócono 100 MHz. [Raport](../reports/lmk61e2-ha-2026-10-01.json). Nie testowano podłączenia do konkretnej instancji Home Assistant; encje i polecenia sprawdzono przez ten sam protokół natywnego API.
