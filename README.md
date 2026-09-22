# Metroflip
Metroflip is a multi-protocol metro card reader app for the Flipper Zero, inspired by the Metrodroid project. It enables the parsing and analysis of metro cards from transit systems around the world, providing a proof-of-concept for exploring transit card data in a portable format. 

# Author
[@luu176](https://github.com/luu176)

# Discord Community Server 

Please join the server https://discord.gg/NR5hhbAXqS if you have any questions for me.
---

![Menu-Top-Screenshot](screenshots/Menu-Top.png)

# Setup Instructions

## Using a pre-built release: Stable (Recommended) or Beta (Newer updates, less stable)
1. Download the appropriate `metroflip.fap` file from the [Releases section](https://github.com/luu176/Metroflip/releases).
2. Drag and drop the `metroflip.fap` file into the `apps` folder on your Flipper Zero's SD card.

## Manual Build Instructions
To build Metroflip manually, follow these steps:

1. **Install Git**  
   Download and install Git on your Windows computer.  
   Run the first command to download the app:  

**Either**:
Stable Release (recommended): 
```git clone https://github.com/luu176/Metroflip.git```

**OR**:
Beta (newer updates but not fully tested): 
```git clone --single-branch --branch dev https://github.com/luu176/Metroflip.git```

2. **Navigate to the Project Folder**  
Run the second command to enter the app folder:  

```cd Metroflip```

3. **Install Python**  
Download and install Python from the [official website](https://www.python.org).  

4. **Install UFBT**  
Run the third command to install UFBT:  

```pip install ufbt```

5. **Update and Build the Project**  
Run the following commands in order to build the app:  

```ufbt update```
```ufbt fap_metroflip```

6. **Connect Your Flipper Zero**  
Ensure your Flipper Zero is connected via USB and close the qFlipper application (if it’s open).  

7. **Launch the Build**  
Run the final command to launch the app on your flipper:  

```ufbt launch```

---

# Metroflip - Card Support TODO List

This is a list of metro cards and transit systems that need support or have partial support.

## ✅ Supported Cards

| **Card / Agency**  | **City / Country**                           | **Card Type**     |
|--------------------|----------------------------------------------|-------------------|
| **Bip!**           | 🇨🇱 Santiago de Chile, Chile                  | MIFARE Classic    |
| **Charliecard**    | 🇺🇸 Boston, MA, USA                           | MIFARE Classic    |
| **Clipper**        | 🇺🇸 San Francisco, CA, USA                    | MIFARE DESFire    |
| **Go Card**        | 🇦🇺 Gold Coast, QLD, Australia                | MIFARE Classic    |
| **Intertic**       | 🇫🇷 France, About 21 Cities / Companies       | ST25TB            |
| **ITSO**           | 🇬🇧 United Kingdom                            | MIFARE DESFire    |
| **Metromoney**     | 🇬🇪 Tbilisi, Georgia                          | MIFARE Classic    |
| **myki**           | 🇦🇺 Melbourne (and surrounds), VIC, Australia | MIFARE DESFire    |
| **Navigo**         | 🇫🇷 Paris, France                             | Calypso           |
| **nol**            | 🇦🇪 Dubai, UAE                                | MIFARE DESFire    |
| **Octopus**        | 🇭🇰 Hong Kong                                 | FeliCa            |
| **Opal**           | 🇦🇺 Sydney (and surrounds), NSW, Australia    | MIFARE DESFire    |
| **Opus**           | 🇨🇦 Montreal, QC, Canada                      | Calypso           |
| **Rav-Kav**        | 🇮🇱 Israel                                    | Calypso           |
| **RENFE**          | 🇪🇸 Spain                                     | MIFARE Classic    |
| **SmartRider**     | 🇦🇺 Perth, WA, Australia                      | MIFARE Classic    |
| **Suica**          | 🇯🇵 Japan                                     | FeliCa            |
| **T-Mobilitat**    | 🇪🇸 Barcelona, Spain                          | ISO 14443-4A      |
| **Troika**         | 🇷🇺 Moscow, Russia                            | MIFARE Classic    |
| **Trt**            | 🇨🇳 Tianjin, China                            | MIFARE Ultralight |



---

# Notes on this fork

## Phone-emulated cards (Apple Wallet, Google Wallet)

A Navigo held in Apple Wallet (iPhone, Apple Watch) or Google Wallet is read like
a plastic one: hold the phone or the watch against the Flipper and the card view
comes up, the phone showing its own "success" screen as with a real gate.

Two things differ from a plastic card and are handled by the app:

- The emulated card answers on ISO 14443-4A with an empty ATS, where plastic
  Calypso cards are ISO 14443-4B. The Calypso reader picks its transport at
  runtime, and a type A card with no historical bytes is routed to the Calypso
  parser instead of being reported as an unknown card.
- Only ISO 7816 addressing is available, so the application is selected by AID.
  Three candidates are tried in order: the Calypso RID, the full Navigo AID, and
  the `1TIC.ICA` DF name. A type A card with none of them is a card without a
  Calypso application, and the read stops with an error.

Express mode must be on for the card to answer while the phone is locked, which
is the default for Navigo.

## RAM budget

The Flipper has little free heap, and both the app binary and the loaded parser
plugin are resident while a card is read. When RAM runs out the read fails with
"Not Enough Memory", most often with the USB CLI connected at the same time.

Two things keep the footprint down, and are worth preserving when adding a card:

- Per-card artwork belongs to its plugin, not to the app. The 142 Suica icons
  live in `images_suica/` and are compiled into the Suica plugin through its own
  `fap_icon_assets`, so they are only resident while that plugin runs. The app
  binary went from 89 KB to 61.5 KB this way.
- Plugin sources are not compiled into the app binary.

When debugging on device, prefer `log info` to `log debug` on the CLI: at debug
level the Calypso parser prints one line per APDU over USB, which slows the
poller enough to lose the card.

## Navigo network mapping

Station names come from the CSV files shipped in `files/navigo/stations/`, keyed
by the sector and station ids found in the event records.

Line names are a different story. The Ile-de-France Intercode route numbers are
not published and are not an encoding of the commercial line name: RER A is
recorded as 17 at Auber and as 26 at Neuilly-Plaisance, tram T3a as both 1 and
13. `NAVIGO_LINE_NAMES` in `api/calypso/transit/navigo.c` therefore holds
confirmed observations only. An unknown tram or train code is displayed raw, for
example `Train (line 21)`, rather than guessed; metro and bus codes do match the
commercial numbering, with the metro "bis" lines offset by 100.

Contributions to that table are welcome. Save a scan made right after a trip on
a line you can identify with certainty, ideally validated at a station served by
a single line, then run:

```
python3 tools/navigo_decode.py <save.nfc>
```

It prints the raw Intercode fields of each event next to the line the app would
display, so the transport type and route number to add to the table can be read
off directly.

---

# Credits
- **App Author:** [@luu176](https://github.com/luu176)
- **Info Slaves:** [@equipter](https://github.com/equipter), [@TheDingo8MyBaby](https://github.com/thedingo8mybaby), [@ry4000](https://github.com/ry4000), [@WillyJL](https://github.com/WillyJL), 
- **Bip! Parser:** [@rbasoalto](https://github.com/rbasoalto), [@gornekich](https://github.com/gornekich)
- **Charliecard Parser:** [@zacharyweiss](https://github.com/zacharyweiss)
- **Clipper Parser:** [@ke6jjj](https://github.com/ke6jjj)
- **Go Card Parser:** [@luu176](https://github.com/luu176)
- **Intertic Parser (21 Cities):** [@luu176](https://github.com/luu176), [@gentilkiwi](https://github.com/gentilkiwi)
- **ITSO Parser:** [@gsp8181](https://github.com/gsp8181), [@hedger](https://github.com/hedger), [@gornekich](https://github.com/gornekich)
- **Metromoney Parser:** [@Leptopt1los](https://github.com/Leptopt1los)
- **myki Parser:** [@gornekich](https://github.com/gornekich)
- **Navigo Parser:** [@luu176](https://github.com/luu176), [@DocSystem](https://github.com/docsystem)
- **nol Parser:** [@zinongli](https://github.com/zinongli)
- **Octopus Parser:** [@zinongli](https://github.com/zinongli)
- **Opal Parser:** [@gornekich](https://github.com/gornekich)
- **Opus Parser:** [@DocSystem](https://github.com/docsystem)
- **Rav-Kav Parser:** [@luu176](https://github.com/luu176)
- **RENFE Parser:** [@BocamoCM](https://github.com/BocamoCM)
- **SmartRider Parser:** [@luu176](https://github.com/luu176)
- **Suica Parser:** [@zinongli](https://github.com/zinongli)
- **T-Mobilitat Parser:** [@luu176](https://github.com/luu176)
- **T-Money Parser:** [@justus-perlwitz](https://github.com/justus-perlwitz)
- **Troika Parser:** [@gornekich](https://github.com/gornekich)
- **TRT Parser:** [@luu176](https://github.com/luu176), [@zinongli](https://github.com/zinongli)
- **v1.1 Memory Safety:** [@FatherDivine](https://github.com/FatherDivine)

---

### Special Thanks
Huge thanks to [@equipter](https://github.com/equipter) & [@ry4000](https://github.com/ry4000) for helping out the Discord community!
