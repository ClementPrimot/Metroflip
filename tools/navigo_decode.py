#!/usr/bin/env python3
"""Host-side replica of Metroflip's Navigo event decoding (calypso.c + navigo.c).

Reads a Metroflip .nfc save and prints, for each event record, the raw Intercode
fields and the line the app would display - so a parsing bug can be diagnosed
from a save file without re-scanning the card.

Usage: tools/navigo_decode.py <save.nfc>

Keep LINE_NAMES in sync with NAVIGO_LINE_NAMES in api/calypso/transit/navigo.c.
"""
import sys, time, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EPOCH = 852073200

EVENT_BITMAP = [
    ("EventDisplayData", 8),
    ("EventNetworkId", 24),
    ("EventCode", 8),
    ("EventResult", 8),
    ("EventServiceProvider", 8),
    ("EventNotokCounter", 8),
    ("EventSerialNumber", 24),
    ("EventDestination", 16),
    ("EventLocationId", 16),
    ("EventLocationGate", 8),
    ("EventDevice", 16),
    ("EventRouteNumber", 16),
    ("EventRouteVariant", 8),
    ("EventJourneyRun", 16),
    ("EventVehicleId", 16),
    ("EventVehicleClass", 8),
    ("EventLocationType", 5),
    ("EventEmployee", 240),
    ("EventLocationReference", 16),
    ("EventJourneyInterchanges", 8),
    ("EventPeriodJourneys", 16),
    ("EventTotalJourneys", 16),
    ("EventJourneyDistance", 16),
    ("EventPriceAmount", 16),
    ("EventPriceUnit", 16),
    ("EventContractPointer", 5),
    ("EventAuthenticator", 16),
    ("EventData", [("EventDataDateFirstStamp", 14), ("EventDataTimeFirstStamp", 11),
                   ("EventDataSimulation", 1), ("EventDataTrip", 2),
                   ("EventDataRouteDirection", 2)]),
]

TRANSPORT = {1: "Urban Bus", 2: "Interurban Bus", 3: "Metro", 4: "Tram",
             5: "Train", 8: "Parking"}
TRANSITION = {1: "Entry (First validation)", 2: "Exit", 3: "Validation",
              4: "Inspection", 5: "Test validation", 6: "Entry (Interchange)",
              7: "Exit (Interchange)", 9: "Validation cancelled",
              0xA: "Entry (Public road)", 0xB: "Exit (Public road)",
              0xD: "Distribution", 0xF: "Invalidation"}
PROVIDER = {2: "SNCF", 3: "RATP", 4: "IDF Mobilites", 10: "IDF Mobilites",
            115: "ORA", 116: "CSO (VEOLIA)", 156: "R'Bus (VEOLIA)",
            175: "Phebus", 30: "RATP (Veolia Transport Nanterre)"}
SECTORS = ["Intramuros", "RATP", "Est", "St Lazare", "Sud-Est + Austerlitz",
           "Nord", "Montparnasse", "Unknown"]
# (transport type, EventRouteNumber) -> commercial line name
LINE_NAMES = {
    (5, 17): "RER A", (5, 26): "RER A",
    (3, 103): "Metro 3 bis", (3, 107): "Metro 7 bis",
    (4, 1): "Tram T3a", (4, 9): "Tram T9", (4, 13): "Tram T3a",
    (4, 16): "Tram T6", (4, 18): "Tram T8",
}


def line_name(transport, route, available):
    if not available:
        return TRANSPORT.get(transport, "Unknown")
    if (transport, route) in LINE_NAMES:
        return LINE_NAMES[(transport, route)]
    if transport == 3:
        return f"Metro {route}"
    if transport in (1, 2):
        return f"{TRANSPORT[transport]} {route}"
    return f"{TRANSPORT.get(transport, 'Unknown')} (line {route})"


def bits_of(data):
    return "".join(f"{b:08b}" for b in data)


def dec(bits, start, end):
    return int(bits[start:end + 1], 2) if end >= start else 0


def bitmap_positions(slice_bits):
    """Port of get_bitmap_positions: index counted from the right, ascending."""
    n = len(slice_bits)
    return [i for i in range(n) if slice_bits[n - 1 - i] == "1"]


