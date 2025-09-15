import re
import pandas as pd
import streamlit as st
import usaddress
from rapidfuzz import fuzz
from scourgify import normalize_address_record
from scourgify.normalize import format_address_record, UnParseableAddressError

# =========================================
# 1) ENTITY LISTS (paste your lists below)
# =========================================

progress_entities = [
   "Berm FW Residential Home Buyer Atlanta, LLC",
    "Berm FW Residential Home Buyer Charlotte, LLC",
    "Berm FW Residential Home Buyer Dallas, LLC",
    "Berm FW Residential Home Buyer Houston, LLC",
    "Berm FW Residential Home Buyer Indianapolis, LLC",
    "Berm FW Residential Home Buyer Jacksonville, LLC",
    "Berm FW Residential Home Buyer Nashville, LLC",
    "Berm FW Residential Home Buyer Orlando, LLC",
    "Berm FW Residential Home Buyer Phoenix, LLC",
    "Berm FW Residential Home Buyer Raleigh, LLC",
    "Berm FW Residential Home Buyer San Antonio, LLC",
    "Berm FW Residential Home Buyer Tampa, LLC",
    "Domus Novus Borrower 1, LLC",
    "FREO Progress, LLC",
    "FYR SFR Borrower, LLC",
    "FYR SFR Borrower, LLC (GS)",
    "Home SFR Borrower II, LLC",
    "Home SFR Borrower III, LLC",
    "Home SFR Borrower IV, LLC",
    "Home SFR Borrower, LLC",
    "KaeRuu Co",
    "Midway Exchange Borrower 1, LLC",
    "Midway Exchange Borrower 10, LLC",
    "Midway Exchange Borrower 12, LLC",
    "Midway Exchange Borrower 14, LLC",
    "Midway Exchange Borrower 2, LLC",
    "Midway Exchange Borrower 8, LLC",
    "Midway Exchange TRS 1, LLC",
    "Mile High Borrower 1 (Core), LLC",
    "Mile High Borrower 1 (Income), LLC",
    "Mile High Borrower 1 (Value), LLC",
    "Mile High TL Borrower 1 (Income), LLC",
    "Mile High TL Bwr 1 Core, LLC",
    "MSB Property Holdings LLC",
    "Olympus Borrower 1, LLC",
    "Olympus Borrower TL",
    "P2 Sub REIT 1 Borrower, LLC",
    "P2 Sub REIT 1 UFA, LLC",
    "P2 Sub REIT 2 UFA, LLC",
    "P2 Sub REIT 3 UFA, LLC",
    "P5 2021-2 Borrower, LLC",
    "PMN Residential Buyer, LLC",
    "Pretium SFR Holding, LLC",
    "Pretium SFR Holdings - PR3M",
    "PRNL Residential Buyer, LLC",
    "Progress Atlanta, LLC",
    "Progress Austin, LLC",
    "Progress Charlotte, LLC",
    "Progress Columbus, LLC",
    "Progress Dallas, LLC",
    "Progress Denver, LLC",
    "Progress Houston, LLC",
    "Progress Indianapolis, LLC",
    "Progress Jacksonville, LLC",
    "Progress Las Vegas, LLC",
    "Progress Memphis, LLC",
    "Progress Miami, LLC",
    "Progress Nashville, LLC",
    "Progress Orlando, LLC",
    "Progress Phoenix, LLC",
    "Progress Raleigh, LLC",
    "Progress Residential Borrower 1, LLC",
    "Progress Residential Borrower 10, LLC",
    "Progress Residential Borrower 11, LLC",
    "Progress Residential Borrower 12, LLC",
    "Progress Residential Borrower 13, LLC",
    "Progress Residential Borrower 14, LLC",
    "Progress Residential Borrower 15, LLC",
    "Progress Residential Borrower 16, LLC",
    "Progress Residential Borrower 17, LLC",
    "Progress Residential Borrower 18, LLC",
    "Progress Residential Borrower 19, LLC",
    "Progress Residential Borrower 2, LLC",
    "Progress Residential Borrower 20, LLC",
    "Progress Residential Borrower 21, LLC",
    "Progress Residential Borrower 23, LLC",
    "Progress Residential Borrower 24, LLC",
    "Progress Residential Borrower 25, LLC",
    "Progress Residential Borrower 3, LLC",
    "Progress Residential Borrower 4, LLC",
    "Progress Residential Borrower 5, LLC",
    "Progress Residential Borrower 6, LLC",
    "Progress Residential Borrower 7, LLC",
    "Progress Residential Borrower 8, LLC",
    "Progress Residential Borrower 9, LLC",
    "Progress Salt Lake City, LLC",
    "Progress San Antonio, LLC",
    "Progress Sarasota, LLC",
    "Progress Tampa 1, LLC",
    "Progress Tucson, LLC",
    "Property Owner 13, LLC",
    "RESI REO Sub, LLC",
    "Residential Home Buyer Atlanta, LLC",
    "Residential Home Buyer Austin, LLC",
    "Residential Home Buyer Charlotte, LLC",
    "Residential Home Buyer Columbus, LLC",
    "Residential Home Buyer Denver, LLC",
    "Residential Home Buyer Houston, LLC",
    "Residential Home Buyer Indianapolis, LLC",
    "Residential Home Buyer Jacksonville, LLC",
    "Residential Home Buyer Memphis, LLC",
    "Residential Home Buyer Nashville, LLC",
    "Residential Home Buyer Orlando, LLC",
    "Residential Home Buyer Phoenix, LLC",
    "Residential Home Buyer Raleigh, LLC",
    "Residential Home Buyer San Antonio, LLC",
    "Residential Home Buyer Sarasota, LLC",
    "Residential Home Buyer Tampa, LLC",
    "Residential Home Buyer Tucson, LLC",
    "Residential Home Buyer-E Atlanta, LLC",
    "Residential Home Buyer-E Charlotte, LLC",
    "Residential Home Buyer-E Columbus, LLC",
    "Residential Home Buyer-E Denver, LLC",
    "Residential Home Buyer-E Houston, LLC",
    "Residential Home Buyer-E Indianapolis, LLC",
    "Residential Home Buyer-E Memphis, LLC",
    "Residential Home Buyer-E Nashville, LLC",
    "Residential Home Buyer-E Orlando, LLC",
    "Residential Home Buyer-E Phoenix, LLC",
    "Residential Home Buyer-E Raleigh, LLC",
    "Residential Home Buyer-E San Antonio, LLC",
    "Residential Home Buyer-E Tampa, LLC",
    "Residential Home Buyer-E Tucson, LLC",
    "Residential Home Owner 1, LLC",
    "Residential Home Owner-E 1, LLC",
    "Seven Points Borrower, LLC",
    "SFR Fund VI Borrower, LLC",
    "SFR Investments V Borrower 1, LLC",
    "SFR Investments V Borrower TRS 1, LLC",
    "SFR Investments V UFA, LLC",
    "SFR V Tranche 3 Borrower, LLC",
    "SFR V Tranche 5 Borrower, LLC",
    "Talon FW Residential Home Buyer, LLC",
    "True North Borrower Florida, LLC",
    "True North Borrower Georgia, LLC",
    "True North Borrower Mississippi, LLC",
    "True North Borrower Nevada, LLC",
    "True North Borrower Tennessee, LLC",
    "True North Borrower Texas, LLC",
    "True North Property Owner A, LLC (2021-5)",
    "True North Property Owner B, LLC",
    "True North Property Owner C, LLC (2023-2)",
    "Verm FW Residential Home Buyer Atlanta, LLC",
    "Verm FW Residential Home Buyer Charlotte, LLC",
    "Verm FW Residential Home Buyer Columbus, LLC",
    "Verm FW Residential Home Buyer Dallas, LLC",
    "Verm FW Residential Home Buyer Denver, LLC",
    "Verm FW Residential Home Buyer Houston, LLC",
    "Verm FW Residential Home Buyer Indianapolis, LLC",
    "Verm FW Residential Home Buyer Jacksonville, LLC",
    "Verm FW Residential Home Buyer Memphis, LLC",
    "Verm FW Residential Home Buyer Nashville, LLC",
    "Verm FW Residential Home Buyer Orlando, LLC",
    "Verm FW Residential Home Buyer Phoenix, LLC",
    "Verm FW Residential Home Buyer Raleigh, LLC",
    "Verm FW Residential Home Buyer San Antonio, LLC",
    "Verm FW Residential Home Buyer Tampa, LLC",
    "Verm FW Residential Home Buyer Tucson, LLC",
    "Yamasa Co Affordable Housing",
    "Yamasa Co. LTD Mizuho-1",
    "Yamasa Co. LTD Mizuho-2",
    "Yamasa Co. LTD Mizuho-3",
    "Yamasa Co. LTD SMBC-1",
    "Yamasa Co. LTD SMBC-2",
    "Yamasa Co. LTD SMBC-3",
    "Yamasa Co. LTD SMBC-4",
    "Yamasa Co. LTD SMBC-5",
    "Yamasa Co. LTD Syndicate-1",
    "Yamasa Co. LTD Syndicate-2",
    "Yamasa Co. LTD Syndicate-3",
    "Yamasa Co. LTD Syndicate-4",
    "Yamasa Co. LTD Syndicate-5",
    "Yamasa Co. LTD Syndicate-7",
    "Yamasa Co., Ltd."
]

