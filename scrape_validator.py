import pandas as pd
import usaddress
from scourgify import normalize_address_record
from scourgify.normalize import format_address_record, UnParseableAddressError
from difflib import SequenceMatcher
import streamlit as st
from rapidfuzz import fuzz
import re

# Entity list
entities = [
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

# Fuzzy function
def fuzzy(text, text1):
    normalize = re.sub(r'[,\.\-\(\)]','',text).lower()
    normalize1 = re.sub(r'[,\.\-\(\)]','',text1).lower()
    similarity = fuzz.partial_ratio(normalize, normalize1)
    return similarity 

# Streamlit UI
st.title("📋 Scraping Validator Tool")
st.write("The file must contain the following columns: 'Address', 'Scraped Address', 'Owner', 'Scraped Owner', 'Org'")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    required_columns = ['Address', 'Scraped Address', 'Owner', 'Scraped Owner', 'Org']

    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"❌ Missing required columns: {missing_cols}")
    else:
        df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x).fillna('')
        results = []

        for _, row in df.iterrows():
            address_match = "Pass"
            address_mismatch_reason = ""
            owner_match = "Pass"
            owner_mismatch_reason = "Exact match"

            # Address comparison
            try:
                tp_addr = row['Address']
                scraped_addr = row['Scraped Address'].replace('\n', ' ')
                formatted_tp_addr = format_address_record(normalize_address_record(tp_addr))
                formatted_scraped_addr = format_address_record(normalize_address_record(scraped_addr))
                tp_tags, _ = usaddress.tag(formatted_tp_addr)
                scraped_tags, _ = usaddress.tag(formatted_scraped_addr)

                mismatch_reasons = []
                components = ['AddressNumber', 'StreetName', 'StreetNamePreDirectional', 'StreetNamePostType', 'StreetNamePostDirectional']
                for comp in components:
                    if tp_tags.get(comp) != scraped_tags.get(comp):
                        mismatch_reasons.append(f'{comp} mismatch: "{tp_tags.get(comp)}" vs "{scraped_tags.get(comp)}"')

                if mismatch_reasons:
                    address_match = "Fail"
                    address_mismatch_reason = "; ".join(mismatch_reasons)

            except (UnParseableAddressError, Exception) as e:
                address_match = "Fail"
                address_mismatch_reason = f"Address parsing error: {str(e)}"

            # Owner comparison
            org = row['Org'].strip().lower()

            if org == 'opendoor':
                owner_match = "Pass"
                owner_mismatch_reason = 'Passes due to OpenDoor Parcel'

            elif org == 'progress residential':
                best_owner_score = 0
                best_scraped_score = 0
                for entity in entities: 
                    best_owner_score = max(best_owner_score, fuzzy(row['Owner'], entity))
                    best_scraped_score = max(best_scraped_score, fuzzy(row['Scraped Owner'], entity))

                if best_owner_score > 80 and best_scraped_score > 80:
                    owner_match = 'Pass'
                    owner_mismatch_reason = f"Owner {round(best_owner_score,0)}%, Scraped Owner {round(best_scraped_score,0)}% match to entity list"
                else:
                    owner_match = 'Fail'
                    owner_mismatch_reason = f"Owner {round(best_owner_score,0)}%, Scraped Owner {round(best_scraped_score,0)}% — not both above 80%"
            else:
                tp_owner = row['Owner'].upper()
                scraped_owner = row['Scraped Owner'].upper()
                similarity = SequenceMatcher(None, tp_owner, scraped_owner).ratio()
                if similarity >= 0.75:
                    owner_match = "Pass"
                    owner_mismatch_reason = f"Similar enough ({similarity:.0%})"
                else:
                    owner_match = "Fail"
                    owner_mismatch_reason = f"Too dissimilar ({similarity:.0%})"

            results.append({
                "Address Match": address_match,
                "Address Mismatch Reason": address_mismatch_reason,
                "Owner Match": owner_match,
                "Owner Mismatch Reason": owner_mismatch_reason
            })

        result_df = pd.concat([df, pd.DataFrame(results)], axis=1)

        st.subheader("🔍 Validation Results")
        st.dataframe(result_df, use_container_width=True)

        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Results as CSV",
            data=csv,
            file_name="validated_results.csv",
            mime='text/csv',
        )