def parse_bitmap(bits, offset, elements):
    """Returns {key: (value, bit_offset, size)} for present fields."""
    size = len(elements)
    positions = bitmap_positions(bits[offset:offset + size])
    out = {}
    cur = offset + size
    for p in positions:
        key, spec = elements[p]
        if isinstance(spec, list):
            sub = parse_bitmap(bits, cur, spec)
            out.update(sub)
            consumed = len(spec) + sum(s for (_, _, s) in sub.values())
            cur += consumed
        else:
            out[key] = (dec(bits, cur, cur + spec - 1), cur, spec)
            cur += spec
    return out


def station_file(kind, group):
    return os.path.join(REPO, "files/navigo/stations", kind, f"stations_{group}.txt")


def lookup_station(group, sid, sub, transport):
    kind = {5: "train", 4: "tram", 3: "metro"}.get(transport)
    if kind:
        path = station_file(kind, group)
        if os.path.exists(path):
            for line in open(path, encoding="utf-8", errors="replace"):
                parts = line.rstrip("\r\n").split(",")
                if kind == "metro":
                    if len(parts) >= 2 and parts[0].strip().isdigit() and int(parts[0]) == sid:
                        return parts[1]
                else:
                    if len(parts) >= 3 and parts[0].strip().isdigit() and \
                       int(parts[0]) == sid and int(parts[1]) == sub:
                        return parts[2]
    if sub:
        return f"{group}-{sid}-{sub}"
    if sid:
        return f"{group}-{sid}"
    return f"{group}"


def read_records(path):
    recs = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        m = re.match(r"AID (\w+) FID (\w+): ([0-9A-F ]+)", line.strip())
        if m:
            aid, fid, hexs = m.groups()
            recs.setdefault(aid, {})[fid] = bytes(int(x, 16) for x in hexs.split())
    return recs


def describe(rec):
    bits = bits_of(rec)
    date_raw = dec(bits, 0, 13)
    time_raw = dec(bits, 14, 24)
    f = parse_bitmap(bits, 25, EVENT_BITMAP)

    ts = date_raw * 24 * 3600 + EPOCH + 3600
    d = time.gmtime(ts)
    when = f"{d.tm_mday:02d}/{d.tm_mon:02d}/{d.tm_year} {time_raw // 60:02d}:{time_raw % 60:02d}"

    code = f.get("EventCode", (0, 0, 0))[0]
    transport, transition = code >> 4, code & 0xF
    loc = f.get("EventLocationId")
    if loc:
        v = loc[0]
        group, sid, sub = v >> 9, (v >> 4) & 31, v & 15
    else:
        group = sid = sub = 0
    route = f.get("EventRouteNumber")
    provider = f.get("EventServiceProvider", (0, 0, 0))[0]

    # line label exactly as show_navigo_event_info would print it
    label = line_name(transport, route[0] if route else 0, route is not None)

    station = lookup_station(group, sid, sub, transport)
    sector = SECTORS[group // 10] if transport in (4, 5) and group // 10 < 8 \
        else lookup_station(group, 0, 0, transport)

    print(f"  {when}  {label} - {TRANSITION.get(transition, transition)}")
    print(f"    station   : {station}   (sector {sector}, id {group}-{sid}-{sub})")
    print(f"    provider  : {PROVIDER.get(provider, provider)} ({provider})")
    print(f"    transport={transport} transition={transition} "
          f"route={route[0] if route else None} contract="
          f"{f.get('EventContractPointer', (None,))[0]}")
    extra = {k: v[0] for k, v in sorted(f.items(), key=lambda kv: kv[1][1])}
    print(f"    fields    : {extra}")
    print()


def main(path):
    recs = read_records(path)
    print(f"{path}\n")
    for aid, label in (("2010", "Events"), ("2040", "Special events")):
        if aid not in recs:
            continue
        print(f"== {label} (AID {aid})")
        for fid in sorted(recs[aid]):
            print(f" FID {fid}:")
            describe(recs[aid][fid])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/mnt/e/Téléchargements/T.nfc")