amherst_entities = [
      "ALTO Asset Company 1, LLC",
    "ALTO Asset Company 2, LLC",
    "ALTO Asset Company 3, LLC",
    "ALTO Asset Company 4, LLC",
    "ALTO Asset Company 5, LLC",
    "Amherst Group Properties, LLC",
    "AMLUX Allison Courtyard JV, LLC",
    "AMNL Asset Company 1 LLC",
    "AMNL Asset Company 2 LLC",
    "AMNL Asset Company 3 LLC",
    "ARMM Asset Company 1 LLC",
    "ARMM Asset Company 2 LLC",
    "ARMM Assets 2 LLC",
    "ARVM 5, LLC",
    "BAF 1 TRS, LLC",
    "BAF 1, LLC",
    "BAF 2 TRS, LLC",
    "BAF 2, LLC",
    "BAF 3, LLC",
    "BAF 4, LLC",
    "BAF Assets 2, LLC",
    "BAF Assets 3, LLC",
    "BAF Assets 4, LLC",
    "BAF Assets 5, LLC",
    "BAF Assets 6, LLC",
    "BAF Assets, LLC",
    "Bella Villas Owner, L.L.C.",
    "BTR Scattered Site Owner 2, L.L.C.",
    "CBAR Asset Company LLC",
    "CPI Amherst SFR Program Owner, LLC",
    "CPI/AMHERST SFR PROGRAM II OWNER, L.L.C.",
    "CPI/Amherst SFR Program II RS, L.L.C.",
    "CPI/Amherst SFR Program RS, L.L.C.",
    "EPH 2 ASSETS, LLC",
    "GVII RS TRS, LLC",
    "GVII-RS OwnerCo, LLC",
    "JEFF 1, LLC",
    "LAMCO Asset Company 1, LLC",
    "LAMCO Asset Company 2, LLC",
    "LAMCO TN Asset Company 1, LLC",
    "LAMCO TN Asset Company 2, LLC",
    "Mermaid Borrower LLC",
    "Mesa Verde Assets, LLC",
    "Montpelier Assets, LLC",
    "MUPR 3 ASSETS, LLC",
    "RH Evergreen Owner Co, LLC",
    "RH Partners EquityCo, LLC",
    "RH Partners OwnerCo 2, LLC",
    "RH Partners OwnerCo, LLC",
    "RH Partners Warehouse OwnerCo, LLC",
    "RHP Asset 1",
    "RHP Asset 2",
    "RHP OC 2 Asset 1",
    "RHP OC 2 Asset 2",
    "SRAM Pack I-A, L.L.C.",
    "SRAM Pack I-B, L.L.C.",
    "SRAM Pack I-C, L.L.C.",
    "SRAM Pack I-D, L.L.C.",
    "SRMZ 3 Holdings - Assets",
    "SRMZ 4 Asset Company 3, LLC",
    "Sunbelt Inv Asset Company",
    "VM Master Issuer, LLC",
    "VM Pronto, LLC",
    "VMP Lockhart Properties, LLC",
    "VMP Scattered Properties, LLC"
]

