import pandas as pd
import usaddress
from scourgify import normalize_address_record
from scourgify.normalize import format_address_record, UnParseableAddressError
from difflib import SequenceMatcher
import streamlit as st

st.title("📋 Scraping Validator Tool")

st.write("The file must contain the following columns: 'Address', 'Scraped Address', 'Owner', 'Scraped Owner'")


uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()  # Clean header spaces

    required_columns = ['Address', 'Scraped Address', 'Owner', 'Scraped Owner']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
    else:
        results = []

        for i, row in df.iterrows():
            address_match = "Pass"
            address_mismatch_reason = ""
            owner_match = "Pass"
            owner_mismatch_reason = "Exact match"

            # --- Address Comparison ---
            try:
                tp_addr = str(row['Address'])
                scraped_addr = str(row['Scraped Address']).replace('\n', ' ')
                formatted_tp_addr = format_address_record(normalize_address_record(tp_addr))
                formatted_scraped_addr = format_address_record(normalize_address_record(scraped_addr))

                tp_tags, _ = usaddress.tag(formatted_tp_addr)
                scraped_tags, _ = usaddress.tag(formatted_scraped_addr)

                mismatch_reasons = []

                if tp_tags.get('AddressNumber') != scraped_tags.get('AddressNumber'):
                    mismatch_reasons.append(
                        f'Street number mismatch: "{tp_tags.get("AddressNumber")}" vs "{scraped_tags.get("AddressNumber")}"'
                    )
                if tp_tags.get('StreetName') != scraped_tags.get('StreetName'):
                    mismatch_reasons.append(
                        f'Street name mismatch: "{tp_tags.get("StreetName")}" vs "{scraped_tags.get("StreetName")}"'
                    )
                if tp_tags.get('StreetNamePreDirectional') != scraped_tags.get('StreetNamePreDirectional'):
                    mismatch_reasons.append(
                        f'Pre-directional mismatch: "{tp_tags.get("StreetNamePreDirectional")}" vs "{scraped_tags.get("StreetNamePreDirectional")}"'
                    )
                if tp_tags.get('StreetNamePostType') != scraped_tags.get('StreetNamePostType'):
                    mismatch_reasons.append(
                        f'Suffix mismatch: "{tp_tags.get("StreetNamePostType")}" vs "{scraped_tags.get("StreetNamePostType")}"'
                    )
                if tp_tags.get('StreetNamePostDirectional') != scraped_tags.get('StreetNamePostDirectional'):
                    mismatch_reasons.append(
                        f'Post-directional mismatch: "{tp_tags.get("StreetNamePostDirectional")}" vs "{scraped_tags.get("StreetNamePostDirectional")}"'
                    )

                if mismatch_reasons:
                    address_match = "Fail"
                    address_mismatch_reason = "; ".join(mismatch_reasons)

            except UnParseableAddressError:
                address_match = "Fail"
                address_mismatch_reason = "Unparseable address"

            # --- Owner Comparison ---
            tp_owner = str(row['Owner']).upper().strip()
            scraped_owner = str(row['Scraped Owner']).upper().strip()
            similarity = SequenceMatcher(None, tp_owner, scraped_owner).ratio()

            if tp_owner == scraped_owner:
                owner_match = "Pass"
                owner_mismatch_reason = "Exact match"
            elif similarity >= 0.75:
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

        # Combine original data with results
        result_df = pd.concat([df, pd.DataFrame(results)], axis=1)

        st.subheader("🔍 Validation Results")
        st.dataframe(result_df, use_container_width=True)

        # Download button
        csv = result_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Results as CSV",
            data=csv,
            file_name="validated_results.csv",
            mime='text/csv',
        )