# =========================================
# 2) HELPERS
# =========================================

_CORP_SUFFIX_RE = re.compile(
    r'\b(l\.?l\.?c\.?|inc\.?|co\.?|ltd\.?|company|holdings?)\b',
    re.IGNORECASE
)

def clean_text(s: str) -> str:
    s = str(s or "")
    s = s.lower()
    s = re.sub(r'[,\.\-\(\)]', ' ', s)
    s = _CORP_SUFFIX_RE.sub(' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def best_entity_match(name: str, entities: list[str]):
    name_norm = clean_text(name)
    best_entity, best_score = "", 0
    for ent in entities:
        score = fuzz.token_set_ratio(name_norm, clean_text(ent))
        if score > best_score:
            best_entity, best_score = ent, score
    return best_entity, best_score

def owners_match_progress_amherst(owner: str, scraped_owner: str, entities: list[str], threshold: int = 80):
    ent_a, sc_a = best_entity_match(owner, entities)
    ent_b, sc_b = best_entity_match(scraped_owner, entities)

    if sc_a >= threshold and sc_b >= threshold and ent_a == ent_b:
        return True, ""
    return False, (
        f"Different/weak entity: Owner→'{ent_a}' ({sc_a}%), "
        f"Scraped→'{ent_b}' ({sc_b}%)"
    )

def owners_match_general(a: str, b: str, threshold: int = 80):
    sim = fuzz.token_set_ratio(clean_text(a), clean_text(b))
    if sim >= threshold:
        return True, ""
    else:
        return False, f"Too dissimilar ({sim}%)"

def compare_addresses(tp_addr: str, scraped_addr: str):
    try:
        fmt_tp = format_address_record(normalize_address_record(tp_addr or ""))
        fmt_sc = format_address_record(normalize_address_record((scraped_addr or "").replace('\n', ' ')))

        tp_tags, _ = usaddress.tag(fmt_tp)
        sc_tags, _ = usaddress.tag(fmt_sc)

        components = [
            'AddressNumber',
            'StreetName',
            'StreetNamePreDirectional',
            'StreetNamePostType',
            'StreetNamePostDirectional',
        ]

        mismatches = []
        for comp in components:
            if tp_tags.get(comp) != sc_tags.get(comp):
                mismatches.append(
                    f'{comp} mismatch: "{tp_tags.get(comp)}" vs "{sc_tags.get(comp)}"'
                )

        if mismatches:
            return False, "; ".join(mismatches)
        return True, ""

    except (UnParseableAddressError, Exception) as e:
        return False, f"Address parsing error: {e}"


# =========================================
# 3) STREAMLIT UI
# =========================================

st.set_page_config(page_title="Scraping Validator Tool", page_icon="📋", layout="wide")
st.title("📋 Scraping Validator Tool")
st.write("Upload a CSV with columns: **Address**, **Scraped Address**, **Owner**, **Scraped Owner**, **Org**")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

required_columns = ['Address', 'Scraped Address', 'Owner', 'Scraped Owner', 'Org']
validation_cols = [
    "Address Match", "Address Mismatch Reason",
    "Owner Match", "Owner Mismatch Reason"
]

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        st.error(f"❌ Missing required columns: {missing}")
        st.stop()

    df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x).fillna('')
    df = df.drop(columns=[c for c in validation_cols if c in df.columns])

    results = []
    for _, row in df.iterrows():
        # ---------- Address ----------
        addr_pass, addr_reason = compare_addresses(row['Address'], row['Scraped Address'])
        address_match = "Pass" if addr_pass else "Fail"
        address_reason = "" if addr_pass else addr_reason

        # ---------- Owner ----------
        org = str(row['Org']).strip().lower()
        owner = str(row['Owner'])
        scraped_owner = str(row['Scraped Owner'])

        if org == 'opendoor':
            owner_pass = True
            owner_reason = ""
        elif org == 'progress residential':
            owner_pass, owner_reason = owners_match_progress_amherst(owner, scraped_owner, progress_entities, threshold=80)
        elif org == 'amherst':
            owner_pass, owner_reason = owners_match_progress_amherst(owner, scraped_owner, amherst_entities, threshold=80)
        else:
            owner_pass, owner_reason = owners_match_general(owner, scraped_owner, threshold=80)

        owner_match = "Pass" if owner_pass else "Fail"
        owner_reason_out = "" if owner_pass else owner_reason

        results.append({
            "Address Match": address_match,
            "Address Mismatch Reason": address_reason,
            "Owner Match": owner_match,
            "Owner Mismatch Reason": owner_reason_out
        })

    result_df = pd.concat([df, pd.DataFrame(results)], axis=1)

    st.subheader("🔍 Validation Results")
    st.dataframe(result_df, use_container_width=True)

    csv_bytes = result_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Results as CSV",
        data=csv_bytes,
        file_name="validated_results.csv",
        mime="text/csv",
    )

else:
    st.info("Upload a CSV to begin.")
